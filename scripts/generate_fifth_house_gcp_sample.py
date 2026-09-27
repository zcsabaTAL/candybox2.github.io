#!/usr/bin/env python3
import os
import json
import base64
import urllib.request
import urllib.error

API_KEY = os.environ.get("GCP_TTS_KEY") or os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Required API key environment variable (GCP_TTS_KEY or GEMINI_API_KEY) is not set")

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "fifth_house"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEST_TEXT = "Hey, you! I see you carry a weapon! If you kill the rats pestering my cellar, I'll reward you!"
OUT_FILE = os.path.join(OUTPUT_DIR, "cand_gcp_chirp3_kore.wav")

def synthesize_gcp():
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"
    payload = {
        "input": {"text": TEST_TEXT},
        "voice": {
            "languageCode": "en-GB",
            "name": "en-GB-Chirp3-HD-Kore"
        },
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "speakingRate": 1.0
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        audio_content = base64.b64decode(res["audioContent"])
        with open(OUT_FILE, "wb") as f:
            f.write(audio_content)
        print(f"[+] Saved {OUT_FILE} ({len(audio_content)/1024:.1f} KB)")

def update_audition_html():
    cands = [
        {
            "id": "cand1_kore_geordie_housewife",
            "badge": "JELÖLT 1 (GEMINI FLASH)",
            "title": "Kétségbeesett, hisztérikus háziasszony (Gemini Flash – Kore – Geordie akcentus)",
            "description": "Északkelet-angol (Geordie) dallamú, kapkodó háziasszony. Heves kétségbeesés és sírós felháborodás a pincei patkányok miatt.",
            "file": "cand1_kore_geordie_housewife.wav"
        },
        {
            "id": "cand_gcp_chirp3_kore",
            "badge": "JELÖLT 1B (VÁLLALATI GCP CHIRP 3 HD)",
            "title": "Természetes brit női hang (GCP Chirp 3 HD – Kore – en-GB)",
            "description": "Google Cloud Chirp 3 HD hivatalos stúdióminőségű brit Kore hangmodell. Kristálytiszta, rendkívül természetes és kifejező hanglejtés vállalati fiókból.",
            "file": "cand_gcp_chirp3_kore.wav"
        },
        {
            "id": "cand2_aoede_dramatic_teenager",
            "badge": "JELÖLT 2 (GEMINI FLASH)",
            "title": "Pánikoló, drámai kamasz lány (Gemini Flash – Aoede)",
            "description": "Magasabb fekvésű, túldramatizáló tinédzser lány. Halálra van rémülve, undorodik a dögöktől, hisztérikusan ugrál a széken.",
            "file": "cand2_aoede_dramatic_teenager.wav"
        }
    ]

    cards = ""
    for c in cands:
        cards += f"""
        <div style="background:#1a1b23; border:1px solid #2e303e; border-radius:8px; padding:20px; margin-bottom:20px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="background:#ff7b54; color:#121318; font-weight:bold; font-size:0.75rem; padding:4px 8px; border-radius:4px;">{c['badge']}</span>
                <h2 style="margin:0; font-size:1.15rem; color:#fff;">{c['title']}</h2>
            </div>
            <p style="color:#a0a4b8; margin-bottom:14px; line-height:1.5;">{c['description']}</p>
            <audio controls preload="auto" style="width:100%;" src="{c['file']}"></audio>
            <div style="margin-top:10px;"><a style="color:#64b5f6; font-size:0.85rem;" href="file://{OUTPUT_DIR}/{c['file']}" target="_blank">WAV közvetlen megnyitása</a></div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>5. Ház Lakója – Audíció és Hang-összehasonlítás</title>
</head>
<body style="font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#121318; color:#e0e2eb; max-width:850px; margin:0 auto; padding:30px 20px;">
    <h1 style="color:#ffb4a2; border-bottom:2px solid #3d2620; padding-bottom:10px;">Candy Box 2 – 5. Ház Lakója (Cellar Quest) Női Hang Audíció</h1>
    <div style="background:#1c1d24; border-left:4px solid #ff7b54; padding:14px 20px; margin:20px 0 25px; font-style:italic;">
        <strong>Tesztmondat:</strong><br>
        \"{TEST_TEXT}\"
    </div>
    {cards}
</body>
</html>"""

    html_path = os.path.join(OUTPUT_DIR, "audition.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Updated audition HTML at {html_path}")

if __name__ == "__main__":
    synthesize_gcp()
    update_audition_html()
