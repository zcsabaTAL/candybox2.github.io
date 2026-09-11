#!/usr/bin/env python3
import os
import json
import base64
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "ai-lab-499118"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEXT = "Who are you?"

VOICES = [
    {
        "id": "A_british_male",
        "description": "en-GB Neural2-B (young British male adventurer)",
        "languageCode": "en-GB",
        "name": "en-GB-Neural2-B",
        "speakingRate": 1.0,
        "pitch": 0.0
    },
    {
        "id": "B_us_journey_male",
        "description": "en-US Journey-D (natural, conversational male protagonist)",
        "languageCode": "en-US",
        "name": "en-US-Journey-D",
        "speakingRate": 1.0,
        "pitch": None
    },
    {
        "id": "C_british_female",
        "description": "en-GB Neural2-C (curious British female adventurer)",
        "languageCode": "en-GB",
        "name": "en-GB-Neural2-C",
        "speakingRate": 1.0,
        "pitch": 0.0
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

def synthesize(token, voice_config):
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    
    audio_config = {
        "audioEncoding": "MP3",
        "speakingRate": voice_config["speakingRate"]
    }
    if voice_config.get("pitch") is not None:
        audio_config["pitch"] = voice_config["pitch"]
    
    payload = {
        "input": {
            "text": TEXT
        },
        "voice": {
            "languageCode": voice_config["languageCode"],
            "name": voice_config["name"]
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
    
    print(f"\nSynthesizing player sample: \"{TEXT}\"")
    for v in VOICES:
        out_filename = f"player_sample_{v['id']}.mp3"
        out_path = os.path.join(OUTPUT_DIR, out_filename)
        print(f"Generating {v['description']} -> {out_filename}...")
        try:
            audio_data = synthesize(token, v)
            with open(out_path, "wb") as f:
                f.write(audio_data)
            print(f"  ✓ Saved {len(audio_data)} bytes to {out_path}")
        except Exception as ex:
            print(f"  ✗ Failed: {ex}")

    print("\nGeneration process complete. Files in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
