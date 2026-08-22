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

    # Vercel only invokes GET, but handle HEAD gracefully
    def do_HEAD(self):
        self.do_GET()
