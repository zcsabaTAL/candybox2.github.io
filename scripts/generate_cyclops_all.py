#!/usr/bin/env python3
import os
import json
import base64
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "ai-lab-499118"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "cyclops"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICE_CONFIG = {
    "languageCode": "en-GB",
    "name": "en-GB-Neural2-D",
    "speakingRate": 0.88,
    "pitch": -3.0
}

LINES = [
    {
        "id": "lighthouseQuestionWhoSpeech",
        "text": "I'm a very old cyclops."
    },
    {
        "id": "lighthouseQuestionWhatSpeech",
        "text": "I live here all day long, waiting for a boat to come. It's been a long time since I've seen a boat, but I must stay here, staring at the sea, because a boat may come."
    },
    {
        "id": "lighthouseQuestionWhyEatCandiesSpeech",
        "text": "Because they're good for your health!"
    },
    {
        "id": "lighthouseQuestionCandyBoxSpeech",
        "text": "It is a very old box that is said to contain all the candies in the world. The legends say that whoever manages to open it would have so much candies that anything could be possible."
    },
    {
        "id": "lighthouseQuestionDragonSpeech",
        "text": "Oh, I see... Well, I cannot provide you candies directly, but I can give you something essential for you to ultimately get a LOT of candies. I just need to test you before that. Because what I have can't be given to everyone. Solve this puzzle and it will be yours."
    },
    {
        "id": "lighthouseFoundStone",
        "text": "Congratulations! You passed the test and found the stone. It's very precious, but is only useful if you have three other stones like this one. Good luck!"
    },
    {
        "id": "lighthouseFoundStoneAgain",
        "text": "Good job, you did the puzzle once again. You seem to like that."
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
    
    print(f"\nSynthesizing {len(LINES)} Cyclops lines with {VOICE_CONFIG['name']}...")
    for item in LINES:
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

    print("\nAll Cyclops voice files generated in:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
