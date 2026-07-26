import numpy as np

import embeddings
from recommender import Song


def make_song(id, title="Song"):
    return Song(
        id=id, title=title, artist="Artist", genre="pop", primary_genre="pop",
        mood="joy", energy=0.5, valence=0.5, danceability=0.5, acousticness=0.5,
        tempo_bpm=120, popularity=50, good_for=[], lyrics_snippet="",
    )


def fake_embed_texts(texts):
    return np.array([[float(len(t) % 7), 1.0, 0.0] for t in texts], dtype=np.float32)


def test_get_or_build_embeddings_writes_and_reloads_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(embeddings, "embed_texts", fake_embed_texts)
    cache_path = str(tmp_path / "cache.npz")

    ids, vectors = embeddings.get_or_build_embeddings([make_song(1), make_song(2)], cache_path=cache_path)

    assert set(ids) == {1, 2}
    assert vectors.shape == (2, 3)


def test_get_or_build_embeddings_only_embeds_new_songs(tmp_path, monkeypatch):
    cache_path = str(tmp_path / "cache.npz")
    monkeypatch.setattr(embeddings, "embed_texts", fake_embed_texts)
    embeddings.get_or_build_embeddings([make_song(1), make_song(2)], cache_path=cache_path)

    calls = []

    def counting_embed(texts):
        calls.append(texts)
        return fake_embed_texts(texts)

    monkeypatch.setattr(embeddings, "embed_texts", counting_embed)
    ids, vectors = embeddings.get_or_build_embeddings(
        [make_song(1), make_song(2), make_song(3)], cache_path=cache_path
    )

    assert set(ids) == {1, 2, 3}
    assert vectors.shape == (3, 3)
    assert len(calls) == 1
    assert len(calls[0]) == 1  # only the new song (id=3) was embedded


def test_get_or_build_embeddings_skips_entirely_when_up_to_date(tmp_path, monkeypatch):
    cache_path = str(tmp_path / "cache.npz")
    monkeypatch.setattr(embeddings, "embed_texts", fake_embed_texts)
    embeddings.get_or_build_embeddings([make_song(1)], cache_path=cache_path)

    def fail_if_called(texts):
        raise AssertionError("embed_texts should not be called when cache is already up to date")

    monkeypatch.setattr(embeddings, "embed_texts", fail_if_called)
    ids, vectors = embeddings.get_or_build_embeddings([make_song(1)], cache_path=cache_path)

    assert ids == [1]


def test_semantic_search_ranks_by_cosine_similarity(monkeypatch):
    monkeypatch.setattr(embeddings, "embed_texts", lambda texts: np.array([[1.0, 0.0]], dtype=np.float32))

    songs = [make_song(1, title="Aligned"), make_song(2, title="Orthogonal")]
    song_ids = [1, 2]
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)

    results = embeddings.semantic_search("query text", songs, song_ids, vectors, k=2)

    assert [song.id for song, _ in results] == [1, 2]
    assert results[0][1] > results[1][1]


def test_semantic_search_respects_k(monkeypatch):
    monkeypatch.setattr(embeddings, "embed_texts", lambda texts: np.array([[1.0, 0.0]], dtype=np.float32))

    songs = [make_song(i) for i in range(1, 6)]
    song_ids = [1, 2, 3, 4, 5]
    vectors = np.array([[1.0, 0.0]] * 5, dtype=np.float32)

    results = embeddings.semantic_search("query text", songs, song_ids, vectors, k=2)

    assert len(results) == 2
