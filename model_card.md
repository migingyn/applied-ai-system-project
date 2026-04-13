# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder 1.0 is a classroom simulation of a content-based music recommender. It is designed to suggest songs from a small catalog based on a user's preferred genre, mood, and energy level.

- **What it does:** Given a user profile (genre, mood, target energy), it scores every song in the catalog and returns the top 5 matches with a plain-language explanation of why each song was chosen.
- **Who it is for:** This system is for educational exploration only. It is not designed for real users or production deployment.
- **Assumptions:** It assumes the user can accurately describe their musical preferences using the three supported features (genre, mood, energy). It does not learn from user behavior or update its weights over time.

---

## 3. How the Model Works

VibeFinder scores each song in the catalog by comparing it to the user's stated preferences across three dimensions.

**Genre** is the most important signal. If a song's genre exactly matches what the user asked for, it earns 2 full points. Genre is treated as binary, it either matches or it does not. There is no concept of "rock is closer to alternative rock than to classical."

**Mood** works the same way. An exact match adds 1 point, anything else adds nothing.

**Energy** is the only continuous signal. Every song has an energy value between 0 and 1 (0 = very calm, 1 = very intense). The system calculates how far the song's energy is from the user's target and awards up to 1.5 points, a perfect match earns the full 1.5, and every unit of distance reduces the score proportionally.

The total score for a song is the sum of these three parts. Songs are then sorted from highest to lowest score, and the top results are returned.

---

## 4. Data

The catalog used by VibeFinder 1.0 is stored in `data/songs.csv`.

- **Size:** 20 songs (10 starter songs + 10 added during the project)
- **Features per song:** id, title, artist, genre, mood, energy, tempo_bpm, valence, danceability, acousticness
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, country, edm, r&b, classical, hip-hop, alternative rock, blues, folk
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, sad, energetic, peaceful, confident, melancholy, romantic

The 10 added songs were designed to fill gaps in the starter catalog, specifically the absence of country, EDM, R&B, classical, hip-hop, blues, and folk genres. Despite the expansion, the dataset still heavily favors Western popular music styles and does not include K-pop, Latin, Afrobeats, or regional music traditions.

---

## 5. Strengths

- **Transparent:** Every recommendation comes with a plain-language explanation (e.g., "genre match (+2.0), energy similarity (+1.47)"). Users and developers can see exactly why a song was chosen.
- **Predictable:** The scoring formula is fixed and deterministic. The same user profile always produces the same ranked list, which makes it easy to test and debug.
- **Good for mainstream profiles:** Users who want "happy pop" or "chill lofi" are well-served because these are the most represented categories in the catalog.
- **Fast:** Scoring 20 songs is nearly instantaneous, the system could realistically scale to thousands of songs with no algorithmic changes.

---

## 6. Limitations and Bias

**Genre dominance.** The genre weight (2.0) is larger than mood (1.0) and the maximum energy contribution (1.5 combined). This means a pop song with the wrong mood can outrank a perfect-mood song in a different genre. Users who care more about mood than genre will be poorly served.

**Binary matching.** Genre and mood are either an exact match or a miss. The system does not know that "alternative rock" is closer to "rock" than it is to "jazz." A user who types "rock" will completely miss "alternative rock" songs.

**Filter bubble risk.** Because the scoring is purely based on the user's stated profile, the system will always recommend songs similar to what the user already knows. There is no diversity mechanism to surface surprising or discovery-oriented results.

**Pop-heavy catalog.** Even after expansion, Western pop-adjacent genres make up a large share of the dataset. Users who prefer non-Western or underrepresented genres will find few or no matches.

**Static weights.** The weights (2.0, 1.0, 1.5) were chosen manually. They encode one developer's assumptions about what matters most in a music recommendation. A user who cares deeply about energy and not at all about genre is systematically disadvantaged by this design.

---

## 7. Evaluation

Five user profiles were tested manually:

| Profile | Top Result | Matched Intuition? |
|---|---|---|
| Happy Pop (energy 0.8) | Sunrise City | Yes, perfect genre/mood/energy match |
| Chill Lofi (energy 0.35) | Library Rain | Yes, exact energy match was the tiebreaker |
| Intense Rock (energy 0.9) | Storm Runner | Yes, correctly prioritized rock |
| Ambient Intense (conflicting) | Gym Hero (pop) | Partially, no ambient/intense song exists |
| Chill Classical (energy 0.2) | Cathedral Echo | Yes, rare win for an underrepresented genre |

The adversarial profile (ambient + intense) revealed the biggest failure mode: when the genre and mood cannot both be satisfied simultaneously, the system defaults to energy proximity and mood match, which can return very different-sounding music than the user intended.

Unit tests in `tests/test_recommender.py` verify that a pop/happy user profile produces a pop/happy top result, and that explanations are non-empty strings.

---

## 8. Future Work

1. **Genre similarity scoring.** Instead of binary genre matching, define a genre similarity matrix so "alternative rock" earns partial credit when the user asks for "rock."
2. **Learned weights.** Collect feedback ("did you like this recommendation?") and use it to adjust the genre/mood/energy weights per user over time.
3. **Diversity injection.** Intentionally include at least one "wildcard" in the top 5, a song that scores lower but is from a different genre, to promote discovery.
4. **Expand the catalog.** Add songs from non-Western traditions, and explicitly track catalog coverage by genre and mood to identify gaps.
5. **Tempo and valence scoring.** Both features are currently loaded but not used. Incorporating them would add nuance, for example, two songs with the same energy but very different valence (one dark, one bright) would score identically under the current formula.

---

## 9. Personal Reflection

Building VibeFinder made the abstract concept of a "recommendation algorithm" feel very concrete. What looks like magic in Spotify or YouTube is, at its core, a loop: judge every item in the catalog against the user's preferences, assign a number, sort the numbers. The intelligence is in how well the scoring formula captures what users actually care about.

The most surprising moment was running the adversarial profile (ambient + intense) and seeing a pop gym track at the top of the list. The system was not "wrong" by its own rules, it scored correctly, but the result felt completely off. That gap between "correct by the formula" and "useful to the user" is where human judgment still matters enormously. Real recommenders handle this through massive datasets and constant feedback loops, but those mechanisms also introduce their own biases by amplifying the preferences of the most active users.
This project changed how I think about music apps. Every "Recommended for You" playlist reflects someone's decision about what to measure, how to weight it, and whose feedback to trust. Those decisions encode values, and they are worth examining.
