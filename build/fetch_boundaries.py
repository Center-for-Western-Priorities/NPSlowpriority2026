#!/usr/bin/env python3
"""Rebuild build/vendor/nps-boundaries.json from the NPS boundary service.

The map draws a soft outline of each park it plots. Those outlines come from the
same authority as the centroids: layer 2, "NPS Boundary", of the NPS Land Resources
Division Boundary and Tract Data Service.

The full polygons are far too heavy to inline in a single-file page, so this script
fetches them once, simplifies them, and writes a compact lookup keyed by unit code.
The result is committed, so `build.py` never touches the network. Run this only when
the set of mapped parks changes or NPS republishes a boundary.

    python build/fetch_boundaries.py

What the simplification does, and what it costs:

  * Douglas-Peucker, with the tolerance capped per ring so a small unit such as
    a single historic site is not reduced to a triangle. EPS is the ceiling.
  * Interior holes are dropped. Inholdings inside a park do not read at the zoom
    levels this map is used at, and keeping them roughly doubles the payload.
  * Detached pieces smaller than MIN_EXTRA are dropped, and each unit keeps at most
    MAX_RINGS pieces. The largest piece of every unit is always kept, so no park
    silently loses its outline.
  * Coordinates are rounded to four decimal places, about 11 metres.

These outlines are for orientation. They are not a legal or survey boundary, and
anyone needing the authoritative geometry should go to the service itself.
"""

import json
import math
import os
import urllib.parse
import urllib.request

SERVICE = (
    "https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/"
    "NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/2/query"
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(HERE, "vendor", "nps-boundaries-raw.geojson")
OUT = os.path.join(HERE, "vendor", "nps-boundaries.json")

# Sequoia and Kings Canyon share one administrative code in the records but are two
# units in the boundary service, so both are fetched and merged. National Mall and
# Memorial Parks is drawn with the National Mall outline.
MERGE = {"SEQU": "SEKI", "KICA": "SEKI", "MALL": "NAMA"}

EPS = 0.005        # degrees, upper bound on Douglas-Peucker tolerance
MIN_EXTRA = 8e-5   # square degrees, floor for a detached piece after the largest
MAX_RINGS = 6      # pieces kept per unit


def park_codes():
    """The park units the map actually plots, from the built data file."""
    with open(os.path.join(ROOT, "data", "projects.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    codes = sorted(u["code"] for u in data["units"] if u["kind"] == "park")
    expanded = []
    for code in codes:
        hits = [src for src, dest in MERGE.items() if dest == code]
        expanded.extend(hits or [code])
    return codes, expanded


def fetch(query_codes):
    where = "UNIT_CODE IN (%s)" % ",".join("'%s'" % c for c in query_codes)
    body = urllib.parse.urlencode({
        "where": where,
        "outFields": "UNIT_CODE,UNIT_NAME",
        "returnGeometry": "true",
        "f": "geojson",
        "outSR": "4326",
        "maxAllowableOffset": "0.002",
        "geometryPrecision": "4",
        "resultRecordCount": "2000",
    }).encode()
    # A GET URL with 40 codes in it runs past what some proxies will pass, so POST.
    req = urllib.request.Request(
        SERVICE, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def rdp(pts, eps):
    """Douglas-Peucker, iterative so a long coastline cannot blow the stack."""
    if len(pts) < 4 or eps <= 0:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        ax, ay = pts[i]
        bx, by = pts[j]
        dx, dy = bx - ax, by - ay
        d2 = dx * dx + dy * dy
        best, bi = -1.0, -1
        for k in range(i + 1, j):
            px, py = pts[k]
            if d2 == 0:
                dist = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / d2))
                qx, qy = ax + t * dx, ay + t * dy
                dist = (px - qx) ** 2 + (py - qy) ** 2
            if dist > best:
                best, bi = dist, k
        if best > eps * eps:
            keep[bi] = True
            stack.append((i, bi))
            stack.append((bi, j))
    return [p for p, k in zip(pts, keep) if k]


def ring_area(ring):
    total = 0.0
    for i in range(len(ring) - 1):
        total += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return abs(total) / 2


def simplify(rings_by_unit):
    out = {}
    for code, rings in rings_by_unit.items():
        rings.sort(key=ring_area, reverse=True)
        keep = [rings[0]] + [r for r in rings[1:] if ring_area(r) >= MIN_EXTRA][:MAX_RINGS - 1]
        shaped = []
        for ring in keep:
            eps = min(EPS, math.sqrt(ring_area(ring)) / 25)
            simple = rdp(ring, eps)
            if simple[0] != simple[-1]:
                simple.append(simple[0])
            if len(simple) >= 4:
                shaped.append([[round(x, 4), round(y, 4)] for x, y in simple])
        if shaped:
            out[code] = shaped
    return out


def main():
    codes, query_codes = park_codes()
    # The service caps the size of one response, so ask for the parks in batches.
    features = []
    for i in range(0, len(query_codes), 40):
        batch = fetch(query_codes[i:i + 40])
        if batch.get("error"):
            raise SystemExit("boundary service error: %s" % batch["error"])
        features.extend(batch.get("features") or [])
    raw = {"type": "FeatureCollection", "features": features}
    if not features:
        raise SystemExit("boundary service returned no features: %s" % raw.get("error"))
    with open(RAW, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, separators=(",", ":"))

    rings_by_unit = {}
    for feat in features:
        code = feat["properties"]["UNIT_CODE"]
        code = MERGE.get(code, code)
        geom = feat["geometry"] or {}
        polys = geom["coordinates"] if geom.get("type") == "MultiPolygon" else [geom.get("coordinates")]
        for poly in polys:
            if not poly:
                continue
            rings_by_unit.setdefault(code, []).append([tuple(p[:2]) for p in poly[0]])

    out = simplify(rings_by_unit)
    # A few units have no polygon in the service (a new site, a unit inside a
    # larger one). Those draw as a marker with no outline; they are reported here
    # and listed in docs/PLACEMENTS.md.
    missing = sorted(set(codes) - set(out))
    print("no boundary for: %s" % (", ".join(missing) or "none"))

    text = json.dumps(out, separators=(",", ":"))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)

    print("units   %d" % len(out))
    print("pieces  %d" % sum(len(v) for v in out.values()))
    print("points  %d" % sum(len(r) for v in out.values() for r in v))
    print("size    %d KB" % (len(text) // 1024))


if __name__ == "__main__":
    main()
