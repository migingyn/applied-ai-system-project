"""
Command line runner for the Music Recommender Simulation.
Runs the recommender for multiple user profiles to demonstrate behavior.
"""

from src.recommender import load_songs, recommend_songs


PROFILES = {
    "Happy Pop Fan": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi Listener": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "High-Energy EDM Listener": {"genre": "edm", "mood": "intense", "energy": 0.95},
    "Acoustic Folk Listener": {"genre": "folk", "mood": "peaceful", "energy": 0.3},
}


def run_profile(name: str, user_prefs: dict, songs: list) -> None:
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


def main() -> None:
    songs = load_songs("data/songs.csv")

    for name, prefs in PROFILES.items():
        run_profile(name, prefs, songs)

    print(f"\n{'='*55}")


if __name__ == "__main__":
    main()