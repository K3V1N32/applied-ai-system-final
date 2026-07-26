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

```Bash

          #####################################
          #   Music Recommender Simulation    #
          #####################################
        
> Loaded 20 songs from the dataset.

    #####################################
    #   Intense Rock Recommendations  #
    #####################################
    
Storm Runner - Score: 0.94
Selection Reasoning:
  - matches your favorite genre (rock)
  - matches your favorite mood (intense)
  - energy closely matches
  - leans electronic, matching your preference

Gym Hero - Score: 0.58
Selection Reasoning:
  - matches your favorite mood (intense)
  - energy closely matches
  - leans electronic, matching your preference

Neon Rebellion - Score: 0.43
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans electronic, matching your preference

Static Funeral - Score: 0.42
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans electronic, matching your preference

Broken Mirror - Score: 0.36
Selection Reasoning:
  - emotional tone closely matches
  - leans electronic, matching your preference


    #####################################
    #   Chill Lofi Recommendations  #
    #####################################
    
Library Rain - Score: 0.96
Selection Reasoning:
  - matches your favorite genre (lofi)
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Midnight Coding - Score: 0.95
Selection Reasoning:
  - matches your favorite genre (lofi)
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Focus Flow - Score: 0.70
Selection Reasoning:
  - matches your favorite genre (lofi)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Spacewalk Thoughts - Score: 0.66
Selection Reasoning:
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Marble Halls - Score: 0.42
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference


    #####################################
    #   Angry Metal Recommendations  #
    #####################################
    
Neon Rebellion - Score: 0.94
Selection Reasoning:
  - matches your favorite genre (metal)
  - matches your favorite mood (angry)
  - energy closely matches
  - emotional tone closely matches
  - leans electronic, matching your preference

Static Funeral - Score: 0.71
Selection Reasoning:
  - matches your favorite genre (metal)
  - energy closely matches
  - emotional tone closely matches
  - leans electronic, matching your preference

Broken Mirror - Score: 0.37
Selection Reasoning:
  - emotional tone closely matches
  - leans electronic, matching your preference

Night Drive Loop - Score: 0.35
Selection Reasoning:
  - energy closely matches
  - leans electronic, matching your preference

Storm Runner - Score: 0.35
Selection Reasoning:
  - energy closely matches
  - leans electronic, matching your preference


    #####################################
    #   Happy Pop Recommendations  #
    #####################################
    
Sunrise City - Score: 0.95
Selection Reasoning:
  - matches your favorite genre (pop)
  - matches your favorite mood (happy)
  - energy closely matches
  - emotional tone closely matches

Gym Hero - Score: 0.67
Selection Reasoning:
  - matches your favorite genre (pop)
  - energy closely matches
  - emotional tone closely matches

Rooftop Lights - Score: 0.66
Selection Reasoning:
  - matches your favorite mood (happy)
  - energy closely matches
  - emotional tone closely matches

Golden Hour Drive - Score: 0.63
Selection Reasoning:
  - matches your favorite mood (happy)
  - energy closely matches
  - emotional tone closely matches

Barnyard Stomp - Score: 0.40
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference


    #####################################
    #   Moody Synthwave Recommendations  #
    #####################################
    
Night Drive Loop - Score: 0.94
Selection Reasoning:
  - matches your favorite genre (synthwave)
  - matches your favorite mood (moody)
  - energy closely matches
  - emotional tone closely matches
  - leans electronic, matching your preference

Broken Mirror - Score: 0.38
Selection Reasoning:
  - energy closely matches
  - leans electronic, matching your preference

Storm Runner - Score: 0.37
Selection Reasoning:
  - emotional tone closely matches
  - leans electronic, matching your preference

Glacier Hum - Score: 0.36
Selection Reasoning:
  - emotional tone closely matches
  - leans electronic, matching your preference

Midnight Coding - Score: 0.35
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches

> Music Recommender Simulation completed.
```

**Edge-Case Tests**:
```Bash

    ######################################################
           Angry Classical (Edge-Case) Recommendations
    ######################################################
    
Marble Halls - Score: 0.68
Selection Reasoning:
  - matches your favorite genre (classical)
  - emotional tone closely matches
  - leans acoustic, matching your preference

Neon Rebellion - Score: 0.51
Selection Reasoning:
  - matches your favorite mood (angry)

Midnight Coding - Score: 0.41
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Focus Flow - Score: 0.40
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Library Rain - Score: 0.39
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference


    ######################################################
           Acoustic Chill (Edge-Case) Recommendations
    ######################################################
    
Midnight Coding - Score: 0.96
Selection Reasoning:
  - matches your favorite genre (lofi)
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Library Rain - Score: 0.94
Selection Reasoning:
  - matches your favorite genre (lofi)
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Focus Flow - Score: 0.70
Selection Reasoning:
  - matches your favorite genre (lofi)
  - energy closely matches
  - emotional tone closely matches
  - leans acoustic, matching your preference

Spacewalk Thoughts - Score: 0.62
Selection Reasoning:
  - matches your favorite mood (chill)
  - emotional tone closely matches
  - leans acoustic, matching your preference

Velvet Ballad - Score: 0.38
Selection Reasoning:
  - energy closely matches
  - emotional tone closely matches


    ######################################################
           Electronic Chill (Edge-Case) Recommendations
    ######################################################
    
Midnight Coding - Score: 0.94
Selection Reasoning:
  - matches your favorite genre (lofi)
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches

Library Rain - Score: 0.91
Selection Reasoning:
  - matches your favorite genre (lofi)
  - matches your favorite mood (chill)
  - energy closely matches
  - emotional tone closely matches

Focus Flow - Score: 0.67
Selection Reasoning:
  - matches your favorite genre (lofi)
  - energy closely matches
  - emotional tone closely matches

Spacewalk Thoughts - Score: 0.58
Selection Reasoning:
  - matches your favorite mood (chill)
  - emotional tone closely matches

Night Drive Loop - Score: 0.39
Selection Reasoning:
  - emotional tone closely matches
  - leans electronic, matching your preference
```

---

## Experiments

For the first experiment, I halved the genre weight, and doubled the energy weight:

**Comparison Table**

| Profile | #1 pick | Changes further down the list |
|:--------|:--------|:------------------------------|
| Intense Rock | unchanged (Storm Runner)	| Warehouse Pulse (energy 0.89) bumps out Broken Mirror at #5 |
| Chill Lofi | unchanged (Library Rain) |	Spacewalk Thoughts (low energy 0.28, close to target 0.3) jumps ahead of Focus Flow |
| Angry Metal	| unchanged (Neon Rebellion) | Night Drive Loop and Concrete Kingdom (hip hop, energy 0.80) push out Broken Mirror — a genre-mismatched song now cracks top 5 |
| Happy Pop |	unchanged (Sunrise City) | Rooftop Lights and Golden Hour Drive (both indie pop, high energy) leapfrog Gym Hero |
| Moody Synthwave |	unchanged (Night Drive Loop) | Velvet Ballad and Concrete Kingdom (both genre-mismatched) enter top 5, pushing out Glacier Hum |

  - **Key takeaways**:
  - The #1 recommendation never changes — for every profile the top pick already had a strong genre match and a close energy match, so it dominates either way.
  - The effect shows up in the #3–#5 slots: songs with the right genre but so-so energy match start losing ground to songs with the wrong genre but energy very close to target.
  - Most strikingly, "Concrete Kingdom" (hip hop, confident) shows up in both Angry Metal's and Moody Synthwave's top 5 under the new weights — it has no genre/mood match at all, but its energy (0.80) is close enough to both targets that the doubled energy weight alone earns it a spot. That's a case where the recommender starts surfacing genre-mismatched songs, which may or may not be desirable depending on what "good recommendation" means for this app.

For the second experiment, I removed mood entirely, and relied heavily on valence to score songs, giving valence 0.45 weight:

**Comparison Table**

| Profile | #1 pick | Changes further down the list |
|:--------|:--------|:------------------------------|
| Intense Rock | unchanged (Storm Runner) | Rest of the list reshuffles heavily — Gym Hero (mood match "intense") drops out of top 5 entirely since mood no longer counts; Broken Mirror and Night Drive Loop rise on valence proximity to the low target (0.2) |
| Chill Lofi | unchanged | Focus Flow jumps from #3 (0.70) to essentially tied for #1 (0.93) — its valence (0.59) is very close to target (0.5), and losing mood weight cost it nothing since it was already a mood mismatch that got dragged down |
| Angry Metal	| flips: Static Funeral overtakes Neon Rebellion | Both are genre="metal" matches, so this is decided purely by valence: Static Funeral's valence (0.15) is closer to the target (0.1) than Neon Rebellion's (0.22) — mood weight was previously masking this |
| Happy Pop | unchanged	| Gym Hero rockets from #2 (0.67) to #2 (0.91) — despite mood="intense" (a mismatch), its valence (0.77) is close to target (0.8) |
| Moody Synthwave	| unchanged |	Glacier Hum and Broken Mirror swap ranks based on valence closeness alone |


  - **Key takeaway**: this is a much bigger structural change than the genre/energy experiment — it actually flips a #1 recommendation (Angry Metal: Neon Rebellion → Static Funeral). Since genre score is often a tie (many songs share a genre with only one mood variant, or ties happen among same-genre songs), removing mood as a tiebreaker hands that decision entirely to valence proximity. The pattern across all 5 profiles: songs with the wrong mood but right valence now consistently outrank songs that used to win on mood alone — the recommender effectively stops caring about labeled mood tags and starts trusting the numeric emotional-tone value instead.

For the most part, my system prioritizes a users favorite genre and mood, and uses energy, valence, and acousticness as tie breakers and to give more variance to suggestions. It will always give the same list to the same user everytime they run the recommender, there is no variance in the weights or even something like a similar genres matcher to give more options to a user in its current state.

---

## Limitations and Risks

Limitations of my recommender:

- It only works on smaller datasets, given a larger sample it will recommend songs of only a single genre or mood, given that those are what it weighs heaviest.
- It does not understand lyrics, true vibe or language, it will easily recommend spanish or foreign origin songs over native language if the genre or mood is right.
- It might recommend 3-4 of the same genre song over a diverse list of genres, making it feel stale for many users.

---

## Reflection

[**Model Card**](model_card.md)

Building this recommender showed me that "prediction" here is really just weighted similarity scoring dressed up in a friendlier name - every song gets reduced to five numbers (genre match, mood match, energy distance, valence distance, acoustic fit), each multiplied by a fixed weight, and summed into a single 0-1 score. There's no learning happening; the model doesn't discover that genre matters more than acoustics, I decided that by setting genre to 0.30 and acoustic to 0.05. My weight experiments made this obvious: doubling the energy weight and halving genre didn't change any #1 pick, but it let genre-mismatched songs like "Concrete Kingdom" crack the top 5 purely on energy proximity, and dropping mood in favor of valence actually flipped a #1 recommendation (Angry Metal). The "prediction" is entirely a function of which knobs the designer chose to turn up - the data doesn't push back.

That's also where I think bias shows up most clearly. Because the system has no sense of lyrics, language, or cultural context, it will happily rank a foreign-language song above a native-language one as long as the genre and mood tags match - it's optimizing for labeled similarity, not for what the song actually communicates to a listener. The same blind spot shows up with dataset size: on a small catalog the recommender feels reasonably balanced, but I noted in the Limitations section that a larger dataset would let it collapse into recommending almost exclusively one dominant genre or mood, since those are the two heaviest-weighted features. In other words, the system doesn't just reflect bias in the data, it actively amplifies whatever genre or mood is already overrepresented, and a real-world version of this would need either more nuanced signals (lyrics, cultural context) or deliberate diversity constraints to keep it from flattening user taste into whatever the majority of the catalog looks like.
