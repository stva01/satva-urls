from http.server import BaseHTTPRequestHandler
import json
import os
import base64
import urllib.request
import urllib.error

class handler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"status": "ok"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return self._send_json(400, {"error": "Missing request body."})

        try:
            body_data = self.rfile.read(content_length).decode("utf-8")
            payload = json.loads(body_data)
        except Exception as e:
            return self._send_json(400, {"error": f"Invalid JSON payload: {str(e)}"})

        slug = payload.get("slug", "").strip().strip("/").lower()
        target_url = payload.get("url", "").strip()
        user_secret = payload.get("secret", "").strip()
        custom_commit_msg = payload.get("commit_msg", "").strip()

        # Validate Inputs
        if not slug:
            return self._send_json(400, {"error": "Slug is required."})
        if not target_url:
            return self._send_json(400, {"error": "Target URL is required."})

        # Validate Admin PIN / Secret (Default: "0110")
        admin_secret = os.environ.get("ADMIN_SECRET", "0110")
        if user_secret != admin_secret:
            return self._send_json(403, {"error": "Invalid PIN passcode. Please enter the correct PIN."})

        github_token = (
            os.environ.get("GITHUB_TOKEN")
            or os.environ.get("GH_TOKEN")
            or os.environ.get("GITHUB_PAT")
            or os.environ.get("GITHUB_SECRET")
            or os.environ.get("SECRET")
        )
        github_repo = os.environ.get("GITHUB_REPO", "stva01/satva-urls")
        github_branch = os.environ.get("GITHUB_BRANCH", "master")

        if not github_token:
            return self._send_json(500, {
                "error": "GitHub token environment variable is not configured in Vercel settings (e.g. GITHUB_TOKEN)."
            })

        # 1. Fetch current redirects.json from GitHub REST API
        api_url = f"https://api.github.com/repos/{github_repo}/contents/redirects.json?ref={github_branch}"
        req_headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "satva-urls-app"
        }

        try:
            req = urllib.request.Request(api_url, headers=req_headers, method="GET")
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                current_sha = data["sha"]
                encoded_content = data.get("content", "")
                decoded_json_str = base64.b64decode(encoded_content).decode("utf-8")
                redirects = json.loads(decoded_json_str)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            return self._send_json(e.code, {
                "error": f"Failed to fetch redirects.json from GitHub: {e.reason}",
                "details": error_body
            })
        except Exception as e:
            return self._send_json(500, {"error": f"Error loading existing redirects: {str(e)}"})

        # 2. Append or update the slug
        redirects[slug] = target_url

        # Format updated JSON
        new_content_str = json.dumps(redirects, indent=2, ensure_ascii=False) + "\n"
        new_content_b64 = base64.b64encode(new_content_str.encode("utf-8")).decode("utf-8")

        commit_message = custom_commit_msg if custom_commit_msg else f"Add redirect: {slug}"

        # 3. Commit and push back to GitHub
        put_api_url = f"https://api.github.com/repos/{github_repo}/contents/redirects.json"
        update_payload = {
            "message": commit_message,
            "content": new_content_b64,
            "sha": current_sha,
            "branch": github_branch
        }

        try:
            put_req = urllib.request.Request(
                put_api_url,
                data=json.dumps(update_payload).encode("utf-8"),
                headers={**req_headers, "Content-Type": "application/json"},
                method="PUT"
            )
            with urllib.request.urlopen(put_req) as put_resp:
                put_data = json.loads(put_resp.read().decode("utf-8"))
                commit_info = put_data.get("commit", {})
                return self._send_json(200, {
                    "success": True,
                    "message": f"Successfully updated redirects.json with '{slug}'!",
                    "slug": slug,
                    "url": target_url,
                    "commit_sha": commit_info.get("sha", "")[:7],
                    "commit_msg": commit_message
                })
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            return self._send_json(e.code, {
                "error": f"Failed to commit to GitHub: {e.reason}",
                "details": error_body
            })
        except Exception as e:
            return self._send_json(500, {"error": f"Error committing to GitHub: {str(e)}"})
