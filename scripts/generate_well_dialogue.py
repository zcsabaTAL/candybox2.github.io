#!/usr/bin/env python3
import os
import json
import base64
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "ai-lab-499118"
VOICE_NAME = "en-US-Journey-F"
SPEAKING_RATE = 0.92
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "wishing_well"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

SPEECHES = {
    "wishingWellCandyIntroductionSpeech": "Hello, wanderer! I am the wishing well. I shall grant you wishes in exchange of some sweets! When you'll throw candies into me, I will heal your wounds.",
    "wishingWellThrewCandiesSpeech": "Your wounds are now healed!",
    "wishingWellNoWoundSpeech": "You have no wounds to heal!",
    "wishingWellLollipopIntroductionSpeech": "Hello, wanderer! I am the wishing well. I shall grant you wishes in exchange of some sweets! When you'll throw lollipops into me, I will convert them into candies.",
    "wishingWellThrewLollipopsSpeech": "Your lollipops are converted into candies! Two lollipops for one candy.",
    "wishingWellChocolateBarIntroductionSpeech": "Hello, wanderer! I am the wishing well. I shall grant you wishes in exchange of some sweets! I love chocolate bars. I really love them. For each chocolate bar you will throw into me, including this one, you will be granted one magical enchantment.",
    "wishingWellThrewChocolateBarSpeech": "Which object would you like to enchant?",
    "wishingWellPainAuChocolatIntroductionSpeech": "Hello, wanderer! I am the wishing well. I shall grant you wishes in exchange of some sweets! When you throw a pain au chocolat into me, you will be given a very special gift. Choose wisely.",
    "wishingWellThrewPainAuChocolatSpeech": "Thanks for the pain au chocolat! You can now choose your gift.",
    "wishingWellGiftDoneSpeech": "Done! You now have a new gift. It will appear in your inventory stats panel.",
    "wishingWellEnchantmentDoneSpeech": "There it is! Your object is enchanted."
}

def get_gcp_token():
    try:
        return subprocess.check_output(["/opt/homebrew/bin/gcloud", "auth", "print-access-token"], universal_newlines=True).strip()
    except Exception:
        return subprocess.check_output(["gcloud", "auth", "print-access-token"], universal_newlines=True).strip()

def synthesize_line(token, filename, text):
    out_file = os.path.join(OUTPUT_DIR, filename + ".mp3")
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    payload = {
        "input": {"text": text},
        "voice": {
            "languageCode": "en-US",
            "name": VOICE_NAME
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": SPEAKING_RATE
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "X-Goog-User-Project": PROJECT_ID,
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            content = base64.b64decode(resp_data["audioContent"])
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"[OK] {filename}.mp3 ({len(content)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"[ERR] {filename}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR] {filename}: {e}")

def main():
    print(f"Synthesizing {len(SPEECHES)} Wishing Well speeches with {VOICE_NAME}...")
    token = get_gcp_token()
    for name, text in SPEECHES.items():
        synthesize_line(token, name, text)
    print("All Wishing Well speeches synthesized!")

if __name__ == "__main__":
    main()
