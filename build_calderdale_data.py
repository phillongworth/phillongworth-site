"""
Enrich calderdale50.json: fix encoding and add approximate lat/lon from area names.

Usage: py build_calderdale_data.py
"""

import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
INPUT_FILE = os.path.join(DATA_DIR, "calderdale50.json")
OUTPUT_FILE = INPUT_FILE

# Approximate centre coordinates for each area
AREA_COORDS = {
    "Cornholme": (53.7200, -2.1150),
    "Greetland": (53.6850, -1.8500),
    "Halifax": (53.7250, -1.8600),
    "Hebden Bridge": (53.7430, -2.0120),
    "Luddenden": (53.7250, -1.9350),
    "Mytholmroyd": (53.7350, -1.9750),
    "Ripponden": (53.6700, -1.9400),
    "Shibden": (53.7300, -1.8300),
    "Sowerby Bridge": (53.7080, -1.9100),
    "Stainland": (53.6700, -1.8800),
    "The Far East": (53.7100, -1.8100),
    "Todmorden": (53.7150, -2.0950),
    "Walsden": (53.6900, -2.1050),
}


def fix_encoding(text):
    """Fix common encoding issues from WordPress scraping."""
    if not text:
        return text
    # Replace non-breaking space artifacts
    text = text.replace("\u00a0", " ")
    text = text.replace("\u00c2\u00a0", " ")
    text = text.replace("\xc2\xa0", " ")
    # Fix common mojibake for special chars
    text = text.replace("\u00e9", "e")  # é -> e (Côte)
    text = text.replace("\u2019", "'")  # right single quote
    text = text.replace("\u2018", "'")  # left single quote
    text = text.replace("\u2013", "-")  # en dash
    text = text.replace("\u2014", "-")  # em dash
    return text.strip()


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Track used offsets per area to spread markers
    area_count = {}

    for climb in data["climbs"]:
        # Fix encoding in name
        if "name" in climb:
            climb["name"] = fix_encoding(climb["name"])

        # Add coordinates based on area
        area = climb.get("area")
        if area and area in AREA_COORDS:
            base_lat, base_lon = AREA_COORDS[area]
            # Add small offset so markers don't overlap
            idx = area_count.get(area, 0)
            area_count[area] = idx + 1
            # Spread in a grid pattern
            row = idx // 3
            col = idx % 3
            climb["lat"] = round(base_lat + row * 0.003 + col * 0.001, 5)
            climb["lon"] = round(base_lon + col * 0.003 - row * 0.001, 5)
        elif "category" in climb and climb["category"] == "other" and "lat" not in climb:
            # Place "others" near Halifax centre with offset
            idx = area_count.get("_other", 0)
            area_count["_other"] = idx + 1
            climb["lat"] = round(53.7200 + idx * 0.002, 5)
            climb["lon"] = round(-1.8700 - idx * 0.003, 5)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    with_coords = sum(1 for c in data["climbs"] if "lat" in c)
    print(f"Enriched {with_coords}/{len(data['climbs'])} climbs with coordinates")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
