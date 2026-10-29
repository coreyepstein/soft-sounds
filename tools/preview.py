"""Write index.html, a self-contained page to hear every sound in the library.

Usage: python3 tools/preview.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
manifest = json.load(open(os.path.join(ROOT, "sounds", "manifest.json")))
ORDER = ["ui", "foley", "cards", "drones"]
TITLES = {"ui": "Interface", "foley": "Foley", "cards": "Cards", "drones": "Drones"}

groups = {}
for m in manifest:
    groups.setdefault(m["category"], {}).setdefault(m["group"], []).append(m)

sections = []
for cat in [c for c in ORDER if c in groups] + [c for c in groups if c not in ORDER]:
    rows = []
    for g, items in groups[cat].items():
        btns = "".join(
            f'<button data-src="sounds/{m["file"]}"{" data-loop" if m.get("loop") else ""}>{m["name"].rsplit("-", 1)[-1] if not m.get("loop") else "play loop"}</button>'
            for m in items)
        rnd = "" if items[0].get("loop") else f'<button class="rnd" data-group="{g}">random</button>'
        rows.append(f'<div class="row"><span class="name">{g}</span><span class="btns">{btns}{rnd}</span></div>')
    sections.append(f'<section><h2>{TITLES.get(cat, cat)}</h2>{"".join(rows)}</section>')

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Soft Sounds</title>
<style>
:root {{ color-scheme: light dark; --bg:#f6f5f2; --fg:#1c1c1c; --mute:#6b6b6b; --line:#e2e0db; --btn:#fff; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#141414; --fg:#ededed; --mute:#9a9a9a; --line:#2a2a2a; --btn:#1e1e1e; }} }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 -apple-system,BlinkMacSystemFont,"Inter",sans-serif; }}
main {{ max-width:760px; margin:0 auto; padding:48px 20px 80px; }}
h1 {{ font-size:28px; margin:0 0 4px; letter-spacing:-0.01em; }}
p.lede {{ color:var(--mute); margin:0 0 28px; }}
h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:.08em; color:var(--mute); margin:32px 0 8px; }}
.row {{ display:flex; align-items:center; justify-content:space-between; gap:12px; padding:10px 0; border-top:1px solid var(--line); }}
.name {{ font-weight:600; }}
.btns {{ display:flex; flex-wrap:wrap; gap:6px; justify-content:flex-end; }}
button {{ font:inherit; font-size:13px; padding:5px 12px; border-radius:8px; border:1px solid var(--line); background:var(--btn); color:var(--fg); cursor:pointer; }}
button:hover {{ border-color:var(--mute); }}
button.on {{ background:var(--fg); color:var(--bg); }}
button.rnd {{ color:var(--mute); }}
.vol {{ display:flex; align-items:center; gap:10px; color:var(--mute); font-size:13px; }}
</style></head><body><main>
<h1>Soft Sounds</h1>
<p class="lede">Quiet interface sounds, close-mic foley and calm drones. Free to use. Click to listen.</p>
<label class="vol">Volume <input id="vol" type="range" min="0" max="1" step="0.05" value="0.8"></label>
{"".join(sections)}
</main>
<script>
const vol = document.getElementById('vol');
let loop = null, loopBtn = null;
function play(src) {{ const a = new Audio(src); a.volume = +vol.value; a.play(); }}
document.addEventListener('click', e => {{
  const b = e.target.closest('button'); if (!b) return;
  if (b.dataset.group) {{
    const all = [...b.parentElement.querySelectorAll('button[data-src]')];
    return play(all[Math.floor(Math.random() * all.length)].dataset.src);
  }}
  if (b.hasAttribute('data-loop')) {{
    if (loop) {{ loop.pause(); loopBtn.classList.remove('on'); loopBtn.textContent = 'play loop'; }}
    if (loopBtn === b) {{ loop = loopBtn = null; return; }}
    loop = new Audio(b.dataset.src); loop.loop = true; loop.volume = +vol.value; loop.play();
    loopBtn = b; b.classList.add('on'); b.textContent = 'stop'; return;
  }}
  play(b.dataset.src);
}});
vol.addEventListener('input', () => {{ if (loop) loop.volume = +vol.value; }});
</script></body></html>
"""
open(os.path.join(ROOT, "index.html"), "w").write(html)
print(f"index.html: {len(manifest)} sounds")
