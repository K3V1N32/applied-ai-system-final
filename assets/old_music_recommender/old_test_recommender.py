import pytest

from src.recommender import Song, UserProfile, Recommender, score_song

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


@pytest.mark.parametrize("target_energy", [0.0, 0.5, 1.0])
def test_user_profile_accepts_boundary_target_energy(target_energy):
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=target_energy,
        target_valence=0.5,
        likes_acoustic=False,
    )
    assert user.target_energy == target_energy


@pytest.mark.parametrize("target_valence", [0.0, 0.5, 1.0])
def test_user_profile_accepts_boundary_target_valence(target_valence):
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.5,
        target_valence=target_valence,
        likes_acoustic=False,
    )
    assert user.target_valence == target_valence


@pytest.mark.parametrize("target_energy", [-0.1, 1.1, -5.0, 2.0])
def test_user_profile_rejects_out_of_range_target_energy(target_energy):
    with pytest.raises(ValueError):
        UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=target_energy,
            target_valence=0.5,
            likes_acoustic=False,
        )


@pytest.mark.parametrize("target_valence", [-0.1, 1.1, -5.0, 2.0])
def test_user_profile_rejects_out_of_range_target_valence(target_valence):
    with pytest.raises(ValueError):
        UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.5,
            target_valence=target_valence,
            likes_acoustic=False,
        )


@pytest.mark.parametrize("favorite_genre,favorite_mood", [
    ("POP", "HAPPY"),
    ("Pop", "Happy"),
    ("pOp", "hAPPy"),
])
def test_score_song_genre_and_mood_match_is_case_insensitive(favorite_genre, favorite_mood):
    song = Song(
        id=1,
        title="Test Pop Track",
        artist="Test Artist",
        genre="pop",
        mood="happy",
        energy=0.8,
        tempo_bpm=120,
        valence=0.9,
        danceability=0.8,
        acousticness=0.2,
    )
    user = UserProfile(
        favorite_genre=favorite_genre,
        favorite_mood=favorite_mood,
        target_energy=0.8,
        target_valence=0.9,
        likes_acoustic=False,
    )

    _, reasons = score_song(user, song)

    assert any("favorite genre" in reason for reason in reasons)
    assert any("favorite mood" in reason for reason in reasons)


def test_score_song_case_insensitive_match_scores_same_as_exact_match():
    song = Song(
        id=1,
        title="Test Pop Track",
        artist="Test Artist",
        genre="pop",
        mood="happy",
        energy=0.8,
        tempo_bpm=120,
        valence=0.9,
        danceability=0.8,
        acousticness=0.2,
    )
    exact_user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        target_valence=0.9,
        likes_acoustic=False,
    )
    mismatched_case_user = UserProfile(
        favorite_genre="Pop",
        favorite_mood="Happy",
        target_energy=0.8,
        target_valence=0.9,
        likes_acoustic=False,
    )

    exact_score, _ = score_song(exact_user, song)
    mismatched_case_score, _ = score_song(mismatched_case_user, song)

    assert exact_score == mismatched_case_score
