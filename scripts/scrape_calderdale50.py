"""
Scrape the Calderdale 50 website to build a JSON file of all climbs.
Extracts: name, area, distance, ascent, plotaroute link.
"""

import urllib.request
import html as html_mod
import re
import json
import time

MAIN_50 = [
    ("Cornholme", "carr-road"),
    ("Cornholme", "cornholme-to-kebs"),
    ("Greetland", "cote-de-greetland"),
    ("Greetland", "holywell-green"),
    ("Greetland", "jagger-green-lane"),
    ("Greetland", "saddleworth-road"),
    ("Halifax", "salterhebble-to-southowram"),
    ("Halifax", "southowram-bank"),
    ("Halifax", "trooper-lane"),
    ("Halifax", "washer-lane"),
    ("Halifax", "wood-lane-and-gibb-lane"),
    ("Hebden Bridge", "birchcliffe"),
    ("Hebden Bridge", "horsehold"),
    ("Hebden Bridge", "mytholm-steeps"),
    ("Hebden Bridge", "the-fox-and-goose-to-slack-bottom"),
    ("Hebden Bridge", "the-white-lion-to-cock-hill"),
    ("Hebden Bridge", "up-the-buttress"),
    ("Luddenden", "bank-house-lane"),
    ("Luddenden", "danny-lane"),
    ("Luddenden", "halifax-lane"),
    ("Luddenden", "halifax-sailing-club"),
    ("Luddenden", "luddenden-foot-to-sykes-gate"),
    ("Luddenden", "midgley-and-height-road"),
    ("Mytholmroyd", "cragg-vale"),
    ("Mytholmroyd", "hinchliffe-arms-to-bell-house-moor"),
    ("Mytholmroyd", "midgley-road"),
    ("Ripponden", "butterworth-lane"),
    ("Ripponden", "cote-de-ripponden"),
    ("Ripponden", "oldham-road"),
    ("Ripponden", "rishworth-mill-lane"),
    ("Ripponden", "stony-lane"),
    ("Shibden", "norcliffe-lane"),
    ("Shibden", "shibden-wall"),
    ("Shibden", "the-hough"),
    ("Sowerby Bridge", "sowerby-bridge-to-blackstone-edge"),
    ("Sowerby Bridge", "sowerby-bridge-to-norland-moor"),
    ("Sowerby Bridge", "sowerby-bridge-to-sowerby"),
    ("Sowerby Bridge", "take-it-from-the-tip"),
    ("Stainland", "barkisland"),
    ("Stainland", "ride-number-4"),
    ("Stainland", "stainland-moor"),
    ("The Far East", "brookfoot-to-southowram"),
    ("The Far East", "toot-hill"),
    ("Todmorden", "doghouse-lane"),
    ("Todmorden", "the-shepherds-rest"),
    ("Todmorden", "todmorden-to-blackshaw-head"),
    ("Todmorden", "todmorden-to-bride-stones"),
    ("Walsden", "foul-clough"),
    ("Walsden", "hollingworth-farms"),
    ("Walsden", "the-road-to-lancashire"),
]

OTHERS = [
    "birdcage-hill",
    "clough-foot-to-flower-scar",
    "eastwood-to-mankinholes",
    "luddenden-foot-to-sowerby",
    "ploughcroft-lane",
    "rochdale-road",
    "shoulder-of-mutton-to-hathershelf-lane",
    "sonoco-mill-to-stainland",
    "windy-bank",
]


def fetch_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        # Try UTF-8 first, fall back to latin-1
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return raw.decode("latin-1")


def extract_title(html):
    """Extract page title from WordPress entry-title or <title>."""
    m = re.search(r'<h1[^>]*class="entry-title"[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    if not m:
        m = re.search(r"<title>(.*?)[\s\|<]", html, re.IGNORECASE)
    if m:
        return html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    return None


def extract_climb_data(html):
    """Extract distance, ascent, plotaroute from page HTML."""
    data = {}

    # Distance/Ascent from "Distance: X metres, Ascent: Y metres" pattern
    dist_match = re.search(r"Distance:\s*([\d,]+)\s*metres", html, re.IGNORECASE)
    if dist_match:
        metres = int(dist_match.group(1).replace(",", ""))
        data["distance_metres"] = metres
        data["distance_miles"] = round(metres * 0.000621371, 2)

    ascent_match = re.search(r"Ascent:\s*([\d,]+)\s*metres", html, re.IGNORECASE)
    if ascent_match:
        metres = int(ascent_match.group(1).replace(",", ""))
        data["ascent_metres"] = metres
        data["ascent_feet"] = round(metres * 3.28084)

    # Calculate gradient if both available
    if "distance_metres" in data and "ascent_metres" in data and data["distance_metres"] > 0:
        data["average_gradient_pct"] = round(
            (data["ascent_metres"] / data["distance_metres"]) * 100, 1
        )

    # Plotaroute link
    plot_match = re.search(r"plotaroute\.com/route/(\d+)", html)
    if plot_match:
        data["plotaroute_id"] = plot_match.group(1)
        data["plotaroute_url"] = f"https://www.plotaroute.com/route/{plot_match.group(1)}"

    return data


def fetch_plotaroute_coords(route_id):
    """Fetch exact lat/lon from plotaroute hidden input fields."""
    url = f"https://www.plotaroute.com/route/{route_id}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        try:
            page = raw.decode("utf-8")
        except UnicodeDecodeError:
            page = raw.decode("latin-1")

    lat_match = re.search(r'id="Lat"[^>]*value="([^"]+)"', page)
    lng_match = re.search(r'id="Lng"[^>]*value="([^"]+)"', page)

    if lat_match and lng_match:
        return round(float(lat_match.group(1)), 5), round(float(lng_match.group(1)), 5)
    return None, None


def main():
    climbs = []

    # Scrape main 50
    for i, (area, slug) in enumerate(MAIN_50):
        number = i + 1
        url = f"https://calderdale50.wordpress.com/50-climbs/{area.lower().replace(' ', '-')}/{slug}/"
        print(f"Fetching {number}/50: {slug}")

        try:
            html = fetch_page(url)
            data = extract_climb_data(html)
            title = extract_title(html)
            data["number"] = number
            data["name"] = title or slug.replace("-", " ").title()
            data["area"] = area
            data["category"] = "main"
            data["url"] = url
            # Fetch exact coords from plotaroute
            if "plotaroute_id" in data:
                try:
                    lat, lon = fetch_plotaroute_coords(data["plotaroute_id"])
                    if lat and lon:
                        data["lat"] = lat
                        data["lon"] = lon
                except Exception as pe:
                    print(f"  plotaroute coords error: {pe}")

            climbs.append(data)
            print(f"  -> {data['name']}, {data.get('distance_miles', '?')} mi, {data.get('ascent_feet', '?')} ft, coords: {data.get('lat', '?')}")
        except Exception as e:
            print(f"  ERROR: {e}")
            climbs.append({"number": number, "name": slug.replace("-", " ").title(), "area": area, "category": "main", "error": str(e)})

        time.sleep(0.5)

    # Scrape 'the others'
    for i, slug in enumerate(OTHERS):
        number = 51 + i
        url = f"https://calderdale50.wordpress.com/the-others/{slug}/"
        print(f"Fetching other {i+1}/{len(OTHERS)}: {slug}")

        try:
            html = fetch_page(url)
            data = extract_climb_data(html)
            title = extract_title(html)
            data["number"] = number
            data["name"] = title or slug.replace("-", " ").title()
            data["category"] = "other"
            data["url"] = url
            climbs.append(data)
            print(f"  -> {data['name']}, {data.get('distance_miles', '?')} mi")
        except Exception as e:
            print(f"  ERROR: {e}")
            climbs.append({"number": number, "name": slug.replace("-", " ").title(), "category": "other", "error": str(e)})

        time.sleep(0.5)

    output_path = "w:\\phillongworth-site\\data\\calderdale50.json"
    with open(output_path, "w") as f:
        json.dump({"climbs": climbs}, f, indent=2)

    main_count = sum(1 for c in climbs if c.get("category") == "main")
    other_count = sum(1 for c in climbs if c.get("category") == "other")
    print(f"\nDone. Wrote {len(climbs)} climbs ({main_count} main + {other_count} others) to {output_path}")


if __name__ == "__main__":
    main()
