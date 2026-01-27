"""
Build script to process GPX files into a single tracks.json for the 1000-miles map.

Reads all numbered GPX files (10*.gpx) from data/, extracts coordinates,
calculates distance/elevation, simplifies tracks, and outputs data/tracks.json.

Usage: python build_map_data.py
"""

import xml.etree.ElementTree as ET
import json
import math
import glob
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "tracks.json")

GPX_NS = "http://www.topografix.com/GPX/1/1"
KM_TO_MILES = 0.621371
METERS_TO_FEET = 3.28084
SIMPLIFY_TOLERANCE = 0.0002  # ~20m in degrees, adjust for desired detail


def haversine(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lon points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def perpendicular_distance(point, line_start, line_end):
    """Distance from a point to a line segment (in coordinate space)."""
    dx = line_end[0] - line_start[0]
    dy = line_end[1] - line_start[1]
    if dx == 0 and dy == 0:
        return math.hypot(point[0] - line_start[0], point[1] - line_start[1])
    t = ((point[0] - line_start[0]) * dx + (point[1] - line_start[1]) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    proj_x = line_start[0] + t * dx
    proj_y = line_start[1] + t * dy
    return math.hypot(point[0] - proj_x, point[1] - proj_y)


def douglas_peucker(points, tolerance):
    """Simplify a polyline using the Douglas-Peucker algorithm."""
    if len(points) <= 2:
        return points

    max_dist = 0
    max_idx = 0
    for i in range(1, len(points) - 1):
        d = perpendicular_distance(points[i], points[0], points[-1])
        if d > max_dist:
            max_dist = d
            max_idx = i

    if max_dist > tolerance:
        left = douglas_peucker(points[:max_idx + 1], tolerance)
        right = douglas_peucker(points[max_idx:], tolerance)
        return left[:-1] + right
    else:
        return [points[0], points[-1]]


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
        ele = float(ele_el.text) if ele_el is not None else None

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
    gpx_files = sorted(glob.glob(os.path.join(DATA_DIR, "10*.gpx")))

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
