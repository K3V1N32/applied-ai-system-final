import json
from unittest.mock import MagicMock

import gemini_dj
from recommender import Song


def make_song(id, title="Song"):
    return Song(
        id=id, title=title, artist="Artist", genre="pop", primary_genre="pop",
        mood="joy", energy=0.8, valence=0.8, danceability=0.8, acousticness=0.1,
        tempo_bpm=120, popularity=50, good_for=[], lyrics_snippet="",
    )


def stub_client(response_text=None, side_effect=None):
    fake_client = MagicMock()
    if side_effect is not None:
        fake_client.models.generate_content.side_effect = side_effect
    else:
        fake_response = MagicMock()
        fake_response.text = response_text
        fake_client.models.generate_content.return_value = fake_response
    return fake_client


def test_get_ai_recommendations_uses_gemini_picks(monkeypatch):
    candidates = [(make_song(1, "Song A"), 0.9), (make_song(2, "Song B"), 0.7)]
    monkeypatch.setattr(
        gemini_dj, "client",
        stub_client(response_text=json.dumps({"picks": [{"song_id": 1, "reasoning": "Great match."}]})),
    )

    results = gemini_dj.get_ai_recommendations("upbeat pop", candidates, k=5)

    assert len(results) == 1
    assert results[0]["song"].title == "Song A"
    assert results[0]["reasoning"] == "Great match."
    assert results[0]["source"] == "gemini"


def test_get_ai_recommendations_respects_k(monkeypatch):
    candidates = [(make_song(1), 0.9), (make_song(2), 0.8), (make_song(3), 0.7)]
    monkeypatch.setattr(
        gemini_dj, "client",
        stub_client(response_text=json.dumps({"picks": [
            {"song_id": 1, "reasoning": "a"},
            {"song_id": 2, "reasoning": "b"},
            {"song_id": 3, "reasoning": "c"},
        ]})),
    )

    results = gemini_dj.get_ai_recommendations("upbeat pop", candidates, k=2)

    assert len(results) == 2


def test_get_ai_recommendations_falls_back_on_api_error(monkeypatch):
    candidates = [(make_song(1), 0.9), (make_song(2), 0.7)]
    monkeypatch.setattr(gemini_dj, "client", stub_client(side_effect=RuntimeError("simulated API failure")))

    results = gemini_dj.get_ai_recommendations("upbeat pop", candidates, k=1)

    assert len(results) == 1
    assert results[0]["source"] == "fallback"
    assert results[0]["song"].id == 1  # highest-similarity candidate


def test_get_ai_recommendations_falls_back_when_response_is_malformed(monkeypatch):
    candidates = [(make_song(1), 0.9)]
    monkeypatch.setattr(gemini_dj, "client", stub_client(response_text="not valid json"))

    results = gemini_dj.get_ai_recommendations("upbeat pop", candidates, k=1)

    assert results[0]["source"] == "fallback"


def test_get_ai_recommendations_falls_back_when_picks_reference_unknown_ids(monkeypatch):
    candidates = [(make_song(1), 0.9)]
    monkeypatch.setattr(
        gemini_dj, "client",
        stub_client(response_text=json.dumps({"picks": [{"song_id": 999, "reasoning": "not a real candidate"}]})),
    )

    results = gemini_dj.get_ai_recommendations("upbeat pop", candidates, k=5)

    assert results[0]["source"] == "fallback"


def test_get_ai_recommendations_drops_hallucinated_id_without_falling_back(monkeypatch):
    candidates = [(make_song(1, "Song A"), 0.9), (make_song(2, "Song B"), 0.7)]
    monkeypatch.setattr(
        gemini_dj, "client",
        stub_client(response_text=json.dumps({"picks": [
            {"song_id": 1, "reasoning": "a real candidate"},
            {"song_id": 999, "reasoning": "a hallucinated id not in the candidate set"},
        ]})),
    )

    results = gemini_dj.get_ai_recommendations("upbeat pop", candidates, k=5)

    # the one valid pick should survive on its own merits, not trigger a full fallback
    assert len(results) == 1
    assert results[0]["song"].title == "Song A"
    assert results[0]["source"] == "gemini"
    assert all(rec["song"].id in {1, 2} for rec in results)
