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

VOICE_CONFIG = {
    "languageCode": "en-GB",
    "name": "en-GB-Chirp3-HD-Puck",
    "speakingRate": 1.05,
    "pitch": None
}

QUESTIONS = [
    {
        "id": "lighthouseQuestionWho",
        "text": "Who are you?"
    },
    {
        "id": "lighthouseQuestionWhat",
        "text": "What are you doing here?"
    },
    {
        "id": "lighthouseQuestionWhyEatCandies",
        "text": "Why would I eat candies?"
    },
    {
        "id": "lighthouseQuestionCandyBox",
        "text": "What is a candy box?"
    },
    {
        "id": "lighthouseQuestionDragon",
        "text": "The dragon told me to come here because I want candies."
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

def synthesize(token, text):
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    
    audio_config = {
        "audioEncoding": "MP3",
        "speakingRate": VOICE_CONFIG["speakingRate"]
    }
    if VOICE_CONFIG.get("pitch") is not None:
        audio_config["pitch"] = VOICE_CONFIG["pitch"]
    
    payload = {
        "input": {
            "text": text
        },
        "voice": {
            "languageCode": VOICE_CONFIG["languageCode"],
            "name": VOICE_CONFIG["name"]
        },
        "audioConfig": audio_config
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Goog-User-Project": PROJECT_ID,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return base64.b64decode(data["audioContent"])
    except urllib.error.HTTPError as err:
        err_body = err.read().decode("utf-8")
        raise RuntimeError(f"API Error {err.code}: {err_body}")

def main():
    print(f"Obtaining Google Cloud auth token for project: {PROJECT_ID}...")
    token = get_access_token()
    print("Token retrieved.")
    
    print(f"\nSynthesizing {len(QUESTIONS)} Player questions with {VOICE_CONFIG['name']}...")
    for item in QUESTIONS:
        filename = f"{item['id']}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)
        print(f"Generating {filename}...")
        try:
            audio_bytes = synthesize(token, item["text"])
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            print(f"  ✓ Saved ({len(audio_bytes)} bytes)")
        except Exception as e:
            print(f"  ✗ Error generating {filename}: {e}")

    print("\nAll Player question voice files generated in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
