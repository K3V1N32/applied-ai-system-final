import csv

from recommender import Song, load_songs, build_song_text

WORKING_CSV_FIELDS = [
    "id", "title", "artist", "genre", "primary_genre", "mood",
    "energy", "valence", "danceability", "acousticness", "tempo_bpm",
    "popularity", "good_for", "lyrics_snippet",
]


def write_songs_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(WORKING_CSV_FIELDS)
        writer.writerows(rows)


def make_song(**overrides):
    defaults = dict(
        id=1, title="Test", artist="Artist", genre="pop,dance", primary_genre="pop",
        mood="joy", energy=0.9, valence=0.8, danceability=0.85, acousticness=0.1,
        tempo_bpm=128, popularity=60, good_for=["Party"], lyrics_snippet="dancing all night",
    )
    defaults.update(overrides)
    return Song(**defaults)


def test_load_songs_parses_good_for_tags(tmp_path):
    csv_path = tmp_path / "songs.csv"
    write_songs_csv(csv_path, [
        ["1", "Test Song", "Test Artist", "pop", "pop", "joy", "0.8", "0.7", "0.75", "0.1", "120", "50", "Party;Exercise", "la la la"],
    ])

    songs = load_songs(str(csv_path))

    assert len(songs) == 1
    song = songs[0]
    assert song.id == 1
    assert song.title == "Test Song"
    assert song.good_for == ["Party", "Exercise"]
    assert song.energy == 0.8


def test_load_songs_handles_empty_good_for(tmp_path):
    csv_path = tmp_path / "songs.csv"
    write_songs_csv(csv_path, [
        ["2", "No Tags Song", "Another Artist", "rock", "rock", "anger", "0.9", "0.2", "0.4", "0.05", "140", "30", "", ""],
    ])

    songs = load_songs(str(csv_path))

    assert songs[0].good_for == []


def test_build_song_text_includes_key_attributes():
    song = make_song()

    text = build_song_text(song)

    assert "pop,dance" in text
    assert "joy" in text
    assert "high energy" in text
    assert "very danceable" in text
    assert "upbeat" in text
    assert "Party" in text
    assert "dancing all night" in text


def test_build_song_text_omits_good_for_when_empty():
    song = make_song(good_for=[], energy=0.2, danceability=0.2, valence=0.2)

    text = build_song_text(song)

    assert "Good for" not in text
    assert "low energy" in text


def test_build_song_text_omits_lyrics_when_missing():
    song = make_song(lyrics_snippet="")

    text = build_song_text(song)

    assert "Lyrics:" not in text
