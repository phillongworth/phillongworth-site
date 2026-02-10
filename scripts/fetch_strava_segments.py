"""
Fetch Strava segment polylines and details for the Facey Fifty climbs.

Requires a Strava API access token. To get one:
1. Go to https://www.strava.com/settings/api and create an app
2. Use the OAuth flow or get a token from https://www.strava.com/settings/api
   (the "Your Access Token" shown on that page works for read-only access)

Usage: py fetch_strava_segments.py <ACCESS_TOKEN>
"""

import json
import math
import os
import sys
import time
import urllib.request

# Go up one level from scripts/ to find data/
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "generated", "facey_fifty.json")
OUTPUT_FILE = INPUT_FILE


def decode_polyline(encoded):
    """Decode a Google encoded polyline string into a list of [lat, lng] pairs."""
    points = []
    index = 0
    lat = 0
    lng = 0

    while index < len(encoded):
        # Decode latitude
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lat += (~(result >> 1) if (result & 1) else (result >> 1))

        # Decode longitude
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lng += (~(result >> 1) if (result & 1) else (result >> 1))

        points.append([round(lat / 1e5, 5), round(lng / 1e5, 5)])

    return points


def fetch_segment(segment_id, token):
    """Fetch segment details from Strava API."""
    url = f"https://www.strava.com/api/v3/segments/{segment_id}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    if len(sys.argv) < 2:
        print("Usage: py fetch_strava_segments.py <STRAVA_ACCESS_TOKEN>")
        print()
        print("To get a token:")
        print("  1. Go to https://www.strava.com/settings/api")
        print("  2. Create an app (or use existing)")
        print("  3. Copy 'Your Access Token' from that page")
        sys.exit(1)

    token = sys.argv[1]

    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    updated = 0
    errors = 0

    for climb in data["climbs"]:
        segments = climb.get("strava_segments", [])
        if not segments:
            continue

        seg_id = segments[0]["segment_id"]
        print(f"Fetching segment {seg_id} for #{climb['number']} {climb['name']}...")

        try:
            seg_data = fetch_segment(seg_id, token)

            # Decode the polyline to get route coordinates
            polyline = seg_data.get("map", {}).get("polyline")
            if polyline:
                track = decode_polyline(polyline)
                climb["track"] = track
                print(f"  -> {len(track)} points")
            else:
                print("  -> no polyline available")

            # Update distance/elevation from Strava if we don't already have it
            if "distance_miles" not in climb and "distance" in seg_data:
                climb["distance_miles"] = round(seg_data["distance"] * 0.000621371, 2)
            if "elevation_feet" not in climb and "total_elevation_gain" in seg_data:
                climb["elevation_feet"] = round(seg_data["total_elevation_gain"] * 3.28084)
            if "average_gradient_pct" not in climb and "average_grade" in seg_data:
                climb["average_gradient_pct"] = seg_data["average_grade"]

            # Use Strava's start coordinates if we don't have lat/lon
            if "lat" not in climb and "start_latlng" in seg_data:
                latlng = seg_data["start_latlng"]
                if latlng and len(latlng) == 2:
                    climb["lat"] = round(latlng[0], 5)
                    climb["lon"] = round(latlng[1], 5)

            updated += 1

        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("  ERROR: Unauthorized - check your access token")
                print("  Token may have expired. Get a new one from https://www.strava.com/settings/api")
                sys.exit(1)
            elif e.code == 429:
                print("  Rate limited - waiting 60 seconds...")
                time.sleep(60)
                continue
            else:
                print(f"  ERROR: HTTP {e.code}")
                errors += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

        time.sleep(1)  # Rate limit: stay well under 100 requests per 15 minutes

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\nDone. Updated {updated}/50 climbs ({errors} errors)")
    print(f"Written to {OUTPUT_FILE} ({file_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
