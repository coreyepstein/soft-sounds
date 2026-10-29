"""Describe each generated clip: loudness over time, separated events, and
whether it sounds pitched (music-like) or noisy (foley-like).

Usage: python3 analyze.py <file> [...]
"""
import subprocess, sys
import numpy as np

SR = 44100


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def frames(x, n=1024, hop=512):
    count = 1 + max(0, (len(x) - n) // hop)
    idx = np.arange(n)[None, :] + hop * np.arange(count)[:, None]
    return x[idx] * np.hanning(n)[None, :]


def describe(path):
    x = load(path)
    f = frames(x)
    rms = np.sqrt((f ** 2).mean(axis=1)) + 1e-9
    db = 20 * np.log10(rms)
    spec = np.abs(np.fft.rfft(f, axis=1)) + 1e-9
    flat = np.exp(np.log(spec).mean(axis=1)) / spec.mean(axis=1)  # 1 = noise, 0 = pure tone
    freqs = np.fft.rfftfreq(1024, 1 / SR)
    centroid = (spec * freqs).sum(axis=1) / spec.sum(axis=1)
    floor = np.percentile(db, 10)
    loud = db > max(floor + 18, db.max() - 30)
    # events: runs of loud frames separated by >=0.25s of quiet
    hop_s = 512 / SR
    events, start, quiet = [], None, 0
    for i, on in enumerate(loud):
        if on:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * hop_s >= 0.25:
                events.append((start, i - quiet))
                start, quiet = None, 0
    if start is not None:
        events.append((start, len(loud) - 1))
    active = loud.mean()
    print(f"{path.split('/')[-1]}: {len(x)/SR:.1f}s peak {db.max():.1f}dB floor {floor:.1f}dB "
          f"active {active*100:.0f}% events {len(events)} flatness(loud) {flat[loud].mean():.2f} "
          f"centroid(loud) {centroid[loud].mean():.0f}Hz")
    for s, e in events[:14]:
        seg = slice(s, e + 1)
        print(f"   {s*hop_s:6.2f}s-{e*hop_s:6.2f}s  len {(e-s+1)*hop_s*1000:5.0f}ms  peak {db[seg].max():5.1f}dB  "
              f"flat {flat[seg].mean():.2f}  centroid {centroid[seg].mean():5.0f}Hz")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        describe(p)
