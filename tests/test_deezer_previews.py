from unittest.mock import MagicMock

import deezer_previews


def stub_get(data, raises=None):
    def fake_get(url, params, timeout):
        if raises is not None:
            raise raises
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"data": data}
        return response
    return fake_get


def test_find_preview_url_returns_first_match(monkeypatch):
    monkeypatch.setattr(deezer_previews.requests, "get", stub_get([{"preview": "https://example.com/preview.mp3"}]))

    assert deezer_previews.find_preview_url("Some Artist", "Some Title") == "https://example.com/preview.mp3"


def test_find_preview_url_returns_none_when_no_match(monkeypatch):
    monkeypatch.setattr(deezer_previews.requests, "get", stub_get([]))

    assert deezer_previews.find_preview_url("Nobody", "Nothing") is None


def test_find_preview_url_returns_none_on_network_error(monkeypatch):
    monkeypatch.setattr(
        deezer_previews.requests, "get",
        stub_get([], raises=deezer_previews.requests.RequestException("network down")),
    )

    assert deezer_previews.find_preview_url("Artist", "Title") is None


def test_find_preview_url_queries_first_artist_only(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["query"] = params["q"]
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"data": [{"preview": "url"}]}
        return response

    monkeypatch.setattr(deezer_previews.requests, "get", fake_get)

    deezer_previews.find_preview_url("Post Malone,Morgan Wallen", "Some Title")

    assert "Post Malone" in captured["query"]
    assert "Morgan Wallen" not in captured["query"]
