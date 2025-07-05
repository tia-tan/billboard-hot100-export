import requests
import pandas as pd
import base64
import time
import webbrowser
from urllib.parse import urlencode, urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- CONFIG ---
CLIENT_ID = 'bf584b99b7104119a8f53c818c91f080'
CLIENT_SECRET = '0fa4c7f20f1b4ab3b7c5aa50ff4a20cd'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'playlist-read-private'
PLAYLIST_ID = '6UeSakyzhiEt4NB3UAd6NQ'
CSV_FILENAME = 'billboard_hot_100.csv'

# --- AUTH ---
class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        query = parse_qs(urlparse(self.path).query)
        setattr(self.server, 'auth_code', query.get('code', [None])[0])
        self.wfile.write(b'Success! You can close this window.')

def get_auth_code():
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(params)
    webbrowser.open(auth_url)
    server = HTTPServer(('localhost', 8888), AuthHandler)
    server.handle_request()
    return getattr(server, 'auth_code', None)

def get_user_token(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    r = requests.post('https://accounts.spotify.com/api/token', data=data)
    r.raise_for_status()
    return r.json()['access_token']

# --- SPOTIFY DATA ---
def get_playlist_tracks(playlist_id, token):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {token}'}
    items = []
    params = {'limit': 100}
    while url:
        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        items.extend(data['items'])
        url = data['next']
        params = None
    return items

def get_audio_features_single(track_id, token):
    url = f'https://api.spotify.com/v1/audio-features/{track_id}'
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(url, headers=headers)
    if r.status_code == 403:
        print(f"⚠️ Skipping track — 403 Forbidden for {track_id}")
        return None
    r.raise_for_status()
    return r.json()

def extract_track_info(item, rank):
    track = item['track']
    if not track:
        return None
    return {
        'rank': rank,
        'name': track['name'],
        'artists': ', '.join([a['name'] for a in track['artists']]),
        'spotify_id': track['id'],
        'album': track['album']['name'],
        'duration_ms': track['duration_ms'],
        'explicit': track['explicit'],
        'popularity': track['popularity'],
        'added_at': item['added_at']
    }

# --- MAIN ---
def main():
    print("🔐 Launching Spotify Login...")
    auth_code = get_auth_code()
    token = get_user_token(auth_code)

    print("📥 Fetching playlist data...")
    items = get_playlist_tracks(PLAYLIST_ID, token)

    rows = []
    print(f"🎵 Total tracks: {len(items)}")
    for i, item in enumerate(items, 1):
        info = extract_track_info(item, i)
        if not info or not info['spotify_id']:
            continue

        af = get_audio_features_single(info['spotify_id'], token)
        if af:
            info.update({
                'danceability': af.get('danceability'),
                'energy': af.get('energy'),
                'key': af.get('key'),
                'loudness': af.get('loudness'),
                'mode': af.get('mode'),
                'speechiness': af.get('speechiness'),
                'acousticness': af.get('acousticness'),
                'instrumentalness': af.get('instrumentalness'),
                'liveness': af.get('liveness'),
                'valence': af.get('valence'),
                'tempo': af.get('tempo'),
                'time_signature': af.get('time_signature')
            })
        rows.append(info)
        time.sleep(0.2)  # avoid rate limits

    df = pd.DataFrame(rows)
    df.to_csv(CSV_FILENAME, index=False)
    print(f"✅ Done! Saved {len(df)} tracks to {CSV_FILENAME}")

if __name__ == '__main__':
    main()
