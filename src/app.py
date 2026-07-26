import logging
import os
import streamlit as st

# Streamlit's dev-server file watcher walks every imported module to decide
# what to watch, which trips transformers' lazy import of optional
# torchvision-dependent submodules (unused by this project). Streamlit
# already catches the resulting ModuleNotFoundError -- it's harmless -- but
# logs the full traceback as a warning, which looks like a real crash.
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)

from recommender import load_songs
from embeddings import get_or_build_embeddings, semantic_search
from gemini_dj import get_ai_recommendations
from deezer_previews import find_track_media

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_PATH = os.path.join(APP_DIR, "..", "data", "songs_working.csv")
DEFAULT_COVER_PATH = os.path.join(APP_DIR, "..", "assets", "images", "default_cover.png")

CANDIDATE_POOL_SIZE = 20
COVER_ART_WIDTH = 120

st.set_page_config(page_title="VectorVibe", page_icon="🎧")


@st.cache_resource
def load_data():
    songs = load_songs(SONGS_PATH)
    song_ids, vectors = get_or_build_embeddings(songs)
    return songs, song_ids, vectors


@st.cache_data(ttl=600, show_spinner=False)
def cached_track_media(artist: str, title: str):
    # Short TTL is intentional: Deezer's preview/cover URLs are signed links
    # that expire in ~15 minutes, so this cache must not outlive them.
    return find_track_media(artist, title)


songs, song_ids, vectors = load_data()

st.title("VectorVibe")
st.caption("Your AI DJ - describe what you want to hear, in your own words.")

with st.form("query_form"):
    query = st.text_input(
        "What kind of music would you like me to recommend?",
        placeholder="e.g. high energy dance songs, or sad acoustic songs for a rainy day",
    )
    num_recommendations = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)
    submitted = st.form_submit_button("Get Recommendations")

if submitted and query.strip():
    with st.spinner("Searching and asking your AI DJ..."):
        candidates = semantic_search(query, songs, song_ids, vectors, k=CANDIDATE_POOL_SIZE)
        recommendations = get_ai_recommendations(query, candidates, k=num_recommendations)

    if not recommendations:
        st.warning("No recommendations found for that query -- try describing it differently.")
    else:
        if recommendations[0]["source"] == "fallback":
            st.info("Gemini's explanations were unavailable right now, so these are the closest semantic matches instead.")

        for rec in recommendations:
            song = rec["song"]
            source_label = (
                "🤖 Picked and explained by your AI DJ (Gemini)"
                if rec["source"] == "gemini"
                else "📊 Closest semantic match (AI DJ unavailable)"
            )
            media = cached_track_media(song.artist, song.title)

            with st.container(border=True):
                col_cover, col_info = st.columns([1, 4])
                with col_cover:
                    st.image(media.cover_url or DEFAULT_COVER_PATH, width=COVER_ART_WIDTH)
                with col_info:
                    st.subheader(f"{song.title} - {song.artist}")
                    st.write(rec["reasoning"])
                    st.caption(f"Genre: {song.genre} · Mood: {song.mood} · Popularity: {song.popularity}")
                    st.caption(source_label)

                if media.preview_url:
                    st.audio(media.preview_url)
                else:
                    st.caption("No preview available for this track.")
elif submitted:
    st.warning("Type something first -- what kind of music are you in the mood for?")
