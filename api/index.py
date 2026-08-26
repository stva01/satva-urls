from http.server import BaseHTTPRequestHandler
import json
import os
import time
import urllib.parse

# ── Load redirects once at cold start ──────────────────────────────────────────
_REDIRECTS_PATH = os.path.join(os.path.dirname(__file__), "..", "redirects.json")
with open(_REDIRECTS_PATH, "r", encoding="utf-8") as f:
    _REDIRECTS: dict[str, str] = {k.lower(): v for k, v in json.load(f).items()}

_CONTACT_FOOTER = """
<style>
  .site-contact-footer { margin-top: 3rem; padding: 1.5rem 0; border-top: 1px solid #d1d5db; color: #4b5563; font: 0.9rem/1.5 system-ui, sans-serif; }
  .site-contact-footer__inner { max-width: 70rem; margin: 0 auto; padding: 0 1.5rem; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 0.75rem 1.5rem; }
  .site-contact-footer__links { display: flex; flex-wrap: wrap; gap: 1rem; }
  .site-contact-footer a { color: inherit; }
</style>
<footer class="site-contact-footer" data-contact-footer>
  <div class="site-contact-footer__inner">
    <span>© 2026 Satva Shah</span>
    <nav class="site-contact-footer__links" aria-label="Contact links">
      <a href="mailto:satvalite@gmail.com">Email</a>
      <a href="https://github.com/stva01" target="_blank" rel="noopener">GitHub</a>
      <a href="https://www.linkedin.com/in/satva-shah/" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://medium.com/@satvashah" target="_blank" rel="noopener">Medium</a>
    </nav>
  </div>
</footer>
"""


def _with_contact_footer(html: str) -> str:
    """Add the shared contact footer to locally served pages that do not define one."""
    if "data-contact-footer" in html:
        return html
    return html.replace("</body>", f"{_CONTACT_FOOTER}</body>")

# ── 404 page ───────────────────────────────────────────────────────────────────
_404_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>404 — Link Not Found</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: #0a0a0a;
      color: #e5e5e5;
    }
    .card {
      text-align: center;
      max-width: 440px;
      padding: 3rem 2rem;
    }
    .code {
      font-size: 6rem;
      font-weight: 800;
      background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      line-height: 1;
    }
    .msg {
      margin-top: 1rem;
      font-size: 1.15rem;
      color: #a3a3a3;
      line-height: 1.6;
    }
    .slug-name {
      font-family: 'SF Mono', 'Fira Code', monospace;
      background: #1e1e2e;
      padding: 2px 8px;
      border-radius: 4px;
      color: #c084fc;
    }
    a {
      display: inline-block;
      margin-top: 2rem;
      padding: 0.65rem 1.6rem;
      border-radius: 8px;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      color: #fff;
      text-decoration: none;
      font-weight: 600;
      transition: opacity 0.2s;
    }
    a:hover { opacity: 0.85; }
  </style>
</head>
<body>
  <div class="card">
    <div class="code">404</div>
    <p class="msg">
      The link <span class="slug-name">/{slug}</span> doesn&rsquo;t exist.<br>
      Double-check the URL and try again.
    </p>
    <a href="https://www.linkedin.com/in/satva01/">Visit my LinkedIn &rarr;</a>
  </div>
</body>
</html>"""


class handler(BaseHTTPRequestHandler):
    """Vercel Python serverless handler — redirects or 404s."""

    def do_GET(self):
        # Vercel rewrites the URL to /api/index.py?slug=...
        # Extract slug from the query string instead of the path
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        
        # 'slug' comes from the rewrite rule `/(.*)` -> `/api/index.py?slug=$1`
        slug = qs.get("slug", [""])[0].strip("/").lower()

        # Treat empty slug as root
        if slug == "":
            slug = "/"

        # Log the hit (Vercel captures stdout in function logs)
        ua = self.headers.get("User-Agent", "-")
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"[HIT] slug={slug!r}  time={ts}  ua={ua}")

        destination = _REDIRECTS.get(slug)

        if destination:
            if destination.endswith(".html"):
                # Serve the HTML file from the 'pages' directory
                pages_dir = os.path.join(os.path.dirname(__file__), "..", "pages")
                html_path = os.path.join(pages_dir, destination)
                
                try:
                    with open(html_path, "r", encoding="utf-8") as html_file:
                        content = html_file.read()
                        
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Cache-Control", "public, max-age=0, s-maxage=60")
                    self.end_headers()
                    self.wfile.write(_with_contact_footer(content).encode("utf-8"))
                except FileNotFoundError:
                    # Fallback to 404 if the HTML file is missing
                    self._send_404(slug)
            else:
                # Standard URL redirect
                self.send_response(302)
                self.send_header("Location", destination)
                self.send_header("Cache-Control", "public, max-age=0, s-maxage=60")
                self.end_headers()
        else:
            self._send_404(slug)

    def _send_404(self, slug):
        body = _with_contact_footer(_404_HTML.replace("{slug}", slug))
        self.send_response(404)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body.encode())

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
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

        # Validate PIN passcode (Default: "0110")
        admin_secret = os.environ.get("ADMIN_SECRET", "0110")
        if user_secret != admin_secret:
            return self._send_json(403, {"error": "Invalid PIN passcode. Please enter the correct PIN (0110)."})

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
                "error": "GITHUB_TOKEN is not configured in Vercel environment variables."
            })

        import base64
        import urllib.request
        import urllib.error

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
                "error": f"GitHub API error fetching file: {e.reason}",
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

    # Vercel only invokes GET, but handle HEAD gracefully
    def do_HEAD(self):
        self.do_GET()

