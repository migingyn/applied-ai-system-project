"""
Music Recommender — CLI entry point.

Default mode  : runs four hardcoded listener profiles (rule-based scoring).
AI / RAG mode : python -m src.main --query "your request in plain English"
                Claude parses the request, retrieves matching songs, then
                generates a personalized explanation.
"""
import argparse
import logging

from src.logger_setup import setup_logging
from src.recommender import load_songs, recommend_songs

logger = logging.getLogger(__name__)

PROFILES = {
    "Happy Pop Fan":           {"genre": "pop",  "mood": "happy",   "energy": 0.80},
    "Chill Lofi Listener":     {"genre": "lofi", "mood": "chill",   "energy": 0.35},
    "High-Energy EDM Listener":{"genre": "edm",  "mood": "intense", "energy": 0.95},
    "Acoustic Folk Listener":  {"genre": "folk", "mood": "peaceful","energy": 0.30},
}


def run_profile(name: str, user_prefs: dict, songs: list) -> None:
    logger.info("Running profile: %s", name)
    print(f"\n{'='*55}")
    print(f"  Profile: {name}")
    print(f"  Prefs:   {user_prefs}")
    print(f"{'='*55}")

    recommendations = recommend_songs(user_prefs, songs, k=5)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{i}: {song['title']} by {song['artist']}")
        print(f"      Genre: {song['genre']} | Mood: {song['mood']} | Energy: {song['energy']}")
        print(f"      Score: {score:.2f}")
        print(f"      Why:   {explanation}")


def run_ai_query(query: str, songs: list, k: int = 5) -> None:
    from src.ai_recommender import get_ai_recommendations

    logger.info("AI query mode: %s", query)
    print(f"\n{'='*55}")
    print(f"  Query: {query}")
    print(f"{'='*55}")

    recommendations, ai_response = get_ai_recommendations(query, songs, k=k)

    print(f"\n  AI Response:\n  {ai_response}\n")
    print("  Top Matches:")
    for i, (song, score, _) in enumerate(recommendations, 1):
        print(
            f"    #{i}: {song['title']} by {song['artist']}"
            f" | {song['genre']} | {song['mood']} | energy {song['energy']} | score {score:.2f}"
        )


def main() -> None:
    log_file = setup_logging()

    parser = argparse.ArgumentParser(description="Music Recommender")
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Natural language music request — activates the AI/RAG pipeline (requires ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="K",
        help="Number of songs to return (default: 5)",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    logger.info("Loaded %d songs from catalog", len(songs))

    if args.query:
        run_ai_query(args.query, songs, k=args.top)
    else:
        for name, prefs in PROFILES.items():
            run_profile(name, prefs, songs)

    print(f"\n{'='*55}")
    print(f"  Log saved to: {log_file}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
