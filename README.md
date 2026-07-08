# 🎵 Music Recommender Simulation

## Music Recommender Plan

This is where my main plan is located: [Plan.md](/plan.md)

## Project Summary

In this project, together with Claude AI, I built a music recommender system that:

- Represents songs, and userProfiles as data
- Designed scoring and ranking rules that turns that data into recommendations
- Give rankings and reasonings for each ranking.

I also evaluated what my system is good at vs what it gets wrong, and reflect on how this mirros real world AI recommendations.

---

## How The System Works

### Music Recommendation Systems

After having Claude research how spotify and youtube rank songs and make recommendations, the most popular approach is mixing more than one style, such as weighing both content-based, and collaborative filtering into the algorithms. Collaborative filtering usually follows patterns from other users such as "users who listened to/watched similar things as you also liked X, so you might too". Content-based filtering predicts what you will like based on properties of the content itself, such as the mood, genre, or even lyrics/emotional feel. While both companies use both methods in different ways, both use collaborative filtering as the primary driver for recommendations. For the small dataset in this project, we do not have much access to collaborative data such as similar profiles or users to match data to, so our best bet is to use the content-based rules and figure out how each data point should weigh in on the score we give to rank different songs for recommending songs to our user profiles.

**Scoring a song**:
  - 0.30 weight for genre -> Genre matching is the most important factor, it plays the biggest role in the 'vibe' of a song.
  - 0.25 weight for mood -> Mood is the next most important, as the next step in matching the 'vibe' of the profile and it lets genre + mood outweigh energy/valence since we have a smaller dataset to work with.
  - 0.20 weight for energy -> Energy and valence both play an equal part in ranking a song, and together can outweigh genre when both match, letting a user experience a new genre, while matching the 'vibe' of energy vs emotion.
  - 0.20 weight for valence ^
  - 0.05 weight for acousticness -> Acousticness can matter in the 'vibe' of a song, so I wanted it to at least have a small part in the wight of scoring.

**And the profiles will look like this**:

*profile_name = Intense Rock*
- favorite_genre = rock
- favorite_moods = intense
- energy_target = 1.0
- valence_target = 0.50
- likes_acoustic = false

*profile_name = Chill Lofi*
- favorite_genre = lofi
- favorite_mood = chill
- energy_target = 0.50
- valence_target = 0.50
- likes_acoustic = true

Songs will have genre, mood, energy, valence, and acoustic attributes

userProfiles will have favorite_genre, favorite_mood, target_energy, target_valence, and likes_acoustics attributes.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Limitations of my recommender:

- It only works on smaller datasets, given a larger sample it will recommend songs of only a single genre or mood, given that those are what it weighs heaviest.
- It does not understand lyrics, true vibe or language, it will easily recommend spanish or foreign origin songs over native language if the genre or mood is right.
- It might recommend 3-4 of the same genre song over a diverse list of genres, making it feel stale for many users.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



