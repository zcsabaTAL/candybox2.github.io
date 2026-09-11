#!/usr/bin/env python3
import os
import json
import base64
import wave
import time
import urllib.request
import urllib.error
import re

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "blacksmith"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

BLACKSMITH_LINES = [
    {
        "filename": "mapVillageForgeIntroductionSpeech.wav",
        "text": "Hi! I'm a blacksmith. I can sell you various weapons and pieces of equipment."
    },
    {
        "filename": "mapVillageForgeIntroductionSpeechNoMoreToSell.wav",
        "text": "Hi! I'm a blacksmith. Sadly, I have nothing more to sell. Come back later, maybe?"
    },
    {
        "filename": "mapVillageForgeBuyWoodenSwordSpeech.wav",
        "text": "Thanks for buying! This wooden sword is quite weak, but it's a start."
    },
    {
        "filename": "mapVillageForgeBuyIronAxeSpeech.wav",
        "text": "I hope you'll like this iron axe. I have just sharpened it for you!"
    },
    {
        "filename": "mapVillageForgeBuyPolishedSilverSwordSpeech.wav",
        "text": "It took me a lot of time to create this sword. I assure you that it's worth its price."
    },
    {
        "filename": "mapVillageForgeBuyLightweightBodyArmourSpeech.wav",
        "text": "This body armour will offer you a protection against your enemies."
    },
    {
        "filename": "mapVillageForgeBuyScytheSpeech.wav",
        "text": "It took me several months to make this scythe. It's a real piece of art. This is probably the fastest weapon you will ever be able to use. Good luck!"
    }
]

PROMPT_TEMPLATE = (
    "You are an old, weathered 70-year-old Appalachian hillbilly blacksmith from West Virginia. "
    "You have worked iron in the mountains all your life and have a raspy, gravelly voice, chewing tobacco in your cheek. "
    "Speak with a hardcore, thick, authentic Appalachian mountain drawl with heavy nasality, flat diphthongs, and folksy mountain cadence. "
    "Read this exact line in character in your hardcore Appalachian dialect:\n\n"
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

    prompt = PROMPT_TEMPLATE.format(text=item["text"])
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Charon"
                    }
                }
            }
        }
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    
    max_retries = 12
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
                err_str = e.read().decode("utf-8")
                m = re.search(r"retry in ([0-9.]+)s", err_str)
                if m:
                    wait_time = float(m.group(1)) + 2.5
                else:
                    m2 = re.search(r'"retryDelay":\s*"([0-9]+)s"', err_str)
                    if m2:
                        wait_time = float(m2.group(1)) + 2.5
                    else:
                        wait_time = 20.0 * (attempt + 1)
                log(f"[WAIT] 429 Rate limit for {item['filename']}, waiting {wait_time:.1f}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                log(f"[ERR] Failed for {item['filename']}: {e.code} - {e.read().decode('utf-8')}")
                return False
        except Exception as e:
            log(f"[ERR] Unexpected error for {item['filename']}: {e}")
            return False
    return False

def main():
    log(f"Starting Appalachian Blacksmith dialogue generation ({len(BLACKSMITH_LINES)} lines)...")
    for idx, item in enumerate(BLACKSMITH_LINES):
        success = synthesize_line(item)
        if not success:
            log(f"[WARN] Failed to synthesize {item['filename']}")
        if idx < len(BLACKSMITH_LINES) - 1:
            time.sleep(8)
    log("Blacksmith voice generation finished!")

if __name__ == "__main__":
    main()
