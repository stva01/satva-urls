#!/usr/bin/env python3
"""Repairs the CURRENT (broken) satva-portfolio-light.html in place-safe fashion.
Usage: python3 fix_current.py /path/to/satva-portfolio-light.html
Writes <name>.fixed.html next to it. The original is not touched."""
import re, sys

MENU_JS = r'''<script>
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

ORIG_TICK = """  function tick(now) {
    raf = 0;
    var dt = Math.min(now - prev, 64); prev = now;
    var runCrowd = !reduce && inView && tabOn;
    var runGlyph = !reduce && tabOn;
    if (runCrowd) { gT += dt; if (!paused) { cT += dt; crowd.draw(cT); } }
    if (runGlyph && glyph) { gT += dt; glyph.draw(gT); }
    if (runGlyph || runCrowd) raf = requestAnimationFrame(tick);
  }
  function kick() { if (!raf && !reduce && tabOn) { prev = performance.now(); raf = requestAnimationFrame(tick); } }
"""

path = sys.argv[1] if len(sys.argv) > 1 else "satva-portfolio-light.html"
s = open(path, encoding="utf-8").read()
log = []

# 1. The hero headline lost its wrapper <div class="hero-copy go" id="herocopy"> (this is what broke the typography)
if 'id="herocopy"' not in s:
    s, n = re.subn(r'(<section class="hero2"[^>]*>\s*)(<h1>)',
                   lambda m: m.group(1) + '<div class="hero-copy go" id="herocopy">\n      ' + m.group(2), s, count=1)
    log.append("restored hero-copy wrapper" if n else "!! could not find hero <section>/<h1>")

# 2. The menu script was never added, so the button did nothing and the text-roll was never built
if "getElementById('menubtn')" not in s:
    j = s.rfind("</body>")
    s = s[:j] + MENU_JS + "\n\n" + s[j:]
    log.append("added menu script")

# 3. Restore the original animation loop (the edited one froze the glyph background after scrolling past the hero)
s, n = re.subn(r"  function tick\(now\) \{.*?\n  function kick\(\) \{[^\n]*\n", lambda m: ORIG_TICK, s, count=1, flags=re.S)
log.append("restored original tick/kick loop" if n else "(tick/kick block not found, left as is)")

# 4. Duplicate comment
s = re.sub(r"(<!-- Global glyph background -->\s*)+", "<!-- Global glyph background -->\n  ", s, count=1)

out = path.rsplit(".", 1)[0] + ".fixed.html"
open(out, "w", encoding="utf-8").write(s)
print("\n".join(log)); print("Wrote", out)
