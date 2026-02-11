"""
Build script to process GPX files into a single tracks.json for the 1000-miles map.

Reads all numbered GPX files (10*.gpx) from data/gpx/activities/, extracts coordinates,
calculates distance/elevation, simplifies tracks, and outputs data/generated/tracks.json.

Usage: python build_map_data.py
"""

import xml.etree.ElementTree as ET
import json
import glob
import os
import re
import sys

# Add shared modules to path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "shared", "python"))

from geo_utils import haversine, douglas_peucker, KM_TO_MILES, METERS_TO_FEET

# Paths
DATA_DIR = os.path.join(REPO_ROOT, "data")
GPX_DIR = os.path.join(DATA_DIR, "gpx", "activities")
OUTPUT_FILE = os.path.join(DATA_DIR, "generated", "tracks.json")

GPX_NS = "http://www.topografix.com/GPX/1/1"
SIMPLIFY_TOLERANCE = 0.0002  # ~20m in degrees, adjust for desired detail


def parse_gpx(filepath):
    """Parse a GPX file and return track data."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Extract start date from metadata or first trackpoint
    date = None
    meta_time = root.find(f"{{{GPX_NS}}}metadata/{{{GPX_NS}}}time")
    if meta_time is not None and meta_time.text:
        date = meta_time.text[:10]  # YYYY-MM-DD

    points = []  # (lat, lon, ele)
    for trkpt in root.iter(f"{{{GPX_NS}}}trkpt"):
        lat = float(trkpt.get("lat"))
        lon = float(trkpt.get("lon"))
        ele_el = trkpt.find(f"{{{GPX_NS}}}ele")
        ele = float(ele_el.text) if (ele_el is not None and ele_el.text) else None

        if date is None:
            time_el = trkpt.find(f"{{{GPX_NS}}}time")
            if time_el is not None and time_el.text:
                date = time_el.text[:10]

        points.append((lat, lon, ele))

    if not points:
        return None

    # Calculate distance (km) from all points
    total_distance_km = 0
    for i in range(1, len(points)):
        total_distance_km += haversine(
            points[i - 1][0], points[i - 1][1],
            points[i][0], points[i][1]
        )

    # Calculate elevation gain from all points (before simplification)
    total_elevation_m = 0
    for i in range(1, len(points)):
        if points[i][2] is not None and points[i - 1][2] is not None:
            diff = points[i][2] - points[i - 1][2]
            if diff > 0:
                total_elevation_m += diff

    # Simplify coordinates for display
    coords_2d = [(p[0], p[1]) for p in points]
    simplified = douglas_peucker(coords_2d, SIMPLIFY_TOLERANCE)
    # Round to 5 decimal places (~1m precision)
    coordinates = [[round(p[0], 5), round(p[1], 5)] for p in simplified]

    return {
        "date": date,
        "distance_miles": round(total_distance_km * KM_TO_MILES, 2),
        "elevation_feet": round(total_elevation_m * METERS_TO_FEET, 0),
        "coordinates": coordinates,
    }


def main():
    # Find all numbered GPX files
    gpx_files = sorted(glob.glob(os.path.join(GPX_DIR, "10*.gpx")))

    tracks = []
    total_distance = 0
    total_elevation = 0

    for filepath in gpx_files:
        filename = os.path.basename(filepath)
        match = re.match(r"(\d+)\.gpx", filename)
        if not match:
            continue

        track_id = int(match.group(1))
        data = parse_gpx(filepath)
        if data is None:
            print(f"Warning: no track data in {filename}")
            continue

        data["id"] = track_id
        tracks.append(data)
        total_distance += data["distance_miles"]
        total_elevation += data["elevation_feet"]

    # Sort by date
    tracks.sort(key=lambda t: t["date"] or "")

    output = {
        "tracks": tracks,
        "summary": {
            "total_tracks": len(tracks),
            "total_distance_miles": round(total_distance, 2),
            "total_elevation_feet": round(total_elevation, 0),
        },
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f)

    print(f"Generated {OUTPUT_FILE}")
    print(f"  {len(tracks)} tracks, {round(total_distance, 1)} miles, {round(total_elevation, 0)} ft elevation")
    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"  File size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
