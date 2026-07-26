import requests

SEARCH_URL = "https://api.deezer.com/search"
TIMEOUT_SECONDS = 5


def find_preview_url(artist: str, title: str) -> str | None:
    """
    Looks up a song on Deezer's public search API (no auth required) and
    returns a 30-second preview MP3 URL, or None if no match / on error.

    The returned URL is a short-lived signed link (expires in ~15 minutes),
    so it's meant to be fetched fresh right before display, not cached to
    disk alongside the rest of the pipeline's data.
    """
    primary_artist = artist.split(",")[0].strip()
    query = f'artist:"{primary_artist}" track:"{title}"'

    try:
        response = requests.get(SEARCH_URL, params={"q": query}, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        results = response.json().get("data", [])
    except (requests.RequestException, ValueError):
        return None

    return results[0]["preview"] if results else None
