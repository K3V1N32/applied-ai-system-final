import json
from google.genai import types

from ai_integration import client, GEMINI_EXPLANATION_MODEL
from recommender import Song

PICK_SCHEMA = {
    "type": "object",
    "properties": {
        "picks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "song_id": {"type": "integer"},
                    "reasoning": {"type": "string"},
                },
                "required": ["song_id", "reasoning"],
            },
        }
    },
    "required": ["picks"],
}


def _candidate_block(song: Song, score: float) -> str:
    good_for = ", ".join(song.good_for) if song.good_for else "no specific tags"
    return (
        f'id={song.id}, title="{song.title}", artist="{song.artist}", '
        f"genre={song.genre}, mood={song.mood}, energy={song.energy:.2f}, "
        f"danceability={song.danceability:.2f}, valence={song.valence:.2f}, "
        f"good_for=[{good_for}], similarity={score:.2f}"
    )


def _build_prompt(query: str, candidates: list[tuple[Song, float]], k: int) -> str:
    lines = [_candidate_block(song, score) for song, score in candidates]
    return (
        f'A user asked for: "{query}"\n\n'
        "Here are candidate songs, already pre-filtered for relevance:\n"
        + "\n".join(lines)
        + f"\n\nPick the best {k} of these (fewer if fewer than {k} genuinely fit) "
        "by their id, best first. Only include songs that actually fit the request -- "
        "do not include weak or mismatched picks just to fill the list. For each pick, "
        "explain in one sentence why it fits, citing specific attributes from above."
    )


def get_ai_recommendations(
    query: str,
    candidates: list[tuple[Song, float]],
    k: int = 5,
) -> list[dict]:
    """
    Sends pre-filtered candidates to Gemini for final selection + reasoning.
    Falls back to the raw similarity ranking (with a generic explanation) if
    the API call fails, so a demo never dead-ends on a network/quota error.
    """
    try:
        resp = client.models.generate_content(
            model=GEMINI_EXPLANATION_MODEL,
            contents=_build_prompt(query, candidates, k),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=PICK_SCHEMA,
            ),
        )
        picks = json.loads(resp.text)["picks"]

        song_by_id = {song.id: song for song, _ in candidates}
        results = [
            {"song": song_by_id[pick["song_id"]], "reasoning": pick["reasoning"], "source": "gemini"}
            for pick in picks
            if pick["song_id"] in song_by_id
        ]
        if results:
            return results[:k]
    except Exception as exc:
        print(f"Gemini explanation call failed, falling back to similarity ranking: {exc}")

    return [
        {
            "song": song,
            "reasoning": f"Closest semantic match to your query (similarity {score:.2f}).",
            "source": "fallback",
        }
        for song, score in candidates[:k]
    ]
