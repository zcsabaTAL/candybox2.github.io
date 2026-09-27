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

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "talking_candy"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Selected Voice Archetype: Candidate 4 (Aoede - Laza, közvetlen szimpatizáns, bár-flört)
VOICE_NAME = "Aoede"

SYSTEM_PERSONA = (
    "You are The Talking Candy, speaking like an approachable, effortlessly charming woman leaning in across a table for a friendly, teasing chat in a stylish lounge. "
    "Your tone is casual, warm, upbeat, and subtly coquettish, speaking completely naturally with an amused half-smile in your voice as if playfully bantering with someone you find attractive. "
    "Do NOT use heavy breathing, exaggerated whispering, or artificial melodrama. Keep the speech clear, rhythmic, natural, and charmingly flirtatious."
)

LINES = [
    {
        "id": "talkingCandySpeechNoBox",
        "file": "talkingCandySpeechNoBox.wav",
        "title": "Beszélő Cukor – Nincs dobozod (Útmutatás)",
        "acting": "Barátságos, laza, játékosan motiváló félmosollyal adja meg az utolsó lépést.",
        "text": "Hey! I'm the talking candy. You almost won the game. You just need to find the candy box. It's in a house outside the village. This is the last step!",
        "prompt": (
            f"{SYSTEM_PERSONA}\n\n"
            "You are giving the player a friendly, flirtatious nudge. You find them impressive for making it this far. "
            "Deliver this line with casual warmth, teasing encouragement, and effortless charm:\n\n"
            "\"Hey! I'm the talking candy. You almost won the game. You just need to find the candy box. It's in a house outside the village. This is the last step!\""
        )
    },
    {
        "id": "talkingCandySpeech1",
        "file": "talkingCandySpeech1.wav",
        "title": "Beszélő Cukor – Doboz kinyitása előtt (Gratuláció)",
        "acting": "Megnyerő, elismerő, kacéran gratuláló tónus, édes jutalom felajánlása.",
        "text": "Hey! I'm the talking candy. Congratulations, you won the game! I will open your candy box for you, this is your reward. Should I proceed?",
        "prompt": (
            f"{SYSTEM_PERSONA}\n\n"
            "The player has won the game, and you are genuinely impressed and happy for them. "
            "Deliver this line with glowing flirtatious warmth, relaxed charm, and a playful wink in your tone:\n\n"
            "\"Hey! I'm the talking candy. Congratulations, you won the game! I will open your candy box for you, this is your reward. Should I proceed?\""
        )
    },
    {
        "id": "talkingCandySpeech2",
        "file": "talkingCandySpeech2.wav",
        "title": "Beszélő Cukor – Doboz kinyitva (Búcsú/Belépés)",
        "acting": "Elégedett, simogató, meleg és kedves búcsúmondat egy lágy mosollyal a végén.",
        "text": "Done! You can now enter it. I hope you liked the game :)",
        "prompt": (
            f"{SYSTEM_PERSONA}\n\n"
            "You just opened the box for them. You say 'Done!' with satisfaction, then invite them to step inside with fond, relaxed, affectionate warmth. "
            "Deliver this line smoothly and warmly, with a gentle, genuine smile at the end:\n\n"
            "\"Done! You can now enter it. I hope you liked the game :)\""
        )
    }
]

def synthesize_line(line_info):
    out_wav = os.path.join(OUTPUT_DIR, line_info["file"])
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": line_info["prompt"]
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": VOICE_NAME
                    }
                }
            }
        }
    }
    
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL,
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"--> Generating {line_info['file']} ({VOICE_NAME})...", flush=True)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
            
            cand_part = res_json["candidates"][0]["content"]["parts"][0]
            inline_data = cand_part.get("inlineData", {})
            b64_audio = inline_data.get("data", "")
            
            if not b64_audio:
                print(f"[ERROR] No audio data for {line_info['file']}: {res_json}", flush=True)
                return None
            
            raw_pcm = base64.b64decode(b64_audio)
            
            with wave.open(out_wav, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(raw_pcm)
            
            size = os.path.getsize(out_wav)
            duration = round(size / 48000.0, 1)
            print(f"[OK] Generated {line_info['file']} ({size} bytes, ~{duration}s)", flush=True)
            line_info["duration"] = duration
            line_info["size_kb"] = round(size / 1024, 1)
            return out_wav
            
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            print(f"[HTTP {e.code}] Attempt {attempt + 1} failed: {err_body}", flush=True)
            if e.code == 429:
                print("[429 RATE LIMIT] Waiting 15s before retry...", flush=True)
                time.sleep(15)
            else:
                time.sleep(3)
        except Exception as e:
            print(f"[EXCEPTION] {e}", flush=True)
            time.sleep(3)
            
    return None

def build_player_html():
    html_path = os.path.join(OUTPUT_DIR, "player.html")
    cards_html = ""
    for idx, l in enumerate(LINES, 1):
        wav_file = l["file"]
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <h3>{idx}. {l['title']}</h3>
                <span class="badge">{l.get('duration', '~')} mp | {l.get('size_kb', '~')} KB</span>
            </div>
            <p class="file-name">Fájl: <code>{wav_file}</code></p>
            <p class="acting"><strong>Hangulat:</strong> {l['acting']}</p>
            <div class="quote">
                <em>&ldquo;{l['text']}&rdquo;</em>
            </div>
            <div class="player-row">
                <audio controls preload="none">
                    <source src="{wav_file}" type="audio/wav">
                    A böngésződ nem támogatja a lejátszót.
                </audio>
                <a href="{wav_file}" class="download-link" download>Letöltés / Megnyitás (.wav)</a>
            </div>
        </div>
        """
        
    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candy Box 2 – The Talking Candy Teljes Hanganyag</title>
    <style>
        body {{
            background-color: #0f111a;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 30px 20px;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 820px;
            width: 100%;
        }}
        h1 {{
            color: #f472b6;
            margin-bottom: 6px;
            font-size: 26px;
        }}
        .subtitle {{
            color: #94a3b8;
            margin-bottom: 25px;
            font-size: 14px;
            line-height: 1.5;
        }}
        .card {{
            background: #1a1e2e;
            border: 1px solid #2d3748;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}
        .card:hover {{
            border-color: #f472b6;
            transform: translateY(-2px);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .card-header h3 {{
            margin: 0;
            color: #fbcfe8;
            font-size: 18px;
        }}
        .badge {{
            background: #831843;
            color: #fce7f3;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }}
        .file-name {{
            font-size: 13px;
            color: #94a3b8;
            margin: 0 0 8px 0;
        }}
        .file-name code {{
            background: #111420;
            padding: 2px 6px;
            border-radius: 4px;
            color: #f472b6;
        }}
        .acting {{
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 12px;
        }}
        .quote {{
            background: #111420;
            border-left: 3px solid #f472b6;
            padding: 10px 14px;
            border-radius: 0 8px 8px 0;
            color: #e2e8f0;
            font-size: 14px;
            margin-bottom: 16px;
        }}
        .player-row {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}
        audio {{
            height: 38px;
            flex-grow: 1;
            min-width: 250px;
        }}
        .download-link {{
            color: #f472b6;
            text-decoration: none;
            font-size: 13px;
            font-weight: 500;
            padding: 8px 14px;
            border: 1px solid #db2777;
            border-radius: 6px;
            transition: background 0.2s ease;
        }}
        .download-link:hover {{
            background: rgba(244, 114, 182, 0.15);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🍸 The Talking Candy – Végleges Dialógusok</h1>
        <p class="subtitle">
            Karakter: <strong>Aoede (Laza, közvetlen szimpatizáns, elegáns bár-flört)</strong><br>
            Motor: Gemini 3.1 Flash TTS (24kHz Mono WAV) | 3/3 dialógus elkészült.
        </p>
        {cards_html}
    </div>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Master player built: {html_path}", flush=True)

def main():
    print("=== GENERATING THE TALKING CANDY FULL DIALOGUES ===")
    for line in LINES:
        synthesize_line(line)
        time.sleep(3)
    build_player_html()
    print("=== ALL TALKING CANDY DIALOGUES GENERATED ===")

if __name__ == "__main__":
    main()
