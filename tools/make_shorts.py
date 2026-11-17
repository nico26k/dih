#!/usr/bin/env python3
"""
make_shorts.py: cut a downloaded stream/VOD into vertical 9:16 YouTube Shorts.

It needs Python 3.8+ and ffmpeg (free) installed. See tools/README.md.

Three commands:

  frame    Save one frame of the source with a 10% grid, so you can find the facecam.
           python make_shorts.py frame stream.mp4 1:02:30

  preview  Save one frame of the finished 9:16 layout, to check the framing before cutting.
           python make_shorts.py preview stream.mp4 1:02:30 --layout facecam --facecam 75,0,25,25

  cut      Cut every clip listed in a CSV file into its own Short.
           python make_shorts.py cut stream.mp4 clips.csv --layout facecam --facecam 75,0,25,25

Layouts:
  facecam  Facecam on top, gameplay below. Set the facecam box with --facecam.
  crop     Center of the frame cropped to 9:16. Good for IRL / one person talking.
  blur     The whole frame, centered on a blurred copy of itself. Nothing gets cut off.
"""

import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

OUT_W, OUT_H = 1080, 1920


# ---------------------------------------------------------------- helpers

def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_time(text):
    """'1:02:30', '62:30', '3750' or '3750.5' -> seconds (float)."""
    text = str(text).strip()
    if not text:
        die("empty timestamp")
    try:
        parts = [float(p) for p in text.split(":")]
    except ValueError:
        die(f"can't read timestamp '{text}' (use H:MM:SS, MM:SS or seconds)")
    if len(parts) > 3:
        die(f"can't read timestamp '{text}'")
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def parse_box(text):
    """'75,0,25,25' (x%,y%,w%,h% of the source frame) -> tuple of fractions."""
    try:
        x, y, w, h = (float(v) / 100 for v in text.split(","))
    except ValueError:
        die(f"--facecam must be four numbers like 75,0,25,25 (got '{text}')")
    if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > 1.001 or y + h > 1.001:
        die(f"--facecam box {text} goes outside the frame")
    return x, y, w, h


def even(n):
    n = int(round(n))
    return n - (n % 2)


def probe_size(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(video)],
        capture_output=True, text=True,
    )
    if out.returncode != 0 or "x" not in out.stdout:
        die(f"ffprobe couldn't read '{video}'. Is it a video file?\n{out.stderr.strip()}")
    w, h = out.stdout.strip().splitlines()[0].split("x")[:2]
    return int(w), int(h)


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        tail = "\n".join(result.stderr.strip().splitlines()[-15:])
        die(f"ffmpeg failed:\n{tail}")


# ---------------------------------------------------------------- layouts

def build_filter(layout, src_w, src_h, facecam=None, cam_height=0.4):
    """Return an ffmpeg -filter_complex string whose output is labeled [v]."""
    if layout == "crop":
        crop_w = min(src_w, even(src_h * OUT_W / OUT_H))
        crop_h = even(crop_w * OUT_H / OUT_W)
        return (f"[0:v]crop={crop_w}:{crop_h}:(iw-{crop_w})/2:(ih-{crop_h})/2,"
                f"scale={OUT_W}:{OUT_H},setsar=1[v]")

    if layout == "blur":
        return (f"[0:v]split[bg][fg];"
                f"[bg]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
                f"crop={OUT_W}:{OUT_H},boxblur=20:2[bgb];"
                f"[fg]scale={OUT_W}:-2[fgs];"
                f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1[v]")

    if layout == "facecam":
        if facecam is None:
            die("the facecam layout needs --facecam x,y,w,h (run the 'frame' command to find it)")
        fx, fy, fw, fh = facecam
        cam_x, cam_y = even(fx * src_w), even(fy * src_h)
        cam_w, cam_h = even(fw * src_w), even(fh * src_h)

        top_h = even(OUT_H * cam_height)
        bot_h = OUT_H - top_h

        # Gameplay: the tallest center slice of the source that matches the bottom panel's shape.
        g_h = src_h
        g_w = even(g_h * OUT_W / bot_h)
        if g_w > src_w:
            g_w = src_w
            g_h = even(g_w * bot_h / OUT_W)

        return (f"[0:v]split[a][b];"
                f"[a]crop={cam_w}:{cam_h}:{cam_x}:{cam_y},"
                f"scale={OUT_W}:{top_h}:force_original_aspect_ratio=increase,"
                f"crop={OUT_W}:{top_h}[cam];"
                f"[b]crop={g_w}:{g_h}:(iw-{g_w})/2:(ih-{g_h})/2,"
                f"scale={OUT_W}:{bot_h}[game];"
                f"[cam][game]vstack,setsar=1[v]")

    die(f"unknown layout '{layout}' (use facecam, crop or blur)")


# ---------------------------------------------------------------- commands

def cmd_frame(args):
    out = Path(args.out or "frame.png")
    w, h = probe_size(args.video)
    lines = []
    for i in range(1, 10):
        lines.append(f"drawbox=x={even(w * i / 10)}:y=0:w=2:h=ih:color=yellow@0.8:t=fill")
        lines.append(f"drawbox=x=0:y={even(h * i / 10)}:w=iw:h=2:color=yellow@0.8:t=fill")
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(parse_time(args.time)),
         "-i", str(args.video), "-frames:v", "1", "-vf", ",".join(lines), str(out)])
    print(f"Saved {out}  ({w}x{h}). Each yellow line is 10% of the frame.")
    print("Read off where the facecam is, e.g. starts at 75% across and 0% down, "
          "25% wide and 25% tall -> --facecam 75,0,25,25")


def cmd_preview(args):
    out = Path(args.out or "preview.png")
    w, h = probe_size(args.video)
    facecam = parse_box(args.facecam) if args.facecam else None
    filt = build_filter(args.layout, w, h, facecam, args.cam_height)
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(parse_time(args.time)),
         "-i", str(args.video), "-filter_complex", filt, "-map", "[v]",
         "-frames:v", "1", str(out)])
    print(f"Saved {out} ({OUT_W}x{OUT_H}). Open it to check the framing.")


def read_clips(path):
    clips = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    if not rows:
        die(f"{path} has no clips in it")
    header = [c.strip().lower() for c in rows[0]]
    if "start" in header and "end" in header:
        idx = {name: header.index(name) for name in header}
        body = rows[1:]
    else:  # no header: start,end[,name[,layout]]
        idx = {"start": 0, "end": 1, "name": 2, "layout": 3}
        body = rows

    def get(row, key):
        i = idx.get(key)
        return row[i].strip() if i is not None and i < len(row) else ""

    for n, row in enumerate(body, start=1):
        start, end = parse_time(get(row, "start")), parse_time(get(row, "end"))
        if end <= start:
            die(f"clip {n}: end ({get(row, 'end')}) must be after start ({get(row, 'start')})")
        name = get(row, "name") or f"clip_{n:02d}"
        safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in name).strip()
        clips.append({"start": start, "end": end, "name": safe or f"clip_{n:02d}",
                      "layout": get(row, "layout").lower() or None})
    return clips


def cmd_cut(args):
    out_dir = Path(args.out or "shorts")
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = probe_size(args.video)
    facecam = parse_box(args.facecam) if args.facecam else None
    clips = read_clips(args.clips)

    for n, clip in enumerate(clips, start=1):
        layout = clip["layout"] or args.layout
        length = clip["end"] - clip["start"]
        if length > 60:
            print(f"  note: '{clip['name']}' is {length:.0f}s. Shorts are best kept under 60s.")
        filt = build_filter(layout, w, h, facecam, args.cam_height)
        target = out_dir / f"{n:02d}_{clip['name']}.mp4"
        print(f"[{n}/{len(clips)}] {target.name}  ({length:.1f}s, {layout})")
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", f"{clip['start']:.3f}", "-i", str(args.video), "-t", f"{length:.3f}",
             "-filter_complex", filt, "-map", "[v]", "-map", "0:a?",
             "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
             "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
             "-movflags", "+faststart", str(target)])
    print(f"Done. {len(clips)} Short(s) in {out_dir}/")


# ---------------------------------------------------------------- main

def main():
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        die("ffmpeg isn't installed (or isn't on your PATH). See tools/README.md.")

    p = argparse.ArgumentParser(description="Cut a stream into vertical 9:16 Shorts.",
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog=__doc__.split("Three commands:")[1])
    sub = p.add_subparsers(dest="command", required=True)

    def layout_opts(sp):
        sp.add_argument("--layout", default="facecam", choices=["facecam", "crop", "blur"])
        sp.add_argument("--facecam", help="facecam box as x,y,w,h in %% of the frame, e.g. 75,0,25,25")
        sp.add_argument("--cam-height", type=float, default=0.4,
                        help="share of the Short's height for the facecam (default 0.4)")
        sp.add_argument("--out", help="output file (frame/preview) or folder (cut)")

    sp = sub.add_parser("frame", help="save a source frame with a 10%% grid")
    sp.add_argument("video"); sp.add_argument("time"); sp.add_argument("--out")
    sp.set_defaults(func=cmd_frame)

    sp = sub.add_parser("preview", help="save one frame of the 9:16 layout")
    sp.add_argument("video"); sp.add_argument("time"); layout_opts(sp)
    sp.set_defaults(func=cmd_preview)

    sp = sub.add_parser("cut", help="cut every clip in a CSV into a Short")
    sp.add_argument("video"); sp.add_argument("clips"); layout_opts(sp)
    sp.add_argument("--crf", type=int, default=18, help="quality, lower is better (default 18)")
    sp.add_argument("--preset", default="veryfast", help="x264 speed preset (default veryfast)")
    sp.set_defaults(func=cmd_cut)

    args = p.parse_args()
    if not Path(args.video).is_file():
        die(f"can't find the video '{args.video}'")
    if getattr(args, "clips", None) and not Path(args.clips).is_file():
        die(f"can't find the clips file '{args.clips}'")
    args.func(args)


if __name__ == "__main__":
    main()
