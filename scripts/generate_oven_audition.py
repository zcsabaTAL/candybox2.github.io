#!/usr/bin/env python3
import os
import json
import base64
import time
import subprocess
import urllib.request
import urllib.error
import wave

PROJECT_ID = "ai-lab-499118"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "oven"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

AUDITION_TEXT = (
    "Hello! I'm a very old bread oven. I used to cook tons of good pastries, "
    "but no one is using me anymore. Maybe... maybe you could help me? "
    "Just let me take some sweets from you! Don't worry, you won't regret it! You can trust me."
)

def get_gcp_token():
    for cmd in [["/opt/homebrew/bin/gcloud", "auth", "print-access-token"], ["gcloud", "auth", "print-access-token"]]:
        try:
            return subprocess.check_output(cmd, universal_newlines=True).strip()
        except Exception:
            continue
    return None

def generate_gemini(filename, voice_name, prompt):
    if not GEMINI_KEY:
        print(f"[SKIP Gemini] GEMINI_API_KEY not set for {filename}")
        return False
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={GEMINI_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {
                    "prebuiltVoiceConfig": {
                        "voiceName": voice_name
                    }
                }
            }
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_pcm = base64.b64decode(data["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
                out_wav = os.path.join(OUTPUT_DIR, filename + ".wav")
                with wave.open(out_wav, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw_pcm)
                print(f"[OK Gemini] {filename}.wav generated ({len(raw_pcm)} bytes)")
                return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 15.0 * (attempt + 1)
                print(f"[WAIT] 429 Rate limit for {filename}, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[ERR Gemini] {filename}: {e.code} - {e.read().decode('utf-8')}")
                return False
        except Exception as e:
            print(f"[ERR Gemini] {filename}: {e}")
            return False
    return False

def generate_gcp(token, filename, voice_name, speaking_rate=0.90, pitch=0.0):
    if not token:
        print(f"[SKIP GCP] No GCP token for {filename}")
        return False
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    audio_config = {
        "audioEncoding": "MP3",
        "speakingRate": speaking_rate
    }
    if "Chirp" not in voice_name and "Journey" not in voice_name and pitch != 0.0:
        audio_config["pitch"] = pitch
        
    payload = {
        "input": {"text": AUDITION_TEXT},
        "voice": {
            "languageCode": voice_name[:5],
            "name": voice_name
        },
        "audioConfig": audio_config
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
            out_file = os.path.join(OUTPUT_DIR, filename + ".mp3")
            with open(out_file, "wb") as f:
                f.write(content)
            print(f"[OK GCP] {filename}.mp3 generated ({len(content)} bytes)")
            return True
    except urllib.error.HTTPError as e:
        print(f"[ERR GCP] {filename}: {e.code} - {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"[ERR GCP] {filename}: {e}")
        return False

def main():
    print(f"Generating Castle Bread Oven auditions in {OUTPUT_DIR}...")
    
    # 1. Devonshire / West Country Prompts for Gemini
    prompt_devon = (
        "You are an 80-year-old elderly female kitchen maid from Devon in the West Country of England, "
        "whose warm soul resides within an ancient castle bread oven. "
        "You have spent your whole life baking pastries and bread by the hearth fire. "
        "Your voice is warm, raspy, grandmotherly, rustic, and slightly creaky, speaking with a rich, "
        "authentic West Country / Devon dialect with rhotic 'r's, warm rolling vowels, and motherly folksy cadence. "
        "Speak in character with deep rustic warmth:\n\n"
        f"\"{AUDITION_TEXT}\""
    )
    
    # 2. Scouse (Liverpool) Prompt for Gemini
    prompt_scouse = (
        "You are a 75-year-old working-class elderly scullery maid from Liverpool, "
        "whose spirit is inside an ancient castle bread oven. "
        "Your voice is gravelly, raspy, lively, with an authentic Scouse dialect: "
        "distinctive velar fricatives, rising intonation at the end of clauses, cheeky, down-to-earth, and affectionate Northern warmth. "
        "Speak in character in your authentic Scouse accent:\n\n"
        f"\"{AUDITION_TEXT}\""
    )

    # 1. Candidate 1: Devon (Kore)
    print("--- Candidate 1: Devon (Gemini Kore) ---")
    generate_gemini("oven_cand1_devon_kore", "Kore", prompt_devon)
    time.sleep(6)

    # 2. Candidate 2: Devon (Aoede)
    print("--- Candidate 2: Devon (Gemini Aoede) ---")
    generate_gemini("oven_cand2_devon_aoede", "Aoede", prompt_devon)
    time.sleep(6)

    # 3. Candidate 3: Scouse (Gemini Kore)
    print("--- Candidate 3: Scouse (Gemini Kore) ---")
    generate_gemini("oven_cand3_scouse_kore", "Kore", prompt_scouse)
    time.sleep(6)

    # 4. Candidate 4: Scouse (Gemini Aoede)
    print("--- Candidate 4: Scouse (Gemini Aoede) ---")
    generate_gemini("oven_cand4_scouse_aoede", "Aoede", prompt_scouse)
    time.sleep(4)

    # 5. GCP Candidates
    token = get_gcp_token()
    if token:
        print("--- Candidate 5: GCP Chirp3 HD Kore (British Rustic) ---")
        generate_gcp(token, "oven_cand5_gcp_chirp3_kore", "en-GB-Chirp3-HD-Kore", speaking_rate=0.88)
        print("--- Candidate 6: GCP Neural2 F (Elderly British Maid) ---")
        generate_gcp(token, "oven_cand6_gcp_neural2_f_elderly", "en-GB-Neural2-F", speaking_rate=0.86, pitch=-2.5)

    print("Audition generation finished!")

if __name__ == "__main__":
    main()
