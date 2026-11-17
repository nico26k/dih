# GTA 6 Streamer Clips — Channel Hub

A YouTube channel that clips the best moments from big streamers playing **GTA 6**.

## Formats
| Format | Length | Ratio | Cadence |
|---|---|---|---|
| **Shorts** — one moment, hook in the first second | 15–45s | 9:16 | daily (1–3/day) |
| **Compilations** — "Best of the week", one streamer or one theme | 8–15 min | 16:9 | weekly |
| **Reaction-to-news** — streamers reacting to updates, trailers, events | 3–8 min | 16:9 | when it happens |

## Repo layout
```
docs/        how the channel runs (workflow, rights, packaging)
templates/   copy these for each video
trackers/    streamer list, clip log, upload log (CSV, opens in Sheets/Excel)
clips/       local media (git-ignored): raw/ → edited/ → exported/
```

## Start here
1. Read [docs/rights-and-policy.md](docs/rights-and-policy.md) — check clipping permission **before** you post anything.
2. Fill in [trackers/streamers.csv](trackers/streamers.csv) with the streamers you'll follow.
3. Follow [docs/workflow.md](docs/workflow.md) for each video.
