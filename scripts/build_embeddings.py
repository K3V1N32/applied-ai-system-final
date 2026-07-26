"""
Embeds every song in data/songs_working.csv and caches the vectors to
data/embeddings_cache.npz (gitignored, regenerated locally). Safe to
interrupt and re-run -- already-embedded songs are skipped.

Run from the repo root: python3 scripts/build_embeddings.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from recommender import load_songs
from embeddings import get_or_build_embeddings

SONGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "songs_working.csv")


def main() -> None:
    songs = load_songs(SONGS_PATH)
    print(f"Loaded {len(songs)} songs from {SONGS_PATH}")
    ids, vectors = get_or_build_embeddings(songs)
    print(f"Done. {len(ids)} songs embedded, vector shape {vectors.shape}.")


if __name__ == "__main__":
    main()
