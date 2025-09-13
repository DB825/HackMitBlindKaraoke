import whisper
import sounddevice as sd
import numpy as np
import wave
import os
import threading
import time

class AudioTranscriber:
    def __init__(self, model_size="base", sample_rate=16000):
        self.model_size = model_size
        self.sample_rate = sample_rate
        self.temp_filename = "temp_audio.wav"
        self.model = None
        self.is_recording = False
        self.audio_data = None
        self.recording_thread = None
        self.recording_duration = 10  # Default duration in seconds

        print("Loading Whisper model...")
        self.model = whisper.load_model(model_size)
        print(f"Whisper {model_size} model loaded successfully!")

    def start_recording(self):
        if self.is_recording:
            print("Already recording!")
            return

        self.is_recording = True
        self.audio_data = None

        def record_audio():
            print("🎤 Recording started... Press ENTER again to stop.")
            try:
                # Record audio using the working approach from your reference code
                self.audio_data = sd.rec(
                    int(self.recording_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16'
                )

                # Wait until recording is complete or stopped
                while self.is_recording and not sd.wait():
                    time.sleep(0.1)

            except Exception as e:
                print(f"Recording error: {e}")
                self.audio_data = None

        self.recording_thread = threading.Thread(target=record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def stop_recording(self):
        if not self.is_recording:
            print("Not currently recording!")
            return None

        print("🛑 Stopping recording...")
        self.is_recording = False

        # Stop the recording immediately
        sd.stop()

        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)

        if self.audio_data is None:
            print("No audio data recorded!")
            return None

        # Save audio to temporary WAV file using the working approach
        try:
            with wave.open(self.temp_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(self.audio_data.tobytes())

            print("🔄 Transcribing audio...")
            transcribed_text = self.transcribe_audio()

            # Clean up temporary file
            if os.path.exists(self.temp_filename):
                os.remove(self.temp_filename)

            return transcribed_text

        except Exception as e:
            print(f"Error saving/transcribing audio: {e}")
            return None

    def record_fixed_duration(self, duration_seconds=10):
        print(f"Recording for {duration_seconds} seconds... sing now!")

        # Use the exact working approach from your reference code
        audio_data = sd.rec(
            int(duration_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()
        print("Recording complete!")

        # Save to WAV file
        try:
            with wave.open(self.temp_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())

            print("🔄 Transcribing audio...")
            transcribed_text = self.transcribe_audio()

            # Clean up temporary file
            if os.path.exists(self.temp_filename):
                os.remove(self.temp_filename)

            return transcribed_text

        except Exception as e:
            print(f"Error saving/transcribing audio: {e}")
            return None

    def transcribe_audio(self):
        if not os.path.exists(self.temp_filename):
            print("No audio file found to transcribe!")
            return None

        try:
            # Transcribe using Whisper
            result = self.model.transcribe(self.temp_filename, language='en')
            transcribed_text = result["text"].strip()

            if not transcribed_text:
                print("No speech detected in the audio.")
                return None

            print(f"✅ Transcription complete!")
            return transcribed_text

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def transcribe_file(self, audio_file_path):
        if not os.path.exists(audio_file_path):
            print(f"Audio file not found: {audio_file_path}")
            return None

        try:
            print(f"Transcribing file: {audio_file_path}")
            result = self.model.transcribe(audio_file_path, language='en')
            return result["text"].strip()

        except Exception as e:
            print(f"Error transcribing file: {e}")
            return None

    def get_available_audio_devices(self):
        devices = sd.query_devices()
        print("Available audio devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} (Input)")
        return devices

    def set_audio_device(self, device_id):
        try:
            sd.default.device = device_id
            print(f"Audio device set to: {sd.query_devices(device_id)['name']}")
        except Exception as e:
            print(f"Error setting audio device: {e}")

    def cleanup(self):
        self.is_recording = False
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

# Test function
def test_transcriber():
    transcriber = AudioTranscriber()

    print("Testing transcriber...")
    print("Press Enter to start recording for 5 seconds...")
    input()

    # Test the fixed duration method (like your working code)
    result = transcriber.record_fixed_duration(5)
    if result:
        print(f"Transcribed: {result}")
    else:
        print("No transcription available")

    print("\nTesting interactive recording...")
    print("Press Enter to start, then Enter again to stop...")
    input()

    transcriber.start_recording()
    input("Press Enter to stop recording...")

    result = transcriber.stop_recording()
    if result:
        print(f"Transcribed: {result}")
    else:
        print("No transcription available")

if __name__ == "__main__":
    test_transcriber()