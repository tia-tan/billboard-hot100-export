# Spotify Billboard Hot 100 Scraper

This Python script fetches all tracks from the Spotify Billboard Hot 100 playlist and saves detailed track and audio feature information to a CSV file.

## Features
- Uses Spotify Authorization Code Flow for authentication (browser login required)
- Fetches all tracks from the Billboard Hot 100 playlist
- Extracts track info: name, artists, album, duration, explicit, popularity, added date
- Fetches audio features for each track individually (danceability, energy, key, etc.)
- Saves all data to `billboard_hot_100.csv`

## Setup

### 1. Clone or Download
Place the script (`billboard_hot100_to_csv.py`) in your working directory.

### 2. Install Dependencies
```bash
pip install requests pandas
```

### 3. Spotify Developer Setup
- Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
- Create an app to get your `CLIENT_ID` and `CLIENT_SECRET`
- Set the Redirect URI in your app settings to: `http://127.0.0.1:8888/callback`
- Update the script with your credentials and redirect URI

## Usage

1. Run the script:
   ```bash
   python billboard_hot100_to_csv.py
   ```
2. A browser window will open for you to log in and authorize the app.
3. After authorization, the script will fetch playlist data and audio features for each track (with a short delay between requests to avoid rate limits).
4. Output will be saved to `billboard_hot_100.csv` in the current directory.

## Notes
- The script uses the Authorization Code Flow, which requires user login and consent.
- Make sure your Spotify account has access to the Billboard Hot 100 playlist.
- The script fetches audio features one track at a time to avoid 403 errors and rate limits.
- The script includes a delay to avoid hitting Spotify API rate limits.

## Known Issues & Limitations

- Originally, this project aimed to scrape the **Spotify Top 50 Global** playlist, but audio features were **not accessible** for many tracks due to API restrictions or playlist type.
- Switched to the **Billboard Hot 100** playlist on Spotify as an alternative.
- However, even with a valid user token and proper OAuth flow, **audio feature requests** (via `/v1/audio-features`) consistently returned **403 Forbidden** errors for all tracks.
- Affected fields include:

```vbnet
danceability, energy, key, loudness, mode, speechiness,
acousticness, instrumentalness, liveness, valence, tempo, time_signature


## Output
- The resulting CSV file contains columns for track metadata and audio features for each song in the playlist.

## License
MIT 
