import requests
import pandas as pd
import base64

# --- CONFIG ---
CLIENT_ID = 'bf584b99b7104119a8f53c818c91f080'
CLIENT_SECRET = '0fa4c7f20f1b4ab3b7c5aa50ff4a20cd'
PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'
CSV_FILENAME = 'playlist_tracks.csv'

# --- AUTH ---
def get_access_token(client_id, client_secret):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
    }
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(auth_url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['access_token']

# --- FETCH TRACKS ---
def get_playlist_tracks(playlist_id, access_token):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'limit': 100,
        'offset': 0
    }
    tracks = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tracks.extend(data['items'])
        if data['next']:
            url = data['next']
            params = None
        else:
            break
    return tracks

# --- EXTRACT FIELDS ---
def extract_track_info(track_item, rank):
    track = track_item['track']
    if not track:
        return None
    return {
        'rank': rank,
        'name': track['name'],
        'artists': ', '.join([artist['name'] for artist in track['artists']]),
        'spotify_id': track['id'],
        'album_name': track['album']['name'],
        'duration_ms': track['duration_ms'],
        'explicit': track['explicit'],
        'popularity': track['popularity'],
        'added_at': track_item['added_at']
    }

def main():
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    items = get_playlist_tracks(PLAYLIST_ID, access_token)
    rows = []
    for i, item in enumerate(items, start=1):
        info = extract_track_info(item, i)
        if info:
            rows.append(info)
    df = pd.DataFrame(rows)
    df.to_csv(CSV_FILENAME, index=False)
    print(f" Saved {len(df)} tracks to {CSV_FILENAME}")

if __name__ == '__main__':
    main()