#!/usr/bin/env python3
"""Pack the playable into a single self-contained dist/index.html
(inline PIXI + every asset as base64 data URIs). Re-run after any change."""
import base64, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "public")

# Assets the playable loads (keys = path the code passes to assetURL/pub)
ASSETS = [
    "background.webp", "frame.webp",
    # Match-3 board + gems + clear sparkles (from the original WoZ Magic Match)
    "m3_board.png",
    "m3_red.png", "m3_yellow.png", "m3_green.png", "m3_blue.png", "m3_purple.png",
    "m3_sparkle_red.png", "m3_sparkle_yellow.png", "m3_sparkle_green.png",
    "m3_sparkle_blue.png", "m3_sparkle_purple.png",
    "tinman_chest.webp", "tinman_arm.webp", "tinman_leg.webp",
    "tinman_head_0.webp", "tinman_head_1.webp", "tinman_head_2.webp",
    "tinman_head_3.webp", "tinman_head_4.webp", "tinman_head_5.webp",
    "nut_red.webp", "nut_blue.webp", "nut_gold.webp", "hand.webp",
    "woz-logo.webp", "play-now.webp", "tinman-hero.webp",
    # Match-3 sounds (from the original WoZ Magic Match)
    "audio/m3_bgm.mp3", "audio/m3_tap.mp3", "audio/m3_match.mp3",
    "audio/m3_pop.mp3", "audio/m3_sparkle.mp3", "audio/m3_finish.mp3",
]
MIME = {".webp": "image/webp", ".png": "image/png", ".mp3": "audio/mpeg"}

def data_uri(path):
    ext = os.path.splitext(path)[1]
    raw = open(path, "rb").read()
    return "data:" + MIME[ext] + ";base64," + base64.b64encode(raw).decode("ascii")

def safe_script(js):  # avoid breaking out of the <script> tag
    return js.replace("</script", "<\\/script")

amap = {k: data_uri(os.path.join(PUB, k)) for k in ASSETS}
assets_js = "window.__ASSETS=" + json.dumps(amap) + ";"

pixi = open(os.path.join(ROOT, "build", "pixi.min.js")).read()
html = open(os.path.join(ROOT, "wizard-of-oz-playable", "index.html")).read()

inline = ("<script>" + safe_script(pixi) + "</script>\n"
          "  <script>" + safe_script(assets_js) + "</script>")
html, n = re.subn(
    r'<script src="https://cdnjs\.cloudflare\.com/[^"]*pixi[^"]*"></script>',
    lambda m: inline, html, count=1)  # func repl: don't interpret backslashes
assert n == 1, "PIXI CDN <script> tag not found/replaced"

os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
out = os.path.join(ROOT, "dist", "index.html")
open(out, "w").write(html)

mb = os.path.getsize(out) / 1048576
print("packed %d assets -> dist/index.html  (%.2f MB)" % (len(ASSETS), mb))
missing = [k for k in ASSETS if not os.path.exists(os.path.join(PUB, k))]
if missing:
    print("WARNING missing:", missing)
