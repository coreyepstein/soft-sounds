"""Prompts for every source clip in the library.

VEO entries are short macro videos; only their audio is kept. Veo gives the most
natural close-mic foley. LYRIA entries are audio-only clips from Google's music
model; it is best at pitched sounds (chimes, swells) and long beds (drones).
"""

FOLEY = "Close-microphone ASMR foley only. No music, no voices, no ambience, silence between sounds."

VEO = {
    "paper": f"Extreme close-up macro shot in a silent room. A hand slowly turns four pages of a thick paper notebook, one at a time, pausing between each. {FOLEY}",
    "tap": f"Extreme close-up macro shot. A fingertip taps a smooth oak desk five times, slowly, with pauses. Soft woody knocks. {FOLEY}",
    "keys": f"Extreme close-up macro shot. Fingers press single keys on a quiet creamy mechanical keyboard, slow deliberate presses with gaps between them. Soft thocky clicks. {FOLEY}",
    "switch": f"Extreme close-up macro shot. A finger flips a small vintage metal toggle switch on, pauses, then off, three times. Crisp small clicks. {FOLEY}",
    "pop": f"Extreme close-up macro shot. Fingers slowly pop single bubbles on a sheet of bubble wrap, one at a time with pauses. Small soft pops. {FOLEY}",
    "whoosh": f"Extreme close-up macro shot. A hand sweeps quickly past the camera through the air holding a silk cloth, four times with pauses. Soft airy whooshes. {FOLEY}",
    "marble": f"Extreme close-up macro shot. Glass marbles are dropped one at a time into a small ceramic bowl, four times, pausing between each. Bright gentle clinks. {FOLEY}",
    "pen": f"Extreme close-up macro shot. A thumb clicks a metal ballpoint pen slowly, six times with pauses. Small precise clicks. {FOLEY}",
    "stone": f"Extreme close-up macro shot. Two smooth river stones are gently tapped together four times, pausing between taps. Soft dense clacks. {FOLEY}",
    "drop": f"Extreme close-up macro shot. Single water droplets fall one at a time into a still glass bowl of water, slowly, with pauses. Soft round plips. {FOLEY}",
    "cork": f"Extreme close-up macro shot. A small cork is pulled from a glass vial and pushed back in, three times. Soft hollow pops and squeaks. {FOLEY}",
}

NO_MUSIC = "Instrumental only. No drums, no vocals."
REPEAT = "Then two seconds of total silence. Repeat about eight times, each slightly different, always separated by two seconds of silence. Intimate, dry, no reverb tail."

LYRIA = {
    "success": f"{NO_MUSIC} A short soft rising two-note chime of warm glass bells, gentle and pleased, under one second. {REPEAT}",
    "error": f"{NO_MUSIC} A short soft descending two-note tone of muted felt piano, gentle and not alarming, under one second. {REPEAT}",
    "notify": f"{NO_MUSIC} A single soft rounded wooden marimba blip, warm and quiet, under half a second. {REPEAT}",
    "message": f"{NO_MUSIC} A tiny soft bubbly two-note pluck, like a kalimba, friendly and quiet, under half a second. {REPEAT}",
    "sparkle": f"{NO_MUSIC} A single tiny soft sparkle, a fingertip tap on a thin crystal glass, bright and gentle, under half a second. {REPEAT}",
    "drone-warm": f"{NO_MUSIC} No melody, no rhythm. A continuous warm, consonant, slowly breathing low drone with a soft pad, very calm and steady, like a quiet room tone for focus. Unchanging for the full length.",
    "drone-air": f"{NO_MUSIC} No melody, no rhythm. A continuous airy, high, shimmering ambient pad with gentle slow movement, soft and spacious, very calm. Unchanging for the full length.",
    "drone-deep": f"{NO_MUSIC} No melody, no rhythm. A continuous deep, soft sub hum with faint warm harmonics, steady and soothing, like a distant engine room heard through a wall. Unchanging for the full length.",
}
