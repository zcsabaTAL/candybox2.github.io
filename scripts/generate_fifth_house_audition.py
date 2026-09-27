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
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "fifth_house"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEST_TEXT = "Hey, you! I see you carry a weapon! If you kill the rats pestering my cellar, I'll reward you!"

CANDIDATES = [
    {
        "id": "cand1_kore_geordie_housewife",
        "title": "Jelölt 1: Kétségbeesett, hisztérikus háziasszony (Kore – Geordie akcentus)",
        "voice": "Kore",
        "description": "Északkelet-angol (Geordie) dallamú, kapkodó, hisztérikus háziasszony. A végletekig fel van háborodva és el van keseredve a ronda patkányok miatt.",
        "prompt": (
            "You are a desperate, hysterical village housewife from Newcastle speaking with an authentic, lively Geordie regional accent and melody. "
            "You are frantic, terrified, and repulsed because grotesque giant rats have invaded your cellar. "
            "When you spot the player carrying a weapon, your voice bursts with panicked urgency and desperate relief, pleading with rapid, emotional energy: "
            f'"{TEST_TEXT}"'
        )
    },
    {
        "id": "cand2_aoede_dramatic_teenager",
        "title": "Jelölt 2: Pánikoló, drámai kamasz lány (Aoede – Vidéki kamasz tónus)",
        "voice": "Aoede",
        "description": "Magasabb fekvésű, túldramatizáló tinédzser lány. Halálra van rémülve, undorodik a dögöktől, hisztérikusan ugrál a széken, hogy valaki segítsen.",
        "prompt": (
            "You are a dramatic, panicked teenage village girl terrified out of your mind because filthy, giant rats have completely overrun your family cellar. "
            "Your voice is youthful, shrill, disgusted, and melodramatic, sounding like a teenager on the verge of tears jumping atop a table. "
            "When you see someone with a weapon, you shout out in frantic, desperate excitement: "
            f'"{TEST_TEXT}"'
        )
    },
    {
        "id": "cand3_kore_devon_elderly_grandma",
        "title": "Jelölt 3: Tehetetlen, törékeny öreg néni (Kore – Devoni / West Country akcentus)",
        "voice": "Kore",
        "description": "Törékeny, reszketeg hangú falusi nagymama délnyugat-angol (Devon) lágy tájszólással. Sírásra álló, remegő hang, teljesen kiszolgáltatott a rágcsálóknak.",
        "prompt": (
            "You are a frail, trembling, elderly village grandmother from Devon speaking with a soft, gentle West Country rural English accent. "
            "You are helpless, heartbroken, and deeply distressed because vicious rats have invaded your cellar and you cannot fight them off with your walking cane. "
            "Your voice is quavering, tender, and pleading with fragile, tearful hope when you notice someone carrying a weapon: "
            f'"{TEST_TEXT}"'
        )
    },
    {
        "id": "cand4_aoede_devon_rustic_milkmaid",
        "title": "Jelölt 4: Nyers, vaskos devoni parasztasszony (Aoede – Ízes West Country / Devoni akcentus)",
        "voice": "Aoede",
        "description": "Földhözragadt, dolgos vidéki nő ízes devoni kiejtéssel. Általában kemény és bátor, de a patkányhordától kiborult; nyers és erőteljes kétségbeeséssel kiabál.",
        "prompt": (
            "You are a sturdy, rustic Devon country farm woman with an authentic, earthy West Country rural accent. "
            "You are normally tough and hardworking around cattle, but this massive swarm of cellar rats has completely unnerved you. "
            "You speak with a broad, rustic country lilt, loud, robust, urgent, and desperate as you shout across the room to the armed stranger, offering a reward with gritty earnestness: "
            f'"{TEST_TEXT}"'
        )
    }
]

def synthesize(candidate):
    out_path = os.path.join(OUTPUT_DIR, f"{candidate['id']}.wav")
    print(f"[*] Generating {candidate['title']}...")
    payload = {
        "contents": [{"parts": [{"text": candidate["prompt"]}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": candidate["voice"]
                    }
                }
            }
        }
    }
    
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                part = res_data["candidates"][0]["content"]["parts"][0]
                audio_b64 = part.get("inlineData", {}).get("data")
                if not audio_b64:
                    raise RuntimeError("No audio inlineData in response")
                audio_bytes = base64.b64decode(audio_b64)
                
                # If audio is raw PCM 24kHz 16-bit mono (starts without RIFF), wrap in WAV container
                if audio_bytes[:4] == b"RIFF":
                    with open(out_path, "wb") as f:
                        f.write(audio_bytes)
                else:
                    with wave.open(out_path, "wb") as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(24000)
                        wav_file.writeframes(audio_bytes)
                
                size_kb = len(audio_bytes) / 1024
                print(f"[+] Saved {out_path} ({size_kb:.1f} KB)")
                return out_path
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass
            wait_time = 15 * (attempt + 1)
            print(f"[-] HTTP Error {e.code} on attempt {attempt+1} for {candidate['id']}: {body}. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"[-] Attempt {attempt+1} failed for {candidate['id']}: {e}")
            time.sleep(5)
    raise RuntimeError(f"Failed to generate {candidate['id']}")

def generate_html():
    html_path = os.path.join(OUTPUT_DIR, "audition.html")
    cards_html = ""
    
    for i, c in enumerate(CANDIDATES, 1):
        wav_file = f"{c['id']}.wav"
        full_wav_path = os.path.join(OUTPUT_DIR, wav_file)
        cards_html += f"""
        <div class="candidate-card">
            <div class="candidate-header">
                <span class="badge">Jelölt {i}</span>
                <h2>{c['title']}</h2>
            </div>
            <p class="description">{c['description']}</p>
            <div class="audio-box">
                <audio controls preload="auto" src="{wav_file}"></audio>
            </div>
            <div class="file-links">
                <a href="file://{full_wav_path}" target="_blank">WAV közvetlen megnyitása</a>
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>Candy Box 2 – 5. Ház Lakója (Cellar Quest) Női Hang Audíció</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #121318;
            color: #e0e2eb;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px 20px;
        }}
        h1 {{
            color: #ffb4a2;
            border-bottom: 2px solid #3d2620;
            padding-bottom: 12px;
            margin-bottom: 10px;
        }}
        .quote {{
            background: #1c1d24;
            border-left: 4px solid #ff7b54;
            padding: 14px 20px;
            margin: 20px 0 30px;
            font-style: italic;
            border-radius: 4px;
        }}
        .candidate-card {{
            background: #1a1b23;
            border: 1px solid #2e303e;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .candidate-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}
        .badge {{
            background: #ff7b54;
            color: #121318;
            font-weight: bold;
            font-size: 0.8rem;
            padding: 4px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        h2 {{
            margin: 0;
            font-size: 1.15rem;
            color: #ffffff;
        }}
        .description {{
            color: #a0a4b8;
            margin-bottom: 16px;
            line-height: 1.5;
        }}
        .audio-box {{
            margin-bottom: 12px;
        }}
        audio {{
            width: 100%;
            border-radius: 4px;
        }}
        .file-links a {{
            color: #64b5f6;
            text-decoration: none;
            font-size: 0.85rem;
        }}
        .file-links a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>Candy Box 2 – 5. Ház Lakója (Cellar Quest) Női Hang Audíció</h1>
    <p>Az alábbi lejátszóban meghallgatható a falusi ház lakójának 4 különböző brit vidéki női karaktere.</p>
    
    <div class="quote">
        <strong>Tesztmondat:</strong><br>
        "{TEST_TEXT}"
    </div>

    {cards_html}

</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] Audition HTML created: {html_path}")
    return html_path

if __name__ == "__main__":
    for c in CANDIDATES:
        synthesize(c)
        time.sleep(6)
    generate_html()
    print("[*] All candidates generated successfully!")
