# 🎵 Music Recommender Simulation

## Project Summary

This project is a content-based music recommender built from scratch in Python. It loads a catalog of songs from a CSV file, scores each song against a user's taste profile, and returns a ranked list of the top matches with plain-language explanations.

The recommender uses three features, genre, mood, and energy, to calculate a compatibility score for every song. Genre matching carries the most weight (+2.0 points), followed by mood (+1.0 point), with energy similarity contributing up to +1.5 points based on how close the song's energy level is to the user's target. Songs are then sorted from highest to lowest score and the top results are printed to the terminal.

---

## How The System Works

### Features used per `Song`

| Feature | Type | Description |
|---|---|---|
| `genre` | string | Musical category (pop, lofi, rock, edm, etc.) |
| `mood` | string | Emotional tone (happy, chill, intense, sad, etc.) |
| `energy` | float 0–1 | How loud and active the track feels |
| `tempo_bpm` | integer | Beats per minute (stored but not scored in v1) |
| `valence` | float 0–1 | Musical positivity (stored but not scored in v1) |
| `danceability` | float 0–1 | How suitable the track is for dancing |
| `acousticness` | float 0–1 | How acoustic vs electronic the track sounds |

### What `UserProfile` stores

- `favorite_genre` — the genre the user prefers most
- `favorite_mood` — the mood they want right now
- `target_energy` — a 0–1 value for how intense they want the music
- `likes_acoustic` — boolean bonus flag; adds +0.5 for acoustic songs above 0.6

### Scoring rule (one song)

```
score = 0
if song.genre == user.genre:   score += 2.0   # genre match
if song.mood  == user.mood:    score += 1.0   # mood match
energy_gap = |user.energy - song.energy|
score += 1.5 * (1 - energy_gap)               # energy proximity (max 1.5)
if user.likes_acoustic and song.acousticness > 0.6:
    score += 0.5                               # acoustic bonus
```

### Ranking rule (all songs)

The `recommend_songs()` function loops through every song in the catalog, calls `score_song` to get a numeric score, then uses Python's `sorted()` (returns a new sorted list, leaving the original intact) to rank all songs from highest to lowest score. The top `k` results are returned as `(song, score, explanation)` tuples.

**Data flow:**

```
User Preferences
      │
      ▼
Loop over every song in songs.csv
      │
      ▼
score_song(user_prefs, song) → numeric score + reasons list
      │
      ▼
sorted(all_scored_songs, key=score, reverse=True)
      │
      ▼
Top K Recommendations (title, score, explanation)
```

Real-world recommenders like Spotify and YouTube work on the same loop principle but at a scale of millions of songs and users. They also incorporate collaborative filtering (what similar users liked) and use neural networks to embed songs in high-dimensional feature space. Our version is transparent and rule-based, which makes it easy to inspect and explain — a real strength for an educational context.

### Terminal Output

<img width="425" height="835" alt="terminal_output_profiles" src="https://github.com/user-attachments/assets/c41a20a6-bbf3-4676-aa01-e634263bcc28" />

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the recommender:

   ```bash
   python -m src.main
   ```

### Running Tests

```bash
pytest
```

---

## Experiments You Tried

Run all profiles yourself with: `python -m src.main`

---

### Profile 1 — Happy Pop Fan

**Profile:** `{"genre": "pop", "mood": "happy", "energy": 0.8}`

```
=======================================================
  Profile: Happy Pop Fan
  Prefs:   {'genre': 'pop', 'mood': 'happy', 'energy': 0.8}
=======================================================

  #1: Sunrise City by Neon Echo
      Genre: pop | Mood: happy | Energy: 0.82
      Score: 4.47
      Why:   genre match (+2.0); mood match (+1.0); energy similarity (+1.47)

  #2: Gym Hero by Max Pulse
      Genre: pop | Mood: intense | Energy: 0.93
      Score: 3.30
      Why:   genre match (+2.0); energy similarity (+1.30)

  #3: Rooftop Lights by Indigo Parade
      Genre: indie pop | Mood: happy | Energy: 0.76
      Score: 2.44
      Why:   mood match (+1.0); energy similarity (+1.44)

  #4: Street Cipher by Kade Ramos
      Genre: hip-hop | Mood: confident | Energy: 0.77
      Score: 1.46
      Why:   energy similarity (+1.46)

  #5: Night Drive Loop by Neon Echo
      Genre: synthwave | Mood: moody | Energy: 0.75
      Score: 1.42
      Why:   energy similarity (+1.42)
```

**Observation:** Genre weight (2.0) dominates the rankings. Sunrise City is a near-perfect match (genre + mood + energy). Gym Hero ranks second despite having the wrong mood because the genre match alone is worth more than a mood match in a different genre. Rooftop Lights places third from mood match alone, "indie pop" doesn't count as a genre match for "pop."

---

### Profile 2 — Chill Lofi Listener

**Profile:** `{"genre": "lofi", "mood": "chill", "energy": 0.35}`

```
=======================================================
  Profile: Chill Lofi Listener
  Prefs:   {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35}
=======================================================

  #1: Library Rain by Paper Lanterns
      Genre: lofi | Mood: chill | Energy: 0.35
      Score: 4.50
      Why:   genre match (+2.0); mood match (+1.0); energy similarity (+1.50)

  #2: Midnight Coding by LoRoom
      Genre: lofi | Mood: chill | Energy: 0.42
      Score: 4.40
      Why:   genre match (+2.0); mood match (+1.0); energy similarity (+1.40)

  #3: Focus Flow by LoRoom
      Genre: lofi | Mood: focused | Energy: 0.4
      Score: 3.42
      Why:   genre match (+2.0); energy similarity (+1.42)

  #4: Spacewalk Thoughts by Orbit Bloom
      Genre: ambient | Mood: chill | Energy: 0.28
      Score: 2.40
      Why:   mood match (+1.0); energy similarity (+1.40)

  #5: Coffee Shop Stories by Slow Stereo
      Genre: jazz | Mood: relaxed | Energy: 0.37
      Score: 1.47
      Why:   energy similarity (+1.47)
```

**Observation:** Both genre and mood match for the top two songs; energy becomes the tiebreaker. Library Rain (energy 0.35) scores a perfect 1.50 energy similarity because it exactly matches the target. The top 3 are all lofi tracks, showing that a well-represented genre dominates the list even when mood doesn't match (#3, Focus Flow).

**Comparison with Happy Pop:** The output is completely different, both genre and energy are on opposite ends of the spectrum. Happy Pop surfaces loud, upbeat tracks; Chill Lofi surfaces quiet, low-energy tracks. This confirms the scoring formula is sensitive to all three features.

---

### Profile 3 — High-Energy EDM Listener

**Profile:** `{"genre": "edm", "mood": "intense", "energy": 0.95}`

```
=======================================================
  Profile: High-Energy EDM Listener
  Prefs:   {'genre': 'edm', 'mood': 'intense', 'energy': 0.95}
=======================================================

  #1: Bass Drop Theory by Flux Engine
      Genre: edm | Mood: intense | Energy: 0.94
      Score: 4.48
      Why:   genre match (+2.0); mood match (+1.0); energy similarity (+1.48)

  #2: Circuit Breaker by Voltage Drop
      Genre: edm | Mood: energetic | Energy: 0.96
      Score: 3.48
      Why:   genre match (+2.0); energy similarity (+1.48)

  #3: Gym Hero by Max Pulse
      Genre: pop | Mood: intense | Energy: 0.93
      Score: 2.47
      Why:   mood match (+1.0); energy similarity (+1.47)

  #4: Storm Runner by Voltline
      Genre: rock | Mood: intense | Energy: 0.91
      Score: 2.44
      Why:   mood match (+1.0); energy similarity (+1.44)

  #5: Sunrise City by Neon Echo
      Genre: pop | Mood: happy | Energy: 0.82
      Score: 1.30
      Why:   energy similarity (+1.30)
```

**Observation:** The EDM profile correctly surfaces both EDM tracks first. Positions #3 and #4 are non-EDM songs that share the "intense" mood and high energy, showing that mood + energy can partially substitute for a missing genre match. The Chill Lofi songs disappear entirely from the top 5 because their energy (0.35–0.42) is far from the target of 0.95.

**Comparison with Chill Lofi:** These two profiles produce completely non-overlapping top-5 lists. EDM favors loud, intense tracks with energy near 1.0; Chill Lofi favors quiet, focused tracks with energy near 0.35. This is the clearest demonstration that the energy dimension meaningfully separates different listener types.

---

### Profile 4 — Acoustic Folk Listener

**Profile:** `{"genre": "folk", "mood": "peaceful", "energy": 0.3}`

```
=======================================================
  Profile: Acoustic Folk Listener
  Prefs:   {'genre': 'folk', 'mood': 'peaceful', 'energy': 0.3}
=======================================================

  #1: Mountain High by Cedar & Stone
      Genre: folk | Mood: peaceful | Energy: 0.33
      Score: 4.46
      Why:   genre match (+2.0); mood match (+1.0); energy similarity (+1.46)

  #2: Cathedral Echo by Aria Collective
      Genre: classical | Mood: peaceful | Energy: 0.22
      Score: 2.38
      Why:   mood match (+1.0); energy similarity (+1.38)

  #3: Spacewalk Thoughts by Orbit Bloom
      Genre: ambient | Mood: chill | Energy: 0.28
      Score: 1.47
      Why:   energy similarity (+1.47)

  #4: Library Rain by Paper Lanterns
      Genre: lofi | Mood: chill | Energy: 0.35
      Score: 1.42
      Why:   energy similarity (+1.42)

  #5: Coffee Shop Stories by Slow Stereo
      Genre: jazz | Mood: relaxed | Energy: 0.37
      Score: 1.40
      Why:   energy similarity (+1.40)
```

**Observation:** Only one folk song exists in the catalog, so after the #1 result there are no more genre matches. The remaining slots are filled by low-energy songs from classical, ambient, lofi, and jazz, correct in "vibe" but not in genre. This highlights the small catalog problem: niche genres have only one representative, leaving no diversity in the results.

**Comparison with EDM:** These profiles share zero overlap in their top 5. EDM surfaces high-energy electronic tracks; Folk surfaces quiet acoustic tracks. This pair best illustrates how the energy dimension alone can fully separate listener types even without relying on genre matches.

---

## Limitations and Risks

- **Tiny catalog** — 20 songs means the top result is often the only real match for a niche preference. A real system needs thousands of tracks for meaningful diversity.
- **Genre dominance** — The +2.0 genre weight is the single biggest factor. A user who gets the genre slightly wrong (e.g., "indie pop" vs "pop") will see dramatically different results.
- **No collaborative filtering** — The system has no knowledge of what other users liked. It cannot discover that fans of "chill lofi" also enjoy "ambient."
- **Binary matching** — Genre and mood are treated as either equal or not. There is no concept of genre similarity (rock ≈ alternative rock more than rock ≈ classical).
- **Static weights** — Everyone gets the same formula. A user who cares deeply about energy but not genre is served poorly.

---

## Reflection

See [model_card.md](model_card.md) for the full model card.

Building this recommender made the "loop" structure of recommendation engines very concrete. Every song gets judged independently against the user's preferences and assigned a number. The ranking is just sorting those numbers. What seems "intelligent" in apps like Spotify is really an extremely large and well-tuned version of the same idea, every song in a catalog gets a score, and the highest ones surface.

The place where bias enters is in the weights. Choosing genre weight = 2.0 and mood weight = 1.0 is a design decision that encodes the assumption that genre matters twice as much as mood. In a real product, those weights would be learned from user behavior data, which means they would reflect the preferences of the majority of users, potentially at the expense of users whose tastes don't fit the dominant pattern.
