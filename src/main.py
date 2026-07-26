"""
Command-line demo for the Music Recommender.

Runs the same pipeline as src/app.py (semantic search -> Gemini explanation)
without the Streamlit UI: prompts for a free-text query and prints the
AI DJ's picks with reasoning.
"""
import os

from recommender import load_songs
from embeddings import get_or_build_embeddings, semantic_search
from gemini_dj import get_ai_recommendations

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_PATH = os.path.join(APP_DIR, "..", "data", "songs_working.csv")

CANDIDATE_POOL_SIZE = 20
NUM_RECOMMENDATIONS = 5


def main() -> None:
    print("Welcome to the VectorVibe command-line demo!")
    query = input("What kind of music would you like me to recommend? ").strip()
    if not query:
        print("You didn't enter anything -- nothing to recommend.")
        return

    songs = load_songs(SONGS_PATH)
    print(f"Loaded {len(songs)} songs.")

    print("Searching and asking your AI DJ...")
    song_ids, vectors = get_or_build_embeddings(songs)
    candidates = semantic_search(query, songs, song_ids, vectors, k=CANDIDATE_POOL_SIZE)
    recommendations = get_ai_recommendations(query, candidates, k=NUM_RECOMMENDATIONS)

    if not recommendations:
        print("No recommendations found for that query -- try describing it differently.")
        return

    print(f'\nRecommendations for: "{query}"\n')
    for rec in recommendations:
        song = rec["song"]
        source = "AI DJ (Gemini)" if rec["source"] == "gemini" else "closest match (AI DJ unavailable)"
        print(f"{song.title} - {song.artist}  [{source}]")
        print(f"  {rec['reasoning']}")
        print(f"  Genre: {song.genre} | Mood: {song.mood} | Popularity: {song.popularity}\n")


if __name__ == "__main__":
    main()
