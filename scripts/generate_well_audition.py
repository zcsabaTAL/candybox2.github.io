#!/usr/bin/env python3
import os
import json
import base64
import time
import subprocess
import urllib.request
import urllib.error

PROJECT_ID = "ai-lab-499118"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audio", "test", "wishing_well"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

AUDITION_TEXT = "Hello, wanderer... I am the wishing well. I shall grant you wishes in exchange of some sweets... When you throw candies into me, I will heal your wounds."

def get_gcp_token():
    try:
        return subprocess.check_output(["/opt/homebrew/bin/gcloud", "auth", "print-access-token"], universal_newlines=True).strip()
    except Exception:
        return subprocess.check_output(["gcloud", "auth", "print-access-token"], universal_newlines=True).strip()

def generate_gemini(filename, voice_name, prompt):
    if not GEMINI_KEY:
        return
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
            
            out_m4a = os.path.join(OUTPUT_DIR, filename + ".m4a")
            subprocess.run(["/usr/bin/afconvert", "-f", "m4af", "-d", "aac", out_wav, out_m4a], check=False)
            print(f"[OK Gemini] {filename}.wav + .m4a")
    except Exception as e:
        print(f"[ERR Gemini] {filename}: {e}")

def generate_gcp(token, filename, voice_name, speaking_rate=0.95, pitch=0.0):
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
            print(f"[OK GCP] {filename}.mp3")
    except urllib.error.HTTPError as e:
        print(f"[ERR GCP] {filename}: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[ERR GCP] {filename}: {e}")

def main():
    import wave
    token = get_gcp_token()

    # GCP candidates
    # Chirp3-HD Kore (British, high definition)
    generate_gcp(token, "well_gcp_chirp3_kore_gb", "en-GB-Chirp3-HD-Kore", speaking_rate=0.92)
    # Chirp3-HD Aoede (British, melodic)
    generate_gcp(token, "well_gcp_chirp3_aoede_gb", "en-GB-Chirp3-HD-Aoede", speaking_rate=0.90)
    # Chirp3-HD Kore (US, ethereal, soft)
    generate_gcp(token, "well_gcp_chirp3_kore_us", "en-US-Chirp3-HD-Kore", speaking_rate=0.90)
    # Studio-C (British, pitch shifted for light fairy nymph timbre)
    generate_gcp(token, "well_gcp_studio_c_fairy", "en-GB-Studio-C", speaking_rate=0.88, pitch=2.0)
    # Neural2-F (British, airy and gentle)
    generate_gcp(token, "well_gcp_neural2_f_fairy", "en-GB-Neural2-F", speaking_rate=0.88, pitch=1.5)
    # Wavenet-C (whispery resonance)
    generate_gcp(token, "well_gcp_wavenet_c_ethereal", "en-GB-Wavenet-C", speaking_rate=0.85, pitch=2.2)

    # Now retry Gemini with sleep
    print("Trying Gemini with backoff...")
    time.sleep(5)
    prompt_1 = (
        "You are the mystical elven fairy spirit dwelling within the ancient Wishing Well. "
        "Your voice is soft, breathy, gentle, and ethereal, with a melodic, cooing fairy whisper. "
        "Speak with serene, enchanting grace and an otherworldly, magical, soothing tone:\n\n"
        f"\"{AUDITION_TEXT}\""
    )
    generate_gemini("well_gemini_aoede_fairy", "Aoede", prompt_1)

    time.sleep(5)
    prompt_2 = (
        "You are an ancient water nymph and well maiden. Your voice is velvety, warm, hypnotic, "
        "and deeply mystical, with a soft, cooing resonance like shimmering moonlit water. "
        "Speak gently and tenderly in a serene, magical whisper:\n\n"
        f"\"{AUDITION_TEXT}\""
    )
    generate_gemini("well_gemini_kore_nymph", "Kore", prompt_2)

    print("Done!")

if __name__ == "__main__":
    main()
