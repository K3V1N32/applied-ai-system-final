from unittest.mock import MagicMock

from ..src import deezer_previews


def stub_get(data, raises=None):
    def fake_get(url, params, timeout):
        if raises is not None:
            raise raises
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"data": data}
        return response
    return fake_get


def test_find_track_media_returns_preview_and_cover_from_first_match(monkeypatch):
    monkeypatch.setattr(deezer_previews.requests, "get", stub_get([{
        "preview": "https://example.com/preview.mp3",
        "album": {"cover_medium": "https://example.com/cover.jpg"},
    }]))

    media = deezer_previews.find_track_media("Some Artist", "Some Title")

    assert media.preview_url == "https://example.com/preview.mp3"
    assert media.cover_url == "https://example.com/cover.jpg"


def test_find_track_media_returns_none_fields_when_no_match(monkeypatch):
    monkeypatch.setattr(deezer_previews.requests, "get", stub_get([]))

    media = deezer_previews.find_track_media("Nobody", "Nothing")

    assert media.preview_url is None
    assert media.cover_url is None


def test_find_track_media_returns_none_fields_on_network_error(monkeypatch):
    monkeypatch.setattr(
        deezer_previews.requests, "get",
        stub_get([], raises=deezer_previews.requests.RequestException("network down")),
    )

    media = deezer_previews.find_track_media("Artist", "Title")

    assert media.preview_url is None
    assert media.cover_url is None


def test_find_track_media_handles_missing_album_data(monkeypatch):
    monkeypatch.setattr(deezer_previews.requests, "get", stub_get([{"preview": "url"}]))

    media = deezer_previews.find_track_media("Artist", "Title")

    assert media.preview_url == "url"
    assert media.cover_url is None


def test_find_track_media_queries_first_artist_only(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["query"] = params["q"]
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"data": [{"preview": "url", "album": {"cover_medium": "cover"}}]}
        return response

    monkeypatch.setattr(deezer_previews.requests, "get", fake_get)

    deezer_previews.find_track_media("Post Malone,Morgan Wallen", "Some Title")

    assert "Post Malone" in captured["query"]
    assert "Morgan Wallen" not in captured["query"]
