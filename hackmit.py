import whisper
import sounddevice as sd
import numpy as np
import wave
import os

# -----------------------------
# Parameters
# -----------------------------
DURATION = 10  # seconds
SAMPLE_RATE = 16000  # 16kHz, works best with Whisper
FILENAME = "temp_audio.wav"

# -----------------------------
# Record audio from microphone
# -----------------------------
print("Recording... sing now!")
audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
sd.wait()
print("Recording complete!")

# Save to WAV file
with wave.open(FILENAME, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit audio
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_data.tobytes())

# -----------------------------
# Load Whisper model and transcribe
# -----------------------------
print("Loading Whisper model...")
model = whisper.load_model("base")  # use tiny/base/small/medium/large

print("Transcribing...")
result = model.transcribe(FILENAME)

print("\n--- Transcribed Lyrics ---")
print(result["text"])

# Optional: delete temp file
os.remove(FILENAME)