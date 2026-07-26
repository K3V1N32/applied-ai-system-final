# \<VectorVibe\> - *Your AI DJ!*
VecotrVibe is a full rework/refactor of the CodePath Music Recommender project from module 3 of AI110 Foundation of AI Engineering

The original version of this project was CLI interface only. Its goal was to weigh song data against userProfiles to give recommendation through scoring and ranking rules

Represents songs, and userProfiles as data
Designed scoring and ranking rules that turns that data into recommendations
Give rankings and reasonings for each ranking.

[View my original submission on github!](https://github.com/K3V1N32/ai110-module3show-musicrecommendersimulation-starter)


## Reproduceable reproduction execution evidence
### Here are 3 seperate CLI executions of VectorVibe:
Input: Songs for going to the beach
```Bash
Welcome to the VectorVibe command-line demo!
What kind of music would you like me to recommend? Songs for going to the beach
Loaded 2500 songs.
Searching and asking your AI DJ...
Embedding cache is up to date (2500 songs).
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|█████████████████████████████████| 103/103 [00:00<00:00, 10277.47it/s]

Recommendations for: "Songs for going to the beach"

SURFIN' SAFARI - Ramones  [AI DJ (Gemini)]
  This song fits a beach theme perfectly with its title 'SURFIN' SAFARI' and high valence of 0.90 conveying pure joy.
  Genre: pop punk,punk,punk rock | Mood: joy | Popularity: 75

Plastic Beach - Gorillaz  [AI DJ (Gemini)]
  With the title 'Plastic Beach', it is directly relevant to a beach setting while offering a high danceability of 0.69.
  Genre: trip-hop,rock,electronic | Mood: anger | Popularity: 78

NCT 127 -  Road Trip English Translation - NewJeans  [AI DJ (Gemini)]
  This upbeat track is ideal for a beach trip, featuring a high danceability of 0.80 and great energy of 0.77.
  Genre: k-pop | Mood: joy | Popularity: 80

Stand Tall - Dirty Heads  [AI DJ (Gemini)]
  This track brings a fun beachside vibe with high danceability at 0.71 and a joyful valence of 0.82, plus good for parties.
  Genre: alternative,pop rock,new wave | Mood: sadness | Popularity: 64

Maryland - Elephanz  [AI DJ (Gemini)]
  The cheerful electro-pop vibe matches a sunny beach day with a high valence of 0.83 and high danceability of 0.73.
  Genre: electro,pop | Mood: joy | Popularity: 54
```

Input: Lofi Chill songs for when its thunderstorming
```Bash
Welcome to the VectorVibe command-line demo!
What kind of music would you like me to recommend? Lofi Chill songs for when its thunderstorming
Loaded 2500 songs.
Searching and asking your AI DJ...
Embedding cache is up to date (2500 songs).
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|█████████████████████████████████| 103/103 [00:00<00:00, 16225.24it/s]

Recommendations for: "Lofi Chill songs for when its thunderstorming"

Winter Winds - Øneheart  [AI DJ (Gemini)]
  Winter Winds by Øneheart is a great chillout and ambient track with very low energy (0.18) and a mood of anger that matches stormy weather, making it ideal for relaxation.
  Genre: chillout,ambient,house | Mood: anger | Popularity: 71

Illusions - Zonyo  [AI DJ (Gemini)]
  Illusions by Zonyo features a lo-fi and chillwave genre combination with low energy and good suitability for relaxation, fitting a cozy thunderstorm vibe.
  Genre: chillwave,hip hop,lo-fi | Mood: joy | Popularity: 51

Spooky Song - Cmd q  [AI DJ (Gemini)]
  Spooky Song by Cmd q has a lo-fi chillwave genre and a mood of fear with low energy (0.27), echoing the dramatic feel of a thunderstorm.
  Genre: chillwave,hip hop,lo-fi | Mood: fear | Popularity: 51

Bad Attitudes - Øneheart  [AI DJ (Gemini)]
  Bad Attitudes by Øneheart shares the chillout and ambient style with very low energy (0.18) and works well for meditation during a heavy storm.
  Genre: chillout,ambient,house | Mood: anger | Popularity: 71

100000 Fireflies - The Magnetic Fields  [AI DJ (Gemini)]
  100000 Fireflies by The Magnetic Fields belongs to the lo-fi genre and features low energy (0.26), providing a calm background appropriate for studying while it storms.
  Genre: lo-fi,indie pop,synthpop | Mood: anger | Popularity: 58
```

Input: Country songs for a square dance
```Bash
Welcome to the VectorVibe command-line demo!
What kind of music would you like me to recommend? Country songs for a square dance
Loaded 2500 songs.
Searching and asking your AI DJ...
Embedding cache is up to date (2500 songs).
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|█████████████████████████████████| 103/103 [00:00<00:00, 27070.20it/s]

Recommendations for: "Country songs for a square dance"

You Proof - Morgan Wallen  [AI DJ (Gemini)]
  This country song features high energy of 0.84 and strong danceability of 0.73, making it suitable for a square dance.
  Genre: country | Mood: sadness | Popularity: 84

Thinkin Bout You - Morgan Wallen  [AI DJ (Gemini)]
  With a country genre, high energy of 0.76, and good danceability of 0.66, this track works well for party dancing.
  Genre: country | Mood: sadness | Popularity: 85

Reasons The Writers Cut - Luke Combs  [AI DJ (Gemini)]
  This country song is tagged as good for exercise and parties, supported by a high energy of 0.80.
  Genre: country | Mood: sadness | Popularity: 84

Drink U Back - Morgan Wallen  [AI DJ (Gemini)]
  As a country track with a solid energy of 0.70, it fits the genre requirement for a dancing environment.
  Genre: country | Mood: sadness | Popularity: 87

Pimplikeness - Morgan Wallen  [AI DJ (Gemini)]
  Featuring a country genre alongside high energy at 0.84 and danceability of 0.73, it provides a lively rhythm.
  Genre: country | Mood: anger | Popularity: 84
```