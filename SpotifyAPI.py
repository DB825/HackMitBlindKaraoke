import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import keyboard
import threading

class SpotifyController:
    def __init__(self):
        # You'll need to set these up in your Spotify Developer Dashboard
        # https://developer.spotify.com/dashboard/applications
        self.client_id = "YOUR_CLIENT_ID"
        self.client_secret = "YOUR_CLIENT_SECRET"
        self.redirect_uri = "http://[::1]:8888/callback"

        self.scope = "user-modify-playback-state user-read-playback-state"
        self.sp = None
        self.current_track_id = None
        self.is_playing = False

        self.setup_spotify()

    def setup_spotify(self):
        try:
            # Set up authentication
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=".spotify_cache"
            )

            self.sp = spotipy.Spotify(auth_manager=auth_manager)

            # Test the connection
            user = self.sp.current_user()
            print(f"Connected to Spotify as: {user['display_name']}")

        except Exception as e:
            print(f"Spotify authentication failed: {e}")
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
            # Use specific device
            for device in devices:
                if device['id'] == device_id:
                    return device
        else:
            # Use first available device
            active_devices = [d for d in devices if d['is_active']]
            if active_devices:
                return active_devices[0]
            else:
                return devices[0]

    def play_track(self, track_id, device_id=None):
        if not self.sp:
            print("Spotify not connected!")
            return False

        try:
            # Get available devices
            device = self.select_device(device_id)
            if not device:
                return False

            # Create the track URI
            track_uri = f"spotify:track:{track_id}"

            # Start playback
            self.sp.start_playback(
                device_id=device['id'],
                uris=[track_uri]
            )

            self.current_track_id = track_id
            self.is_playing = True

            # Get track info
            track_info = self.sp.track(track_id)
            print(f"▶️ Playing: {track_info['name']} by {track_info['artists'][0]['name']}")
            print(f"On device: {device['name']}")

            return True

        except Exception as e:
            print(f"Error playing track: {e}")
            return False

    def pause_playback(self, device_id=None):
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

    def set_volume(self, volume_percent, device_id=None):
        if not self.sp:
            print("Spotify not connected!")
            return False

        try:
            device = self.select_device(device_id)
            if not device:
                return False

            volume = max(0, min(100, volume_percent))
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
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,
                    'preview_url': track['preview_url']
                }
                search_results.append(track_info)
                print(f"{i+1}. {track_info['name']} by {track_info['artist']}")

            return search_results

        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []

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

def setup_credentials():
    print("=== Spotify API Setup ===")
    print("1. Go to https://developer.spotify.com/dashboard/applications")
    print("2. Create a new app")
    print("3. Add 'http://localhost:8888/callback' to Redirect URIs")
    print("4. Copy your Client ID and Client Secret")
    print("\nReplace the placeholders in SpotifyAPI.py:")
    print("- YOUR_CLIENT_ID")
    print("- YOUR_CLIENT_SECRET")

# Test function
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

        print("Playing for 5 seconds...")
        time.sleep(5)

        controller.pause_playback()
        print("Test completed!")

if __name__ == "__main__":
    test_spotify()