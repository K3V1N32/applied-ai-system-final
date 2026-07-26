import os
import numpy as np
from sentence_transformers import SentenceTransformer

from recommender import Song, build_song_text

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
CACHE_PATH = os.path.join(DATA_DIR, "embeddings_cache.npz")

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 256

_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embeds texts locally -- no API calls, no rate limits."""
    vectors = _get_model().encode(texts, batch_size=BATCH_SIZE, show_progress_bar=False, convert_to_numpy=True)
    return vectors.astype(np.float32)


def _load_cache(cache_path: str) -> tuple[list[int], np.ndarray]:
    if not os.path.exists(cache_path):
        return [], np.empty((0, 0), dtype=np.float32)
    data = np.load(cache_path)
    return [int(i) for i in data["ids"]], data["vectors"]


def _save_cache(ids: list[int], vectors: np.ndarray, cache_path: str) -> None:
    np.savez(cache_path, ids=np.array(ids), vectors=vectors)


def get_or_build_embeddings(songs: list[Song], cache_path: str = CACHE_PATH) -> tuple[list[int], np.ndarray]:
    """
    Returns (song_ids, vectors) aligned to `songs`, embedding only whatever
    isn't already cached.
    """
    cached_ids, cached_vectors = _load_cache(cache_path)
    cached_set = set(cached_ids)

    pending = [song for song in songs if song.id not in cached_set]
    if not pending:
        print(f"Embedding cache is up to date ({len(cached_ids)} songs).")
        return cached_ids, cached_vectors

    print(f"Embedding {len(pending)} songs ({len(cached_ids)} already cached)...")
    new_vectors = embed_texts([build_song_text(song) for song in pending])

    ids = cached_ids + [song.id for song in pending]
    vectors = new_vectors if cached_vectors.size == 0 else np.vstack([cached_vectors, new_vectors])
    _save_cache(ids, vectors, cache_path)

    return ids, vectors


def semantic_search(
    query: str,
    songs: list[Song],
    song_ids: list[int],
    vectors: np.ndarray,
    k: int = 20,
) -> list[tuple[Song, float]]:
    """Ranks songs by cosine similarity between the query embedding and cached song vectors."""
    query_vector = embed_texts([query])[0]

    normed_vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    normed_query = query_vector / np.linalg.norm(query_vector)
    scores = normed_vectors @ normed_query

    id_to_song = {song.id: song for song in songs}
    ranked = sorted(zip(song_ids, scores), key=lambda pair: pair[1], reverse=True)
    return [(id_to_song[song_id], float(score)) for song_id, score in ranked[:k] if song_id in id_to_song]
