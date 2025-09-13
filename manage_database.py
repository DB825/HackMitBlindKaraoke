#!/usr/bin/env python3
"""
Simple script to manage the song database JSON file
"""

import json
import os
from datetime import datetime

DATABASE_PATH = "blind-karaoke/src/lib/database/songs.json"

def load_database():
    """Load the database from JSON file"""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Database file not found at {DATABASE_PATH}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None

def save_database(database):
    """Save the database to JSON file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        print("✅ Database saved successfully!")
        return True
    except Exception as e:
        print(f"❌ Error saving database: {e}")
        return False

def add_song_interactive():
    """Add a new song interactively"""
    print("\n--- Add New Song ---")
    
    title = input("Song title: ").strip()
    if not title:
        print("❌ Title is required!")
        return False
    
    artist = input("Artist: ").strip()
    if not artist:
        print("❌ Artist is required!")
        return False
    
    print("Lyrics (press Enter twice when done):")
    lyrics_lines = []
    while True:
        line = input()
        if line == "" and lyrics_lines and lyrics_lines[-1] == "":
            break
        lyrics_lines.append(line)
    
    lyrics = "\n".join(lyrics_lines).strip()
    if not lyrics:
        print("❌ Lyrics are required!")
        return False
    
    spotify_id = input("Spotify Track ID (optional): ").strip() or None
    genre = input("Genre (default: Unknown): ").strip() or "Unknown"
    
    year_input = input("Year (default: 2024): ").strip()
    try:
        year = int(year_input) if year_input else 2024
    except ValueError:
        year = 2024
    
    difficulty = input("Difficulty (easy/medium/hard, default: medium): ").strip() or "medium"
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"
    
    # Load existing database
    database = load_database()
    if database is None:
        database = {"songs": []}
    
    # Generate new ID
    new_id = max([song.get("id", 0) for song in database["songs"]], default=0) + 1
    
    new_song = {
        "id": new_id,
        "title": title,
        "artist": artist,
        "lyrics": lyrics,
        "spotify_track_id": spotify_id,
        "genre": genre,
        "year": year,
        "difficulty": difficulty
    }
    
    database["songs"].append(new_song)
    
    print(f"\n✅ Song added:")
    print(f"   ID: {new_song['id']}")
    print(f"   Title: {new_song['title']}")
    print(f"   Artist: {new_song['artist']}")
    print(f"   Genre: {new_song['genre']}")
    print(f"   Year: {new_song['year']}")
    print(f"   Difficulty: {new_song['difficulty']}")
    if spotify_id:
        print(f"   Spotify: https://open.spotify.com/track/{spotify_id}")
    
    return save_database(database)

def list_songs():
    """List all songs in the database"""
    database = load_database()
    if database is None:
        return
    
    songs = database.get("songs", [])
    if not songs:
        print("📭 Database is empty!")
        return
    
    print(f"\n📚 Song Database ({len(songs)} songs)")
    print("=" * 60)
    
    for song in songs:
        print(f"ID: {song['id']:3d} | {song['title']} by {song['artist']}")
        print(f"     Genre: {song['genre']} | Year: {song['year']} | Difficulty: {song['difficulty']}")
        if song.get('spotify_track_id'):
            print(f"     Spotify: https://open.spotify.com/track/{song['spotify_track_id']}")
        print(f"     Lyrics: {song['lyrics'][:80]}{'...' if len(song['lyrics']) > 80 else ''}")
        print()

def search_songs():
    """Search songs in the database"""
    database = load_database()
    if database is None:
        return
    
    query = input("Enter search term (title or artist): ").strip().lower()
    if not query:
        print("❌ Please enter a search term!")
        return
    
    songs = database.get("songs", [])
    results = []
    
    for song in songs:
        if (query in song["title"].lower() or 
            query in song["artist"].lower()):
            results.append(song)
    
    if results:
        print(f"\n🔍 Found {len(results)} songs matching '{query}':")
        print("=" * 50)
        for song in results:
            print(f"ID: {song['id']:3d} | {song['title']} by {song['artist']}")
            print(f"     Genre: {song['genre']} | Difficulty: {song['difficulty']}")
            print()
    else:
        print(f"❌ No songs found matching '{query}'")

def show_database_info():
    """Show database information and statistics"""
    database = load_database()
    if database is None:
        return
    
    songs = database.get("songs", [])
    if not songs:
        print("📭 Database is empty!")
        return
    
    # Calculate statistics
    genres = {}
    difficulties = {}
    years = []
    
    for song in songs:
        genre = song.get("genre", "Unknown")
        genres[genre] = genres.get(genre, 0) + 1
        
        difficulty = song.get("difficulty", "medium")
        difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        years.append(song.get("year", 2024))
    
    print(f"\n📊 Database Statistics")
    print("=" * 30)
    print(f"Total songs: {len(songs)}")
    print(f"Genres: {dict(genres)}")
    print(f"Difficulties: {dict(difficulties)}")
    print(f"Year range: {min(years)} - {max(years)}")
    
    # Check file info
    if os.path.exists(DATABASE_PATH):
        stat = os.stat(DATABASE_PATH)
        size_kb = stat.st_size / 1024
        modified = datetime.fromtimestamp(stat.st_mtime)
        print(f"File size: {size_kb:.1f} KB")
        print(f"Last modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main menu"""
    while True:
        print("\n" + "="*50)
        print("🎵 SONG DATABASE MANAGER")
        print("="*50)
        print("1. List all songs")
        print("2. Search songs")
        print("3. Add new song")
        print("4. Database statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            list_songs()
        elif choice == "2":
            search_songs()
        elif choice == "3":
            add_song_interactive()
        elif choice == "4":
            show_database_info()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter 1-5.")

if __name__ == "__main__":
    main()
