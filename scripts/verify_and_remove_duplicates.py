#!/usr/bin/env python3
"""
Verify exact duplicates and provide options to remove them.
"""

import xml.etree.ElementTree as ET
import os
import hashlib

def get_file_hash(filepath):
    """Get MD5 hash of entire file content."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_track_data_hash(filepath):
    """Get hash of just the track point data."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}

    track_points = []
    for trkpt in root.findall('.//gpx:trkpt', ns):
        lat = trkpt.get('lat')
        lon = trkpt.get('lon')
        time_elem = trkpt.find('gpx:time', ns)
        time = time_elem.text if time_elem is not None else None
        track_points.append(f"{lat},{lon},{time}")

    return hashlib.md5(''.join(track_points).encode()).hexdigest()

def verify_duplicates():
    """Verify the identified duplicate pairs."""
    # All files are now in /var/www/phillongworth-site/data/gpx/activities
    # Update this list with any new duplicate pairs found
    duplicate_pairs = []

    print("=" * 80)
    print("VERIFYING DUPLICATES")
    print("=" * 80)

    verified_dups = []

    for file1, file2 in duplicate_pairs:
        print(f"\nComparing:")
        print(f"  File 1: {os.path.basename(file1)}")
        print(f"  File 2: {os.path.basename(file2)}")

        # Check if files exist
        if not os.path.exists(file1):
            print(f"  ❌ File 1 not found!")
            continue
        if not os.path.exists(file2):
            print(f"  ❌ File 2 not found!")
            continue

        # Compare file hashes
        hash1_full = get_file_hash(file1)
        hash2_full = get_file_hash(file2)

        # Compare track data hashes
        hash1_track = get_track_data_hash(file1)
        hash2_track = get_track_data_hash(file2)

        # Get file sizes
        size1 = os.path.getsize(file1)
        size2 = os.path.getsize(file2)

        print(f"  File sizes: {size1:,} bytes vs {size2:,} bytes")
        print(f"  Full file hash match: {'✓ YES' if hash1_full == hash2_full else '✗ NO'}")
        print(f"  Track data hash match: {'✓ YES' if hash1_track == hash2_track else '✗ NO'}")

        if hash1_track == hash2_track:
            print(f"  Status: ✓ EXACT DUPLICATE (same track data)")
            verified_dups.append((file1, file2))
        elif hash1_full == hash2_full:
            print(f"  Status: ✓ IDENTICAL FILES")
            verified_dups.append((file1, file2))
        else:
            print(f"  Status: ✗ NOT DUPLICATES")

    print("\n" + "=" * 80)
    print(f"\nVerified duplicates: {len(verified_dups)} pairs")
    print("=" * 80)

    return verified_dups

def remove_duplicates(verified_dups, remove_from='1000-miles'):
    """Remove duplicate files from specified directory."""
    print("\n" + "=" * 80)
    print(f"REMOVING DUPLICATES FROM {remove_from} DIRECTORY")
    print("=" * 80)

    removed = []
    for file1, file2 in verified_dups:
        # Determine which file to remove
        if remove_from == '1000-miles' and '1000-miles' in file2:
            to_remove = file2
            to_keep = file1
        elif remove_from == 'activities' and 'activities' in file1:
            to_remove = file1
            to_keep = file2
        else:
            continue

        print(f"\n  Keeping: {os.path.basename(to_keep)}")
        print(f"  Removing: {os.path.basename(to_remove)}")

        try:
            os.remove(to_remove)
            print(f"  ✓ Removed successfully")
            removed.append(to_remove)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    print("\n" + "=" * 80)
    print(f"Removed {len(removed)} duplicate files")
    print("=" * 80)

    return removed

if __name__ == '__main__':
    import sys

    # Verify duplicates
    verified = verify_duplicates()

    # Ask for confirmation before removing
    if verified:
        print("\n" + "=" * 80)
        print("REMOVAL OPTIONS")
        print("=" * 80)
        print("\nWhich files should be removed?")
        print("  1. Remove from 1000-miles directory (keep activities)")
        print("  2. Remove from activities directory (keep 1000-miles)")
        print("  3. Do not remove (verification only)")

        if len(sys.argv) > 1:
            choice = sys.argv[1]
        else:
            print("\nUsage: python3 verify_and_remove_duplicates.py [1|2|3]")
            print("Or run interactively and enter choice:")
            choice = input("\nEnter choice (1-3): ").strip()

        if choice == '1':
            remove_duplicates(verified, '1000-miles')
        elif choice == '2':
            remove_duplicates(verified, 'activities')
        elif choice == '3':
            print("\nNo files removed (verification only)")
        else:
            print("\nInvalid choice. No files removed.")
    else:
        print("\nNo verified duplicates to remove.")
