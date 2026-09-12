#!/usr/bin/env python3
import os
import json
import base64
import time
import urllib.request
import urllib.error
import wave

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "merchant"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

CANDIDATES = [
    {
        "filename": "merchant_cand1_puck_goblin",
        "voice": "Puck",
        "title": "1. Puck – A hiperaktív, kapzsi gnóm/kobold árus (Játékos, gyors, rekedtes, izgága)",
        "prompt": (
            "You are the eccentric, sugar-addicted Candy Merchant from a whimsical fantasy world. "
            "You are a fast-talking, slightly manic gnome peddler whose eyes gleam greedily at the thought of sweets. "
            "You speak with high-energy excitement, a raspy playful tone, lively pacing, and utter delight whenever you mention candies. "
            "Act out this line with full theatrical personality:\n\n"
            "\"Hello, I'm the candy merchant. I would do anything for candies. What do you need?\""
        )
    },
    {
        "filename": "merchant_cand2_charon_cunning",
        "voice": "Charon",
        "title": "2. Charon – A ravasz, mély hangú, sokat látott vándorárus (Suttogó, dörzsölt, furcsa humorral)",
        "prompt": (
            "You are the eccentric old traveling Candy Merchant in a dusty fantasy outpost. "
            "You have a weathered, deep, resonant voice with a sly, whimsical edge. "
            "You sound seasoned and mysterious, but when it comes to candies, a spark of cunning obsession lights up your voice. "
            "Speak naturally with character and a sly grin:\n\n"
            "\"Hello, I'm the candy merchant. I would do anything for candies. What do you need?\""
        )
    },
    {
        "filename": "merchant_cand3_fenrir_gruff",
        "voice": "Fenrir",
        "title": "3. Fenrir – A bohókás, morcos bazáros (Karcos, komikus, színházi energiával)",
        "prompt": (
            "You are a comical, gruff, and slightly unhinged candy peddler with a lively fantasy bazaar accent. "
            "You sound a bit conspiratorial, blunt, yet delightfully passionate about sweets. "
            "Act out the line with vibrant character:\n\n"
            "\"Hello, I'm the candy merchant. I would do anything for candies. What do you need?\""
        )
    },
    {
        "filename": "merchant_cand4_zephyr_theatrical",
        "voice": "Zephyr",
        "title": "4. Zephyr – A modoros, kissé baljós viktoriánus édességboltos (Finomkodó, selymes, melodramatikus)",
        "prompt": (
            "You are a theatrical, eccentric Victorian candy shopkeeper. "
            "You speak with a smooth, purring British cadence, melodramatic flair, and a delightfully eerie obsession with sweets. "
            "Act out the line in character:\n\n"
            "\"Hello, I'm the candy merchant. I would do anything for candies. What do you need?\""
        )
    }
]

def generate(item):
    out_wav = os.path.join(OUTPUT_DIR, item["filename"] + ".wav")
    print(f"\n---> Generating {item['title']}...", flush=True)
    payload = {
        "contents": [{"parts": [{"text": item["prompt"]}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": item["voice"]
                    }
                }
            }
        }
    }
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                with wave.open(out_wav, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw_pcm)
                size = os.path.getsize(out_wav)
                print(f"[SUCCESS] {item['filename']}.wav ({size} bytes, ~{round(size/48000, 1)}s)", flush=True)
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"[RETRY {attempt+1}] HTTP {e.code}: {err_body}", flush=True)
            time.sleep(2 * (attempt + 1))
        except Exception as e:
            print(f"[RETRY {attempt+1}] {e}", flush=True)
            time.sleep(2 * (attempt + 1))
    print(f"[FAILED] Could not generate {item['filename']}", flush=True)
    return False

if __name__ == "__main__":
    for item in CANDIDATES:
        generate(item)
        time.sleep(1)
