"""Generate source clips with Google Lyria 3 Clip (chimes, drones) and Gemini Omni Flash (foley, via video audio).

Reads GEMINI_SFX_API_KEY from the environment (injected by `hq secrets exec`);
the key is never printed or written. Output goes to ./gen/, and a cost tally
goes to ./gen/cost.json.
"""
import base64, json, os, sys, time, urllib.request, urllib.error

KEY = os.environ["GEMINI_SFX_API_KEY"]
BASE = "https://generativelanguage.googleapis.com/v1beta"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "raw")
os.makedirs(OUT, exist_ok=True)
COST = os.path.join(OUT, "cost.json")
cost = json.load(open(COST)) if os.path.exists(COST) else {"items": [], "usd": 0.0}


def charge(what, usd):
    cost["items"].append({"what": what, "usd": usd})
    cost["usd"] = round(cost["usd"] + usd, 2)
    json.dump(cost, open(COST, "w"), indent=2)


def call(method, url, body=None):
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None)
    req.add_header("x-goog-api-key", KEY)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:400]
        raise SystemExit(f"HTTP {e.code}: {msg}")


def audio_blocks(o):
    if isinstance(o, dict):
        if o.get("type") == "audio" and "data" in o:
            yield o
        for v in o.values():
            yield from audio_blocks(v)
    elif isinstance(o, list):
        for v in o:
            yield from audio_blocks(v)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import LYRIA, VEO


def lyria(name):
    path = os.path.join(OUT, f"lyria-{name}.mp3")
    if os.path.exists(path):
        print(f"skip {path}")
        return
    d = call("POST", f"{BASE}/models/lyria-3-clip-preview:generateContent", {"contents": [{"parts": [{"text": LYRIA[name]}]}]})
    parts = [p for c in d.get("candidates", []) for p in c.get("content", {}).get("parts", []) if "inlineData" in p]
    if not parts:
        raise SystemExit(f"lyria {name}: no audio in response ({json.dumps(d)[:300]})")
    open(path, "wb").write(base64.b64decode(parts[-1]["inlineData"]["data"]))
    charge(f"lyria-3-clip {name}", 0.04)
    print(f"wrote {path}")


def veo(name):
    """Foley source: a short 360p video from Gemini Omni Flash; only its audio is used."""
    path = os.path.join(OUT, f"{name}.mp4")
    if os.path.exists(path):
        print(f"skip {path}")
        return
    req = urllib.request.Request(f"{BASE}/interactions", method="POST", data=json.dumps({
        "model": "gemini-omni-1.1-flash",
        "input": VEO[name],
        "response_format": {"type": "video", "resolution": "360p"},
        "store": False,
    }).encode())
    req.add_header("x-goog-api-key", KEY)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=1200) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"omni {name}: HTTP {e.code}: {e.read().decode()[:400]}")
    vids = [o for o in walk(d) if o.get("type") == "video" and "data" in o]
    if not vids:
        raise SystemExit(f"omni {name}: no video ({json.dumps(d)[:400]})")
    open(path, "wb").write(base64.b64decode(vids[0]["data"]))
    json.dump({k: v for k, v in d.items() if k not in ("steps", "outputs")}, open(path + ".meta.json", "w"), indent=1)
    charge(f"gemini-omni-1.1-flash 360p {name}", round(d.get("usage", {}).get("total_output_tokens", 0) * 17.5 / 1e6, 2))
    print(f"wrote {path}")


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


if __name__ == "__main__":
    which = sys.argv[1]
    for n in sys.argv[2:]:
        (lyria if which == "lyria" else veo)(n)
    print(f"total so far ${cost['usd']:.2f}")
