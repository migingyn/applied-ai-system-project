"""
RAG-based music recommendation pipeline (Anthropic Claude backend).

Flow:
  1. Parse — Claude interprets the user's natural language query into structured preferences
  2. Retrieve — rule-based scoring selects top candidate songs from the catalog
  3. Generate — Claude writes a personalized response grounded in the retrieved songs
"""
import json
import logging
import os

import anthropic

from src.recommender import recommend_songs

logger = logging.getLogger(__name__)

_PARSE_SYSTEM = """\
You are a music preference parser. Extract structured preferences from a user's natural language music request.

Return ONLY a valid JSON object with exactly these three fields:
  "genre"  — best matching genre from: pop, rock, lofi, edm, jazz, folk, ambient, hip-hop, r&b, \
classical, synthwave, indie pop, country, blues, alternative rock
  "mood"   — best matching mood from: happy, chill, intense, peaceful, relaxed, focused, energetic, \
sad, moody, melancholy, romantic, confident
  "energy" — float 0.0 (very calm) to 1.0 (very energetic) that reflects the request's energy level

No explanation, no markdown, no extra keys — only the JSON object.\
"""

_RECOMMEND_SYSTEM = """\
You are a warm and knowledgeable music recommender. Given the user's request and a list of songs \
retrieved from the catalog, write a friendly 2-3 sentence response explaining why these picks suit them.
Mention specific song titles and connect them to what the user asked for. Keep it conversational and concise.\
"""

_FALLBACK_PREFS = {"genre": "pop", "mood": "happy", "energy": 0.5}

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def _make_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Set it or create a .env file (see .env.example)."
        )
    return anthropic.Anthropic(api_key=api_key)


def get_ai_recommendations(
    user_query: str,
    songs: list,
    k: int = 5,
    model: str = _DEFAULT_MODEL,
) -> tuple[list, str]:
    """
    RAG pipeline: returns (recommendations, ai_response_text).

    recommendations — list of (song_dict, score, explanation) tuples
    ai_response_text — Claude's natural language summary for the user
    """
    if not user_query or not user_query.strip():
        raise ValueError("user_query must be a non-empty string")
    if not songs:
        raise ValueError("songs list must not be empty")

    client = _make_client()

    # ── Step 1: Parse ────────────────────────────────────────────────────────
    logger.info("Parsing query (%d chars): %s", len(user_query), user_query[:80])
    user_prefs = _parse_preferences(client, user_query, model)

    # ── Step 2: Retrieve ─────────────────────────────────────────────────────
    logger.info("Retrieving top %d songs for prefs: %s", k, user_prefs)
    recommendations = recommend_songs(user_prefs, songs, k=k)
    logger.debug("Retrieved %d songs", len(recommendations))

    # ── Step 3: Generate ─────────────────────────────────────────────────────
    ai_response = _generate_response(client, user_query, recommendations, model)

    return recommendations, ai_response


# ── Internal helpers ─────────────────────────────────────────────────────────

def _parse_preferences(client: anthropic.Anthropic, query: str, model: str) -> dict:
    """Call Claude to convert free-text query into {genre, mood, energy}."""
    try:
        response = client.messages.create(
            model=model,
            max_tokens=150,
            system=[
                {
                    "type": "text",
                    "text": _PARSE_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": query}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown fences if Claude wraps the JSON
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        logger.debug("Raw preference JSON: %s", raw)
        prefs = json.loads(raw)

        # Guardrail: clamp energy to [0, 1]
        prefs["energy"] = max(0.0, min(1.0, float(prefs.get("energy", 0.5))))
        return prefs

    except Exception as exc:
        logger.warning(
            "Preference parsing failed (%s: %s); using fallback prefs",
            type(exc).__name__,
            exc,
        )
        return dict(_FALLBACK_PREFS)


def _generate_response(
    client: anthropic.Anthropic,
    user_query: str,
    recommendations: list,
    model: str,
) -> str:
    """Call Claude to produce a natural language recommendation using retrieved songs."""
    songs_context = "\n".join(
        f'  #{i}. "{song["title"]}" by {song["artist"]}'
        f' — genre: {song["genre"]}, mood: {song["mood"]}, energy: {float(song["energy"]):.2f}'
        f", match score: {score:.2f}"
        for i, (song, score, _) in enumerate(recommendations, 1)
    )
    prompt = (
        f'User request: "{user_query}"\n\n'
        f"Retrieved songs from catalog:\n{songs_context}"
    )

    logger.info("Generating recommendation response")
    try:
        response = client.messages.create(
            model=model,
            max_tokens=400,
            system=[
                {
                    "type": "text",
                    "text": _RECOMMEND_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        logger.info("Response generated (%d chars)", len(text))
        return text

    except anthropic.APIError as exc:
        logger.error("Claude API error during generation: %s", exc)
        top = recommendations[0][0] if recommendations else None
        return (
            f'Based on your request, "{top["title"]}" by {top["artist"]} is a strong match.'
            if top
            else "Here are some songs you might enjoy."
        )
