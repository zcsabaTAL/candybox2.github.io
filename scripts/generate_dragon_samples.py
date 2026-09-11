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

TEXT = "Hey, you! Stop tickling me, please. I am the dragon and this is my castle."

VOICES = [
    {
        "id": "dragon_sample_A_studio_q",
        "description": "en-US Studio-Q (deep baritone, -3.5st pitch, majestic bass)",
        "languageCode": "en-US",
        "name": "en-US-Studio-Q",
        "speakingRate": 0.85,
        "pitch": -3.5
    },
    {
        "id": "dragon_sample_B_neural2_j_us",
        "description": "en-US Neural2-J (-4.0st pitch, booming ancient dragon rumble)",
        "languageCode": "en-US",
        "name": "en-US-Neural2-J",
        "speakingRate": 0.82,
        "pitch": -4.0
    },
    {
        "id": "dragon_sample_C_chirp3_fenrir_gb",
        "description": "en-GB Chirp3-HD-Fenrir (deep British mythical dragon)",
        "languageCode": "en-GB",
        "name": "en-GB-Chirp3-HD-Fenrir",
        "speakingRate": 0.85,
        "pitch": None
    },
    {
        "id": "dragon_sample_D_journey_d",
        "description": "en-US Journey-D (warm, wise, natural storytelling dragon)",
        "languageCode": "en-US",
        "name": "en-US-Journey-D",
        "speakingRate": 0.85,
        "pitch": None
    },
    {
        "id": "dragon_sample_E_studio_b_gb",
        "description": "en-GB Studio-B (-3.0st pitch, British noble dragon)",
        "languageCode": "en-GB",
        "name": "en-GB-Studio-B",
        "speakingRate": 0.85,
        "pitch": -3.0
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
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            audio_content = base64.b64decode(resp_data["audioContent"])
            out_file = os.path.join(OUTPUT_DIR, f"{voice_config['id']}.mp3")
            with open(out_file, "wb") as f:
                f.write(audio_content)
            print(f"[OK] Generated: {out_file} ({voice_config['description']})")
    except urllib.error.HTTPError as e:
        print(f"[ERR] Failed for {voice_config['name']}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR] Unexpected error for {voice_config['name']}: {e}")

def main():
    print(f"Synthesizing {len(VOICES)} Dragon audition samples for text:\n\"{TEXT}\"\n")
    token = get_access_token()
    for v in VOICES:
        synthesize(token, v)
    print("\nAudition samples ready in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
