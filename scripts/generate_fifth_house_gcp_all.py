#!/usr/bin/env python3
import os
import json
import base64
import time
import urllib.request
import urllib.error

# API kulcs környezeti változóból (Strict API key rule)
API_KEY = os.environ.get("GCP_TTS_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Required API key environment variable (GCP_TTS_KEY or GEMINI_API_KEY) is not set")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(BASE_DIR, "audio", "voice", "fifth_house")
os.makedirs(OUTPUT_DIR, exist_ok=True)

VOICE_NAME = "en-GB-Chirp3-HD-Kore"
LANG_CODE = "en-GB"

LINES = [
    {
        "id": "mapVillageFifthHouseNoWeaponSpeech",
        "text": "Hello. My cellar is full of rats, I need to get rid of them... if only someone with a weapon could help me...",
        "speakingRate": 1.02
    },
    {
        "id": "mapVillageFifthHouseWeaponSpeech",
        "text": "Hey, you! I see you carry a weapon! If you kill the rats pestering my cellar, I'll reward you!",
        "speakingRate": 1.06
    },
    {
        "id": "mapVillageFifthHouseCellarDone",
        "text": "Thank you for getting rid of them! Here's something very precious as a reward : a map of the world. I think you will use it more than I do.",
        "speakingRate": 1.02
    }
]

def synthesize_line(line_info):
    out_path = os.path.join(OUTPUT_DIR, f"{line_info['id']}.wav")
    print(f"[*] Synthesizing {line_info['id']} ({VOICE_NAME})...")
    
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"
    payload = {
        "input": {"text": line_info["text"]},
        "voice": {
            "languageCode": LANG_CODE,
            "name": VOICE_NAME
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "speakingRate": line_info.get("speakingRate", 1.0)
            # FONTOS: Chirp 3 HD esetén a pitch paraméter szigorúan tilos (400-as hibát dob)!
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                audio_bytes = base64.b64decode(res_data["audioContent"])
                with open(out_path, "wb") as f:
                    f.write(audio_bytes)
                size_kb = len(audio_bytes) / 1024
                print(f"[+] Successfully saved {out_path} ({size_kb:.1f} KB)")
                return out_path
        except urllib.error.HTTPError as e:
            err_msg = ""
            try:
                err_msg = e.read().decode("utf-8")
            except Exception:
                pass
            print(f"[-] HTTP Error {e.code} on attempt {attempt+1}: {err_msg}")
            time.sleep(2)
        except Exception as e:
            print(f"[-] Attempt {attempt+1} failed: {e}")
            time.sleep(2)
            
    raise RuntimeError(f"Failed to synthesize {line_info['id']}")

def generate_player():
    cards = ""
    for i, line in enumerate(LINES, 1):
        filename = f"{line['id']}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)
        cards += f"""
        <div style=\"background:#1a1b23; border:1px solid #2e303e; border-radius:8px; padding:20px; margin-bottom:20px;\">
            <div style=\"display:flex; align-items:center; gap:10px; margin-bottom:8px;\">
                <span style=\"background:#ff7b54; color:#121318; font-weight:bold; font-size:0.8rem; padding:4px 8px; border-radius:4px;\">SOR {i}</span>
                <h2 style=\"margin:0; font-size:1.15rem; color:#fff;\">{line['id']}</h2>
            </div>
            <p style=\"color:#ffd166; font-size:1.05rem; margin-bottom:12px; font-style:italic;\">\\\"{line['text']}\\\"</p>
            <audio id=\"audio-{i}\" controls preload=\"auto\" style=\"width:100%;\" src=\"{filename}\"></audio>
            <div style=\"margin-top:10px;\"><a style=\"color:#64b5f6; font-size:0.85rem;\" href=\"file://{filepath}\" target=\"_blank\">WAV közvetlen megnyitása</a></div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang=\"hu\">
<head>
    <meta charset=\"UTF-8\">
    <title>Candy Box 2 - 5. Ház Lakója Dialógus Lejátszó</title>
</head>
<body style=\"font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#121318; color:#e0e2eb; max-width:850px; margin:0 auto; padding:30px 20px;\">
    <h1 style=\"color:#ffb4a2; border-bottom:2px solid #3d2620; padding-bottom:10px;\">Candy Box 2 – 5. Ház Lakója (Cellar Quest) Végleges Hangok</h1>
    <div style=\"background:#1c1d24; border-left:4px solid #ff7b54; padding:14px 20px; margin:20px 0 25px;\">
        <strong>Modell & Karakter:</strong> Google Cloud Text-to-Speech ({VOICE_NAME}), brit női hang.<br>
        <strong>Projekt:</strong> Euroleasing Enterprise GCP ({os.environ.get('GOOGLE_CLOUD_PROJECT', 'ai-lab-499118')}).<br>
        <strong>Konzisztencia:</strong> Mind a 3 szöveg azonos modellel, egy menetben generálva.
    </div>
    
    <div style=\"margin-bottom:25px;\">
        <button id=\"playAllBtn\" onclick=\"playAllSequentially()\" style=\"background:#ff7b54; color:#121318; border:none; padding:12px 24px; font-weight:bold; font-size:1rem; border-radius:6px; cursor:pointer;\">
            ▶ Összes lejátszása sorban
        </button>
    </div>

    {cards}

    <script>
    function playAllSequentially() {{
        const audios = [
            document.getElementById('audio-1'),
            document.getElementById('audio-2'),
            document.getElementById('audio-3')
        ];
        let current = 0;
        function playNext() {{
            if (current < audios.length) {{
                audios[current].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                audios[current].play();
                audios[current].onended = () => {{
                    current++;
                    setTimeout(playNext, 600);
                }};
            }}
        }}
        audios.forEach(a => {{ a.pause(); a.currentTime = 0; }});
        playNext();
    }}
    </script>
</body>
</html>"""

    player_path = os.path.join(OUTPUT_DIR, "player.html")
    with open(player_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Player HTML saved to {player_path}")

if __name__ == "__main__":
    for line in LINES:
        synthesize_line(line)
        time.sleep(1)
    generate_player()
    print("[*] All Fifth House dialogue lines synthesized successfully via Google Cloud TTS!")
