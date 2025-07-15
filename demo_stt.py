import sounddevice as sd
from scipy.io.wavfile import write
import requests
import time
import os

# Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 10  # seconds
TEMP_FILE = "temp.wav"
SERVER_URL = "http://localhost:9000/v1/audio/transcriptions"

def record_audio(filename=TEMP_FILE, duration=DURATION):
    """Record audio from the microphone and save to a file."""
    print(f"🎙️  Recording for {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    print(f"✅ Audio saved to {filename}")
    return duration

def transcribe(filename=TEMP_FILE):
    """Send the recorded audio file to the Whisper server and get transcription."""
    print("🧠 Sending audio to transcription server...")

    start_time = time.time()
    with open(filename, "rb") as f:
        files = {"file": f}
        data = {
            "response_format": "json",  # or "text", "verbose_json", etc.
        }
        response = requests.post(SERVER_URL, files=files, data=data)
    
    response.raise_for_status()
    latency = time.time() - start_time

    try:
        text = response.json().get("text", "").strip()
    except Exception as e:
        print("⚠️ Failed to parse response:", response.text)
        raise e

    return text, latency

def main():
    record_duration = record_audio()
    text, latency = transcribe()
    
    print("\n--- Transcription Result ---")
    print(f"📝 Text: {text or '[No speech detected]'}")
    print(f"📏 Input Duration: {record_duration:.2f} sec")
    print(f"⚡ Time to Transcribe: {latency:.2f} sec")

    # Clean up temporary file
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)

if __name__ == "__main__":
    main()
