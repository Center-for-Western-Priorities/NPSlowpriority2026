#!/usr/bin/env python3
"""Source records  ->  data/projects.json and the published CSV.

Reads data/source/source-records.csv when it is present (gitignored, never
published) and the published CSV otherwise, so a fresh clone rebuilds without
the source file.

    python build/prep.py

What this script does to the records:

  * Repairs text that mixes two encodings (cp1252 and UTF-8) cell by cell.
  * Matches each location name to an NPS unit code, using the NPS Land
    Resources Division boundary centroids in build/vendor/nps-units.json.
  * Places offices, directorates, networks, and trails at the address NPS
    publishes for them. See docs/PLACEMENTS.md.
  * For records with no location, assigns one only when the title or
    description names a park code. Every such inference is listed in INFER
    below and in docs/METHODOLOGY.md.
  * Maps fund source codes to plain-language labels.
  * Sorts records by location and title and numbers them from 1, so the
    published order and IDs carry nothing from the source file.
"""
import csv, io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'source', 'source-records.csv')
CSV_OUT = os.path.join(ROOT, 'data', 'nps-low-priority-projects-2026.csv')
JSON_OUT = os.path.join(ROOT, 'data', 'projects.json')
UNITS = json.load(open(os.path.join(ROOT, 'build', 'vendor', 'nps-units.json'), encoding='utf-8'))

REGIONS = {
    'AKR': 'Alaska', 'IMR': 'Intermountain', 'MWR': 'Midwest', 'NCR': 'National Capital',
    'NER': 'Northeast', 'PWR': 'Pacific West', 'SER': 'Southeast', 'WASO': 'National (WASO)',
    '': 'Not specified',
}

# ---------------------------------------------------------------------------
# Location names in the records that do not match an NPS unit name exactly.
# Value is the unit code this map uses.
# ---------------------------------------------------------------------------
ALIAS = {
    'Craters of the Moon National Monument & Preserve': 'CRMO',
    'Denali National Park & Preserve': 'DENA',
    'Glacier Bay National Park & Preserve': 'GLBA',
    'Grand Canyon-Parashant National Monument': 'PARA',
    'Great Sand Dunes National Park & Preserve': 'GRSA',
    'Katmai National Park & Preserve': 'KATM',
    'Klondike Gold Rush NHP-Seattle Unit': 'KLSE',
    'Lake Clark National Park & Preserve': 'LACL',
    'Natchez Trace National Scenic Trail': 'NATT',
    'National Capital Parks-East': 'NACE',
    'National Mall and Memorial Parks': 'NAMA',
    'Potomac Heritage National Scenic Trail': 'POHE',
    'Salem Maritime National Historic Site': 'SAMA',
    'Sequoia and Kings Canyon National Parks': 'SEKI',
    'Star-Spangled Banner National Historic Trail': 'STSP',
    'Ste. Geneviève National Historical Park': 'STGE',
    'The White House and President\'s Park': 'WHHO',
    'Thomas Cole National Historic Site': 'THCO',
    'Tumacácori National Historical Park': 'TUMA',
    'Western Arctic National Parklands': 'WEAR',
    'Whiskeytown National Recreation Area': 'WHIS',
    'Wrangell-St. Elias National Park & Preserve': 'WRST',
    'Yukon-Charley Rivers NPRES': 'YUCH',
    # Offices, directorates, and networks
    'Alaska Regional Office': 'AKRO',
    'Intermountain Regional Office': 'IMRO',
    'Midwest Regional Office': 'MWRO',
    'NERO-Philadelphia': 'NERO',
    'National Capital Regional Office': 'NCRO',
    'PWRO-SF': 'PWRO',
    'Southeast Regional Office': 'SERO',
    'Washington Office': 'WASO',
    'Assoc. Director, Natural Resource Stewardship & Science': 'NRSS',
    'Associate Director, Park Planning, Fac, Land': 'PPFL',
    'Visitor & Resource Protection': 'VRP',
    'IR': 'IRD',
    'Cultural Resources Washington Support Office (NPS HQ)': 'CRAD',
    'WASORecFee': 'RFEE',
    'AOC': 'AOC',
    'United States Park Police': 'USPP',
    'Harpers Ferry Center': 'HFC',
    'Historic Preservation Training Center': 'HPTC',
    'National Trails Intermountain Region': 'NTIR',
    'Arctic Network': 'ARCN',
    'Southeast Alaska Network': 'SEAN',
    'Southwest Alaska Network': 'SWAN',
    'Klamath Network': 'KLMN',
    'Eastern Rivers and Mountains Network': 'ERMN',
}

# ---------------------------------------------------------------------------
# Units this map draws that are not in the boundary centroid layer, or that
# are offices rather than parks. kind: park = circle, office = square.
# ll is the published address, geocoded; see docs/PLACEMENTS.md.
# site groups units that share one address into one marker.
# ---------------------------------------------------------------------------
HQ = [38.8939, -77.0427]
OHIO = [38.8764, -77.0335]
ANC = [61.2172, -149.8862]
EXTRA = {
    # parks with no centroid in the layer
    'NACE': ('National Capital Parks-East', 'park', [38.8681, -76.9945], 'Washington, DC', None),
    'KLSE': ('Klondike Gold Rush National Historical Park, Seattle Unit', 'park', [47.5994, -122.3319], 'Seattle, Washington', None),
    'THCO': ('Thomas Cole National Historic Site', 'park', [42.2258, -73.8615], 'Catskill, New York', None),
    'PARA': ('Grand Canyon-Parashant National Monument', 'park', [36.4154, -113.6683], '', None),
    'NAMA': ('National Mall and Memorial Parks', 'park', None, '', None),  # MALL centroid, below
    # trails and park groups administered from one office
    'NATT': ('Natchez Trace National Scenic Trail', 'office', [34.3300, -88.7095], 'Tupelo, Mississippi', None),
    'POHE': ('Potomac Heritage National Scenic Trail', 'office', [39.6003, -77.8243], 'Williamsport, Maryland', None),
    'STSP': ('Star-Spangled Banner National Historic Trail', 'office', [39.2632, -76.5798], 'Baltimore, Maryland', None),
    'WEAR': ('Western Arctic National Parklands', 'office', [66.8926, -162.6052], 'Kotzebue, Alaska', None),
    # regional offices
    'AKRO': ('Alaska Regional Office', 'office', ANC, 'Anchorage, Alaska', 'anchorage'),
    'IMRO': ('Intermountain Regional Office', 'office', [39.7008, -105.1426], 'Lakewood, Colorado', None),
    'MWRO': ('Midwest Regional Office', 'office', [41.2649, -95.9245], 'Omaha, Nebraska', None),
    'NERO': ('Northeast Regional Office', 'office', [39.9517, -75.1610], 'Philadelphia, Pennsylvania', None),
    'NCRO': ('National Capital Regional Office', 'office', OHIO, 'Washington, DC', 'ohio'),
    'PWRO': ('Pacific West Regional Office', 'office', [37.7963, -122.4009], 'San Francisco, California', None),
    'SERO': ('Southeast Regional Office', 'office', [33.7534, -84.3925], 'Atlanta, Georgia', None),
    # national offices and directorates
    'WASO': ('Washington Support Office', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'NRSS': ('Natural Resource Stewardship and Science directorate', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'PPFL': ('Park Planning, Facilities, and Lands directorate', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'VRP':  ('Visitor and Resource Protection directorate', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'IRD':  ('Information Resources directorate', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'CRAD': ('Cultural Resources directorate', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'RFEE': ('Recreation fee program, Washington office', 'office', HQ, 'NPS headquarters, Washington, DC', 'hq'),
    'AOC':  ('Accounting Operations Center', 'office', [38.9594, -77.4147], 'Herndon, Virginia', None),
    'USPP': ('U.S. Park Police', 'office', OHIO, 'Washington, DC', 'ohio'),
    'HFC':  ('Harpers Ferry Center', 'office', [39.3232, -77.7412], 'Harpers Ferry, West Virginia', None),
    'HPTC': ('Historic Preservation Training Center', 'office', [39.3663, -77.3882], 'Frederick, Maryland', None),
    'NTIR': ('National Trails Office, Intermountain Region', 'office', [35.6691, -105.9266], 'Santa Fe, New Mexico', None),
    # inventory and monitoring networks
    'ARCN': ('Arctic Inventory and Monitoring Network', 'office', [64.8486, -147.8361], 'Fairbanks, Alaska', None),
    'SEAN': ('Southeast Alaska Inventory and Monitoring Network', 'office', [58.3791, -134.7021], 'Juneau, Alaska', None),
    'SWAN': ('Southwest Alaska Inventory and Monitoring Network', 'office', ANC, 'Anchorage, Alaska', 'anchorage'),
    'KLMN': ('Klamath Inventory and Monitoring Network', 'office', [42.1885, -122.6904], 'Ashland, Oregon', None),
    'ERMN': ('Eastern Rivers and Mountains Inventory and Monitoring Network', 'office', [40.8048, -77.8640], 'University Park, Pennsylvania', None),
}
SITES = {
    'hq': 'NPS headquarters, Washington, DC',
    'ohio': '1100 Ohio Drive SW, Washington, DC',
    'anchorage': 'Anchorage, Alaska',
}

# Display names where the centroid layer splits one unit into a park and a
# preserve, or where the layer's name differs from the unit's full name.
DISPLAY = {
    'CRMO': 'Craters of the Moon National Monument and Preserve',
    'DENA': 'Denali National Park and Preserve',
    'GLBA': 'Glacier Bay National Park and Preserve',
    'GRSA': 'Great Sand Dunes National Park and Preserve',
    'KATM': 'Katmai National Park and Preserve',
    'LACL': 'Lake Clark National Park and Preserve',
    'WRST': 'Wrangell-St. Elias National Park and Preserve',
    'SEKI': 'Sequoia and Kings Canyon National Parks',
    'WHHO': "The White House and President's Park",
    'WHIS': 'Whiskeytown National Recreation Area',
}

# Records with no location in the source. Each entry names the unit the
# record's own title or description identifies, and the text it rests on.
# Concession contract identifiers take the form of a park code plus a number
# (GLAC001, ROMO002). Records not listed here stay unassigned.
INFER = [
    (r'GLAC00\d', 'GLAC'), (r'ROMO00\d', 'ROMO'), (r'PEFO00\d', 'PEFO'),
    (r'YOSE00\d', 'YOSE'), (r'JODR00\d', 'JODR'), (r'BAND00\d', 'BAND'),
    (r'ISRO00\d', 'ISRO'), (r'NACE00\d', 'NACE'),
    (r'\bSCBL\b', 'SCBL'), (r'\bFOSM\b', 'FOSM'), (r'\bTILL monument\b', 'TILL'),
]
UNASSIGNED = 'NONE'

FUNDS = {
    'ONPS': 'Park operations (ONPS)',
    'OTHER': 'Other',
    'CYCLIC': 'Cyclic maintenance', 'CYLIC': 'Cyclic maintenance',
    'FLREA': 'Recreation fees (FLREA)',
    'RE/RE': 'Repair and rehabilitation',
    'TBD - SUBJECT TO FUND AVAILABILITY': 'To be determined',
    'CONCESSION FRANCHISE FEES': 'Concession franchise fees',
    'CULTURAL CYCLIC MAINTENANCE PROGRAM': 'Cultural cyclic maintenance',
    'CULTURAL RESOURCES FUND SOURCE': 'Cultural resources',
    'HOUSING': 'Park housing',
    'LRF (GAOA)': 'Legacy Restoration Fund (GAOA)',
    'CENTRAL HAZARDOUS MATERIALS FUND': 'Central Hazardous Materials Fund',
    'DISASTER SUPPLEMENTAL': 'Disaster supplemental',
    'INTER-AGENCY AGREEMENT': 'Interagency agreement',
    'TRANSPORTATION FEE REVENUE': 'Transportation fee revenue',
    'LINE ITEM CONSTRUCTION': 'Line-item construction',
    'IRA': 'Inflation Reduction Act',
    '': 'Not specified',
}


def fix_encoding(raw):
    """Decode a byte string that mixes UTF-8 sequences with cp1252 bytes."""
    out, i = [], 0
    pat = re.compile(rb'[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xf4][\x80-\xbf]{3}')
    while i < len(raw):
        m = pat.match(raw, i)
        if m:
            out.append(m.group().decode('utf-8')); i = m.end(); continue
        b = raw[i:i + 1]
        try:
            out.append(b.decode('cp1252'))
        except UnicodeDecodeError:
            out.append('')
        i += 1
    return ''.join(out)


def clean(s):
    s = (s or '').replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def unit_info(code):
    if code == UNASSIGNED:
        return {'name': 'No location given', 'kind': 'none', 'll': None, 'place': '', 'site': None}
    if code in EXTRA:
        name, kind, ll, place, site = EXTRA[code]
        if code == 'NAMA':
            ll = UNITS['MALL'][0]['ll']
        return {'name': name, 'kind': kind, 'll': ll, 'place': place, 'site': site}
    if code == 'SEKI':
        a, b = UNITS['SEQU'][0]['ll'], UNITS['KICA'][0]['ll']
        return {'name': DISPLAY['SEKI'], 'kind': 'park',
                'll': [round((a[0] + b[0]) / 2, 4), round((a[1] + b[1]) / 2, 4)], 'place': '', 'site': None}
    feats = UNITS[code]
    main = next((f for f in feats if 'Preserve' not in f['name']), feats[0])
    return {'name': DISPLAY.get(code, main['name']), 'kind': 'park', 'll': main['ll'], 'place': '', 'site': None}


def norm(s):
    s = s.lower().replace('&', 'and')
    return ' '.join(re.sub(r'[^a-z ]', ' ', s).split())


NAME2CODE = {}
for code, feats in UNITS.items():
    for f in feats:
        NAME2CODE.setdefault(norm(f['name']), code)


def read_source():
    raw = open(SRC, 'rb').read()
    rows = list(csv.reader(io.StringIO(fix_encoding(raw))))
    recs, inferred = [], []
    for r in rows[1:]:
        loc, region, _pri, title, desc, fund = [clean(x) for x in r]
        region = '' if region.startswith('#') else region   # spreadsheet error values count as blank
        how = 'as listed'
        if not loc or loc.startswith('#'):
            code, how = UNASSIGNED, 'no location given'
            for pat, c in INFER:
                if re.search(pat, title + ' ' + desc):
                    code, how = c, 'inferred from title or description'
                    inferred.append((title, c))
                    break
        elif loc in ALIAS:
            code = ALIAS[loc]
        elif norm(loc) in NAME2CODE:
            code = NAME2CODE[norm(loc)]
        else:
            raise SystemExit('unmatched location: %r' % loc)
        if not region and code != UNASSIGNED and code in UNITS:
            region = UNITS[code][0]['region']
        f = fund.upper()
        if f not in FUNDS:
            raise SystemExit('unmapped fund source: %r' % fund)
        recs.append({'unit': code, 'region': region, 'title': title, 'desc': desc,
                     'fund': FUNDS[f], 'how': how})
    return recs, inferred


def read_published():
    recs = []
    with open(CSV_OUT, encoding='utf-8-sig', newline='') as fh:
        for d in csv.DictReader(fh):
            recs.append({'unit': d['unit_code'] or UNASSIGNED, 'region': d['region_code'],
                         'title': d['title'], 'desc': d['description'],
                         'fund': d['fund_source'], 'how': d['location_basis']})
    return recs, []


if os.path.exists(SRC):
    recs, inferred = read_source(); source_kind = 'source file'
else:
    recs, inferred = read_published(); source_kind = 'published csv'

units = {}
for r in recs:
    u = r['unit']
    if u not in units:
        units[u] = dict(code=u, region='', n=0, **unit_info(u))
    units[u]['n'] += 1

# A location's region is the one most of its records list (ties alphabetical),
# so the result does not depend on the order records arrive in.
from collections import Counter
for code, u in units.items():
    c = Counter(r['region'] for r in recs if r['unit'] == code and r['region'])
    u['region'] = '' if code == UNASSIGNED or not c else sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

recs.sort(key=lambda r: (units[r['unit']]['name'], r['title'].lower(), r['desc']))
for i, r in enumerate(recs, 1):
    r['id'] = i

json.dump({'recs': recs,
           'units': sorted(units.values(), key=lambda u: (-u['n'], u['name'])),
           'regions': REGIONS, 'sites': SITES},
          open(JSON_OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

COLS = ['record_id', 'region_code', 'region_name', 'unit_code', 'unit_name', 'location_type',
        'mapped_place', 'latitude', 'longitude', 'location_basis', 'title', 'description', 'fund_source']
TYPE = {'park': 'park unit', 'office': 'office, program, network, or trail', 'none': 'no location given'}
with open(CSV_OUT, 'w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, lineterminator='\n')
    w.writeheader()
    for r in recs:
        u = units[r['unit']]
        ll = u['ll'] or ['', '']
        w.writerow({'record_id': r['id'], 'region_code': r['region'],
                    'region_name': REGIONS.get(r['region'], r['region']),
                    'unit_code': '' if r['unit'] == UNASSIGNED else r['unit'],
                    'unit_name': '' if r['unit'] == UNASSIGNED else u['name'],
                    'location_type': TYPE[u['kind']], 'mapped_place': u['place'] or ('' if u['kind'] == 'none' else u['name']),
                    'latitude': ll[0], 'longitude': ll[1], 'location_basis': r['how'],
                    'title': r['title'], 'description': r['desc'], 'fund_source': r['fund']})

print('source:', source_kind)
print('records', len(recs))
print('locations', len(units), '| parks', sum(u['kind'] == 'park' for u in units.values()),
      '| offices', sum(u['kind'] == 'office' for u in units.values()))
print('unassigned', units.get(UNASSIGNED, {}).get('n', 0))
print('inferred', len(inferred))
for t, c in inferred:
    print('   ', c, '<-', t)
print('no coords', [u['code'] for u in units.values() if not u['ll'] and u['kind'] != 'none'])
