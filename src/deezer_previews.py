from dataclasses import dataclass

import requests

SEARCH_URL = "https://api.deezer.com/search"
TIMEOUT_SECONDS = 5


@dataclass
class TrackMedia:
    preview_url: str | None
    cover_url: str | None


def find_track_media(artist: str, title: str) -> TrackMedia:
    """
    Looks up a song on Deezer's public search API (no auth required) and
    returns its 30-second preview MP3 URL and album cover image URL. Both
    come from a single search call so they're guaranteed to be from the
    same matched track, rather than two independent lookups. Returns both
    fields as None if there's no match / on error.

    Both URLs are short-lived signed links (expire in ~15 minutes), so
    they're meant to be fetched fresh right before display, not cached to
    disk alongside the rest of the pipeline's data.
    """
    primary_artist = artist.split(",")[0].strip()
    query = f'artist:"{primary_artist}" track:"{title}"'

    try:
        response = requests.get(SEARCH_URL, params={"q": query}, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        results = response.json().get("data", [])
    except (requests.RequestException, ValueError):
        return TrackMedia(preview_url=None, cover_url=None)

    if not results:
        return TrackMedia(preview_url=None, cover_url=None)

    track = results[0]
    return TrackMedia(
        preview_url=track.get("preview"),
        cover_url=track.get("album", {}).get("cover_medium"),
    )
