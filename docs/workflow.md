# Workflow: stream → clip → upload

## 1. Find (daily, ~30 min)
- Check who's live / just ended a GTA 6 stream (Twitch, Kick, YouTube Live).
- Fastest sources of moments: the streamer's own **Twitch clips page sorted by "Top 24h"**, chat spikes, and community subreddits/Discords.
- Log every candidate in `trackers/clip-log.csv` (streamer, VOD link, timestamp, one-line description).

## 2. Pick
Keep a moment only if it passes at least one:
- **Reaction** — big laugh, rage, shock, scream
- **Chaos** — police chase, heist going wrong, physics glitch
- **Story** — RP drama, betrayal, a payoff to something set up earlier
- **First** — first time seeing a new feature/area/update

Skip it if it needs more than ~5s of context to understand.

## 3. Cut
- Download the VOD segment, put it in `clips/raw/`.
- **Shorts:** start *at* the action (no build-up), end right after the payoff. Facecam on top, gameplay below (9:16 split).
- **Compilations:** 10–20 moments, strongest one first, second-strongest last.

## 4. Edit (this is what makes it *yours*)
- Burned-in captions (big, bold, word-by-word).
- Zoom-ins on reactions, sound effects/meme hits sparingly, a short text hook on screen in the first second.
- Credit the streamer on screen: `@streamername on Twitch`.
- Save to `clips/edited/`, export to `clips/exported/`.

## 5. Package
Use `templates/video-template.md`: title, thumbnail, description, tags.

## 6. Upload & log
- Run through `templates/upload-checklist.md`.
- Add a row to `trackers/upload-log.csv`.

## 7. Review (weekly)
- Which streamers / moment types got the most views and retention?
- Do more of what works; drop streamers whose clips don't perform.
