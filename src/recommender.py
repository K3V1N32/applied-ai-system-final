import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_valence: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: UserProfile, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    genre_score = 1.0 if song["genre"] == user_prefs.favorite_genre else 0.0
    mood_score = 1.0 if song["mood"] == user_prefs.favorite_mood else 0.0
    energy_score = 1.0 - abs(song["energy"] - user_prefs.target_energy)
    valence_score = 1.0 - abs(song["valence"] - user_prefs.target_valence)
    acoustic_score = (
        song["acousticness"] if user_prefs.likes_acoustic
        else 1.0 - song["acousticness"]
    )

    score = (
        0.30 * genre_score
        + 0.25 * mood_score
        + 0.20 * energy_score
        + 0.20 * valence_score
        + 0.05 * acoustic_score
    )

    reasons = []
    if genre_score == 1.0:
        reasons.append(f"matches your favorite genre ({song['genre']})")
    if mood_score == 1.0:
        reasons.append(f"matches your favorite mood ({song['mood']})")
    if energy_score >= 0.8:
        reasons.append("energy closely matches")
    if valence_score >= 0.8:
        reasons.append("emotional tone closely matches")
    if user_prefs.likes_acoustic and song["acousticness"] >= 0.6:
        reasons.append("leans acoustic, matching your preference")
    elif not user_prefs.likes_acoustic and song["acousticness"] <= 0.4:
        reasons.append("leans electronic, matching your preference")

    return score, reasons

def recommend_songs(user_prefs: UserProfile, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda entry: entry[1], reverse=True)
    return scored[:k]
