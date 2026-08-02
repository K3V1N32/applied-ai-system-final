"""
Standalone Streamlit page that visualizes the song embedding space.

Run with: streamlit run src/vector_map.py

Embeddings live in 384 dimensions (see embeddings.py), so we project them
down to 2D with PCA or t-SNE and render the result as a matplotlib scatter
plot -- songs whose embedded text (genre/mood/energy/lyrics) reads similarly
end up close together on the map.
"""
import logging
import os
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.lines import Line2D
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# See app.py for why this warning is silenced.
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)

from recommender import load_songs
from embeddings import get_or_build_embeddings

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_PATH = os.path.join(APP_DIR, "..", "data", "songs_working.csv")

NUM_FEATURED_MOODS = 3
RANDOM_SEED = 7

# Chart chrome tokens (see .claude's dataviz skill palette). Only the first
# three categorical slots are used -- that's the largest set that stays
# pairwise colorblind-safe on a scatter plot, where any two points can end
# up as neighbors. Anything past that folds into a neutral "Other" group
# instead of adding a 4th hue.
LIGHT_CHROME = {
    "surface": "#fcfcfb", "primary_ink": "#0b0b0b",
    "secondary_ink": "#52514e", "muted": "#898781", "axis": "#c3c2b7",
}
DARK_CHROME = {
    "surface": "#1a1a19", "primary_ink": "#ffffff",
    "secondary_ink": "#c3c2b7", "muted": "#898781", "axis": "#383835",
}
CATEGORY_SLOTS = [
    {"light": "#2a78d6", "dark": "#3987e5", "marker": "o"},  # blue circle
    {"light": "#eb6834", "dark": "#d95926", "marker": "s"},  # orange square
    {"light": "#1baf7a", "dark": "#199e70", "marker": "^"},  # aqua triangle
]

st.set_page_config(page_title="VectorVibe - Embedding Map", page_icon="🗺️")


def _detect_theme() -> str:
    try:
        theme_type = st.context.theme.get("type")
    except Exception:
        theme_type = None
    if theme_type in ("light", "dark"):
        return theme_type
    return "dark" if st.get_option("theme.base") == "dark" else "light"


@st.cache_resource
def load_data():
    songs = load_songs(SONGS_PATH)
    song_ids, vectors = get_or_build_embeddings(songs)
    return songs, song_ids, vectors


@st.cache_data(show_spinner=False)
def project_to_2d(vectors: np.ndarray, method: str) -> np.ndarray:
    if method == "PCA":
        reducer = PCA(n_components=2, random_state=RANDOM_SEED)
    else:
        perplexity = min(30, max(5, (len(vectors) - 1) // 3))
        reducer = TSNE(n_components=2, random_state=RANDOM_SEED, perplexity=perplexity, init="pca")
    return reducer.fit_transform(vectors)


if not os.path.exists(SONGS_PATH):
    st.error(
        "Song data not found. Follow the setup steps in README.md -- download the "
        "dataset and run `python3 scripts/prepare_dataset.py` -- before running this app."
    )
    st.stop()

songs, song_ids, vectors = load_data()
id_to_song = {song.id: song for song in songs}

st.title("VectorVibe -- Embedding Map")
st.caption(
    "A 2D projection of each song's semantic embedding -- songs described in "
    "similar terms (genre, mood, energy, lyrics) land close together."
)

col_method, col_color = st.columns(2)
with col_method:
    method_choice = st.radio("Projection", ["PCA (fast)", "t-SNE (slower, tighter clusters)"], horizontal=True)
with col_color:
    color_mode = st.radio("Color by", ["Mood", "Genre"], horizontal=True)

method = "PCA" if method_choice.startswith("PCA") else "TSNE"
if method == "TSNE":
    st.caption("t-SNE recomputes the layout from scratch and can take a few seconds for 2,500 songs.")

with st.spinner("Projecting embeddings..."):
    coords = project_to_2d(vectors, method)

def _group_by_genre(song, picked_genre):
    return 0 if song.primary_genre == picked_genre else None


def _group_by_mood(song, mood_to_slot):
    return mood_to_slot.get(song.mood)


if color_mode == "Genre":
    genre_counts = Counter(song.primary_genre for song in songs)
    genre_options = [genre for genre, _ in genre_counts.most_common()]
    picked_genre = st.selectbox("Genre to highlight", genre_options)
    group_labels = {0: picked_genre}
    group_of = lambda song: _group_by_genre(song, picked_genre)
else:
    mood_counts = Counter(song.mood for song in songs)
    top_moods = [mood for mood, _ in mood_counts.most_common(NUM_FEATURED_MOODS)]
    mood_to_slot = {mood: i for i, mood in enumerate(top_moods)}
    group_labels = {i: mood for i, mood in enumerate(top_moods)}
    st.caption(
        f"Showing the {NUM_FEATURED_MOODS} most common moods distinctly "
        f"({', '.join(top_moods)}); everything else is grouped as \"Other\" "
        "so the colors stay distinguishable."
    )
    group_of = lambda song: _group_by_mood(song, mood_to_slot)

song_labels = sorted(f"{song.title} -- {song.artist}" for song in songs)
label_to_id = {f"{song.title} -- {song.artist}": song.id for song in songs}
highlight_label = st.selectbox("Highlight a song (optional)", ["None"] + song_labels)
highlight_id = label_to_id.get(highlight_label)

theme = _detect_theme()
chrome = DARK_CHROME if theme == "dark" else LIGHT_CHROME
id_to_pos = {song_id: i for i, song_id in enumerate(song_ids)}
groups = [group_of(id_to_song[song_id]) if song_id in id_to_song else None for song_id in song_ids]
groups = np.array(groups, dtype=object)

fig, ax = plt.subplots(figsize=(9, 7), dpi=150)
fig.patch.set_facecolor(chrome["surface"])
ax.set_facecolor(chrome["surface"])

other_mask = groups == None  # noqa: E711 -- vectorized comparison, not an identity check
ax.scatter(
    coords[other_mask, 0], coords[other_mask, 1],
    s=10, alpha=0.35, color=chrome["muted"], linewidths=0, label="Other", zorder=1,
)

handles, labels = [], []
for slot_idx in sorted(group_labels):
    mask = groups == slot_idx
    slot = CATEGORY_SLOTS[slot_idx]
    scatter = ax.scatter(
        coords[mask, 0], coords[mask, 1],
        s=26, alpha=0.85, color=slot[theme], marker=slot["marker"],
        linewidths=0.6, edgecolors=chrome["surface"], label=group_labels[slot_idx], zorder=2,
    )
    handles.append(scatter)
    labels.append(group_labels[slot_idx])

if highlight_id is not None and highlight_id in id_to_pos:
    hx, hy = coords[id_to_pos[highlight_id]]
    ax.scatter(
        [hx], [hy], s=170, facecolors="none",
        edgecolors=chrome["primary_ink"], linewidths=1.8, zorder=3,
    )
    ax.annotate(
        id_to_song[highlight_id].title, (hx, hy), xytext=(8, 8),
        textcoords="offset points", fontsize=9, color=chrome["primary_ink"],
    )

ax.set_xlabel("Component 1", color=chrome["secondary_ink"], fontsize=9)
ax.set_ylabel("Component 2", color=chrome["secondary_ink"], fontsize=9)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_color(chrome["axis"])

other_handle = Line2D(
    [0], [0], marker="o", color="none",
    markerfacecolor=chrome["muted"], markeredgecolor="none", markersize=6,
)
ax.legend(
    [other_handle] + handles, ["Other"] + labels,
    loc="upper right", frameon=False, fontsize=8, labelcolor=chrome["secondary_ink"],
)

st.pyplot(fig)
st.caption("This is a static plot -- points aren't clickable. Use the song search above to locate a specific track.")

def _group_label(song) -> str:
    slot_idx = group_of(song)
    return group_labels[slot_idx] if slot_idx is not None else "Other"


with st.expander("View as table"):
    rows = [
        {
            "Title": id_to_song[song_id].title,
            "Artist": id_to_song[song_id].artist,
            "Genre": id_to_song[song_id].primary_genre,
            "Mood": id_to_song[song_id].mood,
            "Group": _group_label(id_to_song[song_id]),
        }
        for song_id in song_ids if song_id in id_to_song
    ]
    st.dataframe(rows, width="stretch", hide_index=True)
