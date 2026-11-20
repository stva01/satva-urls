#!/usr/bin/env python3
"""Applies the new pill navbar, side menu and bolder hero to your ORIGINAL index.html.
Usage:  python3 apply_update.py index.html      (writes index.updated.html, leaves the original untouched)
Run it on the version from BEFORE your agent edited anything (git / backup)."""
import re, sys

NAV = r'''<div class="pill">
  <a class="pill-brand" href="#top">Satva</a>
  <button class="pill-btn" id="menubtn" type="button" aria-expanded="false" aria-controls="sidemenu" aria-label="Open menu">
    <span class="dots"><i></i><i></i><i></i></span>
    <span class="x"></span>
  </button>
</div>

<div class="side" id="sidemenu" aria-hidden="true">
  <div class="side-overlay" id="sideoverlay"></div>
  <div class="side-panel">
    <div class="side-layer l1"></div>
    <div class="side-layer l2"></div>
    <div class="side-layer l3"></div>
    <div class="side-body">
      <ul class="side-list">
        <li><a href="#top" style="--i:0"><span class="num">01</span><span class="roll" data-roll>Home</span></a></li>
        <li><a href="#stack" style="--i:1"><span class="num">02</span><span class="roll" data-roll>Tech Stack</span></a></li>
        <li><a href="#experience" style="--i:2"><span class="num">03</span><span class="roll" data-roll>Experience</span></a></li>
        <li><a href="#work" style="--i:3"><span class="num">04</span><span class="roll" data-roll>Work</span></a></li>
        <li><a href="#beyond" style="--i:4"><span class="num">05</span><span class="roll" data-roll>Beyond</span></a></li>
      </ul>
      <div class="side-foot">
        <a href="mailto:satvalite@gmail.com">Email</a>
        <a href="https://github.com/stva01" target="_blank" rel="noopener">GitHub</a>
        <a href="https://www.linkedin.com/in/satva-shah/" target="_blank" rel="noopener">LinkedIn</a>
      </div>
    </div>
  </div>
</div>'''

CSS = r'''/* ================= HERO: bigger + bolder ================= */
.hero2 { height: 100vh; height: 100svh; min-height: 640px; }
.hero-copy { top: clamp(84px, 13vh, 150px); }
.hero-copy h1 {
  font-size: clamp(3rem, min(14vw, 19.5vh), 12rem);
  font-weight: 700;
  line-height: .86;
  letter-spacing: -.05em;
  -webkit-text-stroke: .025em var(--ink);   /* extra weight beyond Space Grotesk 700 */
}
.hero-copy h1 i { font-weight: 400; font-size: .8em; }
.hero-meta { max-width: min(1500px, 94vw); margin-top: clamp(10px, 2vh, 24px); }
.hero-meta .c { font-size: clamp(1.8rem, 4vw, 3.4rem); font-weight: 700; letter-spacing: -.03em; }
.hero-meta .tag { font: 500 clamp(.8rem, 1.6vw, 1.4rem)/1.2 'Space Grotesk', sans-serif; letter-spacing: -.01em; }
@media (max-width: 600px) {
  .hero-copy h1 { font-size: clamp(2.6rem, 15.5vw, 5rem); }
  .hero-meta .tag { font-size: .8rem; }
}

/* ================= PILL NAVBAR ================= */
.pill {
  position: fixed; top: 16px; left: 50%; transform: translateX(-50%); z-index: 200;
  width: min(440px, calc(100vw - 32px));
  display: flex; align-items: center; justify-content: space-between;
  padding: 9px 9px 9px 22px;
  background: #131313; color: #F6F5F1; border-radius: 18px;
  box-shadow: 0 10px 30px -12px rgba(0,0,0,.45), inset 0 0 0 1px rgba(255,255,255,.06);
}
.pill-brand { font: 700 1.35rem/1 'Space Grotesk', sans-serif; letter-spacing: -.02em; color: #fff; text-decoration: none; }
.pill-btn {
  all: unset; box-sizing: border-box; position: relative; width: 48px; height: 42px;
  display: grid; place-items: center; border-radius: 10px; background: #F6F5F1; cursor: pointer;
  transition: background .2s ease;
}
.pill-btn:hover { background: #7FBFA8; }
.pill-btn:focus-visible { outline: 2px solid #7FBFA8; outline-offset: 3px; }
.dots { display: flex; gap: 4px; transition: transform .5s cubic-bezier(.65,.01,.05,.99), opacity .25s ease; }
.dots i { width: 5px; height: 5px; border-radius: 50%; background: #131313; }
.x { position: absolute; width: 18px; height: 18px; opacity: 0; transform: rotate(-90deg);
  transition: transform .5s cubic-bezier(.65,.01,.05,.99), opacity .25s ease; }
.x::before, .x::after { content: ""; position: absolute; left: 0; top: 50%; width: 100%; height: 2px; margin-top: -1px; background: #131313; border-radius: 2px; }
.x::before { transform: rotate(45deg); }
.x::after { transform: rotate(-45deg); }
.pill-btn[aria-expanded="true"] .dots { opacity: 0; transform: rotate(90deg); }
.pill-btn[aria-expanded="true"] .x { opacity: 1; transform: none; }

/* ================= SIDE MENU (open/close motion) ================= */
.side { position: fixed; inset: 0; z-index: 150; visibility: hidden; transition: visibility 0s .7s; }
.side.open { visibility: visible; transition-delay: 0s; }
.side-overlay { position: absolute; inset: 0; background: rgba(20,23,26,.45); opacity: 0; transition: opacity .4s ease; }
.side.open .side-overlay { opacity: 1; }
.side-panel { position: absolute; top: 0; right: 0; bottom: 0; width: min(560px, 100vw); overflow: hidden; color: #F6F5F1; }
.side-layer { position: absolute; inset: 0; transform: translateX(101%); transition: transform .45s cubic-bezier(.65,.01,.05,.99); }
.side-layer.l1 { background: #7FBFA8; }
.side-layer.l2 { background: #2F5D50; }
.side-layer.l3 { background: #14171A; }
.side.open .side-layer { transform: none; transition-duration: .575s; }
.side.open .l2 { transition-delay: .12s; }
.side.open .l3 { transition-delay: .24s; }

.side-body { position: relative; z-index: 1; height: 100%; display: flex; flex-direction: column; padding: 104px 44px 32px; }
.side-list { list-style: none; flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 6px; }
.side-list li { overflow: hidden; padding: .02em 0; }
.side-list a {
  display: flex; align-items: baseline; gap: 16px; color: #F6F5F1; text-decoration: none;
  transform: translateY(140%) rotate(10deg); transform-origin: 0 100%; transition: transform .3s ease;
}
.side.open .side-list a { transform: none; transition: transform .7s cubic-bezier(.65,.01,.05,.99) calc(.35s + var(--i) * .05s); }
.num { font: 500 12px 'IBM Plex Mono', monospace; letter-spacing: .06em; color: #7FBFA8; }
.side-foot {
  display: flex; flex-wrap: wrap; gap: 22px; font: 500 12px 'IBM Plex Mono', monospace; letter-spacing: .14em; text-transform: uppercase;
  opacity: 0; transition: opacity .2s ease;
}
.side.open .side-foot { opacity: .85; transition: opacity .5s ease .8s; }
.side-foot a { color: inherit; text-decoration: none; }
.side-foot a:hover { text-decoration: underline; text-underline-offset: 4px; }

/* ================= TEXT-ROLL HOVER ================= */
.roll {
  position: relative; display: block; overflow: hidden; padding-bottom: .06em;
  font: 700 clamp(2.6rem, 7vw, 4.2rem)/.92 'Space Grotesk', sans-serif; letter-spacing: -.035em; text-transform: uppercase;
}
.roll span span { display: inline-block; transition: transform .6s ease-in-out; transition-delay: var(--d, 0s); }
.roll-b { position: absolute; inset: 0; color: #7FBFA8; }
.roll-b span { transform: translateY(100%); }
.side-list a:hover .roll-a span, .side-list a:focus-visible .roll-a span { transform: translateY(-100%); }
.side-list a:hover .roll-b span, .side-list a:focus-visible .roll-b span { transform: none; }
.side-list a:focus-visible { outline: 2px solid #7FBFA8; outline-offset: 4px; }

@media (max-width: 480px) { .side-body { padding: 96px 28px 28px; } }
@media (prefers-reduced-motion: reduce) {
  .side *, .side, .dots, .x { transition: none !important; }
  .side-list a { transform: none; }
}'''

JS = r'''<script>
(function () {
  var side = document.getElementById('sidemenu');
  var btn = document.getElementById('menubtn');
  var overlay = document.getElementById('sideoverlay');
  if (!side || !btn) return;

  // Build the text-roll: two stacked copies of each word, letter by letter, staggered from the centre.
  document.querySelectorAll('[data-roll]').forEach(function (el) {
    var t = el.textContent.trim(), n = t.length;
    function letters() {
      return t.split('').map(function (ch, i) {
        var d = (0.035 * Math.abs(i - (n - 1) / 2)).toFixed(3);
        return '<span style="--d:' + d + 's">' + (ch === ' ' ? '&nbsp;' : ch) + '</span>';
      }).join('');
    }
    el.innerHTML = '<span class="roll-a">' + letters() + '</span><span class="roll-b" aria-hidden="true">' + letters() + '</span>';
    var a = el.closest('a'); if (a) a.setAttribute('aria-label', t);
  });

  function set(open) {
    side.classList.toggle('open', open);
    side.setAttribute('aria-hidden', String(!open));
    btn.setAttribute('aria-expanded', String(open));
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.documentElement.style.overflow = open ? 'hidden' : '';
  }
  btn.addEventListener('click', function () { set(!side.classList.contains('open')); });
  overlay.addEventListener('click', function () { set(false); });
  side.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { set(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') set(false); });
})();
</script>'''

src_path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
s = open(src_path, encoding="utf-8").read()
if 'class="pill"' in s:
    sys.exit("This file already has the new navbar. Run the script on the original file.")

# 1. replace the old <header>...</header> with the new navbar + side menu
s, n = re.subn(r"<header>.*?</header>", lambda m: NAV, s, count=1, flags=re.S)
if n != 1:
    sys.exit("Could not find the old <header> block.")

# 2. CSS at the very end of the <style> block
i = s.find("</style>")
if i < 0:
    sys.exit("Could not find </style>.")
s = s[:i] + "\n" + CSS + "\n  " + s[i:]

# 3. JS just before </body>
j = s.rfind("</body>")
if j < 0:
    sys.exit("Could not find </body>.")
s = s[:j] + JS + "\n\n" + s[j:]

out = src_path.rsplit(".", 1)[0] + ".updated.html"
open(out, "w", encoding="utf-8").write(s)
print("Wrote", out)