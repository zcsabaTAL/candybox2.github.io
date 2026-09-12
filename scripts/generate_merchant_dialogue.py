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
# Use active postpay Gemini 3.1 Flash TTS model
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "merchant"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

CAND1_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "merchant", "merchant_cand1_puck_goblin.wav"))

LINES = [
    {
        "filename": "secondHouseIntroSpeech.wav",
        "text": "Hello, I'm the candy merchant. I would do anything for candies. What do you need?",
        "use_cand1": True
    },
    {
        "filename": "secondHouseLollipop1Speech.wav",
        "text": "This is a lemon-flavored lollipop. My favourite! It costs 60 candies, but it's worth it.",
        "use_cand1": False
    },
    {
        "filename": "secondHouseLollipop2Speech.wav",
        "text": "This one is a strawberry-flavored lollipop. It tastes good. I like its red color. Only 60 candies!",
        "use_cand1": False
    },
    {
        "filename": "secondHouseLollipop3Speech.wav",
        "text": "This is a pumpkin-flavored lollipop. I bet you never tried one! 60 candies and it's yours.",
        "use_cand1": False
    },
    {
        "filename": "secondHouseLeatherBootsSpeech.wav",
        "text": "These high quality leather boots, made from camel leather, will keep your feet warm.",
        "use_cand1": False
    },
    {
        "filename": "secondHouseLeatherGlovesSpeech.wav",
        "text": "These leather gloves are made from camel leather, this is high quality. I have a lot of them in stock, that's why they are so cheap: only 300 candies!",
        "use_cand1": False
    },
    {
        "filename": "secondHouseChocolateBarSpeech.wav",
        "text": "This is a chocolate bar. I don't know what it is used for, but it happens to be quite rare, which explains the price. 800 candies and it's yours!",
        "use_cand1": False
    },
    {
        "filename": "secondHouseTimeRingSpeech.wav",
        "text": "This is a time ring. It's kind of magical. It allows you to slow down the time when you're in trouble.",
        "use_cand1": False
    },
    {
        "filename": "secondHouseMerchantHatSpeech.wav",
        "text": "I could sell you my hat, but it is very precious, you know... You will have to give me a lot of candies for it. Let's say 1 million candies. It seems fair, right?",
        "use_cand1": False
    }
]

PROMPT_TEMPLATE = (
    "You are the eccentric, sugar-addicted Candy Merchant from a whimsical fantasy world. "
    "You are a fast-talking, slightly manic gnome peddler whose eyes gleam greedily at the thought of sweets. "
    "You speak with high-energy excitement, a raspy playful tone, lively pacing, and utter delight whenever you mention candies. "
    "Act out this line with full theatrical personality:\n\n"
    "\"{text}\""
)

def synthesize_line(item):
    out_path = os.path.join(OUTPUT_DIR, item["filename"])
    
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"[ALREADY EXISTS] {item['filename']} ({os.path.getsize(out_path)} bytes) – skipping.", flush=True)
        return True

    if item.get("use_cand1") and os.path.exists(CAND1_PATH) and os.path.getsize(CAND1_PATH) > 1000:
        shutil.copy(CAND1_PATH, out_path)
        size = os.path.getsize(out_path)
        print(f"[COPIED] {item['filename']} copied from approved candidate 1 ({size} bytes, ~{round(size/48000, 1)}s)", flush=True)
        return True

    prompt = PROMPT_TEMPLATE.format(text=item["text"])
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Puck"
                    }
                }
            }
        }
    }

    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                with wave.open(out_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw_pcm)
                size = os.path.getsize(out_path)
                print(f"[SUCCESS] {item['filename']} ({size} bytes, ~{round(size/48000, 1)}s)", flush=True)
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"[RETRY {attempt+1} for {item['filename']}] HTTP {e.code}: {err_body}", flush=True)
            time.sleep(10)
        except Exception as e:
            print(f"[RETRY {attempt+1} for {item['filename']}] {e}", flush=True)
            time.sleep(5)
            
    print(f"[FAILED] Could not synthesize {item['filename']}", flush=True)
    return False

if __name__ == "__main__":
    print(f"Starting Candy Merchant synthesis ({len(LINES)} lines) to {OUTPUT_DIR}...", flush=True)
    for idx, item in enumerate(LINES):
        print(f"\nProcessing [{idx+1}/{len(LINES)}]: {item['filename']}...", flush=True)
        synthesize_line(item)
        if not os.path.exists(os.path.join(OUTPUT_DIR, item["filename"])) or item.get("use_cand1"):
            pass
        else:
            time.sleep(4)
    print("\nAll processing complete!", flush=True)
