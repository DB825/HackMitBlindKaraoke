import json
import keyboard
import time
import threading
import os
from Transcriber import AudioTranscriber
from LyricsComparison import LyricsComparator
from spotify_stuff import SpotifyController

class KaraokeGame:
    def __init__(self):
        self.songs_database = self.load_songs_database()
        self.transcriber = AudioTranscriber()
        self.comparator = LyricsComparator()
        self.spotify = SpotifyController()
        self.current_song = None
        self.is_recording = False
        self.is_playing = False
        self.local_audio_folder = "local_audio"  # Folder for local audio files

    def load_songs_database(self):
        with open('blind-karaoke/src/lib/database/songs.json', 'r') as f:
            data = json.load(f)
            return data['songs']

    def select_random_song(self):
        import random
        self.current_song = random.choice(self.songs_database)
        print(f"Selected song: {self.current_song['title']} by {self.current_song['artist']}")
        return self.current_song

    def select_song_by_id(self, song_id):
        for song in self.songs_database:
            if song['id'] == song_id:
                self.current_song = song
                print(f"Selected song: {self.current_song['title']} by {self.current_song['artist']}")
                return self.current_song
        print(f"Song with ID {song_id} not found")
        return None

    def start_game(self):
        print("=== Karaoke Game ===")
        print("Integrated music player enabled")
        print("\nControls:")
        print("- ENTER: Start/Stop recording")
        print("- SPACE: Play/Stop music")
        print("- ESC: Quit game")

        # Create local audio folder if it doesn't exist
        if not os.path.exists(self.local_audio_folder):
            os.makedirs(self.local_audio_folder)
            print(f"Created folder: {self.local_audio_folder}")
            print("Tip: Place MP3/WAV files here to use as background music")

        # Select a song
        song_choice = input("\nEnter song ID (1-5) or press Enter for random: ").strip()
        if song_choice:
            try:
                song_id = int(song_choice)
                if not self.select_song_by_id(song_id):
                    return
            except ValueError:
                print("Invalid song ID")
                return
        else:
            self.select_random_song()

        print(f"\nDifficulty: {self.current_song['difficulty']}")
        print("Ready to play! Use the controls above.")

        # Set up keyboard listeners
        keyboard.on_press_key('enter', self.toggle_recording)
        keyboard.on_press_key('space', self.toggle_music)
        keyboard.on_press_key('esc', self.quit_game)

        # Keep the program running
        try:
            keyboard.wait('esc')
        except KeyboardInterrupt:
            self.cleanup()

    def toggle_recording(self, e):
        if self.is_recording:
            print("\nStopping recording...")
            transcribed_text = self.transcriber.stop_recording()
            if transcribed_text:
                print(f"You sang: {transcribed_text}")
                self.analyze_performance(transcribed_text)
            self.is_recording = False
        else:
            print("\nStarting recording...")
            self.transcriber.start_recording()
            self.is_recording = True

    def find_local_audio_file(self, song_title, artist):
        """Find local audio file for the song"""
        if not os.path.exists(self.local_audio_folder):
            return None

        # Common audio extensions
        extensions = ['.mp3', '.wav', '.ogg', '.m4a']

        # Try different filename patterns
        patterns = [
            f"{song_title}",
            f"{artist} - {song_title}",
            f"{song_title} - {artist}",
            f"{song_title.lower()}",
            f"{artist.lower()} - {song_title.lower()}"
        ]

        for pattern in patterns:
            for ext in extensions:
                filename = pattern + ext
                filepath = os.path.join(self.local_audio_folder, filename)
                if os.path.exists(filepath):
                    return filepath
        return None

    def toggle_music(self, e):
        if not self.current_song:
            print("No song selected!")
            return

        if self.is_playing:
            print("\nStopping music...")
            self.spotify.pause_playback()
            self.is_playing = False
        else:
            print("\nStarting music...")

            # Try local file first
            local_file = self.find_local_audio_file(
                self.current_song['title'],
                self.current_song['artist']
            )

            if local_file:
                print(f"Playing local file: {os.path.basename(local_file)}")
                if self.spotify.play_local_file(local_file):
                    self.is_playing = True
                else:
                    print("Failed to play local file")
            elif self.current_song['spotify_track_id']:
                print(f"Playing preview (30s): {self.current_song['title']}")
                if self.spotify.play_track(
                    self.current_song['spotify_track_id'],
                    song_title=self.current_song['title'],
                    artist=self.current_song['artist']
                ):
                    self.is_playing = True
                else:
                    print("Failed to play preview")
            else:
                print("No audio source available")
                print("Tip: Add an audio file to the local_audio folder")

    def analyze_performance(self, transcribed_text):
        if not self.current_song:
            return

        lyrics = self.current_song['lyrics']
        results = self.comparator.compare_lyrics(transcribed_text, lyrics)

        print("\n=== Performance Analysis ===")
        print(f"Word Error Rate (WER): {results['wer']:.1f}%")
        print(f"Bag of Words F1: {results['bow_f1']:.1f}%")
        print(f"Bigram F1: {results['bigram_f1']:.1f}%")
        print(f"Overall Score: {results['overall_score']:.1f}%")

        if results['overall_score'] >= 80:
            print("Excellent performance! 🌟")
        elif results['overall_score'] >= 60:
            print("Good job! 👍")
        elif results['overall_score'] >= 40:
            print("Not bad, keep practicing! 😊")
        else:
            print("Keep trying, you'll get better! 💪")

    def quit_game(self, e):
        print("\nThanks for playing!")
        self.cleanup()

    def cleanup(self):
        if self.is_recording:
            self.transcriber.stop_recording()
        if self.is_playing:
            self.spotify.stop_playback()

if __name__ == "__main__":
    game = KaraokeGame()
    game.start_game()