#!/usr/bin/env python3
import os
import json
import base64
import wave
import time
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "blacksmith"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

AUDITION_TEXT = "Hi! I'm a blacksmith. I can sell you various weapons and pieces of equipment. It took me a lot of time to create this sword. I assure you that it's worth its price."

CANDIDATES = [
    {
        "id": "blacksmith_appalachian_fenrir_deep",
        "voice": "Fenrir",
        "prompt": (
            "You are a rugged, burly Appalachian mountain blacksmith living deep in a holler in the Smoky Mountains. "
            "You speak with a thick, authentic, hardcore Appalachian English accent and dialect. "
            "Heavy mountain drawl, distinct Appalachian twang, stretched-out vowels, folksy cadence, deep resonant baritone. "
            "You are speaking to a traveler who just walked into your blacksmith shack. "
            "Say this exact line in a thick, authentic Appalachian mountain accent:\n\n"
            f'"{AUDITION_TEXT}"'
        ),
        "label": "1. Fenrir (Mély hegyi kovács) – Vastag Smoky Mountain twang, öblös bariton, autentikus holler akcentus"
    },
    {
        "id": "blacksmith_appalachian_charon_gravel",
        "voice": "Charon",
        "prompt": (
            "You are an old, weathered 70-year-old Appalachian hillbilly blacksmith from West Virginia. "
            "You have worked iron in the mountains all your life and have a raspy, gravelly voice, chewing tobacco in your cheek. "
            "Speak with a hardcore, thick, authentic Appalachian mountain drawl with heavy nasality, flat diphthongs, and folksy mountain cadence. "
            "Say this exact line in your hardcore Appalachian dialect:\n\n"
            f'"{AUDITION_TEXT}"'
        ),
        "label": "2. Charon (Idős füstös hegyilakó) – Karcos, dohányos, vén West Virginia-i hegyi szaki, nyújtott hangzókkal"
    },
    {
        "id": "blacksmith_appalachian_fenrir_rustic",
        "voice": "Fenrir",
        "prompt": (
            "You are a friendly, boisterous Appalachian country blacksmith from the Blue Ridge Mountains. "
            "You speak with a very pronounced, authentic Southern Appalachian mountain dialect. "
            "Broad vowels, heavy mountain twang, folksy, warm, honest craftsman cadence. "
            "Read this dialogue line naturally in a thick, authentic Appalachian accent:\n\n"
            f'"{AUDITION_TEXT}"'
        ),
        "label": "3. Fenrir (Blue Ridge Kézműves) – Barátságos, ritmusos déli hegyi beszéd, tiszta és ízes akcentus"
    },
    {
        "id": "blacksmith_appalachian_charon_hardcore",
        "voice": "Charon",
        "prompt": (
            "You are an eccentric, hardcore Appalachian backwoods blacksmith. "
            "You speak with an extreme, unmistakable Appalachian English mountain twang, drawing out your words with a slow, rustic, toothless hillbilly drawl. "
            "Say this line in extreme Appalachian mountain character:\n\n"
            f'"{AUDITION_TEXT}"'
        ),
        "label": "4. Charon (Hardcore Hillbilly) – Lassú, extrém backwoods hegyi drawl, igazi eldugott hegyvidéki karakter"
    }
]

def synthesize_candidate(c):
    payload = {
        "contents": [{"parts": [{"text": c["prompt"]}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": c["voice"]
                    }
                }
            }
        }
    }
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    out_file = os.path.join(OUTPUT_DIR, c["id"] + ".wav")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            with wave.open(out_file, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(raw_pcm)
            print(f"[OK] {c['id']}.wav ({len(raw_pcm)} bytes)")
    except urllib.error.HTTPError as e:
        print(f"[ERR] {c['id']}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR] {c['id']}: {e}")

def update_html():
    html_file = os.path.join(OUTPUT_DIR, "audition.html")
    # Read existing or generate fresh
    cards = []
    
    # Add Appalachian candidates first
    cards.append("<h2>🏔️ Autentikus Hardcore Appalache (Appalachian) Változatok (Gemini Flash Audio)</h2>")
    for c in CANDIDATES:
        fname = c["id"] + ".wav"
        cards.append(f"""
        <div class="card" style="border: 1px solid #f59e0b; background: #1e1b18;">
            <h3 style="color: #fbbf24;">{c['label']}</h3>
            <p class="meta">Modell: <code>Gemini 2.5 Flash Audio ({c['voice']})</code> | Hardcore Appalachian Accent</p>
            <audio controls preload="none">
                <source src="{fname}" type="audio/wav">
            </audio>
            <div class="direct-link">
                <a href="{fname}" target="_blank">Közvetlen WAV megnyitása</a>
            </div>
        </div>
        """)

    # Add British / earlier candidates as reference
    cards.append("<h2 style='margin-top: 32px; color: #94a3b8;'>Korábbi Brit / Mesterkovács változatok (Referencia)</h2>")
    earlier = [
        ("blacksmith_chirp3_fenrir_gb.mp3", "1. Fenrir (Brit Chirp3 HD) – Mély brit mesterkovács", "en-GB-Chirp3-HD-Fenrir"),
        ("blacksmith_chirp3_charon_gb.mp3", "2. Charon (Brit Chirp3 HD) – Karcosabb érdes műhelymester", "en-GB-Chirp3-HD-Charon"),
        ("blacksmith_chirp3_enceladus_gb.mp3", "3. Enceladus (Brit Chirp3 HD) – Erőteljes brit kovács", "en-GB-Chirp3-HD-Enceladus"),
        ("blacksmith_neural2_b_gruff.mp3", "4. Neural2-B (Mélyített falusi kovács) – Dörmögő munkás bariton", "en-GB-Neural2-B"),
        ("blacksmith_studio_b_master.mp3", "5. Studio-B (Öblös fegyverkovács) – Tekintélyes fegyverkovács", "en-GB-Studio-B"),
        ("blacksmith_journey_d_us.mp3", "6. Journey-D (Szívélyes kézműves) – Organikus rekedtes amerikai", "en-US-Journey-D")
    ]
    for fname, label, voice in earlier:
        cards.append(f"""
        <div class="card">
            <h3>{label}</h3>
            <p class="meta">Modell: <code>{voice}</code></p>
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
        h2 {{ color: #fbbf24; font-size: 18px; margin-top: 24px; }}
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
    print(f"[OK] audition.html updated at {html_file}")

def main():
    print("Checking missing Appalachian Blacksmith audition candidates...")
    for c in CANDIDATES:
        out_file = os.path.join(OUTPUT_DIR, c["id"] + ".wav")
        if not os.path.exists(out_file) or os.path.getsize(out_file) < 1000:
            print(f"Synthesizing missing {c['id']}...")
            synthesize_candidate(c)
            time.sleep(15)  # 15s delay to stay well within free tier rate limit
        else:
            print(f"Already exists: {c['id']}.wav")
    update_html()

if __name__ == "__main__":
    main()
