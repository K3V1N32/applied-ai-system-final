# Planning the Music Recommender

## Phase 1 - Step 1-5:

### Identify the main data types involved in these systems, such as likes, skips, playlists, tempo, or mood.

- genre ***
- mood **
- tempo
- energy level **
- electronic vs acoustic *
- positive vs negative emotion **
- likes vs dislikes
- skips
- inclusion in other owned playlists

## Phase 1 - Step 3-1:

### Determine "Algorithm Recipe"

Profile data - Genre, Mood, Energy_Level, Valence_Level

High energy = 1.0 Energy \ Low Energy = 0.0 Energy
Positive/Bright valence = 1.0 Valence \ Negative/Sad valence = 0.0 Valence

- Scoring a song:
  - 0.30 weight for genre -> Genre matching is the most important factor, it plays the biggest role in the 'vibe' of a song.
  - 0.25 weight for mood -> Mood is the next most important, as the next step in matching the 'vibe' of the profile and it lets genre + mood outweigh energy/valence since we have a smaller dataset to work with.
  - 0.20 weight for energy -> Energy and valence both play an equal part in ranking a song, and together can outweigh genre when both match, letting a user experience a new genre while matching the 'vibe' of energy vs emotion.
  - 0.20 weight for valence ^
  - 0.05 weight for acousticness -> Acousticness can matter in the 'vibe' of a song, so I wanted it to at least have a small part in the wight of scoring.

So profile attributes might look like this: 

profile_name = Intense Rock
- favorite_genre = rock
- favorite_moods = intense
- energy_target = 1.0
- valence_target = 0.50
- likes_acoustic = false

profile_name = Chill Lofi
- favorite_genre = lofi
- favorite_mood = chill
- energy_target = 0.50
- valence_target = 0.50
- likes_acoustic = true

I originally wanted to have favorites be a list to account for multiple genres or moods, but since we are using a quite small list of songs, it makes more sense to narrow down a single favorite genre and mood to get a better result in the recommendation. If I ever upgrade this project to call on a song database API or similar, I would absolutely convert to a list style genre and mood favorability and add more attributes to a profile in order to combat the extensive variance in the millions of songs available.

# Claude formula:

Each component is normalized to a 0–1 sub-score before applying your weights, so the final `score` is guaranteed to land in [0, 1] (since the weights already sum to 1.0).

**Sub-scores:**

- `genre_score` = `1.0` if `song.genre == profile.favorite_genre` else `0.0`
  (categorical match — genre is either right or it isn't)
- `mood_score` = `1.0` if `song.mood == profile.favorite_mood` else `0.0`
  (same reasoning as genre)
- `energy_score` = `1.0 - abs(song.energy - profile.energy_target)`
  (both are already 0–1 floats, so distance-from-target naturally normalizes)
- `valence_score` = `1.0 - abs(song.valence - profile.valence_target)`
  (same reasoning as energy)
- `acoustic_score` = `song.acousticness` if `profile.likes_acoustic` else `1.0 - song.acousticness`
  (flips the continuous acousticness value depending on whether the user wants acoustic or electronic songs, instead of treating it as a binary match)

**Final formula:**

```
score = (0.30 * genre_score)
      + (0.25 * mood_score)
      + (0.20 * energy_score)
      + (0.20 * valence_score)
      + (0.05 * acoustic_score)
```

**Python translation (matches `score_song(user_prefs, song)` signature in `src/recommender.py`):**

```python
def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    genre_score = 1.0 if song["genre"] == user_prefs["favorite_genre"] else 0.0
    mood_score = 1.0 if song["mood"] == user_prefs["favorite_mood"] else 0.0
    energy_score = 1.0 - abs(song["energy"] - user_prefs["energy_target"])
    valence_score = 1.0 - abs(song["valence"] - user_prefs["valence_target"])
    acoustic_score = (
        song["acousticness"] if user_prefs["likes_acoustic"]
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
        reasons.append("energy closely matches your target")
    if valence_score >= 0.8:
        reasons.append("emotional tone closely matches your target")
    if user_prefs["likes_acoustic"] and song["acousticness"] >= 0.6:
        reasons.append("leans acoustic, matching your preference")
    elif not user_prefs["likes_acoustic"] and song["acousticness"] <= 0.4:
        reasons.append("leans electronic, matching your preference")

    return score, reasons
```

Why this shape fits your design notes:
- Genre and mood stay binary because they're categorical strings, not something you can take a numeric distance between — this preserves your "0.30 + 0.25 = 0.55 can outweigh energy+valence" intent from the weighting rationale.
- Energy and valence use `1 - abs(diff)` rather than binary match because your profile stores them as continuous targets (e.g. `valence_target = 0.50`), so a song at 0.48 should score almost as well as one at exactly 0.50 — a binary match/no-match would throw that signal away.
- Acousticness flips direction based on `likes_acoustic` (a bool) rather than comparing two floats, since the profile only records a preference direction, not a target acousticness value.
