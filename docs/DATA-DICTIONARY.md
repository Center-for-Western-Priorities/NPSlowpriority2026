# Data dictionary

`data/nps-low-priority-projects-2026.csv`: 1,492 rows, one per project. UTF-8 with
a byte-order mark, so Excel on Windows reads the accented characters correctly.

| Column | What it holds |
|---|---|
| `record_id` | Number assigned for this dataset, 1 to 1,492, after sorting by location and title. Not an NPS identifier. |
| `region_code` | NPS region as listed in the record: AKR, IMR, MWR, NCR, NER, PWR, SER, or WASO. Blank for five records that list none. See METHODOLOGY.md for the nine filled from the park. |
| `region_name` | Plain name for the region code. |
| `unit_code` | NPS unit code for parks. For offices, directorates, and networks with no NPS unit code, a short code assigned for this map (listed in PLACEMENTS.md). Blank when no location is given. |
| `unit_name` | Full name of the park or office. |
| `location_type` | `park unit`, `office, program, network, or trail`, or `no location given`. |
| `mapped_place` | Where the marker sits: the park name, or the city of the office. |
| `latitude`, `longitude` | Marker coordinates, WGS 84. Parks: NPS boundary centroid. Offices: the published address, geocoded. Blank when no location is given. |
| `location_basis` | `as listed` when the record names the location, `inferred from title or description` for the 15 records assigned from their own text, or `no location given` for the 21 left unmapped. |
| `title` | Project title as it appears in the record. |
| `description` | Project description as it appears in the record. May repeat the title. |
| `fund_source` | Plain-language fund source. The mapping from the codes in the records is in METHODOLOGY.md. |

Text fields were repaired for encoding and whitespace only. See METHODOLOGY.md.

`data/projects.json` holds the same records in the shape the page reads, plus one
entry per location with its marker coordinates and project count. It is generated
by `build/prep.py` and should not be edited by hand.
