#!/usr/bin/env python3
import os
import json
import base64
import time
import shutil
import urllib.request
import urllib.error
import wave

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "sorceress"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

CAND3_TEST_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "sorceress", "sorceress_cand3_solemn_kore.wav"))

SORCERESS_LINES = [
    {
        "filename": "sorceressHutHello.wav",
        "text": "Hello, I'm the sorceress. I could teach you one thing or two about magic. I can also give you some interesting things, or cast spells for you. But everything has a price! And this price will be lollipops. A lot of them."
    },
    {
        "filename": "sorceressHutClickedGrimoire.wav",
        "text": "This is a grimoire made for beginners. By carrying it with you in quests, you will be able to cast simple but useful spells. You need this! Only 5 000 lollipops."
    },
    {
        "filename": "sorceressHutBuyGrimoireSpeech.wav",
        "text": "Thanks for buying! You will be able to cast three spells with this grimoire. Good luck!"
    },
    {
        "filename": "sorceressHutClickedGrimoire2.wav",
        "text": "This is an advanced grimoire. By carrying it with you in quests, you will be able to cast two advanced spells. I wrote it myself, which wasn't easy. 20 000 lollipops is a fair price."
    },
    {
        "filename": "sorceressHutBuyGrimoire2Speech.wav",
        "text": "Thanks for buying! You will be able to cast two spells with this grimoire. Use them wisely!"
    },
    {
        "filename": "sorceressHutClickedCauldron.wav",
        "text": "This is my cauldron. It allows me to brew magic potions. I could sell it to you, but it's very precious... it will cost you 100 000 lollipops."
    },
    {
        "filename": "sorceressHutBuyCauldronSpeech.wav",
        "text": "Thanks a lot! 100 000 lollipops for me! I also gave you a brewing manual. It's going to be useful."
    },
    {
        "filename": "sorceressHutClickedHat.wav",
        "text": "I have a nice hat, indeed! But I really can't sell it to you. It is waaaay too precious. Really, I can't. Don't insist. No. No no no I shouldn't do that. Oh well, I'll trade it, but for 1 000 000 000 lollipops. You probably won't be able to pay that anyway."
    },
    {
        "filename": "sorceressHutBuyHatSpeech.wav",
        "text": "One billion lollipops for meeeeee! But I don't have a hat anymore.. but one billion lollipops, wow! .. It was worth it."
    }
]

PROMPT_TEMPLATE = (
    "You are Lady Galadriel, the high elven sorceress and lady of the woods. "
    "Your voice is deep, crystalline, solemn, and enchanting, possessing ancient knowledge and a calm, hypnotic cadence. "
    "You speak with clear aristocratic British phrasing, serene majesty, and an aura of supernatural grandeur. "
    "Speak in character in your majestic elven voice:\n\n"
    "\"{text}\""
)

LOG_FILE = os.path.join(OUTPUT_DIR, "gen.log")

def log(msg):
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def synthesize_line(item):
    out_path = os.path.join(OUTPUT_DIR, item["filename"])

    # If it's the hello speech and we already have candidate 3, copy it directly
    if item["filename"] == "sorceressHutHello.wav" and os.path.exists(CAND3_TEST_FILE) and os.path.getsize(CAND3_TEST_FILE) > 1000:
        shutil.copy(CAND3_TEST_FILE, out_path)
        log(f"[COPIED] {item['filename']} copied from candidate 3 ({os.path.getsize(out_path)} bytes)")
        return True

    prompt = PROMPT_TEMPLATE.format(text=item["text"])
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Kore"
                    }
                }
            }
        }
    }

    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers)

    max_retries = 8
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])

                with wave.open(out_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw_pcm)

                log(f"[OK] Generated: {item['filename']} ({len(raw_pcm)} bytes)")
                return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 20.0 * (attempt + 1)
                log(f"[WAIT] 429 Rate limit for {item['filename']}, waiting {wait_time}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                log(f"[ERR] Failed for {item['filename']}: {e.code} - {e.read().decode('utf-8')}")
                return False
        except Exception as e:
            log(f"[ERR] Unexpected error for {item['filename']}: {e}")
            return False
    return False

def main():
    log(f"Starting Sorceress (Galadriel Kore) dialogue generation ({len(SORCERESS_LINES)} lines)...")
    for idx, item in enumerate(SORCERESS_LINES):
        log(f"\n--- [{idx+1}/{len(SORCERESS_LINES)}] {item['filename']} ---")
        success = synthesize_line(item)
        if not success:
            log(f"[ABORT] Failed generating {item['filename']}, stopping.")
            break
        # Sleep between requests to respect Gemini RPM rate limit
        if idx < len(SORCERESS_LINES) - 1 and item["filename"] != "sorceressHutHello.wav":
            log("[SLEEP] Sleeping 15s to respect RPM limit...")
            time.sleep(15)

    log("\nAll Sorceress lines processing complete!")

if __name__ == "__main__":
    main()
