#!/usr/bin/env python3
import os
import json
import base64
import time
import shutil
import urllib.request
import urllib.error
import wave

# Explicitly use Key 1 (Standard tier / postpay)
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable is required")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-tts-preview:generateContent?key={API_KEY}"
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "voice", "squirrel"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

CAND3_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "squirrel", "squirrel_cand3_puck_eccentric_genius.wav"))

LINES = [
    {
        "filename": "mapATreeIntroductionSpeech.wav",
        "role": "Nyitó bemutatkozás",
        "text": "Hello, I'm The Squirrel. I can provide you candies, and lots of things. I know how much you love candies. But I feel alone in this forest.",
        "use_cand3": True
    },
    {
        "filename": "mapATreeFirstQuestion.wav",
        "role": "1. feladvány (Szereted a cukrot?)",
        "text": "I will ask you questions. If you answer correctly, the sweetest sweets will be yours! First one : do you really love candies? (answer in english)",
        "use_cand3": False
    },
    {
        "filename": "mapATreeSecondQuestion.wav",
        "role": "2. feladvány (S-E-I-D-N-A-?)",
        "text": "That's right! Here's 20 candies for you. Now complete this sequence of letters and you'll get a new reward : S, E, I, D, N, A, ?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeThirdQuestion.wav",
        "role": "3. feladvány (A legcukrosabb ember)",
        "text": "Candies! Here's 100 candies for you. Next question : how many candies does the candiest person in the world possess?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeFourthQuestion.wav",
        "role": "4. feladvány (Gyökerek, ágak és levelek)",
        "text": "Here's 500 candies for you! Next reward should be even more interesting... Here's the riddle : In an ancient forest grows a very old tree, on which live the most intelligent animals in this world. It is said that this tree has 60 roots, 360 branches and 2160 leaves. How many marks can you find on its trunk?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeFifthQuestion.wav",
        "role": "5. feladvány (Sárga kalap a Vörös-tengerben)",
        "text": "Congratulations! I was talking about my tree, indeed. Here are 3 lollipops for you. Make good use of them! Next riddle, listen carefully : Under a full moon, I throw a yellow hat into the red sea. What happens to the yellow hat?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeTicTacToeIntro.wav",
        "role": "Amőba felvezetés",
        "text": "Well answered! That wasn't so hard. Here's three chocolate bars for you! For the next reward, we'll change the rules a little bit. You'll have to play a game with me! Are you ready?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeTicTacToeLetsPlay.wav",
        "role": "Amőba szabályok & kezdés",
        "text": "The game is Tic-Tac-Toe. We play on a 3 by 3 game board. You will use the X sign while I will use the O sign. We place our signs alternately, and the goal is to get three signs in a row. I'll let you go first!",
        "use_cand3": False
    },
    {
        "filename": "mapATreeTicTacToeNobodyWins.wav",
        "role": "Amőba döntetlen",
        "text": "The board is filled entirely and we both failed to get three in a row : nobody wins! Do you want to try again?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeTicTacToeYouLose.wav",
        "role": "A mókus nyert",
        "text": "I got three in a row! I won. Do you want to try again?",
        "use_cand3": False
    },
    {
        "filename": "mapATreeTicTacToeYouWin.wav",
        "role": "A játékos nyert (Harmadik Ház kulcsa)",
        "text": "Wow, that's an unexpected move. But you got three in a row, I can't argue. You won! Take this key! It opens one of the houses in the village below the forest.",
        "use_cand3": False
    },
    {
        "filename": "mapATreeNoMoreChallenge.wav",
        "role": "Búcsú (Nincs több kihívás)",
        "text": "Sadly no, I have no more challenge for you... Playing with you was very fun, thank you for that!",
        "use_cand3": False
    }
]

PROMPT_TEMPLATE = (
    "You are The Squirrel, a quirky, eccentric elderly Greek scholar and philosopher living as a hermit high up in an ancient hollow tree. "
    "You speak English with a pronounced Greek Mediterranean accent, gentle rolling Rs, lively Greek vowel inflection, and animated scholar mannerisms. "
    "You are quick-witted, slightly absent-minded, deeply passionate about logic, riddles, numbers, and geometry, but you also feel lonely in your forest canopy. "
    "Act out this line with lively Greek hermit charm, energetic scholarly eccentricity, warmth, and genuine character delivery:\n\n"
    "\"{text}\""
)

def synthesize_line(item):
    out_path = os.path.join(OUTPUT_DIR, item["filename"])
    
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"[ALREADY EXISTS] {item['filename']} ({os.path.getsize(out_path)} bytes) – skipping.", flush=True)
        return True

    if item.get("use_cand3") and os.path.exists(CAND3_PATH) and os.path.getsize(CAND3_PATH) > 1000:
        shutil.copy(CAND3_PATH, out_path)
        size = os.path.getsize(out_path)
        print(f"[COPIED] {item['filename']} copied from approved candidate 3 ({size} bytes, ~{round(size/48000, 1)}s)", flush=True)
        return True

    prompt = PROMPT_TEMPLATE.format(text=item["text"])
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": "Puck"
                    }
                }
            }
        }
    }

    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    max_retries = 4
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                with wave.open(out_path, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw_pcm)
                size = os.path.getsize(out_path)
                print(f"[SUCCESS] {item['filename']} ({size} bytes, ~{round(size/48000, 1)}s)", flush=True)
                return True
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"[RETRY {attempt+1} for {item['filename']}] HTTP {e.code}: {err_body[:200]}", flush=True)
            if e.code == 429:
                print("Rate limit hit. Sleeping 35s before retry...", flush=True)
                time.sleep(35)
            else:
                time.sleep(6)
        except Exception as e:
            print(f"[RETRY {attempt+1} for {item['filename']}] {e}", flush=True)
            time.sleep(6)
            
    print(f"[FAILED] Could not synthesize {item['filename']}", flush=True)
    return False

def generate_player_html():
    player_path = os.path.join(OUTPUT_DIR, "player.html")
    cards_html = ""
    for idx, item in enumerate(LINES):
        fn = item["filename"]
        full_fn = os.path.join(OUTPUT_DIR, fn)
        size_kb = round(os.path.getsize(full_fn) / 1024, 1) if os.path.exists(full_fn) else 0
        dur_s = round(os.path.getsize(full_fn) / 48000, 1) if os.path.exists(full_fn) else 0
        
        cards_html += f"""
        <div class="card" id="card_{idx}">
            <div class="card-header">
                <span class="badge">#{idx+1} {item['role']}</span>
                <span class="file-name"><code>{fn}</code></span>
            </div>
            <div class="quote">„{item['text']}”</div>
            <div class="audio-box">
                <audio id="audio_{idx}" controls src="{fn}" preload="metadata"></audio>
            </div>
            <div class="meta">
                <span>Méret: <strong>{size_kb} KB</strong></span>
                <span>Hossz: <strong>~{dur_s}s</strong></span>
                <span><a href="{fn}" target="_blank" style="color:#38bdf8; text-decoration:none;">Közvetlen WAV letöltés &rarr;</a></span>
            </div>
        </div>
        """
        
    html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <title>Candy Box 2 – Mókus (The Squirrel) Teljes Hangtár</title>
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
            margin-bottom: 25px;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 20px;
        }}
        h1 {{
            color: #38bdf8;
            margin: 0 0 8px 0;
            font-size: 26px;
        }}
        p.subtitle {{
            color: #94a3b8;
            font-size: 15px;
            margin: 0;
        }}
        .control-bar {{
            background: #1e293b;
            padding: 16px 20px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 25px;
            position: sticky;
            top: 20px;
            z-index: 10;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }}
        .btn {{
            background: #2563eb;
            color: #fff;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
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
            gap: 16px;
        }}
        .card {{
            background: #182234;
            border: 1px solid #283548;
            border-radius: 12px;
            padding: 18px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}
        .card.active {{
            border-color: #38bdf8;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .badge {{
            background: #0284c7;
            color: white;
            font-size: 12px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 16px;
        }}
        .file-name code {{
            color: #a5f3fc;
            font-size: 13px;
        }}
        .quote {{
            background: #0b1120;
            border-left: 3px solid #38bdf8;
            padding: 10px 14px;
            font-style: italic;
            color: #cbd5e1;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 12px;
            border-radius: 0 6px 6px 0;
        }}
        audio {{
            width: 100%;
            height: 36px;
            outline: none;
        }}
        .meta {{
            display: flex;
            gap: 16px;
            color: #64748b;
            font-size: 12px;
            margin-top: 10px;
            border-top: 1px solid #1f2d42;
            padding-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Candy Box 2 – Mókus (The Squirrel) Teljes Hangtár</h1>
            <p class="subtitle">12 dialógus sorozat – Gemini 3.1 Flash TTS (Puck – Hóbortos Görög Remete Professzor)</p>
        </header>

        <div class="control-bar">
            <div>
                <strong>Összes dialógus: {len(LINES)} mondat</strong>
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
        const audioCount = {len(LINES)};
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
                if (c) {{
                    c.classList.add('active');
                    c.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                }}
                a.play();
                a.onended = () => {{
                    if (c) c.classList.remove('active');
                    playAllSequentially(startIndex + 1);
                }};
            }}
        }}

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
    with open(player_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] Full player written to {player_path}", flush=True)

if __name__ == "__main__":
    print(f"Starting Squirrel synthesis ({len(LINES)} lines) to {OUTPUT_DIR}...", flush=True)
    for idx, item in enumerate(LINES):
        print(f"\nProcessing [{idx+1}/{len(LINES)}]: {item['filename']}...", flush=True)
        synthesize_line(item)
        if not os.path.exists(os.path.join(OUTPUT_DIR, item["filename"])) or item.get("use_cand3"):
            pass
        else:
            time.sleep(15)
    generate_player_html()
    print("\nAll Squirrel processing complete!", flush=True)
