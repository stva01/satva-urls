#!/usr/bin/env python3
"""Replaces the Experience section with an animated wave timeline built from the resume.
Usage: python3 apply_experience.py /path/to/satva-portfolio-light.html
Writes <name>.exp.html next to it; the original is untouched."""
import re, sys

SECTION = r"""<section id="experience" class="reveal">
      <div class="label">02 — Experience</div>
      <div class="work-top">
        <h2 class="work-title">Experience.</h2>
        <p class="tl-note">Backend, AI pipelines and DevOps, one internship at a time.</p>
      </div>
      <div class="tl" id="tl">
        <svg class="tl-svg" id="tlsvg" aria-hidden="true"><path id="tlpath" fill="none"></path></svg>
        <ol class="tl-cols">
          <li class="tl-item cur">
            <span class="tl-tag">Ongoing</span>
            <div class="tl-date">Present</div>
            <h3>Intern</h3>
            <div class="tl-co">IDfy</div>
            <p class="tl-desc">Internship at IDfy.</p>
          </li>
          <li class="tl-item">
            <div class="tl-date">March 2026 – July 2026</div>
            <h3>DevOps<br>Intern</h3>
            <div class="tl-co">Eagle Industrial Services Pvt. Ltd.</div>
            <div class="tl-loc">Mumbai</div>
            <p class="tl-desc">Built a GitHub Actions CI/CD pipeline for an 8-module microservice repo using matrix builds, and provisioned GCP infrastructure and IAM with Terraform.</p>
            <div class="tl-stack">GitHub Actions / Terraform / GCP / Docker</div>
          </li>
          <li class="tl-item">
            <div class="tl-date">June 2025 – August 2025</div>
            <h3>Backend Developer Intern</h3>
            <div class="tl-co">Senkusha Technologies</div>
            <div class="tl-loc">Mumbai</div>
            <p class="tl-desc">Architected a Redis Streams, Celery and FastAPI worker pipeline reaching 2.2x concurrency, 1.7x throughput and 150 RPS, plus a multi-agent RAG system translating across 98 regional language variants.</p>
            <div class="tl-stack">FastAPI / Redis Streams / Celery / RAG</div>
          </li>
          <li class="tl-item">
            <div class="tl-date">May 2023 – July 2023</div>
            <h3>Junior Developer Intern</h3>
            <div class="tl-co">Senkusha Technologies</div>
            <div class="tl-loc">Mumbai</div>
            <p class="tl-desc">Built a RabbitMQ and Go message queue for push, SMS and email delivery via Twilio and GoMail, and tuned PostgreSQL schemas with indexing and connection pooling.</p>
            <div class="tl-stack">Go / RabbitMQ / PostgreSQL</div>
          </li>
        </ol>
      </div>
    </section>"""

CSS = r"""
    /* ================= EXPERIENCE TIMELINE ================= */
    #experience { --W: min(1120px, calc(100vw - 2 * var(--pad))); width: var(--W); margin-left: calc(50% - var(--W) / 2); border-top: 0; padding-top: 64px; }
    .tl-note { font-size: 13px; color: var(--muted); max-width: 24ch; margin-top: 16px; line-height: 1.45; }
    .tl { position: relative; margin-top: 48px; }
    .tl-svg { position: absolute; left: 0; top: 0; overflow: visible; pointer-events: none; }
    .tl-svg path { stroke: var(--ink); stroke-width: 1.4; stroke-dashoffset: var(--L, 0); }
    .tl.go .tl-svg path { stroke-dashoffset: 0; transition: stroke-dashoffset 1.3s linear; }
    .tl-node .ring { fill: var(--bg); stroke: var(--ink); stroke-width: 1.4; }
    .tl-node .dot { fill: var(--ink); }
    .tl-node.cur .ring { fill: var(--ink); }
    .tl-node.cur .dot { fill: var(--bg); }
    .tl-node.up .ring { stroke-dasharray: 3 3; }
    .tl-pop { opacity: 0; transform: scale(0); transform-box: fill-box; transform-origin: center; }
    .tl.go .tl-pop { animation: tlpop .4s cubic-bezier(.34, 1.56, .64, 1) var(--d, 0s) both; }
    @keyframes tlpop { from { opacity: 0; transform: scale(0); } to { opacity: 1; transform: scale(1); } }
    .tl-cols { list-style: none; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 28px; padding-top: 70px; }
    .tl-item:nth-child(even) { margin-top: 56px; }
    .tl-item { opacity: 0; transform: translateY(14px); transition: opacity .45s ease, transform .45s ease; transition-delay: var(--d, 0s); }
    .tl.go .tl-item { opacity: 1; transform: none; }
    .tl-tag { display: inline-block; font: 500 11.5px/1 'Space Grotesk', sans-serif; background: #14171A; color: #F6F5F1; border-radius: 4px; padding: 6px 9px; margin-bottom: 10px; }
    .tl-item.up .tl-tag { background: transparent; color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
    .tl-date { font: 400 12.5px 'IBM Plex Mono', monospace; color: var(--muted); margin-bottom: 12px; }
    .tl-item h3 { font: 600 clamp(1.35rem, 2.1vw, 1.8rem)/1.08 'Space Grotesk', sans-serif; letter-spacing: -.02em; margin-bottom: 14px; }
    .tl-co { font: 500 1rem/1.3 'Space Grotesk', sans-serif; }
    .tl-loc { font-size: 12.5px; color: var(--muted); }
    .tl-desc { font-size: .9rem; line-height: 1.6; color: #4a4a44; margin-top: 12px; }
    .tl-stack { font: 400 11px/1.5 'IBM Plex Mono', monospace; color: var(--muted); margin-top: 12px; }
    @media (max-width: 860px) {
      #experience .work-top { flex-direction: column; gap: 0; }
      .tl-note { max-width: 34ch; }
      .tl { margin-top: 36px; }
      .tl-svg { display: none; }
      .tl-cols { grid-template-columns: 1fr; gap: 0; padding-top: 0; margin-left: 9px; border-left: 1.5px solid var(--ink); }
      .tl-item:nth-child(even) { margin-top: 0; }
      .tl-item { position: relative; padding: 0 0 38px 26px; }
      .tl-item::before { content: ""; position: absolute; left: -8.5px; top: 2px; width: 15px; height: 15px; border-radius: 50%; background: var(--bg); box-shadow: inset 0 0 0 1.5px var(--ink); }
      .tl-item.cur::before { background: var(--ink); }
    }
    @media (prefers-reduced-motion: reduce) {
      .tl-item { opacity: 1; transform: none; transition: none; }
      .tl-svg path { stroke-dashoffset: 0 !important; transition: none !important; }
      .tl-pop { opacity: 1; transform: none; animation: none !important; }
    }

    /* ================= SECTION SNAP SCROLL ================= */
    html { scroll-padding-top: 0; scroll-snap-type: y mandatory; }
    .hero2, #intro, #stack, #experience, #work, #beyond, .closing { scroll-snap-align: start; scroll-snap-stop: always; }
    .hwf-root { scroll-snap-align: end; }
    @media (min-width: 861px) {
      #intro, #stack, #experience, #work, #beyond {
        min-height: 100vh; min-height: 100svh; display: flex; flex-direction: column; justify-content: center;
        padding-top: 96px; padding-bottom: 64px;
      }
      #intro { align-items: flex-start; }
    }
    @media (max-width: 860px) { html { scroll-snap-type: y proximity; } }
    @media (prefers-reduced-motion: reduce) { html { scroll-snap-type: none; } }
"""

JS = r"""<script>
(function () {
  var tl = document.getElementById('tl');
  if (!tl) return;
  var svg = document.getElementById('tlsvg'), path = document.getElementById('tlpath');
  var items = [].slice.call(tl.querySelectorAll('.tl-item')), NS = 'http://www.w3.org/2000/svg';
  var DUR = 1.3, HI = 26, LO = 82, H = 110, made = [];
  var delay = function (i) { return (i / (items.length - 1) * DUR).toFixed(2) + 's'; };
  items.forEach(function (el, i) { el.style.setProperty('--d', (i / (items.length - 1) * DUR + 0.1).toFixed(2) + 's'); });

  function build() {
    made.forEach(function (n) { n.remove(); }); made = [];
    if (getComputedStyle(svg).display === 'none') return;
    var r = tl.getBoundingClientRect();
    var pts = items.map(function (el, i) {
      var b = el.getBoundingClientRect();
      return { x: b.left - r.left + Math.min(96, b.width * 0.42), y: i % 2 ? LO : HI };
    });
    svg.setAttribute('width', r.width); svg.setAttribute('height', H); svg.setAttribute('viewBox', '0 0 ' + r.width + ' ' + H);
    var d = 'M' + pts[0].x + ' ' + pts[0].y;
    for (var i = 1; i < pts.length; i++) {
      var a = pts[i - 1], b = pts[i], m = (a.x + b.x) / 2;
      d += ' C' + m + ' ' + a.y + ' ' + m + ' ' + b.y + ' ' + b.x + ' ' + b.y;
    }
    path.setAttribute('d', d);
    var L = path.getTotalLength();
    path.style.strokeDasharray = L; path.style.setProperty('--L', L);
    pts.forEach(function (p, i) {
      var g = document.createElementNS(NS, 'g');
      g.setAttribute('transform', 'translate(' + p.x + ' ' + p.y + ')');
      g.setAttribute('class', 'tl-node' + (items[i].classList.contains('cur') ? ' cur' : '') + (items[i].classList.contains('up') ? ' up' : ''));
      g.style.setProperty('--d', delay(i));
      g.innerHTML = '<g class="tl-pop"><circle class="ring" r="17"></circle><circle class="dot" r="3.5"></circle></g>';
      svg.appendChild(g); made.push(g);
    });
  }

  var tick = 0;
  function rebuild() { cancelAnimationFrame(tick); tick = requestAnimationFrame(build); }
  build();
  new ResizeObserver(rebuild).observe(tl);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(rebuild);

  // play when it scrolls into view, reset when it leaves so it replays
  new IntersectionObserver(function (es) {
    var e = es[0];
    if (e.intersectionRatio >= 0.3) tl.classList.add('go');
    else if (e.intersectionRatio === 0) tl.classList.remove('go');
  }, { threshold: [0, 0.3] }).observe(tl);
})();
</script>"""

JS += r"""
<script>
/* one wheel flick = one section (desktop). Touch and keyboard use CSS scroll-snap. */
(function () {
  var mq = matchMedia('(min-width: 861px) and (prefers-reduced-motion: no-preference)');
  var sel = '.hero2,#intro,#stack,#experience,#work,#beyond,.closing';
  var locked = false, last = 0, timer = 0, menu = document.getElementById('sidemenu');
  function pos() {
    var max = document.documentElement.scrollHeight - innerHeight, y = scrollY;
    var els = [].slice.call(document.querySelectorAll(sel)).map(function (e) {
      var r = e.getBoundingClientRect(); return { t: Math.min(Math.round(r.top + y), max), h: r.height };
    });
    var list = els.map(function (e) { return e.t; });
    if (max - list[list.length - 1] > 5) list.push(max);
    return { els: els, list: list };
  }
  addEventListener('wheel', function (e) {
    if (!mq.matches || e.ctrlKey || Math.abs(e.deltaX) > Math.abs(e.deltaY) || Math.abs(e.deltaY) < 2) return;
    if (menu && menu.classList.contains('open')) return;
    var now = performance.now(), dir = e.deltaY > 0 ? 1 : -1;
    if (locked) { e.preventDefault(); last = now; return; }
    var p = pos(), y = scrollY, to;
    for (var i = 0; i < p.els.length; i++) {               // section taller than the screen: scroll inside it normally
      var s = p.els[i];
      if (s.h > innerHeight + 8 && y >= s.t - 4 && y < s.t + s.h - 4) {
        if (dir > 0 && y + innerHeight < s.t + s.h - 8) return;
        if (dir < 0 && y > s.t + 8) return;
      }
    }
    if (dir > 0) { for (var a = 0; a < p.list.length; a++) if (p.list[a] > y + 4) { to = p.list[a]; break; } }
    else { for (var b = p.list.length - 1; b >= 0; b--) if (p.list[b] < y - 4) { to = p.list[b]; break; } }
    if (to === undefined) return;
    e.preventDefault(); locked = true; last = now;
    scrollTo({ top: to, behavior: 'smooth' });
    clearInterval(timer);
    timer = setInterval(function () {
      var t = performance.now();
      if ((t - last > 160 && Math.abs(scrollY - to) < 3) || t - last > 1500) { locked = false; clearInterval(timer); }
    }, 60);
  }, { passive: false });
})();
</script>"""

path = sys.argv[1] if len(sys.argv) > 1 else "satva-portfolio-light.html"
s = open(path, encoding="utf-8").read()
# re-runnable: strip any earlier version of the timeline (CSS + scripts) before rebuilding
MARK = "/* ================= EXPERIENCE TIMELINE ================= */"
k = s.find(MARK)
if k >= 0:
    e = s.find("</style>", k)
    if e > k:
        s = s[:k].rstrip(" \n") + "\n  " + s[e:]
s = re.sub(r"<script>(.*?)</script>\s*",
           lambda m: "" if ("document.getElementById('tl')" in m.group(1) or "one wheel flick" in m.group(1)) else m.group(0),
           s, flags=re.S)

s, n = re.subn(r'<section id="experience" class="reveal">.*?</section>', lambda m: SECTION, s, count=1, flags=re.S)
if n != 1:
    sys.exit('Could not find <section id="experience" class="reveal">.')
i = s.find("</style>")
if i < 0:
    sys.exit("Could not find </style>.")
s = s[:i] + CSS + "  " + s[i:]
j = s.rfind("</body>")
if j < 0:
    sys.exit("Could not find </body>.")
s = s[:j] + JS + "\n\n" + s[j:]

out = path.rsplit(".", 1)[0] + ".exp.html"
open(out, "w", encoding="utf-8").write(s)
print("Wrote", out)