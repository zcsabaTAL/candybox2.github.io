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
    raise ValueError("GEMINI_API_KEY environment variable is not set")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "sorceress"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

AUDITION_TEXT = "Hello, I'm the sorceress. I could teach you one thing or two about magic. I can also give you some interesting things, or cast spells for you. But everything has a price! And this price will be lollipops. A lot of them."

CANDIDATES = [
    {
        "id": "cand1_ethereal_aoede",
        "voice": "Aoede",
        "label": "1. Jelölt: Éteri és suttogó Galadriel (Aoede hangszín)",
        "desc": "Lélegzetelállítóan éteri, titokzatos, mély és breathy tünde királynő hang Lothlórien aranyerdejéből, finom brit arisztokratikus kiejtéssel.",
        "prompt": (
            "You are Lady Galadriel, the ancient, majestic Elven Queen of the golden woods of Lothlórien from The Lord of the Rings. "
            "Your voice is timeless, ethereal, softly resonant, and breathy, with an aristocratic British Received Pronunciation (RP) cadence. "
            "You speak with enchanting grace, deep stillness, quiet authority, and subtle cosmic wisdom, as if whispering ancient secrets from the Undying Lands across centuries. "
            "Speak in character with breathy elven majesty and gentle mystery:\n\n"
            f'"{AUDITION_TEXT}"'
        )
    },
    {
        "id": "cand2_regal_aoede",
        "voice": "Aoede",
        "label": "2. Jelölt: Fenséges és méltóságteljes királynő (Aoede hangszín)",
        "desc": "Mélyebb, bársonyos, uralkodói és dallamos tünde pátosz, lassú, megfontolt és fennkölt intonációval.",
        "prompt": (
            "You are an ancient Elven Queen of immense arcane power and noble stature, inspired by Queen Galadriel of Lothlórien. "
            "Your voice is deep, velvet, melodious, and regal, carrying the poetic cadence of high elven royalty and profound archaic magic. "
            "You speak slowly and deliberately, with aristocratic elegance and quiet celestial command. "
            "Speak in character:\n\n"
            f'"{AUDITION_TEXT}"'
        )
    },
    {
        "id": "cand3_solemn_kore",
        "voice": "Kore",
        "label": "3. Jelölt: Ünnepélyes és hipnotikus tünde úrnő (Kore hangszín)",
        "desc": "Kristálytiszta, mély, ünnepélyes és hipnotikus jelenlét, fenséges higgadtsággal és természetfeletti aurával.",
        "prompt": (
            "You are Lady Galadriel, the high elven sorceress and lady of the woods. "
            "Your voice is deep, crystalline, solemn, and enchanting, possessing ancient knowledge and a calm, hypnotic cadence. "
            "You speak with clear aristocratic British phrasing, serene majesty, and an aura of supernatural grandeur. "
            "Speak in character:\n\n"
            f'"{AUDITION_TEXT}"'
        )
    },
    {
        "id": "cand4_silvery_despina",
        "voice": "Despina",
        "label": "4. Jelölt: Ezüstös és titokzatos erdei varázslónő (Despina hangszín)",
        "desc": "Meleg, selymes, ezüstösen csilingelő és rejtélyesen mosolygó tünde tónus, mint az éjszakai csillagfény a faleveleken.",
        "prompt": (
            "You are an ancient, otherworldly elven enchantress living deep in the enchanted forest, inspired by the high elven ladies of Tolkien's realm. "
            "Your voice is warm, silvery, intimate, and enigmatic, like gentle wind through starlit leaves, laced with subtle, amused mystery and timeless grace. "
            "Speak in character:\n\n"
            f'"{AUDITION_TEXT}"'
        )
    }
]

def synthesize(cand):
    out_path = os.path.join(OUTPUT_DIR, f"sorceress_{cand['id']}.wav")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"[EXISTS] {cand['id']} already exists ({os.path.getsize(out_path)} bytes)")
        return True

    payload = {
        "contents": [{"parts": [{"text": cand["prompt"]}]}],
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

    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers)

    max_retries = 6
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

                print(f"[OK] Generated: {cand['id']} ({len(raw_pcm)} bytes)")
                return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 15.0 * (attempt + 1)
                print(f"[WAIT] 429 Rate limit, waiting {wait_time}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                print(f"[ERR] Failed for {cand['id']}: {e.code} - {e.read().decode('utf-8')}")
                return False
        except Exception as e:
            print(f"[ERR] Unexpected error for {cand['id']}: {e}")
            return False
    return False

def generate_html_player():
    html_path = os.path.join(OUTPUT_DIR, "audition.html")
    cards = []
    for c in CANDIDATES:
        fname = f"sorceress_{c['id']}.wav"
        cards.append(f"""
        <div class="card">
            <h2>{c['label']}</h2>
            <p class="desc">{c['desc']}</p>
            <audio controls preload="auto" src="{fname}"></audio>
            <div class="meta">Hangmodell: <code>{c['voice']}</code> | Fájl: <code>{fname}</code></div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="utf-8">
    <title>Varázslónő – Galadriel Tünde Királynő Meghallgatás</title>
    <style>
        body {{
            background: #0d1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 860px;
            margin: 40px auto;
            padding: 0 20px 40px 20px;
        }}
        h1 {{
            color: #d2a8ff;
            text-align: center;
            font-size: 28px;
            margin-bottom: 8px;
        }}
        .subtitle {{
            text-align: center;
            color: #8b949e;
            margin-bottom: 30px;
            font-size: 15px;
        }}
        .text-box {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 25px;
            font-style: italic;
            color: #e6edf3;
            line-height: 1.5;
        }}
        .card {{
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            transition: border-color 0.2s;
        }}
        .card:hover {{
            border-color: #d2a8ff;
        }}
        .card h2 {{
            margin-top: 0;
            color: #f0f6fc;
            font-size: 18px;
            margin-bottom: 8px;
        }}
        .card .desc {{
            color: #8b949e;
            font-size: 14px;
            margin-bottom: 14px;
            line-height: 1.4;
        }}
        audio {{
            width: 100%;
            height: 40px;
            margin-bottom: 10px;
            outline: none;
        }}
        .meta {{
            font-size: 12px;
            color: #6e7681;
        }}
        code {{
            background: #0d1117;
            padding: 2px 6px;
            border-radius: 4px;
            color: #79c0ff;
        }}
    </style>
</head>
<body>
    <h1>Varázslónő – Tünde Királynő (Galadriel) Meghallgatás</h1>
    <div class="subtitle">Candy Box 2 • Sorceress Voice Audition (Lothlórien Galadriel stílusban)</div>

    <div class="text-box">
        &bdquo;{AUDITION_TEXT}&rdquo;
    </div>

    {''.join(cards)}
</body>
</html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Created audition player: {html_path}")

def main():
    print("Starting Sorceress (Galadriel) audition generation...")
    for idx, c in enumerate(CANDIDATES):
        synthesize(c)
        if idx < len(CANDIDATES) - 1:
            time.sleep(5)
    generate_html_player()
    print("Done!")

if __name__ == "__main__":
    main()
