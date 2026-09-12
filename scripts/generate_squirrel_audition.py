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
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "squirrel"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEXT = "Hello, I'm The Squirrel. I can provide you candies, and lots of things. I know how much you love candies. But I feel alone in this forest."

CANDIDATES = [
    {
        "id": "squirrel_cand1_charon_archimedes",
        "title": "Jelölt 1: Az Excentrikus Arkhimédész (Charon)",
        "voice": "Charon",
        "description": "Idős, rekedtes, bölcs görög remete tudós. Érett tónus, enyhe pörgetett r-ek, mediterrán dallamosság, lelkes és magányos professzor.",
        "prompt": (
            "You are The Squirrel, an ancient, wise, and eccentric Greek hermit philosopher who lives high up in an ancient enchanted tree. "
            "You speak English with an authentic Mediterranean Greek accent, rolling your Rs gently with expressive Greek cadence. "
            "You have an elderly, scholarly, slightly weathered and raspy academic voice like an aged Archimedes. "
            "You are passionate about riddles, geometry, and logic, but you are also deeply touched and lonely in your solitude. "
            "Act out this line with authentic Greek warmth, scholarly eccentricity, and heartfelt longing:\n\n"
            f"\"{TEXT}\""
        )
    },
    {
        "id": "squirrel_cand2_fenrir_aristotle",
        "title": "Jelölt 2: Az Arisztotelészi Akadémikus (Fenrir)",
        "voice": "Fenrir",
        "description": "Tekintélyes, kimért öreg görög filozófus professzor. Artikulált, pedáns, mélyebb professzori előadói hanghordozás görög intonációval.",
        "prompt": (
            "You are The Squirrel, a distinguished elderly Greek professor of philosophy who chose the life of a hermit in the canopy of an ancient forest. "
            "You speak English with an articulate, formal Greek accent, with characteristic Greek vowel sounds and dignified cadence. "
            "Your tone is wise, scholarly, slightly gravelly and professorial, treating candies as units of philosophical exchange. "
            "Deliver this line with elder intellectual dignity, Greek cadence, and solitary warmth:\n\n"
            f"\"{TEXT}\""
        )
    },
    {
        "id": "squirrel_cand3_puck_eccentric_genius",
        "title": "Jelölt 3: A Hóbortos Lombkorona-professzor (Puck)",
        "voice": "Puck",
        "description": "Élénkebb, gyors észjárású, kissé szórakozott idős görög remete zseni. Pattogósabb görög hanglejtés, felvillanyozott öröm az új látogatónak.",
        "prompt": (
            "You are The Squirrel, a quirky, eccentric elderly Greek scholar living as a hermit in an ancient hollow tree. "
            "You speak English with a pronounced Greek accent, lively Mediterranean inflection, and animated scholar mannerisms. "
            "You are quick-witted, slightly absent-minded, muttering before greeting the traveler with joyful excitement that someone came to solve your riddles. "
            "Act out this line with lively Greek hermit charm, energetic scholarly eccentricity, and warmth:\n\n"
            f"\"{TEXT}\""
        )
    },
    {
        "id": "squirrel_cand4_zephyr_stoic_sage",
        "title": "Jelölt 4: A Sztoikus Erdei Bölcs (Zephyr)",
        "voice": "Zephyr",
        "description": "Lágyabb, meditatív, békés öreg görög remete. Lassúbb, filozofikus, csendes rezignációval fogadja a vándort a hatalmas fán.",
        "prompt": (
            "You are The Squirrel, a calm, ancient Greek hermit sage who has contemplated the mysteries of the forest for decades from his high tree branch. "
            "You speak English with a gentle, weathered, serene Greek accent, slow and contemplative. "
            "Your voice is soft, dignified, philosophical, and melancholic about your solitude in the canopy. "
            "Deliver this line with gentle Greek stoicism, peaceful wisdom, and subtle warmth:\n\n"
            f"\"{TEXT}\""
        )
    }
]

def synthesize_candidate(cand):
    filename = f"{cand['id']}.wav"
    out_path = os.path.join(OUTPUT_DIR, filename)
    
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
    
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    for attempt in range(3):
        try:
            print(f"Calling Gemini 3.1 Flash TTS for {cand['id']} ({cand['voice']})...", flush=True)
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                with wave.open(out_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw_pcm)
                size = os.path.getsize(out_path)
                dur = round(size / 48000, 1)
                print(f"[OK] {filename} generated: {size} bytes (~{dur}s)", flush=True)
                return True
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="ignore")
            print(f"[HTTP {e.code} error on attempt {attempt+1}]: {err}", flush=True)
            time.sleep(6)
        except Exception as e:
            print(f"[Error on attempt {attempt+1}]: {e}", flush=True)
            time.sleep(4)
            
    print(f"[FAILED] Could not synthesize {filename}", flush=True)
    return False

def generate_html_audition():
    html_path = os.path.join(OUTPUT_DIR, "audition.html")
    cards_html = ""
    for idx, cand in enumerate(CANDIDATES):
        fn = f"{cand['id']}.wav"
        full_fn = os.path.join(OUTPUT_DIR, fn)
        size_kb = round(os.path.getsize(full_fn) / 1024, 1) if os.path.exists(full_fn) else 0
        dur_s = round(os.path.getsize(full_fn) / 48000, 1) if os.path.exists(full_fn) else 0
        
        cards_html += f"""
        <div class="card" id="card_{idx}">
            <div class="card-header">
                <span class="badge">Jelölt #{idx+1}</span>
                <span class="voice-name">{cand['voice']}</span>
            </div>
            <h3>{cand['title']}</h3>
            <p class="desc">{cand['description']}</p>
            <div class="quote">„{TEXT}”</div>
            <div class="audio-box">
                <audio id="audio_{idx}" controls src="{fn}" preload="metadata"></audio>
            </div>
            <div class="meta">
                <span>Fájl: <code>{fn}</code></span>
                <span>Méret: {size_kb} KB</span>
                <span>Hossz: ~{dur_s}s</span>
            </div>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>Candy Box 2 – Mókus (The Squirrel) Hangmeghallgatás</title>
    <style>
        body {{
            background: #0f1117;
            color: #e2e8f0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 30px;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 20px;
        }}
        h1 {{
            color: #38bdf8;
            margin: 0 0 10px 0;
            font-size: 28px;
        }}
        p.subtitle {{
            color: #94a3b8;
            font-size: 16px;
            margin: 0 0 15px 0;
        }}
        .control-bar {{
            background: #1e293b;
            padding: 16px 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 25px;
        }}
        .btn {{
            background: #2563eb;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 15px;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #1d4ed8;
        }}
        .btn-stop {{
            background: #475569;
            margin-left: 10px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}
        .card {{
            background: #182234;
            border: 1px solid #283548;
            border-radius: 12px;
            padding: 22px;
            transition: border-color 0.2s;
        }}
        .card.active {{
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .badge {{
            background: #0284c7;
            color: white;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 20px;
            text-transform: uppercase;
        }}
        .voice-name {{
            color: #a5f3fc;
            font-family: monospace;
            font-size: 14px;
        }}
        h3 {{
            margin: 0 0 10px 0;
            font-size: 19px;
            color: #f8fafc;
        }}
        p.desc {{
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.5;
            margin: 0 0 14px 0;
        }}
        .quote {{
            background: #0b1120;
            border-left: 3px solid #38bdf8;
            padding: 10px 14px;
            font-style: italic;
            color: #93c5fd;
            font-size: 14px;
            margin-bottom: 16px;
            border-radius: 0 6px 6px 0;
        }}
        audio {{
            width: 100%;
            height: 38px;
            outline: none;
        }}
        .meta {{
            display: flex;
            gap: 16px;
            color: #64748b;
            font-size: 12px;
            margin-top: 12px;
            border-top: 1px solid #1f2d42;
            padding-top: 10px;
        }}
        .meta code {{
            color: #94a3b8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Candy Box 2 – Mókus (The Squirrel) Hangmeghallgatás</h1>
            <p class="subtitle">Koncepció: Magányos erdei görög remete professzor (Gemini 3.1 Flash TTS)</p>
        </header>

        <div class="control-bar">
            <div>
                <strong>Összehasonlító meghallgatás</strong> (4 jelölt)
            </div>
            <div>
                <button class="btn" onclick="playAllSequentially()">Összes lejátszása sorban</button>
                <button class="btn btn-stop" onclick="stopAll()">Leállítás</button>
            </div>
        </div>

        <div class="grid">
            {cards_html}
        </div>
    </div>

    <script>
        const audioCount = {len(CANDIDATES)};
        let currentPlaying = -1;

        function stopAll() {{
            for (let i = 0; i < audioCount; i++) {{
                const a = document.getElementById('audio_' + i);
                if (a) {{
                    a.pause();
                    a.currentTime = 0;
                }}
                const c = document.getElementById('card_' + i);
                if (c) c.classList.remove('active');
            }}
            currentPlaying = -1;
        }}

        function playAllSequentially(startIndex = 0) {{
            stopAll();
            if (startIndex >= audioCount) return;

            currentPlaying = startIndex;
            const a = document.getElementById('audio_' + startIndex);
            const c = document.getElementById('card_' + startIndex);
            if (a) {{
                if (c) c.classList.add('active');
                a.play();
                a.onended = () => {{
                    if (c) c.classList.remove('active');
                    playAllSequentially(startIndex + 1);
                }};
            }}
        }}

        // Listen for individual plays
        for (let i = 0; i < audioCount; i++) {{
            const a = document.getElementById('audio_' + i);
            const c = document.getElementById('card_' + i);
            if (a) {{
                a.onplay = () => {{
                    for (let j = 0; j < audioCount; j++) {{
                        if (i !== j) {{
                            const other = document.getElementById('audio_' + j);
                            if (other) other.pause();
                            const otherC = document.getElementById('card_' + j);
                            if (otherC) otherC.classList.remove('active');
                        }}
                    }}
                    if (c) c.classList.add('active');
                }};
                a.onended = () => {{
                    if (c) c.classList.remove('active');
                }};
            }}
        }}
    </script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Audition HTML player written to {html_path}", flush=True)

if __name__ == "__main__":
    print(f"Generating 4 Greek Hermit Squirrel auditions on Gemini 3.1 Flash TTS...", flush=True)
    for cand in CANDIDATES:
        synthesize_candidate(cand)
        time.sleep(4)
    generate_html_audition()
    print("Audition generation successfully complete!", flush=True)
