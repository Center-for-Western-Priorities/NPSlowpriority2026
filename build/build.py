#!/usr/bin/env python3
"""Inline the processed data, the park outlines, the stylesheet, and the script
into the page template and write the standalone site to index.html.

    python build/prep.py      # source records -> data/projects.json
    python build/build.py     # data + template -> index.html

The page pulls Leaflet from cdnjs, the Google Fonts stylesheet, and Esri basemap
tiles. Everything else ships inside index.html.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = lambda *p: os.path.join(ROOT, 'build', *p)
read = lambda p: open(p, encoding='utf-8').read().strip()


def guard(text):
    """Keep inlined text from closing its <script> element."""
    return (text.replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029'))


html = read(B('template.html'))
html = html.replace('__LEAFLET_CSS__', read(B('vendor', 'leaflet-1.9.4.css')))
html = html.replace('__APP_JS__', read(B('app.js')).replace('</script', '<\\/script'))
html = html.replace('__PAYLOAD__', guard(read(os.path.join(ROOT, 'data', 'projects.json'))))
html = html.replace('__BOUNDARIES__', guard(read(B('vendor', 'nps-boundaries.json'))))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html + '\n')

d = json.load(open(os.path.join(ROOT, 'data', 'projects.json'), encoding='utf-8'))
print('wrote index.html, %d KB' % (len(html.encode('utf-8')) // 1024))
print('  %d projects, %d locations' % (len(d['recs']), len(d['units'])))
