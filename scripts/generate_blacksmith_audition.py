#!/usr/bin/env python3
import os
import json
import base64
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "ai-lab-499118"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "blacksmith"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

AUDITION_TEXT = "Hi! I'm a blacksmith. I can sell you various weapons and pieces of equipment. It took me a lot of time to create this sword. I assure you that it's worth its price."

CANDIDATES = [
    {
        "id": "blacksmith_chirp3_fenrir_gb",
        "voice": "en-GB-Chirp3-HD-Fenrir",
        "lang": "en-GB",
        "rate": 0.95,
        "pitch": None,
        "label": "1. Fenrir (Brit Chirp3 HD) – Mély, tekintélyes, robusztus mesterkovács"
    },
    {
        "id": "blacksmith_chirp3_charon_gb",
        "voice": "en-GB-Chirp3-HD-Charon",
        "lang": "en-GB",
        "rate": 0.92,
        "pitch": None,
        "label": "2. Charon (Brit Chirp3 HD) – Karcosabb, tapasztalt, érdes műhelymester"
    },
    {
        "id": "blacksmith_chirp3_enceladus_gb",
        "voice": "en-GB-Chirp3-HD-Enceladus",
        "lang": "en-GB",
        "rate": 0.95,
        "pitch": None,
        "label": "3. Enceladus (Brit Chirp3 HD) – Erőteljes, szilárd, öblös falusi kovács"
    },
    {
        "id": "blacksmith_neural2_b_gruff",
        "voice": "en-GB-Neural2-B",
        "lang": "en-GB",
        "rate": 0.92,
        "pitch": -2.5,
        "label": "4. Neural2-B (Mélyített falusi kovács) – Dörmögő, nehéz fizikai munkás bariton (-2.5 félhang)"
    },
    {
        "id": "blacksmith_studio_b_master",
        "voice": "en-GB-Studio-B",
        "lang": "en-GB",
        "rate": 0.90,
        "pitch": -2.0,
        "label": "5. Studio-B (Öblös fegyverkovács) – Tiszteletet parancsoló, nehéz műhelyhang (-2.0 félhang)"
    },
    {
        "id": "blacksmith_journey_d_us",
        "voice": "en-US-Journey-D",
        "lang": "en-US",
        "rate": 0.92,
        "pitch": None,
        "label": "6. Journey-D (Szívélyes kézműves) – Organikus, rekedtes, barátságos akcentus"
    }
]

def get_gcp_token():
    try:
        return subprocess.check_output(["/opt/homebrew/bin/gcloud", "auth", "print-access-token"], universal_newlines=True).strip()
    except Exception:
        return subprocess.check_output(["gcloud", "auth", "print-access-token"], universal_newlines=True).strip()

def synthesize_candidate(token, c):
    out_file = os.path.join(OUTPUT_DIR, c["id"] + ".mp3")
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    audio_cfg = {
        "audioEncoding": "MP3",
        "speakingRate": c["rate"]
    }
    if c["pitch"] is not None:
        audio_cfg["pitch"] = c["pitch"]

    payload = {
        "input": {"text": AUDITION_TEXT},
        "voice": {
            "languageCode": c["lang"],
            "name": c["voice"]
        },
        "audioConfig": audio_cfg
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "X-Goog-User-Project": PROJECT_ID,
            "Content-Type": "application/json"
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            content = base64.b64decode(resp_data["audioContent"])
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"[OK] {c['id']}.mp3 ({len(content)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"[ERR] {c['id']}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR] {c['id']}: {e}")

def generate_html():
    html_file = os.path.join(OUTPUT_DIR, "audition.html")
    cards = []
    for c in CANDIDATES:
        fname = c["id"] + ".mp3"
        pitch_str = f" | Pitch: {c['pitch']}st" if c['pitch'] is not None else ""
        cards.append(f"""
        <div class="card">
            <h3>{c['label']}</h3>
            <p class="meta">Modell: <code>{c['voice']}</code> | Tempó: {c['rate']}x{pitch_str}</p>
            <audio controls preload="none">
                <source src="{fname}" type="audio/mpeg">
            </audio>
            <div class="direct-link">
                <a href="{fname}" target="_blank">Közvetlen MP3 megnyitása</a>
            </div>
        </div>
        """)
    html_content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="utf-8">
    <title>Candy Box 2 - Kovács (Blacksmith) Hangválogatás</title>
    <style>
        body {{
            background: #11141a;
            color: #e0e6ed;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 30px;
            max-width: 800px;
            margin: 0 auto;
        }}
        h1 {{ color: #ff9800; border-bottom: 1px solid #ff980033; padding-bottom: 12px; }}
        .prompt-quote {{
            background: #1a202c;
            border-left: 4px solid #ff9800;
            padding: 12px 16px;
            margin-bottom: 24px;
            font-style: italic;
            color: #cbd5e1;
        }}
        .card {{
            background: #18202c;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .card h3 {{ margin: 0 0 6px 0; color: #ffb74d; }}
        .meta {{ font-size: 13px; color: #94a3b8; margin: 0 0 12px 0; }}
        code {{ background: #0f141c; padding: 2px 6px; border-radius: 4px; color: #38bdf8; }}
        audio {{ width: 100%; margin-top: 6px; }}
        .direct-link {{ margin-top: 8px; font-size: 12px; }}
        .direct-link a {{ color: #38bdf8; text-decoration: none; }}
        .direct-link a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>Candy Box 2 – Kovács (Forge Blacksmith) Hangválogatás</h1>
    <div class="prompt-quote">
        "{AUDITION_TEXT}"
    </div>
    {''.join(cards)}
</body>
</html>
"""
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] audition.html generated at {html_file}")

def main():
    print("Generating Blacksmith audition samples...")
    token = get_gcp_token()
    for c in CANDIDATES:
        synthesize_candidate(token, c)
    generate_html()

if __name__ == "__main__":
    main()
