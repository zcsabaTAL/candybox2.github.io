#!/usr/bin/env python3
import os
import sys
import json
import base64
import subprocess
import urllib.request
import urllib.error

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "blacksmith"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Select mode: "appalachian" (default) or "original"
MODE = sys.argv[1] if len(sys.argv) > 1 else "appalachian"

LINES = [
    {
        "filename": "mapVillageForgeIntroductionSpeech.wav",
        "appalachian": "Howdy! Ah'm a blacksmith. Ah kin sell ye various weapons an' pieces o' equipment.",
        "original": "Hi! I'm a blacksmith. I can sell you various weapons and pieces of equipment."
    },
    {
        "filename": "mapVillageForgeIntroductionSpeechNoMoreToSell.wav",
        "appalachian": "Howdy! Ah'm a blacksmith. Sadly, Ah got nothin' more to sell ye. Come on back later, reckon?",
        "original": "Hi! I'm a blacksmith. Sadly, I have nothing more to sell. Come back later, maybe?"
    },
    {
        "filename": "mapVillageForgeBuyWoodenSwordSpeech.wav",
        "appalachian": "Much obliged for buyin'! This wooden sword is mighty weak, but it's a fair start.",
        "original": "Thanks for buying! This wooden sword is quite weak, but it's a start."
    },
    {
        "filename": "mapVillageForgeBuyIronAxeSpeech.wav",
        "appalachian": "Ah hope ye'll take kindly to this iron axe. Ah just honed 'er sharp as a tack fer ye!",
        "original": "I hope you'll like this iron axe. I have just sharpened it for you!"
    },
    {
        "filename": "mapVillageForgeBuyPolishedSilverSwordSpeech.wav",
        "appalachian": "It took me a whole heap o' time to forge this here silver sword. Ah assure ye it's well worth its price.",
        "original": "It took me a lot of time to create this sword. I assure you that it's worth its price."
    },
    {
        "filename": "mapVillageForgeBuyLightweightBodyArmourSpeech.wav",
        "appalachian": "This body armour'll keep ye safe agin them critters an' foes out yonder.",
        "original": "This body armour will offer you a protection against your enemies."
    },
    {
        "filename": "mapVillageForgeBuyScytheSpeech.wav",
        "appalachian": "It took me several months to craft this here scythe. A true work o' art. Reckon it's the quickest weapon you'll ever lay hands on. Good luck to ye!",
        "original": "It took me several months to make this scythe. It's a real piece of art. This is probably the fastest weapon you will ever be able to use. Good luck!"
    }
]

def get_token():
    for cmd in ["/opt/homebrew/bin/gcloud", "gcloud"]:
        try:
            return subprocess.check_output([cmd, "auth", "print-access-token"], universal_newlines=True).strip()
        except Exception:
            continue
    raise RuntimeError("Failed to obtain gcloud access token")

def synthesize_line(token, item, mode):
    text = item[mode]
    out_path = os.path.join(OUTPUT_DIR, item["filename"])
    
    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": "en-US",
            "name": "en-US-Chirp3-HD-Charon"
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "sampleRateHertz": 24000,
            "speakingRate": 0.88
        }
    }
    
    req = urllib.request.Request(
        "https://texttospeech.googleapis.com/v1/text:synthesize",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "X-Goog-User-Project": "ai-lab-499118",
            "Content-Type": "application/json"
        }
    )
    
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        audio_bytes = base64.b64decode(data["audioContent"])
        with open(out_path, "wb") as f:
            f.write(audio_bytes)
        print(f"[OK] Generated {item['filename']} ({len(audio_bytes)} bytes) [{mode}]")

def main():
    print(f"Generating 7 Blacksmith dialogue lines using en-US-Chirp3-HD-Charon (mode: {MODE})...")
    token = get_token()
    for item in LINES:
        synthesize_line(token, item, MODE)
    print("All 7 Blacksmith lines successfully generated!")

if __name__ == "__main__":
    main()
