"""
Lightweight Spotify Web API client using Client Credentials flow.
No user OAuth required — only used for track search.
"""
import time
import requests
from django.conf import settings
from django.core.cache import cache

_TOKEN_CACHE_KEY = 'spotify_access_token'


def is_configured() -> bool:
    """Return True if Spotify credentials are present in settings."""
    return bool(
        getattr(settings, 'SPOTIFY_CLIENT_ID', '') and
        getattr(settings, 'SPOTIFY_CLIENT_SECRET', '')
    )


def get_access_token() -> str | None:
    """
    Fetch a Spotify access token using Client Credentials flow.
    Caches the token until it expires.
    Returns None if credentials are not configured.
    """
    if not is_configured():
        return None

    cached = cache.get(_TOKEN_CACHE_KEY)
    if cached:
        return cached

    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={'grant_type': 'client_credentials'},
        auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET),
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    token = data['access_token']
    expires_in = data.get('expires_in', 3600)
    # Cache with a small buffer to avoid using an about-to-expire token
    cache.set(_TOKEN_CACHE_KEY, token, timeout=expires_in - 60)
    return token


def search_tracks(query: str, limit: int = 10) -> list[dict]:
    """
    Search Spotify for tracks matching the query.
    Returns a list of dicts with: id, title, artist, album, album_art_url,
    spotify_url.
    Returns an empty list if Spotify is not configured or the request fails.
    """
    token = get_access_token()
    if not token:
        return []

    try:
        response = requests.get(
            'https://api.spotify.com/v1/search',
            params={'q': query, 'type': 'track', 'limit': limit},
            headers={'Authorization': f'Bearer {token}'},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    tracks = []
    for item in response.json().get('tracks', {}).get('items', []):
        artists = ', '.join(a['name'] for a in item.get('artists', []))
        images = item.get('album', {}).get('images', [])
        album_art = images[0]['url'] if images else ''
        tracks.append({
            'id': item['id'],
            'title': item['name'],
            'artist': artists,
            'album': item.get('album', {}).get('name', ''),
            'album_art_url': album_art,
            'spotify_url': item.get('external_urls', {}).get('spotify', ''),
        })
    return tracks
