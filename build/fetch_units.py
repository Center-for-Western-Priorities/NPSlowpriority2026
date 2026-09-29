#!/usr/bin/env python3
"""Rebuild build/vendor/nps-units.json from the NPS boundary centroid layer.

prep.py matches every location name in the records against this file and takes
park coordinates from it, so the build itself never touches the network. Rerun
this only if NPS republishes the centroids.

    python build/fetch_units.py

Source: NPS Land Resources Division Boundary and Tract Data Service, layer 0,
"NPS Boundary Centroids".
"""
import json, os, urllib.parse, urllib.request

SERVICE = ("https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/"
           "NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer/0/query")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor", "nps-units.json")

q = urllib.parse.urlencode({"where": "1=1", "outFields": "UNIT_CODE,UNIT_NAME,REGION",
                            "returnGeometry": "true", "outSR": "4326", "f": "json",
                            "resultRecordCount": "2000"})
with urllib.request.urlopen(SERVICE + "?" + q, timeout=120) as resp:
    feats = json.load(resp)["features"]

out = {}
for f in feats:
    a, g = f["attributes"], f["geometry"]
    out.setdefault(a["UNIT_CODE"], []).append(
        {"name": a["UNIT_NAME"], "region": a["REGION"], "ll": [round(g["y"], 4), round(g["x"], 4)]})
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, separators=(",", ":"), sort_keys=True)
print("units", len(out))
