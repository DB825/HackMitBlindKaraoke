import whisper
import sounddevice as sd
import numpy as np
import wave
import os
import json
from scipy.signal import resample_poly
from math import gcd

# -----------------------------
# Parameters
# -----------------------------
DURATION = 10  # seconds
SAMPLE_RATE = 16000  # 16kHz, works best with Whisper
FILENAME = "temp_audio.wav"
DATABASE_PATH = "blind-karaoke/src/lib/database/songs.json"

# -----------------------------
# Database Functions
# -----------------------------
def load_song_database():
    """Load the song database from JSON file"""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Database file not found at {DATABASE_PATH}")
        return {"songs": []}

def save_song_database(database):
    """Save the song database to JSON file"""
    try:
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        print("Database saved successfully!")
    except Exception as e:
        print(f"Error saving database: {e}")

def add_song_to_database(database, title, artist, lyrics, spotify_track_id=None, genre="Unknown", year=2024, difficulty="medium"):
    """Add a new song to the database"""
    # Generate new ID
    new_id = max([song.get("id", 0) for song in database["songs"]], default=0) + 1
    
    new_song = {
        "id": new_id,
        "title": title,
        "artist": artist,
        "lyrics": lyrics,
        "spotify_track_id": spotify_track_id,
        "genre": genre,
        "year": year,
        "difficulty": difficulty
    }
    
    database["songs"].append(new_song)
    return new_song

def search_songs(database, query):
    """Search songs by title or artist"""
    query_lower = query.lower()
    results = []
    
    for song in database["songs"]:
        if (query_lower in song["title"].lower() or 
            query_lower in song["artist"].lower()):
            results.append(song)
    
    return results

def get_song_by_id(database, song_id):
    """Get a specific song by ID"""
    for song in database["songs"]:
        if song["id"] == song_id:
            return song
    return None

def list_all_songs(database):
    """List all songs in the database"""
    print(f"\n=== Song Database ({len(database['songs'])} songs) ===")
    for song in database["songs"]:
        print(f"ID: {song['id']} | {song['title']} by {song['artist']} ({song['genre']}, {song['difficulty']})")
        if song['spotify_track_id']:
            print(f"    Spotify: https://open.spotify.com/track/{song['spotify_track_id']}")
        print(f"    Lyrics: {song['lyrics'][:100]}{'...' if len(song['lyrics']) > 100 else ''}")
        print()

def get_database_stats(database):
    """Get database statistics"""
    songs = database["songs"]
    genres = {}
    difficulties = {}
    years = []
    
    for song in songs:
        # Count genres
        genre = song.get("genre", "Unknown")
        genres[genre] = genres.get(genre, 0) + 1
        
        # Count difficulties
        difficulty = song.get("difficulty", "medium")
        difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        # Collect years
        years.append(song.get("year", 2024))
    
    return {
        "total_songs": len(songs),
        "genres": genres,
        "difficulties": difficulties,
        "year_range": {"min": min(years), "max": max(years)} if years else {"min": 0, "max": 0}
    }

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
# Database Management Menu
# -----------------------------
def database_menu():
    """Interactive database management menu"""
    database = load_song_database()
    
    while True:
        print("\n" + "="*50)
        print("🎵 SONG DATABASE MANAGER")
        print("="*50)
        print("1. List all songs")
        print("2. Search songs")
        print("3. Add new song")
        print("4. View song details")
        print("5. Database statistics")
        print("6. Record and transcribe (karaoke mode)")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            list_all_songs(database)
            
        elif choice == "2":
            query = input("Enter search term (title or artist): ").strip()
            if query:
                results = search_songs(database, query)
                if results:
                    print(f"\nFound {len(results)} songs:")
                    for song in results:
                        print(f"  - {song['title']} by {song['artist']} ({song['genre']})")
                else:
                    print("No songs found matching your search.")
            else:
                print("Please enter a search term.")
                
        elif choice == "3":
            print("\n--- Add New Song ---")
            title = input("Song title: ").strip()
            artist = input("Artist: ").strip()
            lyrics = input("Lyrics: ").strip()
            spotify_id = input("Spotify Track ID (optional): ").strip() or None
            genre = input("Genre (default: Unknown): ").strip() or "Unknown"
            year = input("Year (default: 2024): ").strip()
            year = int(year) if year.isdigit() else 2024
            difficulty = input("Difficulty (easy/medium/hard, default: medium): ").strip() or "medium"
            
            if title and artist and lyrics:
                new_song = add_song_to_database(database, title, artist, lyrics, spotify_id, genre, year, difficulty)
                print(f"\n✅ Song added successfully!")
                print(f"   ID: {new_song['id']}")
                print(f"   Title: {new_song['title']}")
                print(f"   Artist: {new_song['artist']}")
                
                save_choice = input("\nSave to database? (y/n): ").strip().lower()
                if save_choice == 'y':
                    save_song_database(database)
            else:
                print("❌ Title, artist, and lyrics are required!")
                
        elif choice == "4":
            song_id = input("Enter song ID: ").strip()
            if song_id.isdigit():
                song = get_song_by_id(database, int(song_id))
                if song:
                    print(f"\n--- Song Details ---")
                    print(f"ID: {song['id']}")
                    print(f"Title: {song['title']}")
                    print(f"Artist: {song['artist']}")
                    print(f"Genre: {song['genre']}")
                    print(f"Year: {song['year']}")
                    print(f"Difficulty: {song['difficulty']}")
                    if song['spotify_track_id']:
                        print(f"Spotify: https://open.spotify.com/track/{song['spotify_track_id']}")
                    print(f"\nLyrics:\n{song['lyrics']}")
                else:
                    print("❌ Song not found!")
            else:
                print("❌ Please enter a valid song ID!")
                
        elif choice == "5":
            stats = get_database_stats(database)
            print(f"\n--- Database Statistics ---")
            print(f"Total songs: {stats['total_songs']}")
            print(f"Genres: {stats['genres']}")
            print(f"Difficulties: {stats['difficulties']}")
            print(f"Year range: {stats['year_range']['min']} - {stats['year_range']['max']}")
            
        elif choice == "6":
            karaoke_mode(database)
            
        elif choice == "7":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice! Please enter 1-7.")

def karaoke_mode(database):
    """Record, transcribe, and show database info (without comparison)"""
    print("\n--- Karaoke Mode ---")
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

    # Load Whisper model and transcribe
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    print("Transcribing...")
    result = model.transcribe(FILENAME, fp16=False, language='en')

    print("\n--- Transcribed Lyrics ---")
    transcribed_lyrics = result["text"]
    print(transcribed_lyrics)
    
    print(f"\n--- Database Info ---")
    print(f"Database contains {len(database['songs'])} songs")
    print("Available songs:")
    for song in database["songs"][:5]:  # Show first 5 songs
        print(f"  - {song['title']} by {song['artist']}")
    if len(database["songs"]) > 5:
        print(f"  ... and {len(database['songs']) - 5} more")

    # Ask user for playback speed
    print("\n" + "="*30)
    speed = float(input("Enter playback speed (1.0 = normal, 1.5 = faster, 0.8 = slower): "))
    print(f"Playing audio at {speed}x speed...")
    play_audio_with_speed(FILENAME, speed)

    # Clean up
    os.remove(FILENAME)
    print("Temporary audio file deleted.")

if __name__ == "__main__":
    database_menu()
