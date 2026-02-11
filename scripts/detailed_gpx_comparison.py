#!/usr/bin/env python3
"""
Detailed comparison of GPX files to understand differences.
"""

import xml.etree.ElementTree as ET
from datetime import datetime

def parse_gpx_detailed(filepath):
    """Parse GPX file and extract detailed information."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    # Get metadata
    metadata = {}
    metadata_elem = root.find('gpx:metadata', ns)
    if metadata_elem is not None:
        time_elem = metadata_elem.find('gpx:time', ns)
        if time_elem is not None:
            metadata['time'] = time_elem.text

    # Get track info
    track = {}
    trk = root.find('gpx:trk', ns)
    if trk is not None:
        name_elem = trk.find('gpx:name', ns)
        if name_elem is not None:
            track['name'] = name_elem.text
        type_elem = trk.find('gpx:type', ns)
        if type_elem is not None:
            track['type'] = type_elem.text

    # Get all track points with full detail
    track_points = []
    for trkpt in root.findall('.//gpx:trkpt', ns):
        point = {
            'lat': trkpt.get('lat'),
            'lon': trkpt.get('lon')
        }

        time_elem = trkpt.find('gpx:time', ns)
        if time_elem is not None:
            point['time'] = time_elem.text

        ele_elem = trkpt.find('gpx:ele', ns)
        if ele_elem is not None:
            point['ele'] = ele_elem.text

        track_points.append(point)

    return {
        'metadata': metadata,
        'track': track,
        'points': track_points
    }

def compare_gpx_files(file1, file2):
    """Compare two GPX files in detail."""
    print(f"\n{'='*80}")
    print(f"DETAILED COMPARISON")
    print(f"{'='*80}")
    print(f"\nFile 1: {file1}")
    print(f"File 2: {file2}")

    data1 = parse_gpx_detailed(file1)
    data2 = parse_gpx_detailed(file2)

    # Compare metadata
    print(f"\nMETADATA:")
    print(f"  File 1 time: {data1['metadata'].get('time', 'N/A')}")
    print(f"  File 2 time: {data2['metadata'].get('time', 'N/A')}")
    print(f"  Match: {'✓' if data1['metadata'].get('time') == data2['metadata'].get('time') else '✗'}")

    # Compare track info
    print(f"\nTRACK INFO:")
    print(f"  File 1 name: {data1['track'].get('name', 'N/A')}")
    print(f"  File 2 name: {data2['track'].get('name', 'N/A')}")
    print(f"  File 1 type: {data1['track'].get('type', 'N/A')}")
    print(f"  File 2 type: {data2['track'].get('type', 'N/A')}")

    # Compare track points
    points1 = data1['points']
    points2 = data2['points']

    print(f"\nTRACK POINTS:")
    print(f"  File 1 points: {len(points1)}")
    print(f"  File 2 points: {len(points2)}")
    print(f"  Count match: {'✓' if len(points1) == len(points2) else '✗'}")

    if len(points1) == len(points2):
        # Compare first few points
        print(f"\n  Comparing first 5 points:")
        differences = 0
        for i in range(min(5, len(points1))):
            p1 = points1[i]
            p2 = points2[i]

            lat_match = p1['lat'] == p2['lat']
            lon_match = p1['lon'] == p2['lon']
            time_match = p1.get('time') == p2.get('time')
            ele_match = p1.get('ele') == p2.get('ele')

            if not (lat_match and lon_match and time_match and ele_match):
                differences += 1
                print(f"\n  Point {i+1}:")
                if not lat_match:
                    print(f"    Lat: {p1['lat']} vs {p2['lat']}")
                if not lon_match:
                    print(f"    Lon: {p1['lon']} vs {p2['lon']}")
                if not time_match:
                    print(f"    Time: {p1.get('time')} vs {p2.get('time')}")
                if not ele_match:
                    print(f"    Elevation: {p1.get('ele')} vs {p2.get('ele')}")

        # Check all points for differences
        total_diffs = 0
        lat_diffs = 0
        lon_diffs = 0
        time_diffs = 0
        ele_diffs = 0

        for i in range(len(points1)):
            p1 = points1[i]
            p2 = points2[i]

            # Compare as floats for coordinates
            lat_match = abs(float(p1['lat']) - float(p2['lat'])) < 0.000001
            lon_match = abs(float(p1['lon']) - float(p2['lon'])) < 0.000001

            # Compare elevations with small tolerance
            ele_match = True
            if p1.get('ele') and p2.get('ele'):
                ele_match = abs(float(p1['ele']) - float(p2['ele'])) < 5.0  # 5 meter tolerance
            elif p1.get('ele') != p2.get('ele'):
                ele_match = False

            time_match = p1.get('time') == p2.get('time')

            if not lat_match:
                lat_diffs += 1
            if not lon_match:
                lon_diffs += 1
            if not time_match:
                time_diffs += 1
            if not ele_match:
                ele_diffs += 1

            if not (lat_match and lon_match and time_match and ele_match):
                total_diffs += 1

        print(f"\n  Total points with differences: {total_diffs}/{len(points1)}")
        if total_diffs > 0:
            print(f"    Latitude differences: {lat_diffs}")
            print(f"    Longitude differences: {lon_diffs}")
            print(f"    Time differences: {time_diffs}")
            print(f"    Elevation differences: {ele_diffs}")

        # Calculate percentage similarity
        similarity = ((len(points1) - total_diffs) / len(points1)) * 100
        print(f"\n  Similarity: {similarity:.2f}%")

        if similarity == 100:
            print(f"\n  ✓ Files are IDENTICAL")
        elif similarity >= 95:
            print(f"\n  ≈ Files are VERY SIMILAR (likely same ride with minor recording differences)")
        elif similarity >= 80:
            print(f"\n  ~ Files are SIMILAR (same start time but different route or recording)")
        else:
            print(f"\n  ✗ Files are DIFFERENT")

if __name__ == '__main__':
    # Example usage - update these paths as needed
    print("GPX Comparison Tool")
    print("All GPX files are now in: /var/www/phillongworth-site/data/gpx/activities")
    print("\nUsage: Update the pairs list below with files to compare")

    # Example pairs (currently empty - add files to compare)
    pairs = []

    if not pairs:
        print("\nNo file pairs specified for comparison.")
        print("Edit this script to add file pairs to compare.")
    else:
        for file1, file2 in pairs:
            compare_gpx_files(file1, file2)
