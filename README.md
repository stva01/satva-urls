# satva-urls

A minimal URL forwarding service on Vercel. Clean short URLs → long destination URLs.

> **`satva.dev/railvision`** → `https://github.com/stva01/railvision-ai`

---

## How it works

| File | Purpose |
|---|---|
| `redirects.json` | Slug → destination URL mapping (the "database"). Can also point to local `.html` files in `pages/` |
| `api/index.py` | Python serverless function — reads the JSON, redirects, serves local HTML, or 404s |
| `vercel.json` | Routes every incoming path to the serverless function |

---

## Add a new redirect or HTML page

1. Open `redirects.json`.
2. Add one line:

   ```json
   "my-new-slug": "https://example.com/some-long-url",
   "my-page": "mypage.html"
   ```
   *(If pointing to a `.html` file, it will serve that file from the `pages/` directory instead of redirecting.)*

3. Commit and push to `main`:

   ```bash
   git add redirects.json
   git commit -m "Add redirect: my-new-slug"
   git push
   ```

4. Vercel auto-deploys. Live within ~30 seconds.

> **Slugs are case-insensitive** — `satva.dev/RailVision` and `satva.dev/railvision` both work.

---

## Local testing

### Prerequisites

- [Vercel CLI](https://vercel.com/docs/cli) installed globally:

  ```bash
  npm i -g vercel
  ```

### Run locally

```bash
vercel dev
```

This starts a local dev server (usually `http://localhost:3000`). Test:

```
http://localhost:3000/railvision      → should 302 redirect
http://localhost:3000/nonexistent     → should show 404 page
http://localhost:3000/                → should redirect to default landing
```

---

## Deployment

### 1. Push to GitHub

```bash
cd satva-urls
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<your-username>/satva-urls.git
git push -u origin main
```

### 2. Import into Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New…** → **Project**.
2. Import your `satva-urls` GitHub repo.
3. Framework Preset: **Other** (auto-detected).
4. Click **Deploy**.

### 3. Add custom domain

1. In Vercel → your project → **Settings** → **Domains**.
2. Add `satva.dev`.
3. Vercel will show DNS records to configure. At your registrar:
   - **Option A (recommended):** Point nameservers to Vercel's nameservers.
   - **Option B:** Add the `A` record (`76.76.21.21`) and/or `CNAME` record Vercel provides.
4. Wait for DNS propagation + SSL provisioning (~1-10 minutes).

### 4. Verify

```bash
curl -I https://satva.dev/railvision
# Should return HTTP 302 with Location header
```

---

## Logging

Every request logs to stdout (visible in **Vercel Dashboard → Functions → Logs**):

```
[HIT] slug='railvision'  time=2026-08-19T10:15:30Z  ua=Mozilla/5.0 ...
```

---

## Stretch goals (not yet built)

- **Click analytics** — Vercel KV (Upstash Redis) counter per slug.
- **`/stats` endpoint** — Password-protected dashboard of top redirects.
- **QR codes** — Auto-generate QR code image per slug.

---

## License

MIT
