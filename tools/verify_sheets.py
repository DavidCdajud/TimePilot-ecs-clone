# tools/verify_sheets.py

import json
from pathlib import Path
import pygame
from tabulate import tabulate  # pip install tabulate

def verify_sheets(cfg_path: Path):
    pygame.init()
    with open(cfg_path, encoding="utf-8") as f:
        enemies = json.load(f)

    rows = []
    for e in enemies:
        img_path = Path(e["image"])
        try:
            sheet = pygame.image.load(str(img_path))
        except FileNotFoundError:
            rows.append([e.get("type","?"), str(img_path), "NOT FOUND", "-", "-", "-", "-", ""])
            continue

        sw, sh = sheet.get_size()
        fw = e.get("frame_w", sw)
        fh = e.get("frame_h", sh)
        cols = sw // fw if fw else 0
        rows_count = sh // fh if fh else 0
        max_frames = cols * rows_count
        cfg_frames = e.get("frames", max_frames)
        status = "OK" if cfg_frames <= max_frames else "⚠️ too many"

        rows.append([
            e.get("type", "?"),
            f"{sw}×{sh}",
            f"{fw}×{fh}",
            f"{cols}×{rows_count}",
            max_frames,
            cfg_frames,
            status
        ])

    headers = ["type", "sheet", "frame", "cols×rows", "possible", "configured", "status"]
    print(tabulate(rows, headers=headers, tablefmt="github"))

if __name__ == "__main__":
    import sys
    cfg_file = Path("assets/cfg/enemies.json")
    if len(sys.argv) > 1:
        cfg_file = Path(sys.argv[1])
    if not cfg_file.exists():
        print(f"Config file not found: {cfg_file}")
        sys.exit(1)
    verify_sheets(cfg_file)
