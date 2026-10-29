# Soft Sounds

A free library of quiet interface sounds, close-mic foley and calm drones, made for apps, videos and prototypes.

Open `index.html` to hear every sound.

## What's in it

| Folder | Sounds |
| --- | --- |
| `sounds/ui` | success, error, notify, message, sparkle |
| `sounds/foley` | paper, tap, keys, switch, pop, whoosh, marble, pen, stone, drop, cork |
| `sounds/cards` | deal, flip, land, hover, dismiss, intro |
| `sounds/drones` | warm, air and deep loops, 16 seconds each, made to repeat without a seam |

Most sounds have three or four variants (`tap-1.mp3` to `tap-4.mp3`). Playing a random variant each time keeps repeated sounds from feeling mechanical.

One-shot sounds are mono MP3s, mostly under 10 KB, normalized to a quiet level (-12 dBFS peak) so they sit under other audio by default. Drones are stereo MP3s at -18 dBFS peak.

`sounds/manifest.json` lists every file with its group, category and length.

## Using a sound

```js
const variants = ["tap-1", "tap-2", "tap-3", "tap-4"];
const name = variants[Math.floor(Math.random() * variants.length)];
new Audio(`sounds/foley/${name}.mp3`).play();
```

Keep interface sounds optional. Give people a mute setting, and stay silent when the operating system asks for reduced motion.

## How the sounds were made

Every sound was generated with Google's Gemini API, then cut and leveled by the scripts in `tools/`:

- Foley comes from the audio track of short close-up videos made by Gemini Omni Flash.
- Interface tones and drones come from Lyria 3 Clip.
- `tools/prompts.py` has every prompt. `tools/gen.py` calls the API, `tools/build.py` finds the separate sounds in each clip and cuts them, and `tools/preview.py` writes `index.html`.

To make more, add a prompt to `tools/prompts.py` and an entry in `tools/build.py`, then run:

```bash
python3 tools/gen.py veo <name>     # foley
python3 tools/gen.py lyria <name>   # tones and drones
python3 tools/build.py <name>       # needs numpy and ffmpeg
python3 tools/preview.py
```

`gen.py` reads the API key from the `GEMINI_SFX_API_KEY` environment variable. Media generation needs a paid Gemini API project. The first full set cost about $4.

Google's audio models embed an inaudible SynthID watermark in everything they generate.

## License

CC0 1.0. Use the sounds for anything, commercial or not, with no attribution required. See `LICENSE`.
