#!/usr/bin/env python3
import os
import json
import base64
import wave
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "dragon"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

DRAGON_LINES = [
    {
        "filename": "dragonStopTickling.wav",
        "text": "Hey, you! Stop tickling me, please."
    },
    {
        "filename": "dragonTalking.wav",
        "text": "I am the dragon and this is my castle. I see that you managed to enter, you must be very brave... I'd love to help someone like you. What are you looking for?"
    },
    {
        "filename": "dragonTalkingChallengeSpeech.wav",
        "text": "Oh, so you want challenge? I think you should make a trip to hell itself, it is known that the devil is a tough challenger. Jump on my back and I'll take you there!"
    },
    {
        "filename": "dragonTalkingFameSpeech.wav",
        "text": "The best way to become famous is to face the developer himself. I know where he lives and I could take you there. But be prepared, this won't be easy."
    },
    {
        "filename": "dragonTalkingCandiesSpeech.wav",
        "text": "Ultimately, the thing we all want is candies, isn't it? I think a friend of mine could help you with that. You will recognise him easily, he has only one eye. Just tell him that you know me."
    }
]

PROMPT_TEMPLATE = (
    "You are an ancient Scottish dragon. You speak with an authentic, thick Scottish highland brogue "
    "with rolling Rs, raspy vocal fry, and a weathered, gravelly elder tone. You are grumpy, tired, "
    "and sound like a dry old grandpa dragon who has smoked cigars and pipe tobacco for five hundred years. "
    "Read this exact dialogue line in character with authentic Scottish intonation and a smoky rasp:\n\n"
    "\"{text}\""
)

def synthesize_line(item):
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
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            
            out_path = os.path.join(OUTPUT_DIR, item["filename"])
            with wave.open(out_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(raw_pcm)
                
            print(f"[OK] Generated: {out_path} ({len(raw_pcm)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"[ERR] Failed for {item['filename']}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR] Unexpected error for {item['filename']}: {e}")

def main():
    print(f"Generating {len(DRAGON_LINES)} Dragon dialogue lines into {OUTPUT_DIR}...")
    for item in DRAGON_LINES:
        synthesize_line(item)
    print("Dragon voice generation complete!")

if __name__ == "__main__":
    main()
