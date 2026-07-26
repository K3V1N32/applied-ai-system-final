# Applied AI System [AI110 FINAL]

## Initial ideas:
- Better recommendation algorithm - Improve on the algorithm and take in real data that actually reflects how song recommendation should work.
- Streamlit UI - Give the music recommender a new coat of paint for users.
- Bring in a large dataset of actual music to work with, and generate vector embeddings from the metadata of each song to use in tandem with AI.
- AI Suggestions using the search results from the vector embeddings and user input, hand the results to AI and have it give personalized recommendation, citing specific reasons for why a song fits the request. It'll be the users own AI DJ

#My API available models:
```bash
Model Name: models/gemini-2.5-flash
Model Name: models/gemini-2.5-pro
Model Name: models/gemini-2.0-flash
Model Name: models/gemini-2.0-flash-001
Model Name: models/gemini-2.0-flash-lite-001
Model Name: models/gemini-2.0-flash-lite
Model Name: models/gemini-2.5-flash-preview-tts
Model Name: models/gemini-2.5-pro-preview-tts
Model Name: models/gemma-4-26b-a4b-it
Model Name: models/gemma-4-31b-it
Model Name: models/gemini-flash-latest
Model Name: models/gemini-flash-lite-latest
Model Name: models/gemini-pro-latest
Model Name: models/gemini-2.5-flash-lite
Model Name: models/gemini-2.5-flash-image
Model Name: models/gemini-3-pro-preview
Model Name: models/gemini-3-flash-preview
Model Name: models/gemini-3.1-pro-preview
Model Name: models/gemini-3.1-pro-preview-customtools
Model Name: models/gemini-3.1-flash-lite-preview
Model Name: models/gemini-3.1-flash-lite
Model Name: models/gemini-3-pro-image-preview
Model Name: models/gemini-3-pro-image
Model Name: models/nano-banana-pro-preview
Model Name: models/gemini-3.1-flash-image-preview
Model Name: models/gemini-3.1-flash-image
Model Name: models/gemini-3.1-flash-lite-image
Model Name: models/gemini-3.5-flash
Model Name: models/gemini-3.5-flash-lite
Model Name: models/gemini-omni-flash-preview
Model Name: models/gemini-3.6-flash
Model Name: models/lyria-3-clip-preview
Model Name: models/lyria-3-pro-preview
Model Name: models/gemini-3.1-flash-tts-preview
Model Name: models/gemini-robotics-er-1.5-preview
Model Name: models/gemini-robotics-er-1.6-preview
Model Name: models/gemini-2.5-computer-use-preview-10-2025
Model Name: models/antigravity-preview-05-2026
Model Name: models/deep-research-max-preview-04-2026
Model Name: models/deep-research-preview-04-2026
Model Name: models/deep-research-pro-preview-12-2025
Model Name: models/gemini-embedding-001
Model Name: models/gemini-embedding-2-preview
Model Name: models/gemini-embedding-2
Model Name: models/aqa
Model Name: models/imagen-4.0-generate-001
Model Name: models/imagen-4.0-ultra-generate-001
Model Name: models/imagen-4.0-fast-generate-001
Model Name: models/veo-3.1-generate-preview
Model Name: models/veo-3.1-fast-generate-preview
Model Name: models/veo-3.1-lite-generate-preview
Model Name: models/gemini-2.5-flash-native-audio-latest
Model Name: models/gemini-2.5-flash-native-audio-preview-09-2025
Model Name: models/gemini-2.5-flash-native-audio-preview-12-2025
Model Name: models/gemini-3.1-flash-live-preview
Model Name: models/gemini-3.5-live-translate-preview
```

## AI Implementation Plan

### Architecture

Single free-text input ("What kind of music would you like me to recommend?") replaces the old genre/mood/energy/valence sliders entirely.

```
[Kaggle 900k-Spotify CSV, external download, gitignored]
        v
scripts/prepare_dataset.py  -->  data/songs_working.csv (gitignored, regenerated locally)
        v (one-time, cached to disk)
src/embeddings.py: build_song_text() + local sentence-transformers model  -->  data/embeddings_cache.npz (gitignored)
        v
User types query --> embed query locally --> cosine similarity vs cached vectors --> top ~15-20 candidates
        v
Gemini call: candidates + query --> picks top 5, explains reasoning per pick
        v
Streamlit UI displays picks + reasoning
```

**Embedding backend changed mid-build:** Gemini's `embed_content` free tier turned out to have a 1,000-request/day cap (not just per-minute), which we hit at 900/2500 songs with only 32 of 88 genres covered. Switched to a local `sentence-transformers` model (`all-MiniLM-L6-v2`) for both corpus and query embedding instead -- no quota, embeds all 2,500 songs in under a minute, and removes an external dependency from the runtime search path entirely. Gemini is now used only for the explanation layer (`gemini_dj.py`), which is a separate quota and unaffected.

### Decisions locked in

- **Sample size:** ~2,500 songs, stratified across genre/emotion (not the full 500k+ rows — too slow/costly to embed and unnecessary for a demo).
- **Raw dataset and derived working subset are both gitignored.** Lyrics are copyrighted; nothing lyric-derived gets committed to the repo. Only the deterministic prep script is committed, so anyone cloning regenerates the working subset from their own downloaded copy.
- **Composite embedding text**, not raw lyrics alone: genre + emotion + a few adjectives derived from energy/danceability/valence + a short lyric snippet. Pure lyric embeddings drift toward theme/narrative rather than the audio-quality language users will type (e.g. "high energy").
- **Brute-force numpy cosine similarity** over ~2,500 vectors — no FAISS/Chroma/vector DB needed at this scale.
- **Old `UserProfile`/`score_song`/slider-based flow is fully replaced**, not kept alongside. `tests/test_recommender.py` gets rewritten against the new API rather than left as-is.
- **Gemini call has a fallback path**: if the API call fails or is unavailable, fall back to showing the raw similarity-ranked candidates so a demo never dead-ends on a network/API error.
- **Embeddings run locally** via `sentence-transformers` (`all-MiniLM-L6-v2`), not the Gemini embedding API — see note above.
- **Models:** `gemini-flash-lite-latest` for the explanation layer — a rolling alias Google keeps pointed at their current flash-lite model, chosen after `gemini-2.5-flash-lite` (our original pick) turned out to be no longer available to new API keys by the time we tested it live.

### Phases

1. **Setup (10 min)** — `GEMINI_API_KEY` in a gitignored `.env`; confirm which Gemini embedding + chat models the key has access to.
2. **Dataset acquisition & sampling (45 min)** — download raw CSV; write `scripts/prepare_dataset.py` (pandas load → column cleanup/rename → stratified sample with a fixed seed → write `data/songs_working.csv`); spot-check output for nulls/bad rows.
3. **Schema + composite text (20 min)** — extend `Song` in `src/recommender.py` with `emotion`/lyrics fields as needed; write `build_song_text(song)`.
4. **Embedding pipeline + cache (60 min)** — `src/embeddings.py`: `embed_texts()`, cache save/load (skip re-embedding if cache already matches the dataset), `semantic_search(query, k)` returning ranked `(song, score)`.
5. **Gemini explanation layer (45 min)** — send top candidates + query to Gemini, prompt for top-5 picks with per-song reasoning citing specific attributes; handle the fallback path from above.
6. **Streamlit UI (45 min)** — `src/app.py`: single input box, spinner, results with reasoning; cache the loaded dataset/embeddings with `st.cache_data`/`st.cache_resource` so Streamlit's rerun-on-interaction behavior doesn't recompute them.
7. **Rewrite tests (30 min)** — cover `build_song_text`, cosine-similarity ranking (small fixture, fake vectors, no network calls), cache save/load, and a stubbed/mocked Gemini call so tests stay deterministic and offline.
8. **Docs (25 min)** — new model card (architecture, data source/citation, limitations: sampling not full dataset, lyric-bias risk, Gemini cost/latency); README setup steps (download dataset, set API key, run prep script, run Streamlit).
9. **Buffer / end-to-end run-through (30 min)** — run the full pipeline with a handful of real queries before calling it done.

Total: ~5.2 hours, leaving slack inside the 5-6 hour budget. If time gets tight, cut in this order: docs polish (8) → test breadth (7) → Gemini prompt refinement (5) → UI polish (6). Don't cut the embedding cache (4) or the fallback path (5) — those are what keep a live demo from breaking.

### Addendum: Deezer preview playback

Added after Phase 6: each recommendation card embeds a 30-second audio preview via Deezer's public search API (`src/deezer_previews.py`), no API key required. Looked up by artist+title at display time via `st.audio()`. Not cached to disk -- Deezer's preview URLs are signed links that expire in ~15 minutes, so only a short-TTL in-session cache is used (`st.cache_data(ttl=600)`), separate from the permanent on-disk caches used elsewhere in the pipeline.