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
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "talking_candy"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEXT = "Hey! I'm the talking candy. Congratulations, you won the game! I will open your candy box for you, this is your reward. Should I proceed?"

CANDIDATES = [
    {
        "id": "candy_cand1_kore_cocktail_flirt",
        "title": "Jelölt 1: Elegáns Koktélbár Flört (Kore)",
        "voice": "Kore",
        "description": "Természetes, meleg alt. Intelligens, kellemesen búgó hang, barátságos és vonzó félmosollyal, túlzások és lihegés nélkül.",
        "prompt": (
            "You are The Talking Candy, speaking as a confident, charming, and naturally alluring woman having a warm, witty conversation at a stylish cocktail lounge. "
            "You are flirting effortlessly with a gentle smile in your voice, speaking naturally and conversationally without any forced whispering, heavy breathing, or over-the-top melodrama. "
            "Your tone is warm, attractive, intelligent, and subtly playful. "
            "Deliver this line with relaxed cocktail lounge charm and natural flirtatious warmth:\n\n"
            f"\"{TEXT}\""
        )
    },
    {
        "id": "candy_cand2_kore_jazz_lounge",
        "title": "Jelölt 2: Füstös Jazz Lounge (Kore)",
        "voice": "Kore",
        "description": "Egy leheletnyivel mélyebb, lazább éjszakai bárhangulat. Közvetlen, életszerű és magabiztos, finom félmosollyal.",
        "prompt": (
            "You are The Talking Candy, speaking in the style of an effortlessly cool, mature woman at a dimly lit jazz club sipping a drink. "
            "Your voice has a rich, smoky warmth and subtle allure, but you speak naturally, casually, and directly. "
            "You have a relaxed, knowing twinkle in your voice, teasing gently without exaggerated breathiness or theatrics. "
            "Deliver this line with smooth jazz lounge cool and casual flirtation:\n\n"
            f"\"{TEXT}\""
        )
    },
    {
        "id": "candy_cand3_aoede_witty_banter",
        "title": "Jelölt 3: Szellemes és Incselkedő (Aoede)",
        "voice": "Aoede",
        "description": "Élénkebb, frappáns, kacér női hang. Gyorsabb ritmus, játékos hangsúlyok, mintha egy szellemes visszavágást intézne a pultnál.",
        "prompt": (
            "You are The Talking Candy, speaking like a witty, bright, and charming woman engaging in playful bar-counter banter. "
            "You are flirtatious, quick, and conversational, delivering lines with an amused half-smile and spirited charm. "
            "Keep your delivery natural, clear, and engaging, avoiding melodrama or heavy whispering. "
            "Deliver this line with witty flirtatious banter and sparkling charm:\n\n"
            f"\"{TEXT}\""
        )
    },
    {
        "id": "candy_cand4_aoede_casual_charmer",
        "title": "Jelölt 4: Laza, Közvetlen Szimpatizáns (Aoede)",
        "voice": "Aoede",
        "description": "Nagyon közvetlen, megnyerő, laza flört. Kellemesen behízelgő, de hétköznapi, felszabadult stílusban.",
        "prompt": (
            "You are The Talking Candy, speaking like an approachable, effortlessly charming woman leaning in across the table for a friendly, teasing chat. "
            "Your tone is casual, warm, upbeat, and subtly coquettish, speaking completely naturally as if complimenting a friend. "
            "Avoid any breathy or artificial affectations. "
            "Deliver this line with relaxed, friendly charisma and natural teasing warmth:\n\n"
            f"\"{TEXT}\""
        )
    }
]

def synthesize_candidate(cand):
    out_wav = os.path.join(OUTPUT_DIR, f"{cand['id']}.wav")
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": cand["prompt"]
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": cand["voice"]
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
    
    print(f"--> Generating {cand['id']} ({cand['voice']})...", flush=True)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
            
            cand_part = res_json["candidates"][0]["content"]["parts"][0]
            inline_data = cand_part.get("inlineData", {})
            b64_audio = inline_data.get("data", "")
            mime = inline_data.get("mimeType", "")
            
            if not b64_audio:
                print(f"[ERROR] No audio data received for {cand['id']}: {res_json}", flush=True)
                return None
            
            raw_pcm = base64.b64decode(b64_audio)
            
            # Write standard 24kHz 16-bit Mono WAV
            with wave.open(out_wav, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(raw_pcm)
            
            size = os.path.getsize(out_wav)
            duration = round(size / 48000.0, 1)
            print(f"[OK] Generated {cand['id']}.wav ({size} bytes, ~{duration}s, mime: {mime})", flush=True)
            cand["wav_file"] = f"{cand['id']}.wav"
            cand["duration"] = duration
            cand["size_kb"] = round(size / 1024, 1)
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

def build_html():
    html_path = os.path.join(OUTPUT_DIR, "audition.html")
    
    cards_html = ""
    for idx, c in enumerate(CANDIDATES, 1):
        wav_rel = f"{c['id']}.wav"
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <h3>{c['title']}</h3>
                <span class="badge">{c.get('duration', '~')} mp | {c.get('size_kb', '~')} KB</span>
            </div>
            <p class="desc"><strong>Karakter:</strong> {c['description']}</p>
            <div class="quote">
                <em>&ldquo;{TEXT}&rdquo;</em>
            </div>
            <div class="player-row">
                <audio controls preload="none">
                    <source src="{wav_rel}" type="audio/wav">
                    A böngésződ nem támogatja a lejátszót.
                </audio>
                <a href="{wav_rel}" class="download-link" download>Megnyitás / Letöltés (.wav)</a>
            </div>
        </div>
        """
        
    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candy Box 2 – The Talking Candy Audíció (Round 2)</title>
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
            display: flex;
            align-items: center;
            gap: 10px;
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
            margin-bottom: 10px;
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
        .desc {{
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
        <h1>🍸 The Talking Candy – Bár-flört Audíció (Round 2)</h1>
        <p class="subtitle">
            Tesztelt modell: <strong>Gemini 3.1 Flash TTS</strong> (24kHz Mono WAV).<br>
            Koncepció: Természetes, elegáns koktélbár / jazz club flört, szellemes, laza és vonzó tónus, túlzó lihegés és nehéz suttogás nélkül.
        </p>
        {cards_html}
    </div>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Audition player built: {html_path}", flush=True)

def main():
    print("=== THE TALKING CANDY AUDITION GENERATION (ROUND 2: BAR FLIRT) ===")
    for cand in CANDIDATES:
        synthesize_candidate(cand)
        time.sleep(3)
    build_html()
    print("=== FINISHED ===")

if __name__ == "__main__":
    main()
