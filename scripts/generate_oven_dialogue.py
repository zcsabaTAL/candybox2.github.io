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
    raise ValueError("GEMINI_API_KEY environment variable is not set")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "oven"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

CAND3_TEST_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "oven", "oven_cand3_scouse_kore.wav"))

OVEN_LINES = [
    {
        "filename": "castleBigRoomHovenSpeechSad.wav",
        "text": "Hello! I'm a very old bread oven. I used to cook tons of good pastries, but no one is using me anymore. Maybe... maybe you could help me? Just let me take some sweets from you! Don't worry, you won't regret it! You can trust me."
    },
    {
        "filename": "castleBigRoomHovenNotEnough.wav",
        "text": "Oh... you don't have enough sweets, I can't do anything. I'm just useless. I'm the useless bread oven, that's how you should call me."
    },
    {
        "filename": "castleBigRoomHovenSpeechMadePainAuChocolat.wav",
        "text": "Yay! Thanks a lot! I used 100 candies and a chocolate bar, and I made you... a pain au chocolat! It's my favourite pastry, I hope you'll like it too!"
    },
    {
        "filename": "castleBigRoomHovenSpeechHappy.wav",
        "text": "Hey! If you want me to cook another pastry, just tell me! I'd love to help you."
    },
    {
        "filename": "castleBigRoomHovenSpeechHappyNotEnough.wav",
        "text": "Oh, you don't have enough sweets, sadly. I need 100 candies and a chocolate bar. Come back when you'll have that!"
    }
]

PROMPT_TEMPLATE = (
    "You are a 75-year-old working-class elderly scullery maid from Liverpool, "
    "whose spirit is inside an ancient castle bread oven. "
    "Your voice is gravelly, raspy, lively, with an authentic Scouse dialect: "
    "distinctive velar fricatives, rising intonation at the end of clauses, cheeky, down-to-earth, and affectionate Northern warmth. "
    "Speak in character in your authentic Scouse accent:\n\n"
    "\"{text}\""
)

LOG_FILE = os.path.join(OUTPUT_DIR, "gen.log")

def log(msg):
    print(msg, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def synthesize_line(item):
    out_path = os.path.join(OUTPUT_DIR, item["filename"])
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        log(f"[EXISTS] {item['filename']} already synthesized ({os.path.getsize(out_path)} bytes)")
        return True

    # If it's the sad speech and we already have candidate 3, copy it directly
    if item["filename"] == "castleBigRoomHovenSpeechSad.wav" and os.path.exists(CAND3_TEST_FILE) and os.path.getsize(CAND3_TEST_FILE) > 1000:
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
                wait_time = 15.0 * (attempt + 1)
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
    log(f"Starting Castle Bread Oven dialogue generation ({len(OVEN_LINES)} lines)...")
    for idx, item in enumerate(OVEN_LINES):
        success = synthesize_line(item)
        if not success:
            log(f"[WARN] Failed to synthesize {item['filename']}")
        if idx < len(OVEN_LINES) - 1:
            time.sleep(6)
    log("Castle Bread Oven voice generation finished!")

if __name__ == "__main__":
    main()
