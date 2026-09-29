# NPS Low-Priority Projects, 2026

> **Draft.** Bracketed text marked `[PLACEHOLDER]` here and on the map is holding
> space for copy that has not been written or approved yet: the title, the source
> line, and the framing of what a low-priority designation means.

An interactive map of 1,492 National Park Service projects designated low
priority. [FRAMING PLACEHOLDER: who made the designation, when, and what it
means for the projects.] Each marker is a park unit or an NPS office. Click one to
read every project listed there, with its description and fund source.

A companion to the
[2026 NPS Agreement Disapprovals](https://github.com/Center-for-Western-Priorities/2026-NPS-Agreement-Disapprovals)
map, built on the same pipeline and design.

Built by the Center for Western Priorities.

## Live map

**https://center-for-western-priorities.github.io/NPSlowpriority2026/**

This URL goes live once GitHub Pages is turned on for the repository (Settings →
Pages → Deploy from a branch → `main`, `/ (root)`).

## What the map shows

- **1,492 projects** at **276 locations** in eight NPS regions, including the
  national office (WASO)
- **248 park units**, drawn as circles with a simplified outline of the park boundary
- **28 offices and programs** drawn as squares: regional offices, national
  directorates, the U.S. Park Police, Harpers Ferry Center, the Historic
  Preservation Training Center, inventory and monitoring networks, and trails
  administered from one office. Offices that share a published address share a marker.
- **21 projects with no location**, listed from the sidebar rather than mapped
- **18 fund sources**, filterable from a collapsed sidebar section

Filter by region or fund source, search every field, and download the full dataset
as CSV. The map needs no funding figures and shows none; the records carry no
dollar amounts.

For how locations were assigned, see [docs/METHODOLOGY.md](docs/METHODOLOGY.md).
For where each square sits and why, see [docs/PLACEMENTS.md](docs/PLACEMENTS.md).

## The data

[`data/nps-low-priority-projects-2026.csv`](data/nps-low-priority-projects-2026.csv)
is the published dataset: 1,492 rows, 13 columns. Columns are documented in
[docs/DATA-DICTIONARY.md](docs/DATA-DICTIONARY.md).

## Repository layout

```
index.html                     the built site, one file
build/
  prep.py                      records  ->  data/projects.json + the published CSV
  build.py                     data + template + script  ->  index.html
  template.html                page markup and styles
  app.js                       map behavior, inlined into index.html at build time
  fetch_units.py               NPS centroid service  ->  build/vendor/nps-units.json
  fetch_boundaries.py          NPS boundary service  ->  build/vendor/nps-boundaries.json
  vendor/                      Leaflet's stylesheet, unit centroids, park outlines
data/
  nps-low-priority-projects-2026.csv   the published dataset
  projects.json                processed records and marker coordinates
docs/
  METHODOLOGY.md               what is counted, how locations were assigned, known limits
  DATA-DICTIONARY.md           every CSV column
  PLACEMENTS.md                where each square sits, and the source for it
embed/
  wordpress-snippet.html       paste-ready Custom HTML block
```

## Rebuilding

Requires Python 3 and nothing else.

```bash
python build/prep.py     # records -> data/projects.json, data/nps-low-priority-projects-2026.csv
python build/build.py    # data    -> index.html
```

`prep.py` rebuilds from the published CSV when no local source file is present, so
a fresh clone builds as is. Check the printed record count before committing a
rebuilt `index.html`.

`fetch_units.py` and `fetch_boundaries.py` are the only scripts that use the
network. Their output is committed, so the two build steps above run offline.
Rerun them only when the set of mapped parks changes.

To change the design, edit `build/template.html` or `build/app.js` and rerun
`build.py`. Editing `index.html` directly works, but the next build overwrites it.

## Hosting and embedding

`index.html` is a single file. It loads Leaflet from cdnjs, the Google Fonts
stylesheet, and basemap tiles from Esri's Light Gray Canvas service. Everything
else ships inside the page. It runs from any static host.

For WordPress, paste [embed/wordpress-snippet.html](embed/wordpress-snippet.html)
into a Custom HTML block. Inside an iframe, a plain scroll wheel scrolls the
article, and Ctrl or cmd plus scroll zooms the map.

Keep `data/nps-low-priority-projects-2026.csv` next to `index.html`. The download
link is relative.

## Sources

- Project records: [SOURCE PLACEHOLDER]
- Park coordinates and outlines: [NPS Land Resources Division Boundary and Tract Data Service](https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer), layers 0 and 2
- Office locations: addresses published by NPS, listed individually in [docs/PLACEMENTS.md](docs/PLACEMENTS.md)
- Basemap: [Esri Light Gray Canvas](https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer), credited to Esri, HERE, Garmin, and OpenStreetMap contributors

Center for Western Priorities · [westernpriorities.org](https://westernpriorities.org)
