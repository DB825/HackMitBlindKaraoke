import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import keyboard
import threading
import os
import webbrowser
import pygame
import requests
from io import BytesIO

class SpotifyController:
    def __init__(self):
        # Spotify Developer credentials
        self.client_id = "dbff5b5d3efe40c598aff8029738bc38"
        self.client_secret = "da33d9e0c27e4f6caf3dd6dc0adfe9a1"
        self.redirect_uri = "http://127.0.0.1:8888/callback"

        self.scope = "user-modify-playback-state user-read-playback-state"
        self.sp = None
        self.current_track_id = None
        self.is_playing = False
        self.use_integrated_player = True  # Use integrated player instead of Spotify app

        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
            print("Integrated audio player initialized")
        except Exception as e:
            print(f"Warning: Could not initialize audio player: {e}")
            self.use_integrated_player = False

        self.setup_spotify()

    def setup_spotify(self):
        try:
            # Set up Spotify authentication (force new login)
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=".spotify_cache",
                open_browser=True,  # Force browser to open
                show_dialog=True    # Force login dialog even if logged in
            )

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            # Get current user info safely
            user = self.sp.current_user()
            display_name = user.get("display_name", "Unknown User")
            product = user.get("product", "unknown")

            print(f"Connected to Spotify as: {display_name}")
            print(f"Account product type: {product}")

            if product != "premium":
                print("⚠️ Warning: Spotify Premium is required for playback control.")

        except Exception as e:
            print(f"Spotify authentication failed: {e}")

            if "403" in str(e) and "user may not be registered" in str(e):
                print("\n🚨 USER REGISTRATION REQUIRED:")
                print("1. Go to https://developer.spotify.com/dashboard/applications")
                print("2. Click on your app")
                print("3. Go to Settings > Users and Access")
                print("4. Click 'Add New User'")
                print("5. Add the email address of your Spotify account")
                print("6. Try running the script again")
            else:
                print("Please check your credentials and make sure Spotify is installed and running.")

            self.sp = None

    def get_active_devices(self):
        if not self.sp:
            return []

        try:
            devices = self.sp.devices()
            return devices['devices']
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

    def select_device(self, device_id=None):
        devices = self.get_active_devices()
        if not devices:
            print("No active Spotify devices found. Please open Spotify on a device.")
            return None

        if device_id:
            for device in devices:
                if device['id'] == device_id:
                    return device
        else:
            active_devices = [d for d in devices if d['is_active']]
            if active_devices:
                return active_devices[0]
            else:
                return devices[0]

    def play_track_integrated(self, track_id, song_title=None, artist=None):
        """Play track using integrated player (30-second preview)"""
        if not self.sp:
            print("Spotify not connected!")
            return False

        try:
            track_info = self.sp.track(track_id)
            preview_url = track_info.get('preview_url')

            # If no preview, try to find alternative with preview
            if not preview_url and song_title and artist:
                print("No preview for original track, searching for alternative...")
                alternative = self.find_track_with_preview(song_title, artist)
                if alternative:
                    preview_url = alternative['preview_url']
                    print(f"Found alternative: {alternative['name']} by {alternative['artist']}")
                else:
                    print("⚠️ No preview available for this track or alternatives")
                    return False
            elif not preview_url:
                print("⚠️ No preview available for this track")
                return False

            # Download and play preview
            try:
                if 'track_info' in locals():
                    print(f"Playing preview: {track_info['name']} by {track_info['artists'][0]['name']}")
                else:
                    print("Playing preview (alternative track)")
            except UnicodeEncodeError:
                print("Playing preview (encoding issue with name)")

            response = requests.get(preview_url)
            if response.status_code != 200:
                print("Failed to download preview")
                return False

            audio_data = BytesIO(response.content)
            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()

            self.current_track_id = track_id
            self.is_playing = True
            return True

        except Exception as e:
            print(f"Error playing integrated track: {e}")
            return False

    def play_local_file(self, file_path):
        """Play local audio file"""
        try:
            if not os.path.exists(file_path):
                print(f"Audio file not found: {file_path}")
                return False

            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            print(f"Playing local file: {os.path.basename(file_path)}")
            self.is_playing = True
            return True

        except Exception as e:
            print(f"Error playing local file: {e}")
            return False

    def play_track(self, track_id, device_id=None, song_title=None, artist=None):
        """Play track - uses integrated player if enabled, otherwise Spotify app"""
        if self.use_integrated_player:
            return self.play_track_integrated(track_id, song_title, artist)
        else:
            # Original Spotify app playback
            if not self.sp:
                print("Spotify not connected!")
                return False
            try:
                device = self.select_device(device_id)
                if not device:
                    return False

                track_uri = f"spotify:track:{track_id}"
                self.sp.start_playback(device_id=device['id'], uris=[track_uri])

                self.current_track_id = track_id
                self.is_playing = True

                track_info = self.sp.track(track_id)
                try:
                    print(f"▶️ Playing: {track_info['name']} by {track_info['artists'][0]['name']}")
                    print(f"On device: {device['name']}")
                except UnicodeEncodeError:
                    print(f"▶️ Playing track (encoding issue with name)")
                    print(f"On device: {device.get('name', 'Unknown')}")
                return True

            except Exception as e:
                print(f"Error playing track: {e}")
                return False

    def pause_playback(self, device_id=None):
        """Pause playback - works for both integrated and Spotify app"""
        if self.use_integrated_player:
            try:
                pygame.mixer.music.pause()
                self.is_playing = False
                print("⏸️ Paused playback")
                return True
            except Exception as e:
                print(f"Error pausing integrated playback: {e}")
                return False
        else:
            # Original Spotify app pause
            if not self.sp:
                print("Spotify not connected!")
                return False
            try:
                device = self.select_device(device_id)
                if not device:
                    return False

                self.sp.pause_playback(device_id=device['id'])
                self.is_playing = False
                print("⏸️ Paused playback")
                return True

            except Exception as e:
                print(f"Error pausing playback: {e}")
                return False

    def resume_playback(self, device_id=None):
        """Resume playback - works for both integrated and Spotify app"""
        if self.use_integrated_player:
            try:
                pygame.mixer.music.unpause()
                self.is_playing = True
                print("▶️ Resumed playback")
                return True
            except Exception as e:
                print(f"Error resuming integrated playback: {e}")
                return False
        else:
            # Original Spotify app resume
            if not self.sp:
                print("Spotify not connected!")
                return False
            try:
                device = self.select_device(device_id)
                if not device:
                    return False

                self.sp.start_playback(device_id=device['id'])
                self.is_playing = True
                print("▶️ Resumed playback")
                return True

            except Exception as e:
                print(f"Error resuming playback: {e}")
                return False

    def stop_playback(self):
        """Stop playback completely"""
        if self.use_integrated_player:
            try:
                pygame.mixer.music.stop()
                self.is_playing = False
                print("⏹️ Stopped playback")
                return True
            except Exception as e:
                print(f"Error stopping integrated playback: {e}")
                return False
        else:
            return self.pause_playback()

    def set_volume(self, volume_percent, device_id=None):
        """Set volume - works for both integrated and Spotify app"""
        volume = max(0, min(100, volume_percent))

        if self.use_integrated_player:
            try:
                # pygame volume is 0.0 to 1.0
                pygame.mixer.music.set_volume(volume / 100.0)
                print(f"🔊 Volume set to {volume}%")
                return True
            except Exception as e:
                print(f"Error setting integrated volume: {e}")
                return False
        else:
            # Original Spotify app volume
            if not self.sp:
                print("Spotify not connected!")
                return False
            try:
                device = self.select_device(device_id)
                if not device:
                    return False

                self.sp.volume(volume, device_id=device['id'])
                print(f"🔊 Volume set to {volume}%")
                return True

            except Exception as e:
                print(f"Error setting volume: {e}")
                return False

    def search_track(self, query, limit=10):
        if not self.sp:
            print("Spotify not connected!")
            return []

        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = results['tracks']['items']

            search_results = []
            for i, track in enumerate(tracks):
                preview_status = "✅ Preview" if track['preview_url'] else "❌ No Preview"
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,
                    'preview_url': track['preview_url']
                }
                search_results.append(track_info)
                print(f"{i+1}. {track_info['name']} by {track_info['artist']} - {preview_status}")

            return search_results

        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

    def find_track_with_preview(self, song_title, artist):
        """Search for a track and find one with a preview available"""
        if not self.sp:
            return None

        # Try different search queries
        queries = [
            f"track:{song_title} artist:{artist}",
            f"{song_title} {artist}",
            f"{song_title}",
            f"artist:{artist}"
        ]

        for query in queries:
            try:
                results = self.sp.search(q=query, type='track', limit=20)
                tracks = results['tracks']['items']

                # Look for tracks with previews
                for track in tracks:
                    if track['preview_url']:
                        return {
                            'id': track['id'],
                            'name': track['name'],
                            'artist': track['artists'][0]['name'],
                            'preview_url': track['preview_url']
                        }
            except Exception as e:
                print(f"Search error: {e}")
                continue

        return None

    def get_current_playback(self):
        if not self.sp:
            return None

        try:
            playback = self.sp.current_playback()
            if playback and playback['item']:
                return {
                    'track_id': playback['item']['id'],
                    'track_name': playback['item']['name'],
                    'artist_name': playback['item']['artists'][0]['name'],
                    'is_playing': playback['is_playing'],
                    'progress_ms': playback['progress_ms'],
                    'duration_ms': playback['item']['duration_ms']
                }
            return None

        except Exception as e:
            print(f"Error getting current playback: {e}")
            return None

    def create_playlist(self, name, description="Karaoke playlist"):
        if not self.sp:
            print("Spotify not connected!")
            return None

        try:
            user_id = self.sp.current_user()['id']
            playlist = self.sp.user_playlist_create(
                user=user_id,
                name=name,
                public=False,
                description=description
            )
            print(f"Created playlist: {name}")
            return playlist['id']

        except Exception as e:
            print(f"Error creating playlist: {e}")
            return None

    def display_devices(self):
        devices = self.get_active_devices()
        if not devices:
            print("No active Spotify devices found.")
            return

        print("Available Spotify devices:")
        for i, device in enumerate(devices):
            status = "🟢 Active" if device['is_active'] else "⚪ Available"
            print(f"  {i+1}. {device['name']} ({device['type']}) - {status}")

    def force_logout(self):
        """Clear cache and force logout"""
        cache_file = ".spotify_cache"
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print("Spotify cache cleared!")

        # Open Spotify logout URL in browser
        print("Opening Spotify logout page...")
        webbrowser.open("https://accounts.spotify.com/logout")
        print("Please log out manually, then run the script again.")


def setup_credentials():
    print("=== Spotify API Setup ===")
    print("1. Go to https://developer.spotify.com/dashboard/applications")
    print("2. Create a new app")
    print("3. Add 'http://localhost:8888/callback' to Redirect URIs")
    print("4. Copy your Client ID and Client Secret")
    print("\nReplace the placeholders in SpotifyAPI.py:")
    print("- YOUR_CLIENT_ID")
    print("- YOUR_CLIENT_SECRET")


def test_spotify():
    controller = SpotifyController()

    if not controller.sp:
        setup_credentials()
        return

    print("\n=== Testing Spotify Controller ===")
    controller.display_devices()

    # Test search
    print("\nSearching for 'Bohemian Rhapsody':")
    results = controller.search_track("Bohemian Rhapsody Queen")

    if results:
        print(f"\nTesting playback with: {results[0]['name']}")
        controller.play_track(results[0]['id'])

        print("Playing for 10 seconds...")
        time.sleep(10)

        controller.pause_playback()
        print("Test completed!")


if __name__ == "__main__":
    test_spotify()
