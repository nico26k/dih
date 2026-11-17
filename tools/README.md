# make_shorts.py: free Shorts cutter

Turns a downloaded stream into vertical **9:16 Shorts (1080×1920)**. You pick the moments; the script does the cutting and framing. Add captions afterwards in CapCut (free).

## One-time setup

1. **Python 3.** Check with `python --version` (on Mac: `python3 --version`). Get it from python.org if it's missing.
2. **ffmpeg** (free video tool):
   - **Windows:** `winget install ffmpeg` in a terminal, then open a new terminal.
   - **Mac:** `brew install ffmpeg` (needs [Homebrew](https://brew.sh)).
   - Check with `ffmpeg -version`.

On Mac, type `python3` wherever this page says `python`.

## Making Shorts (about 5 minutes once you've found the moments)

**1. Find your moments.** Scrub the video and write down start and end times in a CSV file (open `clips-example.csv`, edit it and save it as `clips.csv`):
```
start,end,name,layout
1:02:10,1:02:38,Kai loses it at the cutscene,
2:15:00,2:15:25,Cop chase goes wrong,
```
Leave `layout` empty to use the default. Keep each clip **15–45 seconds** and start right on the action.

**2. Find the facecam** (only for the facecam layout):
```
python make_shorts.py frame stream.mp4 1:02:15
```
Open `frame.png`. Each yellow line is 10% of the frame. Read off the facecam box: how far across and down it starts, then how wide and tall it is. Facecam in the top-right corner, a quarter of the width and height → `75,0,25,25`.

**3. Check the framing**:
```
python make_shorts.py preview stream.mp4 1:02:15 --facecam 75,0,25,25
```
Open `preview.png`. Adjust the numbers if the face is cut off.

**4. Cut them all**:
```
python make_shorts.py cut stream.mp4 clips.csv --facecam 75,0,25,25
```
Your Shorts land in a `shorts/` folder, numbered in order.

## Layouts

| `--layout` | Looks like | Use for |
|---|---|---|
| `facecam` (default) | facecam on top (40%), gameplay below | gaming streams with a facecam |
| `crop` | center of the frame, cropped to vertical | IRL, one person talking to the camera |
| `blur` | whole frame in the middle, blurred copy behind it | wide shots, groups, anything where cropping would cut stuff off |

## Other options

- `--cam-height 0.5` gives the facecam half the screen (default `0.4`).
- `--out myfolder` saves somewhere else.
- `--crf 20` makes files smaller (default `18`; lower means better quality and bigger files).

## Then, before posting

Import each Short into CapCut, add **auto-captions** (big and bold), credit the streamer on screen, and run through `templates/upload-checklist.md`.
