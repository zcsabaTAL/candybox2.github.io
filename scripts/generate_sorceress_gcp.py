#!/usr/bin/env python3
import os
import sys
import json
import base64
import subprocess
import urllib.request
import urllib.error

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "sorceress"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

LINES = [
    {
        "filename": "sorceressHutHello.wav",
        "text": "Hello, I'm the sorceress. I could teach you one thing or two about magic. I can also give you some interesting things, or cast spells for you. But everything has a price! And this price will be lollipops. A lot of them."
    },
    {
        "filename": "sorceressHutClickedGrimoire.wav",
        "text": "This is a grimoire made for beginners. By carrying it with you in quests, you will be able to cast simple but useful spells. You need this! Only five thousand lollipops."
    },
    {
        "filename": "sorceressHutBuyGrimoireSpeech.wav",
        "text": "Thanks for buying! You will be able to cast three spells with this grimoire. Good luck!"
    },
    {
        "filename": "sorceressHutClickedGrimoire2.wav",
        "text": "This is an advanced grimoire. By carrying it with you in quests, you will be able to cast two advanced spells. I wrote it myself, which wasn't easy. Twenty thousand lollipops is a fair price."
    },
    {
        "filename": "sorceressHutBuyGrimoire2Speech.wav",
        "text": "Thanks for buying! You will be able to cast two spells with this grimoire. Use them wisely!"
    },
    {
        "filename": "sorceressHutClickedCauldron.wav",
        "text": "This is my cauldron. It allows me to brew magic potions. I could sell it to you, but it's very precious... it will cost you one hundred thousand lollipops."
    },
    {
        "filename": "sorceressHutBuyCauldronSpeech.wav",
        "text": "Thanks a lot! One hundred thousand lollipops for me! I also gave you a brewing manual. It's going to be useful."
    },
    {
        "filename": "sorceressHutClickedHat.wav",
        "text": "I have a nice hat, indeed! But I really can't sell it to you. It is way too precious. Really, I can't. Don't insist. No. No, no, no, I shouldn't do that. Oh well, I'll trade it, but for one billion lollipops. You probably won't be able to pay that anyway."
    },
    {
        "filename": "sorceressHutBuyHatSpeech.wav",
        "text": "One billion lollipops for me! But I don't have a hat anymore. But one billion lollipops, wow! It was worth it."
    }
]

def get_token():
    for cmd in ["/opt/homebrew/bin/gcloud", "gcloud"]:
        try:
            return subprocess.check_output([cmd, "auth", "print-access-token"], universal_newlines=True).strip()
        except Exception:
            continue
    raise RuntimeError("Failed to obtain gcloud access token")

def synthesize_line(token, item):
    out_path = os.path.join(OUTPUT_DIR, item["filename"])
    
    payload = {
        "input": {"text": item["text"]},
        "voice": {
            "languageCode": "en-GB",
            "name": "en-GB-Neural2-F"
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "sampleRateHertz": 24000,
            "speakingRate": 0.90,
            "pitch": -1.8
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
        print(f"[OK] Generated {item['filename']} ({len(audio_bytes)} bytes)")

def main():
    print(f"Generating 9 Sorceress (Galadriel Elven Queen) lines using en-GB-Neural2-F...")
    token = get_token()
    for item in LINES:
        synthesize_line(token, item)
    print("All 9 Sorceress lines successfully generated!")

if __name__ == "__main__":
    main()
