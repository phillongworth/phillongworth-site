"""
Enrich facey_fifty.json with lat/lon coordinates converted from OS grid references.
Outputs data/facey_fifty.json with added lat/lon fields.

Usage: py build_facey_data.py
"""

import json
import math
import os

# Go up one level from scripts/ to find data/
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "generated", "facey_fifty.json")
OUTPUT_FILE = INPUT_FILE  # overwrite in place


def os_grid_to_easting_northing(grid_ref):
    """Convert OS grid reference like 'SE 119 157' to easting/northing in metres."""
    grid_ref = grid_ref.strip().upper().replace(" ", "")

    # First letter -> 500km square
    first_letter_map = {"S": (0, 0), "T": (500000, 0), "N": (0, 500000),
                        "O": (500000, 500000), "H": (0, 1000000)}
    # Second letter -> 100km offset within square
    # Grid: V W X Y Z (row 0), Q R S T U (row 1), L M N O P (row 2),
    #        F G H J K (row 3), A B C D E (row 4)
    second_letters = "VWXYZQRSTULMNOPFGHJKABCDE"

    letter1 = grid_ref[0]
    letter2 = grid_ref[1]
    digits = grid_ref[2:]

    e0, n0 = first_letter_map[letter1]

    idx = second_letters.index(letter2)
    col = idx % 5
    row = idx // 5
    e0 += col * 100000
    n0 += row * 100000

    half = len(digits) // 2
    e_digits = digits[:half]
    n_digits = digits[half:]

    # Scale to metres (3 digits = 100m, 4 digits = 10m, etc.)
    scale = 10 ** (5 - half)
    easting = e0 + int(e_digits) * scale
    northing = n0 + int(n_digits) * scale

    return easting, northing


def osgb36_to_wgs84(easting, northing):
    """Convert OSGB36 easting/northing to WGS84 lat/lon.
    Uses the standard reverse Transverse Mercator + Helmert transform."""

    # Airy 1830 ellipsoid (OSGB36)
    a = 6377563.396
    b = 6356256.909
    e2 = 1 - (b * b) / (a * a)
    n = (a - b) / (a + b)

    # National Grid origin
    F0 = 0.9996012717
    phi0 = math.radians(49.0)
    lam0 = math.radians(-2.0)
    N0 = -100000.0
    E0 = 400000.0

    # Reverse TM projection to get OSGB36 lat/lon
    phi = phi0
    M = 0
    while True:
        phi = (northing - N0 - M) / (a * F0) + phi
        M = b * F0 * (
            (1 + n + 1.25 * n**2 + 1.25 * n**3) * (phi - phi0) -
            (3 * n + 3 * n**2 + 21.0/8 * n**3) * math.sin(phi - phi0) * math.cos(phi + phi0) +
            (15.0/8 * n**2 + 15.0/8 * n**3) * math.sin(2 * (phi - phi0)) * math.cos(2 * (phi + phi0)) -
            (35.0/24 * n**3) * math.sin(3 * (phi - phi0)) * math.cos(3 * (phi + phi0))
        )
        if abs(northing - N0 - M) < 0.00001:
            break

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    tan_phi = math.tan(phi)

    nu = a * F0 / math.sqrt(1 - e2 * sin_phi**2)
    rho = a * F0 * (1 - e2) / (1 - e2 * sin_phi**2)**1.5
    eta2 = nu / rho - 1

    VII = tan_phi / (2 * rho * nu)
    VIII = tan_phi / (24 * rho * nu**3) * (5 + 3 * tan_phi**2 + eta2 - 9 * tan_phi**2 * eta2)
    IX = tan_phi / (720 * rho * nu**5) * (61 + 90 * tan_phi**2 + 45 * tan_phi**4)
    X = 1 / (cos_phi * nu)
    XI = 1 / (cos_phi * 6 * nu**3) * (nu / rho + 2 * tan_phi**2)
    XII = 1 / (cos_phi * 120 * nu**5) * (5 + 28 * tan_phi**2 + 24 * tan_phi**4)
    XIIA = 1 / (cos_phi * 5040 * nu**7) * (61 + 662 * tan_phi**2 + 1320 * tan_phi**4 + 720 * tan_phi**6)

    dE = easting - E0
    osgb_lat = phi - VII * dE**2 + VIII * dE**4 - IX * dE**6
    osgb_lon = lam0 + X * dE - XI * dE**3 + XII * dE**5 - XIIA * dE**7

    # Helmert transform OSGB36 -> WGS84
    # Convert to cartesian
    a_osgb = 6377563.396
    b_osgb = 6356256.909
    e2_osgb = 1 - (b_osgb**2) / (a_osgb**2)

    sin_lat = math.sin(osgb_lat)
    cos_lat = math.cos(osgb_lat)
    sin_lon = math.sin(osgb_lon)
    cos_lon = math.cos(osgb_lon)

    nu_osgb = a_osgb / math.sqrt(1 - e2_osgb * sin_lat**2)
    x1 = nu_osgb * cos_lat * cos_lon
    y1 = nu_osgb * cos_lat * sin_lon
    z1 = nu_osgb * (1 - e2_osgb) * sin_lat

    # Helmert parameters (OSGB36 -> WGS84)
    tx = 446.448
    ty = -125.157
    tz = 542.060
    s = -20.4894e-6
    rx = math.radians(0.1502 / 3600)
    ry = math.radians(0.2470 / 3600)
    rz = math.radians(0.8421 / 3600)

    x2 = tx + (1 + s) * x1 + (-rz) * y1 + ry * z1
    y2 = ty + rz * x1 + (1 + s) * y1 + (-rx) * z1
    z2 = tz + (-ry) * x1 + rx * y1 + (1 + s) * z1

    # Convert back to geodetic (WGS84)
    a_wgs = 6378137.0
    b_wgs = 6356752.3142
    e2_wgs = 1 - (b_wgs**2) / (a_wgs**2)

    lon = math.atan2(y2, x2)
    p = math.sqrt(x2**2 + y2**2)
    lat = math.atan2(z2, p * (1 - e2_wgs))

    for _ in range(10):
        nu_wgs = a_wgs / math.sqrt(1 - e2_wgs * math.sin(lat)**2)
        lat = math.atan2(z2 + e2_wgs * nu_wgs * math.sin(lat), p)

    return round(math.degrees(lat), 5), round(math.degrees(lon), 5)


def main():
    with open(INPUT_FILE) as f:
        data = json.load(f)

    for climb in data["climbs"]:
        grid_ref = climb.get("map_reference")
        if grid_ref:
            try:
                e, n = os_grid_to_easting_northing(grid_ref)
                lat, lon = osgb36_to_wgs84(e, n)
                climb["lat"] = lat
                climb["lon"] = lon
            except Exception as ex:
                print(f"Warning: could not convert grid ref '{grid_ref}' for climb {climb['number']}: {ex}")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    converted = sum(1 for c in data["climbs"] if "lat" in c)
    print(f"Enriched {converted}/{len(data['climbs'])} climbs with lat/lon")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
