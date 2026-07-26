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

### Addendum: project structure review

Reviewed before starting the Mermaid diagram / docs work. Flat `src/` (no subpackages) confirmed as the right call at this size (6 modules, no circular deps, matches the flat import style already in use and `pytest.ini`'s `pythonpath`). `scripts/` vs `src/` split confirmed sound (one-time CLI utilities vs. the actual application).

Two changes made:
- **Removed `data/songs.csv`** -- the old 20-song toy dataset, orphaned once `main.py` stopped using it. Nothing else referenced it (confirmed via grep before deleting).
- **`src/main.py` rewritten as a CLI demo** of the new pipeline (query -> semantic search -> Gemini explanation, printed to terminal) instead of being deleted -- it was broken (still imported the removed `UserProfile`/`recommend_songs`). Gives a second, lighter-weight way to demonstrate the system besides Streamlit, satisfying the "working script or UI" rubric bullet two ways instead of one. Verified it runs end-to-end.

Also noted: root-level `README.md`, `model_card.md`, and `ai_interactions.md` are the expected homes for Phase 8's docs -- git history shows the old versions of exactly these three were moved to `assets/old_music_recommender/old_*.md`, establishing where the new ones belong.

### Addendum: Deezer preview playback

Added after Phase 6: each recommendation card embeds a 30-second audio preview via Deezer's public search API (`src/deezer_previews.py`), no API key required. Looked up by artist+title at display time via `st.audio()`. Not cached to disk -- Deezer's preview URLs are signed links that expire in ~15 minutes, so only a short-TTL in-session cache is used (`st.cache_data(ttl=600)`), separate from the permanent on-disk caches used elsewhere in the pipeline.

## RAG Explanation


## Grading rubric for making a checklist:
3pts	Clear Identification of the Base Project and Its Original Scope
1	Student identifies the original project they are extending.
1	Student provides a short description of the original system's goal and capabilities.
1	Description is accurate and sets clear context for extensions.
3pts	Substantial New AI Feature Added (RAG, Agent, Specialization, or Reliability Mechanism)
1	Student adds at least one substantial AI feature such as RAG, a multi-step agent or planning workflow, specialized behavior (mini fine-tune or structured prompting), or a reliability harness (evaluation loop, guardrails, self-checking).
1	Feature is integrated into the working system (not an isolated demo).
1	Feature is functional and produces meaningful changes in system behavior.
3pts	System Architecture Diagram
1	Architecture diagram is submitted as a Mermaid source file (.mmd or embedded in a .md file); a PNG image alone is not sufficient.
1	Diagram clearly illustrates data flow (input → processing steps → output).
1	Diagram matches actual project implementation (not theoretical).
3pts	Functional End-to-End System Demonstration
1	Student provides a working script or UI that demonstrates full system workflow.
1	README includes example commands and sample outputs in code blocks showing the system running end-to-end.
1	System responds consistently to at least 2-3 example inputs.
3pts	Reliability, Evaluation, or Guardrail Component
1	System includes a reliability mechanism such as input validation, output guardrails, self-critique or multi-model agreement, or an evaluation script that tests sample inputs.
1	Mechanism is functional and meaningfully improves reliability.
1	Student provides examples in markdown format (showing input, behavior, and result) demonstrating how the guardrail or evaluator behaves.
3pts	Documentation: README and Setup Instructions
1	README clearly explains project goals and new features.
1	README contains step-by-step instructions to install, run, and test the system.
1	README includes sample input/output illustrating system behavior.
3pts	Reflection on AI Collaboration and System Design
1	Student explains how they used AI during development (prompting, debugging, design).
1	Student identifies at least one helpful and one flawed AI suggestion.
1	Student reflects on system limitations and future improvements.

## Rubric Checklist

Assessed against the implementation as it stands after Phase 7 (tests). Re-check after Phase 8.

### Clear Identification of the Base Project and Its Original Scope — 0/3
- [ ] Identify the original project being extended
- [ ] Short description of the original system's goal and capabilities
- [ ] Description is accurate and sets context for the extension

Not started. The original rule-based "VibeRender 3000" (genre/mood/energy/valence sliders, `score_song`) is fully documented in `assets/old_music_recommender/old_model_card.md`, but nothing in the current docs references it yet -- README.md is empty and there's no current model card. Needs pulling into Phase 8.

### Substantial New AI Feature Added (RAG) — 3/3 ✅
- [x] Adds a substantial AI feature -- RAG: local semantic-search retrieval + Gemini generation
- [x] Integrated into the working system, not an isolated demo (it's the entire flow in `src/app.py`, not a side script)
- [x] Functional and produces meaningful behavior change (verified live in browser; produces genuinely different, query-driven results vs. the old fixed-slider system)

Done.

### System Architecture Diagram — 3/3 ✅
- [x] Submitted as Mermaid source (`diagrams/architecture.mmd`; rendered PNG also saved to `assets/images/architecture.png` for easy viewing)
- [x] Clearly illustrates data flow (offline prep/embedding subgraph -> runtime query subgraph, including the guardrail/fallback branch)
- [x] Matches actual implementation -- real function names (`build_song_text`, `semantic_search`, `get_ai_recommendations`, `find_preview_url`), real file paths, real model name (`gemini-flash-lite-latest`)

Done. Rendered locally with `mermaid-cli` (`npx @mermaid-js/mermaid-cli`) to confirm it actually parses and displays correctly before calling it finished, not just that the syntax looked plausible.

### Functional End-to-End System Demonstration — 1/3
- [x] Working script *and* UI demonstrating the full workflow (`src/app.py` Streamlit UI, verified live in a real browser; `src/main.py` CLI demo of the same pipeline, verified end-to-end from the terminal)
- [ ] README includes example commands and sample outputs in code blocks
- [ ] System responds consistently to 2-3 example inputs, documented

The system itself works, two ways, and was verified against several distinct queries during development ("high energy dance songs," "sad acoustic songs for a rainy day," "hip hop songs good for a workout," "chill study music"). None of that is written down anywhere yet -- `README.md` is currently empty.

### Reliability, Evaluation, or Guardrail Component — 2/3
- [x] Includes a reliability mechanism: Gemini API-failure fallback (`gemini_dj.py`) + hallucinated-pick guardrail (drops any song ID in Gemini's response that isn't in the retrieved candidate set) + input validation in the UI (empty-query warning)
- [x] Mechanism is functional and meaningfully improves reliability, covered by `tests/test_gemini_dj.py` -- including the mixed valid/hallucinated-pick case, which proves a single bad ID gets dropped rather than triggering a full fallback
- [ ] Examples in markdown format showing input/behavior/result

The mechanism is built and tested; it just hasn't been written up as a markdown example anywhere yet.

### Documentation: README and Setup Instructions — 0/3
- [ ] README explains project goals and new features
- [ ] Step-by-step install/run/test instructions
- [ ] Sample input/output

Not started. `README.md` is currently empty.

### Reflection on AI Collaboration and System Design — 0/3
- [ ] Explains how AI was used during development
- [ ] Identifies at least one helpful and one flawed AI suggestion
- [ ] Reflects on limitations and future improvements

Not written yet, but there's concrete material from this session to draw on:
- **Flawed AI suggestions that had to be caught and corrected:** assumed `gemini-2.5-flash-lite` would still be available to a new API key (it wasn't -- caught by live testing, not by reasoning ahead of time); assumed the Gemini embedding free tier was rate-limited only per-minute (there's also an undocumented 1,000/day cap, which killed a background embedding job at 900/2,500 songs); an early Gemini explanation prompt included mismatched candidates with "this doesn't fit" reasoning instead of just excluding them.
- **Helpful AI contributions:** the RAG architecture itself, the checkpointed/resumable embedding cache design, genre-bucketed + popularity-capped dataset sampling (avoiding a single genre dominating the working subset), and the hallucination guardrail + its test.

---

**Overall: 9 of 21 rubric sub-items currently satisfied.** The hard engineering -- the AI feature itself, the guardrail mechanism, and now the architecture diagram -- is done. Everything still missing is writing: base-project framing, guardrail markdown examples, the README itself, and the AI-collaboration reflection.