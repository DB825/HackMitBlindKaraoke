import whisper
import sounddevice as sd
import numpy as np
import wave
import os
from scipy.signal import resample_poly
from math import gcd

# -----------------------------
# Parameters
# -----------------------------
DURATION = 10  # seconds
SAMPLE_RATE = 16000  # 16kHz, works best with Whisper
FILENAME = "temp_audio.wav"

# -----------------------------
# Function: Play WAV at custom speed
# -----------------------------
def play_audio_with_speed(filename, speed=1.0):
    """
    Play WAV file at a given speed without excessive scratchiness.
    speed > 1.0 => faster
    speed < 1.0 => slower
    """
    # Load WAV
    with wave.open(filename, 'rb') as wf:
        n_channels = wf.getnchannels()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        audio = wf.readframes(n_frames)
        audio_np = np.frombuffer(audio, dtype=np.int16)
        if n_channels > 1:
            audio_np = audio_np.reshape(-1, n_channels)

    # Convert to float32 in [-1, 1]
    audio_float = audio_np.astype(np.float32) / 32768.0

    # Resample using resample_poly for higher quality
    up = 1000
    down = int(1000 * speed)
    factor = gcd(up, down)
    up //= factor
    down //= factor
    audio_resampled = resample_poly(audio_float, up, down, axis=0)

    # Normalize to avoid clipping
    audio_resampled /= np.max(np.abs(audio_resampled)) + 1e-9

    # Play audio
    sd.play(audio_resampled, samplerate=framerate)
    sd.wait()

# -----------------------------
# Record audio
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
model = whisper.load_model("base")  # choose tiny/base/small/medium/large

print("Transcribing...")
result = model.transcribe(FILENAME)

print("\n--- Transcribed Lyrics ---")
print(result["text"])

# -----------------------------
# Ask user for playback speed
# -----------------------------
speed = float(input("\nEnter playback speed (1.0 = normal, 1.5 = faster, 0.8 = slower): "))
print(f"Playing audio at {speed}x speed...")
play_audio_with_speed(FILENAME, speed)

# Optional: delete temp file
os.remove(FILENAME)