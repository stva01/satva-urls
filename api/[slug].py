from http.server import BaseHTTPRequestHandler
import json
import os
import time

# ── Load redirects once at cold start ──────────────────────────────────────────
_REDIRECTS_PATH = os.path.join(os.path.dirname(__file__), "..", "redirects.json")
with open(_REDIRECTS_PATH, "r", encoding="utf-8") as f:
    _REDIRECTS: dict[str, str] = {k.lower(): v for k, v in json.load(f).items()}

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
        # Extract slug from the path, strip leading slash
        slug = self.path.lstrip("/").split("?")[0].split("#")[0].lower()

        # Treat empty slug as root
        if slug == "":
            slug = "/"

        # Log the hit (Vercel captures stdout in function logs)
        ua = self.headers.get("User-Agent", "-")
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"[HIT] slug={slug!r}  time={ts}  ua={ua}")

        destination = _REDIRECTS.get(slug)

        if destination:
            self.send_response(302)
            self.send_header("Location", destination)
            self.send_header("Cache-Control", "public, max-age=0, s-maxage=60")
            self.end_headers()
        else:
            body = _404_HTML.replace("{slug}", slug)
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body.encode())

    # Vercel only invokes GET, but handle HEAD gracefully
    def do_HEAD(self):
        self.do_GET()
