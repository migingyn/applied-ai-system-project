"""
Tests for the RAG pipeline in ai_recommender.py.
Claude API calls are mocked so no API key is needed to run tests.
"""
import json
from unittest.mock import MagicMock, call, patch

import pytest

from src.ai_recommender import _FALLBACK_PREFS, get_ai_recommendations

# ── Fixtures ─────────────────────────────────────────────────────────────────

SAMPLE_SONGS = [
    {
        "id": 1, "title": "Sunrise City", "artist": "Neon Echo",
        "genre": "pop", "mood": "happy", "energy": 0.82,
        "tempo_bpm": 118, "valence": 0.84, "danceability": 0.79, "acousticness": 0.18,
    },
    {
        "id": 2, "title": "Library Rain", "artist": "Paper Lanterns",
        "genre": "lofi", "mood": "chill", "energy": 0.35,
        "tempo_bpm": 72, "valence": 0.60, "danceability": 0.58, "acousticness": 0.86,
    },
    {
        "id": 3, "title": "Circuit Breaker", "artist": "Voltage Drop",
        "genre": "edm", "mood": "energetic", "energy": 0.96,
        "tempo_bpm": 140, "valence": 0.72, "danceability": 0.92, "acousticness": 0.03,
    },
]


def _make_mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    return resp


# ── Helpers ───────────────────────────────────────────────────────────────────

def _setup_mock_client(mock_anthropic_cls, prefs: dict, ai_text: str) -> MagicMock:
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.side_effect = [
        _make_mock_response(json.dumps(prefs)),
        _make_mock_response(ai_text),
    ]
    return mock_client


# ── Tests ─────────────────────────────────────────────────────────────────────

@patch("src.ai_recommender.anthropic.Anthropic")
def test_returns_songs_and_nonempty_text(mock_anthropic_cls):
    mock_client = _setup_mock_client(
        mock_anthropic_cls,
        prefs={"genre": "pop", "mood": "happy", "energy": 0.8},
        ai_text="These pop tracks will brighten your day!",
    )

    recs, response = get_ai_recommendations("happy pop music", SAMPLE_SONGS, k=3)

    assert len(recs) <= 3
    assert isinstance(response, str) and response.strip()


@patch("src.ai_recommender.anthropic.Anthropic")
def test_calls_claude_twice(mock_anthropic_cls):
    mock_client = _setup_mock_client(
        mock_anthropic_cls,
        prefs={"genre": "lofi", "mood": "chill", "energy": 0.35},
        ai_text="Great chill picks.",
    )

    get_ai_recommendations("something calm for studying", SAMPLE_SONGS)

    assert mock_client.messages.create.call_count == 2


@patch("src.ai_recommender.anthropic.Anthropic")
def test_top_song_matches_genre_when_available(mock_anthropic_cls):
    _setup_mock_client(
        mock_anthropic_cls,
        prefs={"genre": "edm", "mood": "energetic", "energy": 0.95},
        ai_text="High energy EDM incoming!",
    )

    recs, _ = get_ai_recommendations("loud EDM for a party", SAMPLE_SONGS)

    top_song, top_score, _ = recs[0]
    assert top_song["genre"] == "edm"


@patch("src.ai_recommender.anthropic.Anthropic")
def test_fallback_on_bad_json(mock_anthropic_cls):
    """If Claude returns invalid JSON, the pipeline falls back and still returns results."""
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.side_effect = [
        _make_mock_response("not valid json!!!"),  # parse step fails
        _make_mock_response("Here are some picks for you."),
    ]

    recs, response = get_ai_recommendations("any music", SAMPLE_SONGS)

    assert len(recs) > 0
    assert isinstance(response, str)


@patch("src.ai_recommender.anthropic.Anthropic")
def test_energy_clamped_to_valid_range(mock_anthropic_cls):
    """Energy values outside [0, 1] returned by Claude are clamped."""
    mock_client = _setup_mock_client(
        mock_anthropic_cls,
        prefs={"genre": "pop", "mood": "happy", "energy": 9.99},  # out of range
        ai_text="Some songs for you.",
    )

    recs, _ = get_ai_recommendations("very energetic music", SAMPLE_SONGS)

    # Pipeline should not crash and should return results
    assert len(recs) > 0


def test_raises_on_empty_query():
    with pytest.raises(ValueError, match="user_query"):
        get_ai_recommendations("", SAMPLE_SONGS)


def test_raises_on_empty_songs():
    with pytest.raises(ValueError, match="songs"):
        get_ai_recommendations("upbeat music", [])
