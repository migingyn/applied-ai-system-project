"""
Integration tests — call the real Claude API (requires ANTHROPIC_API_KEY in .env).
Run with: pytest tests/test_integration.py -v
"""
import os
import pytest
from dotenv import load_dotenv

load_dotenv()

from src.recommender import load_songs
from src.ai_recommender import get_ai_recommendations

pytestmark = pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)

SONGS = load_songs("data/songs.csv")


def test_workout_query_returns_high_energy():
    recs, response = get_ai_recommendations(
        "upbeat energetic music for a morning workout", SONGS, k=5
    )
    assert len(recs) == 5
    top_song, top_score, _ = recs[0]
    assert float(top_song["energy"]) >= 0.7, "Top result should be high energy"
    assert isinstance(response, str) and len(response) > 20


def test_chill_query_returns_low_energy():
    recs, response = get_ai_recommendations(
        "something calm and quiet for studying late at night", SONGS, k=5
    )
    assert len(recs) == 5
    top_song, top_score, _ = recs[0]
    assert float(top_song["energy"]) <= 0.6, "Top result should be low energy"
    assert isinstance(response, str) and len(response) > 20


def test_jazz_query_surfaces_jazz_song():
    recs, response = get_ai_recommendations(
        "relaxing jazz for a dinner date", SONGS, k=5
    )
    genres = [song["genre"] for song, _, _ in recs]
    assert "jazz" in genres, "Jazz query should surface the jazz song in top 5"
    assert isinstance(response, str) and len(response) > 20


def test_response_references_song_title():
    recs, response = get_ai_recommendations(
        "chill lofi beats to focus", SONGS, k=5
    )
    top_title = recs[0][0]["title"]
    # Claude should mention at least one song by name in its response
    titles_in_catalog = [song["title"] for song, _, _ in recs]
    assert any(title in response for title in titles_in_catalog), (
        "AI response should reference at least one retrieved song title"
    )


def test_parse_fallback_still_returns_results():
    # Even a vague query should return songs and a non-empty response
    recs, response = get_ai_recommendations("music", SONGS, k=3)
    assert len(recs) == 3
    assert isinstance(response, str) and response.strip()
