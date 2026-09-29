# Marker placements

Two kinds of marker appear on the map.

**Circles** are park units, drawn at the unit's boundary centroid from the
[NPS Land Resources Division Boundary and Tract Data Service](https://services1.arcgis.com/fBc8EJBxQRMcHlei/ArcGIS/rest/services/NPS_Land_Resources_Division_Boundary_and_Tract_Data_Service/FeatureServer),
layer 0, and outlined with a simplified boundary from layer 2 of the same service.
Five circles are placed another way; they are listed below.

**Squares** are offices, directorates, inventory and monitoring networks, and
trails or park groups administered from one office. Each serves more than one park,
so none has a single boundary to draw. Each sits at the address NPS publishes for
it, geocoded through OpenStreetMap Nominatim. The detail panel names the city, so a
square is never mistaken for a park.

## Shared markers

Offices at the same published address share one marker, and the detail panel groups
that marker's projects by office.

| Marker | Offices |
|---|---|
| NPS headquarters, 1849 C Street NW, Washington, DC | Washington Support Office, Natural Resource Stewardship and Science, Park Planning, Facilities, and Lands, Visitor and Resource Protection, Information Resources, Cultural Resources, recreation fee program |
| 1100 Ohio Drive SW, Washington, DC | U.S. Park Police, National Capital Regional Office |
| 240 West 5th Avenue, Anchorage | Alaska Regional Office, Southwest Alaska I&M Network |

## Square markers

Codes marked * have no NPS unit code and were assigned for this map.

| Code | Entity | Mapped at | Address and source |
|---|---|---|---|
| WASO | Washington Support Office | Washington, DC | 1849 C Street NW, [NPS contact information](https://www.nps.gov/aboutus/contactinformation.htm) |
| NRSS* | Natural Resource Stewardship and Science directorate | Washington, DC | NPS headquarters. No separate address is published; the records file it under WASO. |
| PPFL* | Park Planning, Facilities, and Lands directorate | Washington, DC | NPS headquarters, same basis |
| VRP* | Visitor and Resource Protection directorate | Washington, DC | NPS headquarters, same basis |
| IRD* | Information Resources directorate | Washington, DC | NPS headquarters, same basis. The records list it as "IR"; its projects refer to IRMD staff. |
| CRAD* | Cultural Resources directorate | Washington, DC | NPS headquarters. The record itself says "NPS HQ." |
| RFEE* | Recreation fee program, Washington office | Washington, DC | NPS headquarters, same basis |
| USPP* | U.S. Park Police | Washington, DC | 1100 Ohio Drive SW, [Park Police contact page](https://www.nps.gov/subjects/uspp/contactus.htm) |
| NCRO | National Capital Regional Office | Washington, DC | 1100 Ohio Drive SW, [NPS contact information](https://www.nps.gov/aboutus/contactinformation.htm) |
| AOC* | Accounting Operations Center | Herndon, VA | 13461 Sunrise Valley Drive, [NPS donations page](https://www.nps.gov/subjects/partnerships/donate.htm). See the open question below. |
| HFC* | Harpers Ferry Center | Harpers Ferry, WV | 67 Mather Place, [Harpers Ferry Center contact page](https://www.nps.gov/subjects/hfc/contactus.htm) |
| HPTC* | Historic Preservation Training Center | Frederick, MD | 4801A Urbana Pike, [HPTC contact page](https://www.nps.gov/orgs/1098/contactus.htm) |
| AKRO | Alaska Regional Office | Anchorage, AK | 240 West 5th Avenue, [NPS contact information](https://www.nps.gov/aboutus/contactinformation.htm) |
| IMRO | Intermountain Regional Office | Lakewood, CO | 12795 West Alameda Parkway, same source. NPS gives the city as Denver; the building is in Lakewood. |
| MWRO | Midwest Regional Office | Omaha, NE | 601 Riverfront Drive, same source |
| NERO | Northeast Regional Office | Philadelphia, PA | 1234 Market Street, same source |
| PWRO | Pacific West Regional Office | San Francisco, CA | 555 Battery Street, same source |
| SERO | Southeast Regional Office | Atlanta, GA | 100 Alabama Street SW, same source |
| NTIR | National Trails Office, Intermountain Region | Santa Fe, NM | 1100 Old Santa Fe Trail, [National Trails Office contact page](https://www.nps.gov/orgs/1453/contactus.htm) |
| ARCN | Arctic I&M Network | Fairbanks, AK | 4175 Geist Road, [ARCN contact page](https://www.nps.gov/im/arcn/contactus.htm) |
| SEAN | Southeast Alaska I&M Network | Juneau, AK | 3100 National Park Road, [SEAN contact page](https://www.nps.gov/im/sean/contactus.htm) |
| SWAN | Southwest Alaska I&M Network | Anchorage, AK | 240 West 5th Avenue, [SWAN contact page](https://www.nps.gov/im/swan/contactus.htm) |
| KLMN | Klamath I&M Network | Ashland, OR | Southern Oregon University, [Klamath Network contact page](https://www.nps.gov/im/klmn/contactus.htm) |
| ERMN | Eastern Rivers and Mountains I&M Network | University Park, PA | Forest Resources Building, Penn State, [ERMN contact page](https://www.nps.gov/im/ermn/contactus.htm) |
| WEAR | Western Arctic National Parklands | Kotzebue, AK | Northwest Arctic Heritage Center, 171 Third Avenue, [Cape Krusenstern visitor page](https://www.nps.gov/cakr/planyourvisit/northwest-arctic-heritage-center.htm). Administers Cape Krusenstern, Kobuk Valley, and Noatak. |
| NATT | Natchez Trace National Scenic Trail | Tupelo, MS | 2680 Natchez Trace Parkway, [NATT contact page](https://www.nps.gov/natt/contacts.htm) |
| POHE | Potomac Heritage National Scenic Trail | Williamsport, MD | c/o C&O Canal NHP, 142 W. Potomac Street, [POHE contact page](https://www.nps.gov/pohe/contacts.htm). The NPS superintendent list gives the National Capital Regional Office instead. |
| STSP | Star-Spangled Banner National Historic Trail | Baltimore, MD | 2400 East Fort Avenue (Fort McHenry), [STSP contact page](https://www.nps.gov/stsp/contacts.htm) |

## Circles placed another way

| Code | Park | Placement |
|---|---|---|
| NAMA | National Mall and Memorial Parks | Centroid and outline of the National Mall (MALL) from the same NPS service, which has no NAMA entry |
| NACE | National Capital Parks-East | Headquarters, 1900 Anacostia Drive SE, [NACE contact page](https://www.nps.gov/nace/contacts.htm). No outline in the service. |
| KLSE | Klondike Gold Rush NHP, Seattle Unit | 319 Second Avenue S., [KLSE contact page](https://www.nps.gov/klse/contacts.htm). No outline in the service. |
| THCO | Thomas Cole National Historic Site | 218 Spring Street, Catskill, [THCO contact page](https://www.nps.gov/thco/contacts.htm). No outline in the service. |
| PARA | Grand Canyon-Parashant National Monument | The center point NPS publishes for the monument through its parks API. No outline in the service. |
| SEKI | Sequoia and Kings Canyon National Parks | Midpoint of the two parks' centroids, outlined with both boundaries |

## Pacific territories

Guam and the Northern Mariana Islands lie west of the antimeridian. The page shifts
their longitude by 360 degrees for display so they sit beside Hawaiʻi. The CSV
carries the true coordinates.

## Open question on AOC

Two records list their location as "AOC": a mail courier contract and HVAC
maintenance for a network closet. NPS uses "AOC" for its Accounting Operations
Center ([Federal Register, March 15, 2023](https://www.govinfo.gov/content/pkg/FR-2023-03-15/html/2023-05215.htm)),
and the records file both under WASO, so the map places them there. If AOC means a
different office, change its entry in `EXTRA` in `build/prep.py` and rebuild.
