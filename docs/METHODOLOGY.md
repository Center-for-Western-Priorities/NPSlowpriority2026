# Methodology

## Source

The project records come from an internal National Park Service project
database. Every record carries a low-priority designation. The map shows all
1,492. None was excluded, merged, or added.

The records were accessed on TKTKDate. They carry no dates and no cost
estimates, so the map cannot say when each designation was made or whether it
has changed since.

## Context

The Associated Press reported on August 21, 2026, that maintenance projects
approved for 2026 at parks across the country had been moved to a new "low
priority" list, while projects wanted by the White House, including repairs to
the Lincoln Memorial Reflecting Pool and work tied to the Freedom 250
initiative, took precedence
([Matthew Brown, AP](https://apnews.com/article/national-parks-white-house-priorities-051fd27a454094a7cbec0718517e35e3)). According to AP:

- About 1,500 projects were on the low-priority list as of July, spanning more
  than 200 sites, with a combined cost estimate of more than $400 million.
- The priority designations came from NPS headquarters in Washington, according
  to documents AP obtained and one official.
- Officials said almost all of the low-priority projects were expected to go
  undone. Park staff "were told to not expect anything on the low priority list
  to be contracted," one official said.
- A separate high-priority list held more than 2,000 projects, and a third list
  held White House priorities.
- The Interior Department said many entries on the low-priority list had been
  "mis-prioritized and were corrected." It declined to say how many or which ones.

AP's figures come from its own reporting. The counts on this map come from the
records described above. The two are close: 1,492 projects here, about 1,500 in
AP's count. The $400 million figure is AP's and cannot be checked against these
records, which carry no costs.

When describing this map in writing, the accurate phrasing is "1,492 projects
designated low priority in NPS records." Because Interior says some entries were
corrected, avoid saying every project on the map was cancelled or will go unfunded.

## Text shown on the map

Project titles and descriptions appear as they do in the records. No sentence was
rewritten, condensed, or supplied. Three kinds of change were made, all mechanical:

- **Encoding repair.** The records mix two text encodings, which garbled dashes,
  quotation marks, and accented letters in some cells. Each cell was decoded
  character by character, so "27–30” diameter" and "Tumacácori" read correctly.
- **Whitespace.** Runs of spaces, tabs, and line breaks were collapsed to one space,
  and leading and trailing spaces were removed.
- **Duplicate descriptions.** In 129 records the description is empty or repeats the
  title word for word. The map shows the title alone for those; the CSV keeps both
  fields as they are.

Many descriptions carry internal shorthand: park codes (SHEN, GATE), contract and
option-year language, and requisition or order numbers. These were left in place.

## How locations were assigned

Each record names the park or office it belongs to. That name was matched to an
NPS unit code in three steps.

1. **Exact match** against unit names in the NPS boundary centroid layer, ignoring
   case, punctuation, and "&" versus "and". This placed 225 of the 272 names.
2. **Listed aliases** for the rest: abbreviations ("Yukon-Charley Rivers NPRES"),
   "& Preserve" names the centroid layer splits into two units, names that differ
   from the layer's (the records say "Salem Maritime National Historic Site"; the
   layer says national historical park), and every office, directorate, and network. Each
   alias is written out in `ALIAS` in `build/prep.py`.
3. **Records with no location.** Thirty-six records name no park or office. Fifteen
   of them identify one in their own title or description, and those were assigned
   to it. The other 21 stay unassigned and are listed from the sidebar.

The 15 inferred assignments, each resting on text in the record itself:

| Assigned to | Evidence in the record |
|---|---|
| Glacier (GLAC) | Concession contract identifier GLAC001/003 in the title |
| Rocky Mountain (ROMO), two records | ROMO001/002 |
| Petrified Forest (PEFO) | PEFO001 |
| Yosemite (YOSE) | YOSE003 |
| John D. Rockefeller, Jr. Memorial Parkway (JODR), two records | JODR002 |
| Bandelier (BAND) | BAND002 |
| Isle Royale (ISRO) | ISRO006-28 |
| National Capital Parks-East (NACE) | NACE006 |
| Scotts Bluff (SCBL) | "SCBL" in the title and description |
| Fort Smith (FOSM) | "FOSM" in the title and description |
| Emmett Till and Mamie Till-Mobley (TILL), three records | "TILL monument" in the title |

Concession contract identifiers take the form of a park code followed by a number,
which is what makes the first group unambiguous.

Records a reader might reasonably tie to a park but that were **not** assigned,
because their text does not name the unit:

- Two Kobuk and Koyukuk Rivers moose studies. The rivers cross more than one unit.
- A Theodore Roosevelt museum-objects appraisal. Several units carry Roosevelt's name.
- An Everglades restoration water-quality contract. It names the restoration, not
  the park.
- Office construction at "the ETIC" and snow removal at the Robert Temple church
  parking lot. Both relate to Emmett Till sites, but neither names the monument.
- A condition assessment for concession contract NCRO001, whose prefix is a region
  office code rather than a park.

Any of these can move onto the map by adding a line to `INFER` in `build/prep.py`.

## Where the records name an office, the map uses the office

Some records filed under a national office describe work at a specific park. The
13 recreation fee program records, for instance, include projects at Shenandoah,
Gateway, and the George Washington Memorial Parkway, and several environmental
cleanup records under the Washington office name park sites. The map places these
at the office the record lists, because that is the unit the record assigns them
to. Searching a park's name or code finds them.

## Region

The region is the one the record lists. Fourteen records list none. For the nine
of those assigned to a park, the region comes from the park's entry in the NPS
centroid layer. The other five show "Not specified" in the region filter.

## Fund source

Fund source codes were mapped to plain-language labels:

| In the records | On the map |
|---|---|
| ONPS | Park operations (ONPS) |
| CYCLIC, CYLIC | Cyclic maintenance |
| FLREA | Recreation fees (FLREA) |
| Re/Re | Repair and rehabilitation |
| TBD - SUBJECT TO FUND AVAILABILITY | To be determined |
| Concession Franchise Fees | Concession franchise fees |
| Cultural Cyclic Maintenance Program | Cultural cyclic maintenance |
| Cultural Resources Fund Source | Cultural resources |
| Housing | Park housing |
| LRF (GAOA) | Legacy Restoration Fund (GAOA) |
| Central Hazardous Materials Fund | Central Hazardous Materials Fund |
| Disaster Supplemental | Disaster supplemental |
| Inter-Agency Agreement | Interagency agreement |
| Transportation Fee Revenue | Transportation fee revenue |
| Line Item Construction | Line-item construction |
| IRA | Inflation Reduction Act |
| OTHER | Other |
| blank | Not specified |

"CYLIC" appears twice and is read as a misspelling of CYCLIC. 134 records list no
fund source. These are budget categories, not a description of the work, and the
sidebar says so.

## Record numbers

The `record_id` in the CSV and the "Record" number on the map were assigned for
this dataset: records are sorted by location, then title, and numbered from 1.
They are not identifiers from any NPS system.

## Known limits

- The records carry no dollar amounts and no dates, so the map shows neither.
- A marker's size is the number of projects listed there. It says nothing about
  their cost or scale.
- Office squares mark where an office sits, not where its work happens.
