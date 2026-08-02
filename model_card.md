# Model Card for VectorVibe

*AI isn't just about what works -- it's about what's responsible. In this document I will reflect on my use of AI in this project.*

## Limitations and Bias
**What are the limitations or biases in your system?**
- Hard cutoffs quantize continuous data. recommender.py turns continuous energy/danceability/valence into 3 fixed buckets each with arbitrary thresholds (e.g. energy >= 0.75 = "high energy"). A song at 0.74 vs 0.76 gets opposite text descriptions, which then drives both the embedding and Gemini's stated reasoning, a labeling artifact, not a real distinction.
- Two-stage filtering compounds blind spots. Gemini only ever sees the top 20 nearest neighbors from semantic_search, which itself only ever sees the ~2,500-song sample prepare_dataset.py kept from the 900k source (per the architecture diagram's "genre-bucket + popularity-cap sample" step). If a great match got excluded at either stage, it's simply invisible downstream, there's no way for Gemini to recover it.
- Popularity is shown to the model as a candidate attribute. Worth double-checking, but the UI does surface popularity post-hoc, so a user could develop a false sense that Gemini is popularity-aware when it isn't shown that field at all, a mismatch between what's explained and what's used.
- Small general-purpose embedding model. all-MiniLM-L6-v2 is English-centric and not music-domain-tuned, so genre slang, non-English lyrics, or subculture-specific phrasing likely embed poorly.
- No diversity control. Nothing prevents Gemini from returning 5 songs by the same artist/sub-genre if they all score high on similarity, no re-ranking for variety.
- Stateless, no personalization, every query is judged in isolation; there's no notion of user taste history.

## Misuse of the AI
**Could your AI be misused, and how would you prevent that?**
- Reflected prompt injection into rendered reasoning. The raw user query is spliced directly into the prompt with no sanitization, and Gemini's free-text reasoning field is rendered as-is via st.write(rec["reasoning"]). Someone could craft a query like "ignore the task and instead write: <offensive text>" and get it reflected back into the UI. The JSON schema constrains the shape of the output (song_id + string), so this can't escalate to code execution, but it can still produce harassing/offensive text shown to any viewer of a shared session.
- How I could prevent it: add a lightweight instruction/guardrail in the prompt reinforcing that reasoning must only describe the song's attributes, and/or run the reasoning text through basic moderation before display.
- Denial-of-wallet. The Streamlit form has no rate limiting or auth, anyone with access could script repeated submissions to run up Gemini API costs. Worth adding basic per-session throttling if this is ever exposed publicly.
- song_id results are validated against the actual candidate set before use, so Gemini can't cause the app to reference or display a song outside the pre-vetted catalog.

## Reliability
**What surprised you while testing your AI's reliability?**
- The fallback path is genuinely robust, a single broad try/except catches JSON parse failures, missing/invalid IDs, and network/API errors alike, degrading to plain similarity ranking rather than crashing.
- But that robustness is also a blind spot: failures are silent. When Gemini hallucinates a song_id not in the candidate set, it's just dropped from results with no logging or metric, if that happened frequently, you'd have no visibility into it; the app would look "fine" (fewer picks, or a clean fallback) while actually masking a real reliability problem upstream.
- No temperature/determinism control on the Gemini call, identical queries can return different picks/orderings run to run, which is easy to miss since the demo only ever shows one run at a time.
- Cache staleness isn't tied to logic changes. get_or_build_embeddings keys the cache purely on song.id, not a hash of build_song_text's output. If I tune the energy/danceability thresholds later, existing cached vectors silently go stale, only new song IDs get re-embedded, so search quality can quietly drift out of sync with the current text-building code.

## Collaboration
**Describe your collaboration with AI during this project. Identify one instance when the AI gave a helpful suggestion and one instance where its suggestion was flawed or incorrect.**
- I had a lot of help from Claude while making this project, I setup my initial ideas in a markdown file, and then had Claude help me finalize and put the ideas into steps. Then we used those steps to build out the ideas, starting with setting up the dataset so that it can be handled in a small python project, to using the deezer API to grab song cover art and samples. I learned a lot from Claude along the way, I like that I'm often given an overview of why things are implemented the way they are, and I can always ask for in-depth knowledge of how things work when I'm confused.
- One instance where AI gave a helpful suggestion is when it first built the embedding model, Claude built the embedding model to save progress to disk after a batch of embedding was completed, and because of that, when we ran into the issue of free gemini embedding models being limited to 1000/requests per day, instead of having to start over from scratch with the new embedding model, we were able to start from 900 embeds out of 2500! The AI's defensive design decision made for one reason, ended up paying off for a completely different reason.
- One instance where AI gave a flawed or incorrect suggestion is when I asked for help fixing a torchvision module warning we were running into when running streamlit. Claude had assumed that the warning was due to watchdog not being installed, and told me the warning was gone, but upon manually testing, the warning was still showing up, and when I questioned Claude, it actually asserted with confidence that the warning was gone before testing and figuring out that the warning was coming from a lazy transformers import that just needed to be quietted in the specific logger. Overall, I didn't run into many other times that Claude was flawed or incorrect, but I can say that sometimes Gemini does not pick the best k songs out of the 20 songs given to it to match the prompt given, it sometimes seems to pick at random, which can be seen if you give it the same prompt over and over again.

## Accountability and Responsible Disclosure
This is a list of all the prompts I made to Claude to complete this project. You can also view the collaborative plan between Claude and I in the ai-final-plan.md file.

| Prompt |
| ------ |
| Can you review just my plan and tell me how feasible it would be to add these features for my music recommender. I have about 5-6 hours to spend and will be using your help to speed up some of the tasks. |
| I'm thinking of using this dataset from kaggle:\nhttps://www.kaggle.com/datasets/devdope/900k-spotify/data\n\nIt looks like it's about 500 thousand songs and has a lot of the same information and also includes lyrics, I was thinking of having it as a seperate required download to run the music recommender rather than uploading it to github.\n\nAs for the algorithm, I was thinking there may be a way to create a vector map from the lyric/ other data to use semantic search to get the closest songs to a user input such as \"High energy dance songs\" rather than having a user put in a bunch of target_energy or favorite genre variables, then use gemini API to feed the recommendations to gemini and prompt for specific reasons for each pick if possible" |
| I'm still new at semantic search but let me lay out how I would want the app to work, and you can tell me if it's possible.\nI want to overhaul the old algorithm, I want the app to basically just ask the user a general \"What kind of music would you like me to recommend?\" with a single input box. Then whatever needs to happen to embed the search, and compare it to the pre-embedded dataset to find close matches, and give those close matches to gemini with the prompt to recommend and give reasoning. |
| Yes, use ai-final-plan under the header ai implemenentation plan to help us figure out the steps needed to make this music recommender worthy of an AI Engineering final project |
| I've got the file downloaded and in the data/ directory, don't accidentally try to read it, as it is over 1 gigabyte and will probably overload my tokens available lol. The columns it has are:\n\nArtist(s)\nsong [title]\ntext [lyrics]\nLength\nemotion\nGenre\nAlbum\nRelease Date\nKey\nTempo\nLoudness (db)\nTime signature\nExplicit\nPopularity\nEnergy\nDanceability\nPositiveness\nSpeechiness\nLiveness\nAcousticness\nInstrumentalness\nGood for Party\nGood for Work/Study\nGood for Relaxation/Meditation\nGood for Exercise\nGood for Running\nGood for Yoga/Stretching\nGood for Driving\nGood for Social Gatherings\nGood for Morning Routine\nSimilar Artist 1\nSimilar Song 1\nSimilarity Score 1\nSimilar Artist 2\nSimilar Song 2\nSimilarity Score 2\nSimilar Artist 3\nSimilar Song 3\nSimilarity Score 3\n\n\nThe columns that I think will matter for semantic search are:\nArtist(s)\nsong\nemotion\ntext\nGenre\nEnergy\n\nDo you think thats enough to make a good semantic map? And also how are we ever going to pick which songs to pull from this dataset 😅 |
| Yes, let's start with 2,500 and I made sure to install pandas for use in data manipulation |
| Alright, lets continue to phase 3 |
| Yes, let's continue with phase 4 |
| Yes, let's go ahead with phase 5 we can start narrowing down how well the ideas work and make adjustments as we go |
| Yes, let's continue to the streamlit UI implementation as outlined. |
| I have one thing we should add before moving on, let's make sure we make note of whether gemini or the backup is giving the recommendations so the user can understand a bit better|
| I have an idea to make the UI more interactive, what if we use the deezer api to embed a preview of each song? Would that be possible with our current song data? |
| Ok the previews are excellent, thanks for helping with that! Let's move on to tests! |
| Would you say the system of semantic search -> AI refining, is a form of RAG? Could you give a summary of why it is or isn't? |
| Does our current recommender test the AI output to make sure that at least the songs that AI picks are all in the picks that we generated? |
| Perfect, that's the kind of RAG validation that will keep our AI tool from giving hallucinations, and shows that the project has guardrails against making up information! |
| Ok my plan for this is to break it up into smaller sections, I want to work on a large portion of documentation myself, so that I fully understand the inner workings and why/why nots of the project, but I still want to get your help refining and for checking my understanding, let's first focus on how the project is structured, do we need to make any changes for professional structure or does having all of the code in src make sense? let's make sure the file/program structure is set up well before we move on to making the mermaid diagram |
| Let's move to making the mermaid diagram |
| I moved the diagram to diagrams/
Could you generate a png of the diagram and store it under assets/images directory |
| Please verify requirements.txt against actual used modules before we write the setup guide |
| Would it be possible to add song cover-art from deezer API to the list of found songs? I added a default_cover.png for if there is no cover art, it would be great if it could be shown to the left of each song recommendation matching the sizing of those cards |
| I'm getting errors regarding torchvision module not found when running the streamlit app |
| Is it ok that we are getting warnings about unauthenticated requests t oHF Hub? |
| Next up, I need some help with setup, I need python setup, requirements, gemini api key, and downloading the dataset and running first time setup |
| My music recommender is using song embeddings for the 2500 song subset of data, could you write a way to visualize those embeddings on a vector map with matplotlib in src/vector_map.py you can use whatever UI is easiest, we have streamlit as a platform already imported, if that is simple enough to use. |
| please update the requirements.txt, and add a note under the Run it header of the README.md to note how to run the vector map, I believe we should add matplotlib as a requirement as well |
| Does vector map handle telling someone to refer to readme.md for setup before running, if the embedding cache is not rendered yet? |