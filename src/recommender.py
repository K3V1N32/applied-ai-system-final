import csv
from typing import List
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song from data/songs_working.csv (see scripts/prepare_dataset.py).
    """
    id: int
    title: str
    artist: str
    genre: str
    primary_genre: str
    mood: str
    energy: float
    valence: float
    danceability: float
    acousticness: float
    tempo_bpm: float
    popularity: int
    good_for: List[str]
    lyrics_snippet: str


def load_songs(csv_path: str) -> List[Song]:
    """
    Loads the prepared working subset produced by scripts/prepare_dataset.py.
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            good_for = row["good_for"].split(";") if row["good_for"] else []
            songs.append(Song(
                id=int(row["id"]),
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                primary_genre=row["primary_genre"],
                mood=row["mood"],
                energy=float(row["energy"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
                tempo_bpm=float(row["tempo_bpm"]),
                popularity=int(row["popularity"]),
                good_for=good_for,
                lyrics_snippet=row["lyrics_snippet"],
            ))
    return songs


def _energy_descriptor(energy: float) -> str:
    if energy >= 0.75:
        return "high energy"
    if energy <= 0.35:
        return "low energy, mellow"
    return "moderate energy"


def _danceability_descriptor(danceability: float) -> str:
    if danceability >= 0.7:
        return "very danceable"
    if danceability <= 0.35:
        return "not very danceable"
    return "somewhat danceable"


def _valence_descriptor(valence: float) -> str:
    if valence >= 0.7:
        return "upbeat, positive mood"
    if valence <= 0.3:
        return "melancholic, dark mood"
    return "neutral mood"


def build_song_text(song: Song) -> str:
    """
    Builds the text that gets embedded for semantic search. Deliberately a
    composite of structured attributes plus a lyric snippet rather than the
    full lyrics alone -- raw lyrics skew toward theme/narrative rather than
    the audio-quality language users type (e.g. "high energy"), and full
    lyrics would drown out the genre/mood/energy signal in the embedding.
    """
    parts = [
        f"Genre: {song.genre}.",
        f"Emotion: {song.mood}.",
        f"{_energy_descriptor(song.energy)}, "
        f"{_danceability_descriptor(song.danceability)}, "
        f"{_valence_descriptor(song.valence)}.",
    ]
    if song.good_for:
        parts.append(f"Good for: {', '.join(song.good_for)}.")
    if song.lyrics_snippet:
        parts.append(f"Lyrics: {song.lyrics_snippet}")
    return " ".join(parts)
