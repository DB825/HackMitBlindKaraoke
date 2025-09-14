from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import threading
import time
import random
import os
from Transcriber import AudioTranscriber
from LyricsComparison import LyricsComparator
from spotify_stuff import SpotifyController

app = Flask(__name__)
app.secret_key = 'karaoke_secret_key_2024'  # Change this in production
CORS(app)

class KaraokeWebGame:
    def __init__(self):
        self.songs_database = self.load_songs_database()
        self.transcriber = AudioTranscriber()
        self.comparator = LyricsComparator()
        self.spotify = SpotifyController()
        self.local_audio_folder = "local_audio"

        # Create local audio folder
        if not os.path.exists(self.local_audio_folder):
            os.makedirs(self.local_audio_folder)

        # Mood-based song categorization based on the moods in songs.json
        self.mood_songs = {
            'happy': [3],      # Happy Birthday (celebratory, joyful, cheerful)
            'sad': [4],        # Those Eyes (peaceful, reflective, calming) - moved to sad for demo
            'energetic': [2],  # Toxic (energetic, seductive, playful)
            'chill': [5]       # Twinkle Twinkle (innocent, peaceful, nostalgic)
        }

    def load_songs_database(self):
        with open('blind-karaoke/src/lib/database/songs.json', 'r') as f:
            data = json.load(f)
            return data['songs']

    def get_songs_by_mood(self, mood):
        song_ids = self.mood_songs.get(mood, [])  # Return empty list if mood not found
        return [song for song in self.songs_database if song['id'] in song_ids]

    def select_random_song_by_mood(self, mood):
        mood_songs = self.get_songs_by_mood(mood)
        if mood_songs:
            return random.choice(mood_songs)
        # Fallback to first song if no mood songs available
        print(f"Warning: No songs found for mood '{mood}', using fallback")
        return self.songs_database[0]

    def find_local_audio_file(self, song):
        """Find local audio file for the song using tagged filename"""
        if not os.path.exists(self.local_audio_folder):
            return None

        # First try the tagged local_audio_file from songs.json
        if 'local_audio_file' in song and song['local_audio_file']:
            tagged_file = os.path.join(self.local_audio_folder, song['local_audio_file'])
            if os.path.exists(tagged_file):
                return tagged_file

        # Fallback to pattern matching if tagged file doesn't exist
        extensions = ['.mp3', '.wav', '.ogg', '.m4a']
        patterns = [
            f"{song['title']}",
            f"{song['artist']} - {song['title']}",
            f"{song['title']} - {song['artist']}",
            f"{song['title'].lower()}",
            f"{song['artist'].lower()} - {song['title'].lower()}"
        ]

        for pattern in patterns:
            for ext in extensions:
                filename = pattern + ext
                filepath = os.path.join(self.local_audio_folder, filename)
                if os.path.exists(filepath):
                    return filepath
        return None

    def start_music(self, song):
        # Try local file first
        local_file = self.find_local_audio_file(song)

        if local_file:
            if self.spotify.play_local_file(local_file):
                return {'status': 'success', 'source': 'local', 'file': os.path.basename(local_file)}
        elif song['spotify_track_id']:
            if self.spotify.play_track(
                song['spotify_track_id'],
                song_title=song['title'],
                artist=song['artist']
            ):
                return {'status': 'success', 'source': 'spotify_preview'}

        return {'status': 'error', 'message': 'No audio source available'}

    def stop_music(self):
        self.spotify.pause_playback()
        return {'status': 'success'}

    def start_recording(self):
        self.transcriber.start_recording()
        return {'status': 'success'}

    def stop_recording(self):
        transcribed_text = self.transcriber.stop_recording()
        return transcribed_text

    def analyze_performance(self, transcribed_text, song_lyrics):
        results = self.comparator.compare_lyrics(transcribed_text, song_lyrics)
        return results

# Global game instance
game = KaraokeWebGame()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mood-selection')
def mood_selection():
    return render_template('mood_selection.html')

@app.route('/karaoke/<mood>')
def karaoke(mood):
    # Select random song based on mood
    song = game.select_random_song_by_mood(mood)
    session['current_song'] = song
    session['mood'] = mood
    return render_template('karaoke.html', mood=mood, song_title="Mystery Song")

@app.route('/results')
def results():
    if 'results_data' not in session:
        return redirect(url_for('home'))

    results_data = session['results_data']
    song = session.get('current_song', {})

    return render_template('results.html',
                         song=song,
                         results=results_data['results'],
                         transcribed_text=results_data['transcribed_text'])

# API Routes
@app.route('/api/start-music', methods=['POST'])
def start_music():
    song = session.get('current_song')
    if not song:
        return jsonify({'status': 'error', 'message': 'No song selected'})

    result = game.start_music(song)
    return jsonify(result)

@app.route('/api/stop-music', methods=['POST'])
def stop_music():
    result = game.stop_music()
    return jsonify(result)

@app.route('/api/start-recording', methods=['POST'])
def start_recording():
    result = game.start_recording()
    return jsonify(result)

@app.route('/api/stop-recording', methods=['POST'])
def stop_recording():
    transcribed_text = game.stop_recording()
    song = session.get('current_song')

    if transcribed_text and song:
        # Stop music when recording stops
        game.stop_music()

        # Analyze performance
        results = game.analyze_performance(transcribed_text, song['lyrics'])

        # Store results in session
        session['results_data'] = {
            'transcribed_text': transcribed_text,
            'results': results
        }

        return jsonify({
            'status': 'success',
            'transcribed_text': transcribed_text,
            'redirect': url_for('results')
        })

    return jsonify({'status': 'error', 'message': 'No transcription available'})

@app.route('/api/start-karaoke', methods=['POST'])
def start_karaoke():
    """Combined endpoint: Start music and recording together"""
    song = session.get('current_song')
    if not song:
        return jsonify({'status': 'error', 'message': 'No song selected'})

    # Start music first
    music_result = game.start_music(song)
    if music_result['status'] != 'success':
        return jsonify(music_result)

    # Start recording
    recording_result = game.start_recording()
    if recording_result['status'] != 'success':
        game.stop_music()  # Stop music if recording fails
        return jsonify(recording_result)

    # Return combined success result
    return jsonify({
        'status': 'success',
        'music_source': music_result.get('source', 'unknown'),
        'message': 'Karaoke started! Music playing and recording...'
    })

@app.route('/api/stop-karaoke', methods=['POST'])
def stop_karaoke():
    """Combined endpoint: Stop music and recording together"""
    transcribed_text = game.stop_recording()
    game.stop_music()

    song = session.get('current_song')

    if transcribed_text and song:
        # Analyze performance
        results = game.analyze_performance(transcribed_text, song['lyrics'])

        # Store results in session
        session['results_data'] = {
            'transcribed_text': transcribed_text,
            'results': results
        }

        return jsonify({
            'status': 'success',
            'transcribed_text': transcribed_text,
            'redirect': url_for('results')
        })

    return jsonify({'status': 'error', 'message': 'No transcription available'})

if __name__ == '__main__':
    print("Blind Karaoke Web App Starting...")
    print("Open your browser to: http://localhost:5000")
    print("Multi-page karaoke experience ready!")
    app.run(debug=True, host='0.0.0.0', port=5000)