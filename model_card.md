# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeRender 3000**

---

## 2. Intended Use

Describe what your recommender is designed to do and who it is for. 

- VibeRender generates a list of recommended songs from a list of song data. The recommendations given are based mostly on genre and mood preferences of the user, and since our dataset is small, the genre and mood can actually be overwritten by energy and valence targets.
- VibeRender currently assumes this about it's users:
  - That a user only has one favorite genre, or mood.
  - That a user would be able to articulate taste such as energy, and valence as precise numeric targets.
  - That a user would only prefer only acoustic, or only electronic with a boolean value for likeing acoustics.
  - That a user would always weigh taste factors identically over any profile.
- VibeRender is currently mainly for classroom use as an experiment in converting data into recommendations. The songs that the recommender are not real songs, so it would be of little use to actual users.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.

- The features of each song that are scored are Genre, Mood, Energy, Valance, and acuousticness.
- User Preferences that are considered are favorite Genre, favorite Mood, Energy target, Valance target, and whether the user favors acoustic vs electronic music.
- How does the model turn those into a score
- VibeRender 3000 turns these preferences into a score by comparing each songs attributes to how close it is to the user preferences on a scale of 0-1, 0 being 0% match, and 1 being a 100% match, such as the genre of a song being the favorite genre of the user. Once each preference is converted into a 0-1 scale, we multiply each one by the weight we assign to that attribute, and those weights added together become a scale of 0-1 of how well the song matches the user profile

What changes did you make from the starter logic?
- I originally had song loading store the songs in a dictionary format, but switched later on to use the Song class for songs to unify how songs are handled.

---

## 4. Data  

Describe the dataset the model uses.  

- The dataset for this model is 20 songs all with a different mix of genre, mood, energy, and valence.
- There are 14 genres and 14 moods represented.
- I added 10 songs on top of the original 10 with the help of Claude.
- There are 2 major parts of musical taste missing from this dataset:
  - Temporal/Cultural dimension - No release year or regional/language origin is represented, so this dataset can't capture generational nostalgia or non-Western genre preferences.
  - No lyrical content signal - Mood/Valence are inferred from audio features only, but two songs with identical energy/valence can feel completely different depending on lyrics, and this dataset does not capture this.

---

## 5. Strengths

Where does your system seem to work well

- User profiles that give reasonable results are usually ones that have more than one matching genre or mood since those are the datapoints that match best.
- The patterns that scoring correctly captures are when genre and mood feel are closely matched with energy and valence feel.
- The user profile "Chill Lofi" has the best matches in this data set, and matches my intuition that it would get better matches based on the fact that we have so many songs in the chill/lofi category

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

- The largest factor this model does not factor in is lyrical closeness, given more time and resources, I'd love to implement Semantic Searching to compare lyrical likeness to find songs that match lyrical feeling.
- Some genres or moods that are underrepresented are classical/jazz and rap, and for moods, I would say romantic/sad/moody.
- The system overfits on Genre/Mood exact matches as those are where most of the weight is put when scoring the songs. Also the last 3 results overfit by the system since the dataset is so small and we always grab the top 5 even if all 5 don't match very well.
- Ways the scoring might unintentionally favor some users
- The sorting system will always favor the higher weighted scoring factors, causing some unintentional favor for some users. In the future, I would try to find more ways to compare and even out the weights so each one has more variance in the dataset.

---

## 7. Evaluation

How you checked whether the recommender behaved as expected. 

- Which user profiles you tested
- I tested [Intense Rock] and [Chill Lofi] User Profiles
- What you looked for in the recommendations
- For Intense Rock I was looking for Storm Hero to be the top pick as it matches the genre and mood for that profile, and also has close matching energy. With Chill Lofi, I looked for Library Rain or Midnight Coding to be the top pick, as they match the genre and mood, and both have close matching energy and valence to the profile.
- What suprised me about the test is how far off the feel of the last 4 songs the scoring picks is to the profile, since the dataset is so small it gave a happy pop song as the second recommendation for [Intense Rock], due to intense mood and close energy.
- What I did to test and run comparisons to my expectations:
- I wrote unit tests (tests/test_recommender.py) covering the scoring logic directly rather than just eyeballing output: that recommend() sorts results by score, that genre/mood matching is case-insensitive ("pop" vs "POP" vs "pOp" score identically), and that UserProfile validation correctly accepts boundary values (0.0, 0.5, 1.0) but rejects out-of-range energy/valence targets (-0.1, 1.1, -5.0, 2.0).
- I also ran paired comparisons in main.py to isolate one variable at a time. acoustic_chill vs. electronic_chill are identical profiles except for likes_acoustic, and even though acoustic match is only 5% of the score weight, it was enough to flip the 5th recommendation (Velvet Ballad vs. Night Drive Loop) - showing the weight has real effect even at low percentages.
- I used angry_classical (a profile with no genre/mood match anywhere in the dataset) to find the ceiling score reachable without an exact genre/mood hit - capped at 0.75 - which helped me understand how much weight those two fields carry relative to energy/valence/acoustic.

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.

- Here are some ideas I had for additional features/preferences
- tempo_bpm and danceability are already loaded onto every Song but never used in score_song() - I'd add target_tempo and target_danceability to UserProfile so those fields actually count toward the score.
- Right now weights (0.30/0.25/0.20/0.20/0.05) are hardcoded the same for every user. I'd let a profile specify its own weight distribution, so a user who cares more about energy than genre could say so.
- I'd add a "disliked genres/moods" list so a song can be penalized, not just fail to get a bonus - right now a bad match and a neutral match score the same on that factor.
- I'd also think about making genre/moods a favorite list instead of just a single instance to make sure to get a better idea of what a profile likes.
- Ways I could explain recommendations better
- The reason list only fires on binary/threshold checks (genre_score == 1.0, energy_score >= 0.8, etc.), so a song that's a decent-but-not-great energy match (say 0.75) gets zero credit in the explanation even though it moved the score. I'd show the actual weighted contribution of each factor (e.g. "genre match: +0.30, energy: +0.15 of 0.20") instead of pass/fail language.
- I'd add a line comparing this pick to the next-highest one, so the explanation answers "why this song over the other one," not just "why this song."
- Improving diversity among the top results
- recommend()/recommend_songs() just slice the top-k by raw score with no dedup, which is exactly why the last few picks in a small dataset all look alike (see the Limitations section). I'd add a diversity re-rank (like MMR) that penalizes a candidate for being too similar to a song already selected in the list.
- A simpler version: cap how many songs from the same genre can appear in one result list, so the top 5 aren't just "5 pop songs" when pop dominates the dataset.
- Handling more complex user tastes
- As I mentioned earlier, favorite_genre/favorite_mood are single strings, so a user who likes both rock and metal can't express that today - I'd change these to weighted lists.
- likes_acoustic is a hard boolean; I'd make it a continuous acoustic_preference float (like energy/valence) so "mostly acoustic but okay with electronic" is representable.
- Instead of forcing users to state numeric energy/valence targets (which the model card already flags as an unrealistic assumption), I'd let them submit a few songs they already like and infer targets from those.

---

## 9. Personal Reflection  

A few sentences about your experience.

- What you learned about recommender systems
- I learned a lot about weighing a user's preferences against a fixed set of features - deciding that genre and mood should carry more weight than energy and valence, for example, meant accepting that a close energy match could sometimes outrank a genre match. I also learned that comparing expected vs. actual results only works if you define your expectation before running the test, and that using too many similar datapoints in a small dataset makes the tail of your recommendations predictable and repetitive.
- Something unexpected or interesting you discovered
- Something unexpected was watching the weights fight each other in practice, not just in theory - my Intense Rock test returned a happy pop song as its #2 pick purely because 'intense' mood and close energy outweighed the fact that the genre didn't match at all. It made it obvious how much tuning goes into real content algorithms just to keep recommendations from feeling random, even when the underlying math is simple.
- How this changed the way you think about music recommendation apps
- This project changed how I think about services like Pandora or Spotify - I used to assume 'good recommendations' meant a smarter algorithm, but building even a simple weighted-scoring version showed me it's really a series of small, deliberate tradeoffs (how much genre should matter vs. energy, how many results to show, when to sacrifice diversity for relevance). The algorithm is only as good as those tradeoffs.
