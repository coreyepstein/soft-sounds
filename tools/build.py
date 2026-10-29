"""Cut finished sounds out of the raw generated clips.

For one-shot sounds it finds separate events (loud runs with at least 0.25 s of
quiet between them), keeps those of a sensible length, and writes the loudest
few as variants: sounds/<category>/<name>-1.mp3, -2.mp3, ...
For drones it cuts a 16 s seamless loop with a 2 s crossfade.

Every one-shot gets an 8 ms pre-roll, a 4 ms fade-in, an exponential fade-out
over its last 40 %, and is peak-normalized to -12 dBFS so it sits quiet by default.

Usage: python3 tools/build.py            (rebuild everything)
       python3 tools/build.py tap pop    (rebuild some)
"""
import json, os, subprocess, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW, OUT = os.path.join(ROOT, "raw"), os.path.join(ROOT, "sounds")
SR = 44100

# name -> (category, source file, min ms, max ms, variants)
ONESHOT = {
    "paper":   ("foley", "paper.mp4", 150, 1500, 4),
    "tap":     ("foley", "tap.mp4", 40, 600, 4),
    "keys":    ("foley", "keys.mp4", 30, 500, 4),
    "switch":  ("foley", "switch.mp4", 20, 500, 4),
    "pop":     ("foley", "pop.mp4", 20, 500, 4),
    "whoosh":  ("foley", "whoosh.mp4", 120, 1500, 4),
    "marble":  ("foley", "marble.mp4", 60, 1500, 4),
    "pen":     ("foley", "pen.mp4", 20, 500, 4),
    "stone":   ("foley", "stone.mp4", 30, 800, 4),
    "drop":    ("foley", "drop.mp4", 40, 1000, 4),
    "cork":    ("foley", "cork.mp4", 40, 1200, 4),
    "success": ("ui", "lyria-success.mp3", 150, 2000, 4),
    "error":   ("ui", "lyria-error.mp3", 150, 2000, 4),
    "notify":  ("ui", "lyria-notify.mp3", 80, 1500, 4),
    "message": ("ui", "lyria-message.mp3", 80, 1500, 4),
    "sparkle": ("ui", "lyria-sparkle.mp3", 60, 1500, 4),
}
DRONES = {"drone-warm": "lyria-drone-warm.mp3", "drone-air": "lyria-drone-air.mp3", "drone-deep": "lyria-drone-deep.mp3"}


def load(path, ch=1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x.reshape(-1, ch) if ch > 1 else x


def write_mp3(x, path, ch=1, kbps=96):
    tmp = path + ".f32"
    x.astype(np.float32).tofile(tmp)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", tmp,
                    "-c:a", "libmp3lame", "-b:a", f"{kbps}k", path], check=True)
    os.remove(tmp)


def events(x, hop=512, n=1024):
    count = 1 + max(0, (len(x) - n) // hop)
    idx = np.arange(n)[None, :] + hop * np.arange(count)[:, None]
    db = 20 * np.log10(np.sqrt(((x[idx] * np.hanning(n)) ** 2).mean(axis=1)) + 1e-9)
    floor = np.percentile(db, 10)
    loud = db > max(floor + 18, db.max() - 30)
    out, start, quiet, gap = [], None, 0, int(0.25 * SR / hop)
    for i, on in enumerate(loud):
        if on:
            start = i if start is None else start
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet >= gap:
                out.append((start * hop, (i - quiet + 1) * hop + n, db[start:i - quiet + 1].max()))
                start, quiet = None, 0
    if start is not None:
        out.append((start * hop, len(x), db[start:].max()))
    return out


def oneshot(name):
    cat, src, lo, hi, k = ONESHOT[name]
    path = os.path.join(RAW, src)
    if not os.path.exists(path):
        print(f"{name}: missing {src}, skipped")
        return []
    x = load(path)
    ev = [e for e in events(x) if lo <= (e[1] - e[0]) / SR * 1000 <= hi]
    ev = sorted(sorted(ev, key=lambda e: -e[2])[:k], key=lambda e: e[0])
    os.makedirs(os.path.join(OUT, cat), exist_ok=True)
    made = []
    for i, (a, b, _) in enumerate(ev, 1):
        a = max(0, a - int(0.008 * SR))
        b = min(len(x), b + int(0.06 * SR))
        seg = x[a:b] - x[a:b].mean()
        fin = int(0.004 * SR)
        seg[:fin] *= np.linspace(0, 1, fin)
        fout = max(int(0.03 * SR), int(len(seg) * 0.4))
        seg[-fout:] *= np.exp(np.linspace(0, -6, fout))
        seg *= 10 ** (-12 / 20) / (np.abs(seg).max() or 1)
        rel = f"{cat}/{name}-{i}.mp3"
        write_mp3(seg, os.path.join(OUT, rel))
        made.append({"name": f"{name}-{i}", "group": name, "category": cat, "file": rel, "ms": round(len(seg) / SR * 1000)})
    print(f"{name}: {len(made)} of {k} variants ({len(ev)} usable events)")
    return made


def drone(name, loop_s=16, xf_s=2):
    path = os.path.join(RAW, DRONES[name])
    if not os.path.exists(path):
        print(f"{name}: missing, skipped")
        return []
    x = load(path, 2)
    L, X = int(loop_s * SR), int(xf_s * SR)
    start = int(3 * SR)
    if len(x) < start + L + X:
        start = max(0, len(x) - L - X)
    body = x[start:start + L].copy()
    tail = x[start + L:start + L + X]
    ramp = np.linspace(0, 1, X)[:, None]
    body[:X] = body[:X] * ramp + tail * (1 - ramp)
    body *= 10 ** (-18 / 20) / (np.abs(body).max() or 1)
    os.makedirs(os.path.join(OUT, "drones"), exist_ok=True)
    rel = f"drones/{name}-loop.mp3"
    write_mp3(body.reshape(-1), os.path.join(OUT, rel), ch=2, kbps=160)
    print(f"{name}: {loop_s}s loop")
    return [{"name": f"{name}-loop", "group": name, "category": "drones", "file": rel, "ms": loop_s * 1000, "loop": True}]


def cards():
    """Card sounds (deal, flip, land, hover, dismiss, intro) are kept as finished files."""
    d = os.path.join(OUT, "cards")
    out = []
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith(".mp3"):
            x = load(os.path.join(d, f))
            out.append({"name": f[:-4], "group": f[:-4].rsplit("-", 1)[0], "category": "cards",
                        "file": f"cards/{f}", "ms": round(len(x) / SR * 1000)})
    return out


if __name__ == "__main__":
    want = sys.argv[1:] or list(ONESHOT) + list(DRONES)
    man_path = os.path.join(OUT, "manifest.json")
    manifest = json.load(open(man_path)) if os.path.exists(man_path) and sys.argv[1:] else []
    manifest = [m for m in manifest if m["group"] not in want]
    for n in want:
        manifest += oneshot(n) if n in ONESHOT else drone(n)
    manifest = [m for m in manifest if m["category"] != "cards"] + cards()
    manifest.sort(key=lambda m: (m["category"], m["name"]))
    json.dump(manifest, open(man_path, "w"), indent=1)
    print(f"{len(manifest)} sounds in manifest")
