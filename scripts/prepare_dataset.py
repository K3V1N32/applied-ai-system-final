"""
Filters, dedupes, and samples the raw Kaggle Spotify dataset down to a
working subset for the recommender's embedding pipeline.

Run once locally after downloading data/spotify_dataset.csv (gitignored,
~1.1GB, not committed). Produces data/songs_working.csv (also gitignored).
"""
import pandas as pd

RAW_PATH = "data/spotify_dataset.csv"
OUT_PATH = "data/songs_working.csv"
CHUNK_SIZE = 20_000
TARGET_TOTAL = 2500
BUCKET_BUFFER_CAP = 500
MIN_LYRIC_CHARS = 30
LYRIC_SNIPPET_CHARS = 400

GOOD_FOR_COLUMNS = [
    "Good for Party",
    "Good for Work/Study",
    "Good for Relaxation/Meditation",
    "Good for Exercise",
    "Good for Running",
    "Good for Yoga/Stretching",
    "Good for Driving",
    "Good for Social Gatherings",
    "Good for Morning Routine",
]

USECOLS = [
    "Artist(s)", "song", "text", "emotion", "Genre", "Tempo", "Popularity",
    "Energy", "Danceability", "Positiveness", "Acousticness",
] + GOOD_FOR_COLUMNS

REQUIRED_COLUMNS = [
    "Artist(s)", "song", "text", "emotion", "Genre",
    "Energy", "Danceability", "Positiveness", "Acousticness", "Tempo",
]


def filter_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    chunk = chunk.dropna(subset=REQUIRED_COLUMNS)
    return chunk[chunk["text"].str.len() >= MIN_LYRIC_CHARS]


def bucket_key(genre: str) -> str:
    return genre.split(",")[0].strip().lower()


def collect_buckets() -> dict:
    """
    Streams the ~1.1GB file in chunks and keeps only a popularity-capped
    buffer per genre bucket, so memory stays bounded regardless of file size.
    """
    buckets: dict[str, pd.DataFrame] = {}
    reader = pd.read_csv(RAW_PATH, usecols=USECOLS, chunksize=CHUNK_SIZE, encoding="utf-8-sig")
    for chunk in reader:
        chunk = filter_chunk(chunk)
        if chunk.empty:
            continue
        chunk = chunk.assign(primary_genre=chunk["Genre"].map(bucket_key))
        for genre, group in chunk.groupby("primary_genre"):
            existing = buckets.get(genre)
            combined = pd.concat([existing, group]) if existing is not None else group
            if len(combined) > BUCKET_BUFFER_CAP:
                combined = combined.sort_values("Popularity", ascending=False).head(BUCKET_BUFFER_CAP)
            buckets[genre] = combined
    return buckets


def water_fill_quotas(bucket_sizes: dict, target_total: int) -> dict:
    """Distributes target_total across buckets evenly, capped by each bucket's size,
    redistributing any leftover to buckets that still have room."""
    remaining_buckets = dict(bucket_sizes)
    quotas = {genre: 0 for genre in bucket_sizes}
    remaining_target = target_total
    while remaining_target > 0 and remaining_buckets:
        share = max(1, remaining_target // len(remaining_buckets))
        for genre in list(remaining_buckets):
            take = min(share, remaining_buckets[genre], remaining_target)
            quotas[genre] += take
            remaining_buckets[genre] -= take
            remaining_target -= take
            if remaining_buckets[genre] == 0:
                del remaining_buckets[genre]
            if remaining_target == 0:
                break
    return quotas


def select_final_rows(buckets: dict) -> pd.DataFrame:
    pool = pd.concat(buckets.values(), ignore_index=True)
    pool = pool.sort_values("Popularity", ascending=False).drop_duplicates(
        subset=["Artist(s)", "song"], keep="first"
    )

    by_genre = {genre: group for genre, group in pool.groupby("primary_genre")}
    quotas = water_fill_quotas({genre: len(group) for genre, group in by_genre.items()}, TARGET_TOTAL)

    selected = [
        group.sort_values("Popularity", ascending=False).head(quotas[genre])
        for genre, group in by_genre.items()
        if quotas.get(genre)
    ]
    return pd.concat(selected, ignore_index=True)


def good_for_tags(row: pd.Series) -> str:
    return ";".join(
        label.replace("Good for ", "")
        for label in GOOD_FOR_COLUMNS
        if row[label] == 1
    )


def to_song_schema(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        "id": range(1, len(df) + 1),
        "title": df["song"],
        "artist": df["Artist(s)"],
        "genre": df["Genre"],
        "primary_genre": df["primary_genre"],
        "mood": df["emotion"],
        "energy": df["Energy"] / 100.0,
        "valence": df["Positiveness"] / 100.0,
        "danceability": df["Danceability"] / 100.0,
        "acousticness": df["Acousticness"] / 100.0,
        "tempo_bpm": df["Tempo"],
        "popularity": df["Popularity"],
        "good_for": df.apply(good_for_tags, axis=1),
        "lyrics_snippet": df["text"].str.slice(0, LYRIC_SNIPPET_CHARS),
    })


def main() -> None:
    buckets = collect_buckets()
    print(f"Scanned raw file, found {len(buckets)} genre buckets after filtering.")
    final_pool = select_final_rows(buckets)
    result = to_song_schema(final_pool)
    result.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(result)} songs across {result['primary_genre'].nunique()} genres to {OUT_PATH}")


if __name__ == "__main__":
    main()
