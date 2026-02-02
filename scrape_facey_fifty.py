"""
Scrape the Facey Fifty website to build a JSON file of all 50 climbs.
Extracts: name, number, stats, Strava segment URLs, VeloViewer URLs.
"""

import urllib.request
import html as html_mod
import re
import json
import time

BASE = "http://www.facey-fifty.uk"

CLIMB_URLS = [
    "/climbs/01-Deep-Lane.html",
    "/climbs/02-Scar-Lane.html",
    "/climbs/03-Cowersley-Lane.html",
    "/climbs/04-Hoyle-Ing-&-Tommy-Lane.html",
    "/climbs/05-Lowestwood-Lane,-Linthwaite-Copley-Bank,-Bolster-Moor.html",
    "/climbs/06-Hoyle-House-Causeway-Side.html",
    "/climbs/07-Chapel-Hill-Stones-Lane-Upper-Clough.html",
    "/climbs/08-Linfit-lane-High-House-Edge.html",
    "/climbs/09-Varley-Road.html",
    "/climbs/10.html",
    "/climbs/11-Lingards-Road,-Slaithwaite.html",
    "/climbs/12-Clough-Road-Slaithwaite-Gate,-Slaithwaite.html",
    "/climbs/13-Meal-Hill-Lane,-Slaithwaite.html",
    "/climbs/14-Bank-Gate-Longlands-Rd-Heys-Lane-Tiding-Fields-Ln-Pole-Gate,-Slaitwaite-to-Scammonden.html",
    "/climbs/15-Holme-Lane,-SLaithwaite.html",
    "/climbs/16-White-Hill-Shaw-Field-Lane,-West-Slaithwaite.html",
    "/climbs/17-Marsden-Lane,-West-Slaithwaite.html",
    "/climbs/18-Mount-Road,-Marsden.html",
    "/climbs/19-Old-Mount-Road,-Marsden.html",
    "/climbs/20-Manchester-Road,-Marsden.html",
    "/climbs/21-Lockwood-Scar-Jackroyd-Lane,-Lockwood-to-Castle-Hill.html",
    "/climbs/22-Lady-House-Lane,-Berry-Brow.html",
    "/climbs/23-Robin-Hood-Hill-Park-Lane,-Berry-Brow.html",
    "/climbs/24-Station-Road-Northgate,-Honley.html",
    "/climbs/25-Gynn-Lane-Hall-Ing-Lane,-Honley.html",
    "/climbs/26-Brockholes-Lane,-Brockholes.html",
    "/climbs/27-Thurstonland-Bank,-Thurstonland.html",
    "/climbs/28-Cold-Hill-Lane-Halstead-Lane,-New-Mill.html",
    "/climbs/29-Sude-Hill-Horn-Lane,-New-Mill.html",
    "/climbs/30-Penistone-Road-A635,-New-Mill.html",
    "/climbs/31-Sheffield-Road,-New-Mill.html",
    "/climbs/32-V9912-Jackson-Bridge-Hill-Climb,-South-View-Staley-Royd-Lane,-Jackson-Bridge.html",
    "/climbs/33-Butt-Lane-Dean-Lane,-Jackson-Bridge-to-Flight-Hill.html",
    "/climbs/34-Thong-Lane-Giles-Lane-Miry-Lane,-Netherthong.html",
    "/climbs/35-South-Lane-Cinderhills-Rd,-Holmfirth.html",
    "/climbs/36-Dunford-Road,-Holmfirth.html",
    "/climbs/37-Rotcher-Road-Cemetery-Road-National-Cycle-route-68.html",
    "/climbs/38-Upperthong-Lane,-Holmfirth.html",
    "/climbs/39-Greenfield-Road,-A635-Holmfirth.html",
    "/climbs/40-Woodside-View-Shaw-Lane-Booth-House-Lane,-Burnlee,-Holmfirth.html",
    "/climbs/41-Yew-Tree-Lane-Flush-House-Lane,-Burnlee.html",
    "/climbs/42-Dobb-Lane-Woodhouse-Lane,-Hinchliffe-Mill.html",
    "/climbs/43-Field-End-Lane,-via-Digley-reservoir,-Holmbridge.html",
    "/climbs/44-Holme-Moss,-Holmbridge.html",
    "/climbs/45-Bradshaw-Road,-Honley.html",
    "/climbs/46-Knowle-Lane,-Meltham-Mills.html",
    "/climbs/47-Acre-Lane-Thick-Hollins-Road,-Meltham-Mills.html",
    "/climbs/48-Wessenden-Head-Road,-Meltham.html",
    "/climbs/49-Slaithwaite-Road,-Meltham.html",
    "/climbs/50-Meltham-Road-Church-Lane,-Netherton.html",
]


def fetch_page(url):
    """Fetch raw HTML from a URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_climb_data(html, number):
    """Extract climb data from raw HTML."""
    data = {"number": number}

    # Title - look for h1 or h2 with climb name
    title_match = re.search(r"<h[12][^>]*>(.*?)</h[12]>", html, re.DOTALL | re.IGNORECASE)
    if title_match:
        # Strip HTML tags from title
        data["name"] = html_mod.unescape(re.sub(r"<[^>]+>", "", title_match.group(1)).strip())

    # Strava segment URLs from iframes
    strava_iframes = re.findall(r'src=["\']([^"\']*strava\.com[^"\']*)["\']', html, re.IGNORECASE)
    strava_segments = []
    for url in strava_iframes:
        seg_match = re.search(r"segments/(\d+)", url)
        if seg_match:
            seg_id = seg_match.group(1)
            strava_segments.append({
                "segment_id": seg_id,
                "url": f"https://www.strava.com/segments/{seg_id}",
            })
    if strava_segments:
        data["strava_segments"] = strava_segments

    # VeloViewer URLs from iframes or links
    vv_urls = re.findall(r'(?:src|href)=["\']([^"\']*veloviewer\.com[^"\']*)["\']', html, re.IGNORECASE)
    if vv_urls:
        data["veloviewer_urls"] = list(set(vv_urls))

    # Extract structured data from dt/dd pairs
    dt_dd_pairs = re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", html, re.DOTALL | re.IGNORECASE)
    for dt, dd in dt_dd_pairs:
        dt_clean = html_mod.unescape(re.sub(r"<[^>]+>", "", dt)).strip().lower()
        dd_clean = html_mod.unescape(re.sub(r"<[^>]+>", "", dd)).strip()

        if "distance" in dt_clean:
            m = re.search(r"([\d.]+)", dd_clean)
            if m:
                data["distance_miles"] = float(m.group(1))
        elif "ascent" in dt_clean or "elevation" in dt_clean:
            m = re.search(r"([\d,]+)", dd_clean)
            if m:
                data["elevation_feet"] = int(m.group(1).replace(",", ""))
        elif "gradient" in dt_clean:
            m = re.search(r"([\d.]+)", dd_clean)
            if m:
                data["average_gradient_pct"] = float(m.group(1))
        elif "map" in dt_clean and "ref" in dt_clean:
            data["map_reference"] = dd_clean

    return data


def main():
    climbs = []

    for i, path in enumerate(CLIMB_URLS):
        number = i + 1
        url = BASE + path
        print(f"Fetching climb {number}/50: {url}")

        try:
            html = fetch_page(url)
            data = extract_climb_data(html, number)
            climbs.append(data)
            print(f"  -> {data.get('name', 'Unknown')}, strava: {len(data.get('strava_segments', []))}")
        except Exception as e:
            print(f"  ERROR: {e}")
            climbs.append({"number": number, "error": str(e)})

        time.sleep(0.5)  # Be polite

    output_path = "w:\\phillongworth-site\\data\\facey_fifty.json"
    with open(output_path, "w") as f:
        json.dump({"climbs": climbs}, f, indent=2)

    print(f"\nDone. Wrote {len(climbs)} climbs to {output_path}")


if __name__ == "__main__":
    main()
