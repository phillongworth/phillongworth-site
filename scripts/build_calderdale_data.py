"""
Enrich calderdale50.json: fix encoding, add coordinates, and add GPX track data.

Reads GPX files from data/gpx/climbs/calderdale/ and matches them to climbs by name.
Adds simplified track coordinates for rendering on the map.

Usage: py build_calderdale_data.py
"""

import json
import os
import sys
import xml.etree.ElementTree as ET
import glob
import unicodedata

# Add shared modules to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "shared", "python"))

from geo_utils import douglas_peucker

# Paths
DATA_DIR = os.path.join(REPO_ROOT, "data")
INPUT_FILE = os.path.join(DATA_DIR, "generated", "calderdale50.json")
OUTPUT_FILE = INPUT_FILE
GPX_DIR = os.path.join(DATA_DIR, "gpx", "climbs", "calderdale")

GPX_NS = "http://www.topografix.com/GPX/1/1"
SIMPLIFY_TOLERANCE = 0.0001  # ~10m, tighter than 1000-miles since these are short climbs

# Approximate centre coordinates for each area (fallback)
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
    text = text.replace("\u00a0", " ")
    text = text.replace("\u00c2\u00a0", " ")
    text = text.replace("\xc2\xa0", " ")
    text = text.replace("\u00e9", "e")
    text = text.replace("\u2019", "'")
    text = text.replace("\u2018", "'")
    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    return text.strip()


def parse_gpx_track(filepath):
    """Parse a GPX file and return simplified track coordinates."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    points = []
    for trkpt in root.iter(f"{{{GPX_NS}}}trkpt"):
        lat = float(trkpt.get("lat"))
        lon = float(trkpt.get("lon"))
        points.append((lat, lon))

    if not points:
        return None

    simplified = douglas_peucker(points, SIMPLIFY_TOLERANCE)
    return [[round(p[0], 5), round(p[1], 5)] for p in simplified]


def normalise(name):
    """Normalise a climb name for fuzzy matching against GPX filenames."""
    # Decompose unicode (e.g. ô -> o + combining accent), then strip accents
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_name.lower().replace("'", "").replace("'", "").strip()


def build_gpx_lookup():
    """Build a dict mapping normalised GPX filename -> filepath."""
    lookup = {}
    for filepath in glob.glob(os.path.join(GPX_DIR, "*.gpx")):
        basename = os.path.splitext(os.path.basename(filepath))[0]
        key = normalise(basename)
        lookup[key] = filepath
    return lookup


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    gpx_lookup = build_gpx_lookup()
    area_count = {}
    matched = 0
    unmatched = []

    for climb in data["climbs"]:
        # Fix encoding
        if "name" in climb:
            climb["name"] = fix_encoding(climb["name"])

        # Only add approximate coordinates if exact ones are missing
        if "lat" not in climb or "lon" not in climb:
            area = climb.get("area")
            if area and area in AREA_COORDS:
                base_lat, base_lon = AREA_COORDS[area]
                idx = area_count.get(area, 0)
                area_count[area] = idx + 1
                row = idx // 3
                col = idx % 3
                climb["lat"] = round(base_lat + row * 0.003 + col * 0.001, 5)
                climb["lon"] = round(base_lon + col * 0.003 - row * 0.001, 5)
            elif climb.get("category") == "other":
                idx = area_count.get("_other", 0)
                area_count["_other"] = idx + 1
                climb["lat"] = round(53.7200 + idx * 0.002, 5)
                climb["lon"] = round(-1.8700 - idx * 0.003, 5)

        # Match to GPX file by name
        name = climb.get("name", "")
        key = normalise(name)
        gpx_path = gpx_lookup.get(key)

        if not gpx_path:
            # Try matching without "No X - " prefix or area suffix
            alt_key = normalise(name.split(" - ", 1)[-1] if " - " in name else name)
            gpx_path = gpx_lookup.get(alt_key)

        if gpx_path:
            coords = parse_gpx_track(gpx_path)
            if coords:
                climb["track"] = coords
                matched += 1
        else:
            unmatched.append(name)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total = len(data["climbs"])
    print(f"Matched {matched}/{total} climbs to GPX tracks")
    if unmatched:
        print(f"Unmatched: {unmatched}")
    with_coords = sum(1 for c in data["climbs"] if "lat" in c)
    print(f"Coordinates: {with_coords}/{total}")

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"Written to {OUTPUT_FILE} ({file_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
