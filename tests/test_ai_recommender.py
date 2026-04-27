"""
Tests for the RAG pipeline in ai_recommender.py.
Claude API calls are mocked so no API key is needed to run tests.
"""
import json
import os
from unittest.mock import MagicMock, patch

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

_FAKE_ENV = {"ANTHROPIC_API_KEY": "sk-ant-fake-test-key"}


def _make_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.content = [MagicMock(text=text)]
    return resp


def _mock_client(parse_prefs: dict, gen_text: str) -> MagicMock:
    """Return a mock Anthropic client whose messages.create fires twice."""
    client = MagicMock()
    client.messages.create.side_effect = [
        _make_response(json.dumps(parse_prefs)),
        _make_response(gen_text),
    ]
    return client


# ── Tests ─────────────────────────────────────────────────────────────────────

@patch.dict(os.environ, _FAKE_ENV)
@patch("src.ai_recommender.anthropic.Anthropic")
def test_returns_songs_and_nonempty_text(mock_cls):
    mock_cls.return_value = _mock_client(
        {"genre": "pop", "mood": "happy", "energy": 0.8},
        "These pop tracks will brighten your day!",
    )
    recs, response = get_ai_recommendations("happy pop music", SAMPLE_SONGS, k=3)

    assert len(recs) <= 3
    assert isinstance(response, str) and response.strip()


@patch.dict(os.environ, _FAKE_ENV)
@patch("src.ai_recommender.anthropic.Anthropic")
def test_calls_claude_twice(mock_cls):
    mock = _mock_client(
        {"genre": "lofi", "mood": "chill", "energy": 0.35},
        "Great chill picks.",
    )
    mock_cls.return_value = mock

    get_ai_recommendations("something calm for studying", SAMPLE_SONGS)

    assert mock.messages.create.call_count == 2


@patch.dict(os.environ, _FAKE_ENV)
@patch("src.ai_recommender.anthropic.Anthropic")
def test_top_song_matches_genre_when_available(mock_cls):
    mock_cls.return_value = _mock_client(
        {"genre": "edm", "mood": "energetic", "energy": 0.95},
        "High energy EDM incoming!",
    )
    recs, _ = get_ai_recommendations("loud EDM for a party", SAMPLE_SONGS)

    top_song, _, _ = recs[0]
    assert top_song["genre"] == "edm"


@patch.dict(os.environ, _FAKE_ENV)
@patch("src.ai_recommender.anthropic.Anthropic")
def test_fallback_on_bad_json(mock_cls):
    """If Claude returns invalid JSON for the parse step, the pipeline falls back."""
    client = MagicMock()
    client.messages.create.side_effect = [
        _make_response("not valid json!!!"),
        _make_response("Here are some picks for you."),
    ]
    mock_cls.return_value = client

    recs, response = get_ai_recommendations("any music", SAMPLE_SONGS)

    assert len(recs) > 0
    assert isinstance(response, str)


@patch.dict(os.environ, _FAKE_ENV)
@patch("src.ai_recommender.anthropic.Anthropic")
def test_energy_clamped_to_valid_range(mock_cls):
    """Energy values outside [0, 1] returned by Claude are clamped."""
    mock_cls.return_value = _mock_client(
        {"genre": "pop", "mood": "happy", "energy": 9.99},
        "Some songs for you.",
    )
    recs, _ = get_ai_recommendations("very energetic music", SAMPLE_SONGS)

    assert len(recs) > 0


def test_raises_on_empty_query():
    with pytest.raises(ValueError, match="user_query"):
        get_ai_recommendations("", SAMPLE_SONGS)


def test_raises_on_empty_songs():
    with pytest.raises(ValueError, match="songs"):
        get_ai_recommendations("upbeat music", [])
