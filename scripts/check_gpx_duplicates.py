#!/usr/bin/env python3
"""
Check for duplicate GPX files based on track data rather than filenames.
"""

import xml.etree.ElementTree as ET
import hashlib
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def parse_gpx_file(filepath):
    """Extract key data from a GPX file for comparison."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        # Handle namespace
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

        # Extract metadata time
        metadata_time = None
        metadata = root.find('gpx:metadata', ns)
        if metadata is not None:
            time_elem = metadata.find('gpx:time', ns)
            if time_elem is not None:
                metadata_time = time_elem.text

        # Extract all track points
        track_points = []
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = trkpt.get('lat')
            lon = trkpt.get('lon')

            time_elem = trkpt.find('gpx:time', ns)
            time = time_elem.text if time_elem is not None else None

            ele_elem = trkpt.find('gpx:ele', ns)
            ele = ele_elem.text if ele_elem is not None else None

            track_points.append((lat, lon, time, ele))

        # Get track name
        track_name = None
        name_elem = root.find('.//gpx:trk/gpx:name', ns)
        if name_elem is not None:
            track_name = name_elem.text

        return {
            'metadata_time': metadata_time,
            'track_name': track_name,
            'track_points': track_points,
            'num_points': len(track_points),
            'filepath': filepath
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None

def create_track_hash(track_points):
    """Create a hash from track points (ignoring small variations)."""
    # Use first and last 10 points, plus every 10th point for efficiency
    sample_points = []

    if len(track_points) > 0:
        # First 10 points
        sample_points.extend(track_points[:10])
        # Last 10 points
        sample_points.extend(track_points[-10:])
        # Every 10th point
        sample_points.extend(track_points[::10])

    # Create hash from lat/lon/time data
    hash_str = ''.join([f"{pt[0]},{pt[1]},{pt[2]}" for pt in sample_points])
    return hashlib.md5(hash_str.encode()).hexdigest()

def find_duplicates(gpx_directories):
    """Find duplicate GPX files based on track data."""
    if isinstance(gpx_directories, str):
        gpx_directories = [gpx_directories]

    # Parse all files from all directories
    gpx_data = []
    for gpx_directory in gpx_directories:
        print(f"Scanning GPX files in {gpx_directory}...")
        gpx_files = list(Path(gpx_directory).glob('*.gpx'))
        print(f"Found {len(gpx_files)} GPX files in {os.path.basename(gpx_directory)}\n")

        for gpx_file in gpx_files:
            data = parse_gpx_file(gpx_file)
            if data:
                # Add directory info
                data['directory'] = os.path.basename(gpx_directory)
                gpx_data.append(data)

    print(f"Successfully parsed {len(gpx_data)} total files\n")

    # Group by different criteria
    by_time_hash = defaultdict(list)
    by_track_hash = defaultdict(list)
    by_exact_match = defaultdict(list)

    for data in gpx_data:
        # Group by metadata time (exact duplicates likely)
        if data['metadata_time']:
            by_time_hash[data['metadata_time']].append(data)

        # Group by track point hash
        track_hash = create_track_hash(data['track_points'])
        by_track_hash[track_hash].append(data)

        # Group by exact track point match
        track_signature = str(data['track_points'])
        exact_hash = hashlib.md5(track_signature.encode()).hexdigest()
        by_exact_match[exact_hash].append(data)

    # Report findings
    print("=" * 80)
    print("DUPLICATE DETECTION RESULTS")
    print("=" * 80)

    print("\n1. EXACT DUPLICATES (identical track data):")
    print("-" * 80)
    exact_dups = {k: v for k, v in by_exact_match.items() if len(v) > 1}
    if exact_dups:
        for hash_val, files in exact_dups.items():
            print(f"\nGroup (hash: {hash_val[:8]}...):")
            print(f"  Metadata time: {files[0]['metadata_time']}")
            print(f"  Track points: {files[0]['num_points']}")
            print(f"  Files:")
            for f in files:
                dir_label = f['directory']
                print(f"    - {dir_label}/{os.path.basename(f['filepath'])}")
    else:
        print("  No exact duplicates found")

    print("\n\n2. SAME START TIME (likely duplicates):")
    print("-" * 80)
    time_dups = {k: v for k, v in by_time_hash.items() if len(v) > 1}
    if time_dups:
        for time, files in time_dups.items():
            print(f"\nStart time: {time}")
            print(f"  Files ({len(files)}):")
            for f in files:
                dir_label = f['directory']
                print(f"    - {dir_label}/{os.path.basename(f['filepath'])} ({f['num_points']} points)")
    else:
        print("  No files with same start time found")

    print("\n\n3. SIMILAR TRACKS (same route with minor variations):")
    print("-" * 80)
    track_dups = {k: v for k, v in by_track_hash.items() if len(v) > 1}
    if track_dups:
        for hash_val, files in track_dups.items():
            # Exclude if already reported as exact duplicates
            if len(set(f['filepath'] for f in files)) > 1:
                print(f"\nSimilar track group (hash: {hash_val[:8]}...):")
                print(f"  Files ({len(files)}):")
                for f in files:
                    dir_label = f['directory']
                    print(f"    - {dir_label}/{os.path.basename(f['filepath'])}")
                    print(f"      Time: {f['metadata_time']}, Points: {f['num_points']}")
    else:
        print("  No similar tracks found")

    print("\n" + "=" * 80)
    print(f"\nSummary:")
    print(f"  Total files scanned: {len(gpx_data)}")
    print(f"  Exact duplicate groups: {len(exact_dups)}")
    print(f"  Same start time groups: {len(time_dups)}")
    print(f"  Similar track groups: {len(track_dups)}")
    print("=" * 80)

if __name__ == '__main__':
    gpx_dir = '/var/www/phillongworth-site/data/gpx/activities'
    find_duplicates(gpx_dir)
