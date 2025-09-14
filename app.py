from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import threading
import time
from Transcriber import AudioTranscriber
from LyricsComparison import LyricsComparator
from spotify_stuff import SpotifyController
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class KaraokeWebApp:
    def __init__(self):
        self.songs_database = self.load_songs_database()
        self.transcriber = AudioTranscriber()
        self.comparator = LyricsComparator()
        self.spotify = SpotifyController()
        self.current_song = None
        self.is_recording = False
        self.is_playing = False
        self.local_audio_folder = "local_audio"

        # Create local audio folder
        if not os.path.exists(self.local_audio_folder):
            os.makedirs(self.local_audio_folder)

    def load_songs_database(self):
        with open('blind-karaoke/src/lib/database/songs.json', 'r') as f:
            data = json.load(f)
            return data['songs']

    def select_song_by_id(self, song_id):
        for song in self.songs_database:
            if song['id'] == song_id:
                self.current_song = song
                return self.current_song
        return None

    def start_recording(self):
        if not self.is_recording:
            self.transcriber.start_recording()
            self.is_recording = True
            return True
        return False

    def stop_recording(self):
        if self.is_recording:
            transcribed_text = self.transcriber.stop_recording()
            self.is_recording = False
            if transcribed_text and self.current_song:
                results = self.comparator.compare_lyrics(
                    transcribed_text,
                    self.current_song['lyrics']
                )
                return {
                    'transcribed_text': transcribed_text,
                    'results': results
                }
        return None

    def find_local_audio_file(self, song_title, artist):
        """Find local audio file for the song"""
        if not os.path.exists(self.local_audio_folder):
            return None

        extensions = ['.mp3', '.wav', '.ogg', '.m4a']
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

    def start_music(self):
        if self.current_song and not self.is_playing:
            # Try local file first
            local_file = self.find_local_audio_file(
                self.current_song['title'],
                self.current_song['artist']
            )

            if local_file:
                if self.spotify.play_local_file(local_file):
                    self.is_playing = True
                    return {'status': 'success', 'source': 'local', 'file': os.path.basename(local_file)}
            elif self.current_song['spotify_track_id']:
                if self.spotify.play_track(
                    self.current_song['spotify_track_id'],
                    song_title=self.current_song['title'],
                    artist=self.current_song['artist']
                ):
                    self.is_playing = True
                    return {'status': 'success', 'source': 'spotify_preview'}

            return {'status': 'error', 'message': 'No audio source available'}
        return {'status': 'error', 'message': 'No song selected or already playing'}

    def stop_music(self):
        if self.is_playing:
            self.spotify.pause_playback()
            self.is_playing = False
            return {'status': 'success'}
        return {'status': 'error', 'message': 'Not currently playing'}

# Create global app instance
karaoke_app = KaraokeWebApp()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/songs', methods=['GET'])
def get_songs():
    return jsonify(karaoke_app.songs_database)

@app.route('/api/select-song', methods=['POST'])
def select_song():
    song_id = request.json.get('song_id')
    song = karaoke_app.select_song_by_id(song_id)
    if song:
        return jsonify({'status': 'success', 'song': song})
    return jsonify({'status': 'error', 'message': 'Song not found'})

@app.route('/api/start-recording', methods=['POST'])
def start_recording():
    if karaoke_app.start_recording():
        return jsonify({'status': 'success', 'message': 'Recording started'})
    return jsonify({'status': 'error', 'message': 'Already recording'})

@app.route('/api/stop-recording', methods=['POST'])
def stop_recording():
    result = karaoke_app.stop_recording()
    if result:
        return jsonify({'status': 'success', 'data': result})
    return jsonify({'status': 'error', 'message': 'Not recording or no transcription'})

@app.route('/api/start-music', methods=['POST'])
def start_music():
    return jsonify(karaoke_app.start_music())

@app.route('/api/stop-music', methods=['POST'])
def stop_music():
    return jsonify(karaoke_app.stop_music())

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'is_recording': karaoke_app.is_recording,
        'is_playing': karaoke_app.is_playing,
        'current_song': karaoke_app.current_song
    })

if __name__ == '__main__':
    print("🎤 Karaoke Web Server Starting...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🎵 Ready for frontend connection!")
    app.run(debug=True, host='0.0.0.0', port=5000)