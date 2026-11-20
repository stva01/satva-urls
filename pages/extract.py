import re, base64, pathlib

SRC = "satva-portfolio.html"   # change this if your file has a different name

html = pathlib.Path(SRC).read_text(encoding="utf-8")
pathlib.Path("assets").mkdir(exist_ok=True)

names = ["char", "crowd"]   # the order they appear in your file
count = 0

def swap(m):
    global count
    name = f"assets/{names[count]}.webp"
    pathlib.Path(name).write_bytes(base64.b64decode(m.group(1)))
    count += 1
    return name

html = re.sub(r"data:image/webp;base64,([A-Za-z0-9+/=]+)", swap, html)
pathlib.Path("index-light.html").write_text(html, encoding="utf-8")
print(f"Done. Extracted {count} images. New file: index-light.html")