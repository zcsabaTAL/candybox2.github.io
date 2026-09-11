#!/usr/bin/env python3
import os
import json
import base64
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "ai-lab-499118"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "player"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Player Hero configuration (Pixar-style British teen adventurer)
VOICE_NAME = "en-GB-Chirp3-HD-Puck"
LANGUAGE_CODE = "en-GB"
SPEAKING_RATE = 1.05

PLAYER_LINES = [
    {
        "filename": "dragonStopTicklingButton.mp3",
        "text": "Uh, oh, sorry, I thought I was supposed to attack you."
    },
    {
        "filename": "dragonTalkingChallengeButton.mp3",
        "text": "Challenge!"
    },
    {
        "filename": "dragonTalkingFameButton.mp3",
        "text": "Fame!"
    },
    {
        "filename": "dragonTalkingCandiesButton.mp3",
        "text": "Candies!"
    },
    {
        "filename": "dragonTalkingChallengeAnswer.mp3",
        "text": "Let's go then!"
    },
    {
        "filename": "dragonTalkingFameAnswer.mp3",
        "text": "I am ready."
    },
    {
        "filename": "dragonTalkingCandiesAnswer.mp3",
        "text": "Okay, thanks!"
    }
]

def get_access_token():
    try:
        token = subprocess.check_output(
            ["/opt/homebrew/bin/gcloud", "auth", "print-access-token"],
            universal_newlines=True
        ).strip()
        return token
    except Exception:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            universal_newlines=True
        ).strip()
        return token

def synthesize(token, item):
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    
    payload = {
        "input": {
            "text": item["text"]
        },
        "voice": {
            "languageCode": LANGUAGE_CODE,
            "name": VOICE_NAME
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": SPEAKING_RATE
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": PROJECT_ID,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            audio_content = base64.b64decode(resp_data["audioContent"])
            out_file = os.path.join(OUTPUT_DIR, item["filename"])
            with open(out_file, "wb") as f:
                f.write(audio_content)
            print(f"[OK] Generated: {out_file}")
    except urllib.error.HTTPError as e:
        print(f"[ERR] Failed for {item['filename']}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR] Unexpected error for {item['filename']}: {e}")

def main():
    print(f"Synthesizing {len(PLAYER_LINES)} Player dialogue lines for Dragon into {OUTPUT_DIR}...")
    token = get_access_token()
    for item in PLAYER_LINES:
        synthesize(token, item)
    print("Player lines generation complete!")

if __name__ == "__main__":
    main()
