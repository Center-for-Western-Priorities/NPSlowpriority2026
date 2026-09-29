(function(){
  var D = JSON.parse(document.getElementById('data').textContent);
  var recs = D.recs, units = D.units, regions = D.regions, SITES = D.sites;
  var byUnit = {}; units.forEach(function(u){ byUnit[u.code] = u; });

  /* Pacific territories sit west of the antimeridian. Shifting their longitude by
     -360 keeps them beside Hawaii instead of on the far side of the world map. */
  function wrap(ll){ return ll && ll[1] > 0 ? [ll[0], ll[1] - 360] : ll; }

  /* ---------- markers ------------------------------------------------------
     One marker per place. Offices that share a published address (the national
     directorates at NPS headquarters, for instance) share one marker, and the
     detail panel groups that marker's projects by office. */
  var marks = {}, markOf = {};
  units.forEach(function(u){
    if(!u.ll) return;
    var key = u.site || u.code;
    if(!marks[key]){
      marks[key] = { key:key, codes:[], kind:u.kind, ll:wrap(u.ll),
                     name: u.site ? SITES[u.site] : u.name, place: u.site ? '' : u.place,
                     region:u.region };
    }
    marks[key].codes.push(u.code);
    markOf[u.code] = key;
  });
  var markList = Object.keys(marks).map(function(k){ return marks[k]; });
  var NONE = 'NONE';

  var FUND_ORDER = uniq(recs.map(function(r){ return r.fund; }))
    .sort(function(a,b){
      if(a === 'Not specified') return 1; if(b === 'Not specified') return -1;
      return cnt('fund',b) - cnt('fund',a);
    });

  var sel = null, lastPer = {};
  var f = { funds: FUND_ORDER.slice(), region:'', q:'' };

  /* ---------- basemap ---------- */
  var map = L.map('map', {
    zoomControl: true, attributionControl: true, worldCopyJump: false,
    minZoom: 2, maxZoom: 16, zoomSnap: 1, zoomDelta: 1, wheelPxPerZoomLevel: 120
  });
  var ESRI = 'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/',
      ESRI_CREDIT = 'Tiles &copy; <a href="https://www.esri.com" target="_blank" rel="noopener">Esri</a>' +
                    ' &mdash; Esri, HERE, Garmin, &copy; <a href="https://www.openstreetmap.org/copyright"' +
                    ' target="_blank" rel="noopener">OpenStreetMap</a> contributors';
  L.tileLayer(ESRI + 'World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16, maxNativeZoom: 16, attribution: ESRI_CREDIT
  }).addTo(map);
  L.tileLayer(ESRI + 'World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16, maxNativeZoom: 16, pane: 'shadowPane', attribution: ''
  }).addTo(map);
  map.attributionControl.setPrefix(
    '<a href="https://westernpriorities.org" target="_blank" rel="noopener">Center for Western Priorities</a>');

  /* ---------- park outlines ---------- */
  var BOUNDS = JSON.parse(document.getElementById('bounds').textContent);
  var bndLayers = {};
  Object.keys(BOUNDS).forEach(function(code){
    if(!byUnit[code]) return;
    var rings = BOUNDS[code].map(function(ring){
      return ring.map(function(pt){ return [pt[1], pt[0] > 0 ? pt[0] - 360 : pt[0]]; });
    });
    var poly = L.polygon(rings, {
      className: 'bnd', interactive: true, bubblingMouseEvents: false,
      stroke: true, fill: true, weight: 1, color: '#4e7524', fillColor: '#78b43c',
      opacity: .5, fillOpacity: .17
    });
    poly.on('click', function(){ pick(markOf[code]); });
    bndLayers[code] = poly;
  });

  function px(n){ return Math.round((6 + Math.sqrt(n) * 3.6) * 10) / 10; }

  var layers = {};
  markList.slice().sort(function(a, b){ return total(b) - total(a); })
    .forEach(function(m){
      var n = total(m), d = px(n);
      var icon = L.divIcon({
        className: '',
        html: '<span class="mk ' + (m.kind === 'park' ? 'circ' : 'sq') + '" style="width:' + d + 'px;height:' + d + 'px"></span>',
        iconSize: [d, d], iconAnchor: [d / 2, d / 2]
      });
      var lay = L.marker(m.ll, { icon: icon, keyboard: true, riseOnHover: true }).addTo(map);
      lay.on('add', function(){ label(m); });
      lay.on('click', function(){ pick(m.key); });
      lay.on('keypress', function(e){ if(e.originalEvent.key === 'Enter') pick(m.key); });
      lay.bindTooltip(function(){
        var k = visibleFor(m.key).length;
        return '<b>' + esc(m.name) + '</b><span>' + k + ' project' + (k === 1 ? '' : 's') +
               (m.codes.length > 1 ? ' &middot; ' + m.codes.length + ' offices' : '') +
               (m.place ? '<br>' + esc(m.place) : '') + '</span>';
      }, { className: 'tip', direction: 'top', offset: [0, -4], sticky: false });
      layers[m.key] = lay;
      label(m);
    });

  function total(m){ return m.codes.reduce(function(a, c){ return a + byUnit[c].n; }, 0); }
  function span(lay){ return lay && lay.getElement() ? lay.getElement().querySelector('.mk') : null; }
  function label(m){
    var el = layers[m.key] && layers[m.key].getElement && layers[m.key].getElement();
    if(!el) return;
    var n = lastPer[m.key]; if(n === undefined) n = total(m);
    el.setAttribute('role', 'button');
    el.setAttribute('aria-label', m.name + ', ' + n + ' project' + (n === 1 ? '' : 's'));
  }
  function draw(m, n){
    var lay = layers[m.key], el = span(lay);
    if(!el) return;
    var d = px(n);
    el.style.width = d + 'px'; el.style.height = d + 'px';
    var ic = lay.options.icon;
    ic.options.iconSize = [d, d]; ic.options.iconAnchor = [d / 2, d / 2];
    var w = lay.getElement();
    if(w){ w.style.width = d + 'px'; w.style.height = d + 'px';
           w.style.marginLeft = (-d / 2) + 'px'; w.style.marginTop = (-d / 2) + 'px'; }
  }

  /* ---------- views ---------- */
  var VIEWS = {
    all:     null,
    lower48: [[24.4, -125.0], [49.4, -66.9]],
    ak:      [[51.0, -173.0], [71.5, -129.0]],
    hi:      [[18.8, -160.3], [22.3, -154.7]],
    pac:     [[12.5, -215.5], [16.0, -213.5]],   // Guam and the Northern Marianas, shifted
    car:     [[17.6, -67.4], [18.6, -64.4]]
  };
  /* "All" covers the states and the Caribbean. The Pacific territories have
     their own button: including them would shrink everything else to a speck. */
  var allBounds = L.latLngBounds(markList.filter(function(m){ return m.ll[1] > -180; })
                                         .map(function(m){ return m.ll; }));
  var autoFit = true, fitting = false;
  function fitTo(b, animate){
    var s = map.getSize();
    if(s.x < 140 || s.y < 140) return false;
    fitting = true;
    map.fitBounds(b, { padding: [34, 34], animate: !!animate });
    fitting = false;
    return true;
  }
  function go(view, animate){
    return fitTo(view === 'all' ? allBounds : L.latLngBounds(VIEWS[view]), animate);
  }
  map.setView([44.5, -103.0], 3);
  go('all', false);
  map.on('dragstart zoomstart', function(){ if(!fitting) autoFit = false; });
  function settle(){
    map.invalidateSize({ animate: false });
    if(autoFit) go('all', false);
  }
  window.addEventListener('load', settle);
  if(window.ResizeObserver) new ResizeObserver(settle).observe(document.getElementById('mapinner'));
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(settle).catch(function(){});
  Array.prototype.forEach.call(document.querySelectorAll('.regionjump button'), function(btn){
    btn.addEventListener('click', function(){ autoFit = false; go(btn.getAttribute('data-view'), true); });
  });

  /* ---------- wheel behaviour: in an iframe, plain wheel scrolls the page ---------- */
  var embedded = window.parent && window.parent !== window,
      hint = document.getElementById('zoomhint'), hintTimer;
  function showHint(msg){
    hint.textContent = msg; hint.hidden = false;
    requestAnimationFrame(function(){ hint.classList.add('show'); });
    clearTimeout(hintTimer);
    hintTimer = setTimeout(function(){
      hint.classList.remove('show');
      setTimeout(function(){ hint.hidden = true; }, 200);
    }, 1400);
  }
  if(embedded){
    document.getElementById('mapinner').addEventListener('wheel', function(e){
      if(e.ctrlKey || e.metaKey){ e.preventDefault(); }
      else {
        e.stopPropagation();
        showHint((navigator.platform.indexOf('Mac') === 0 ? '⌘' : 'Ctrl') + ' + scroll to zoom the map');
      }
    }, { capture: true, passive: false });
  }

  /* ---------- sidebar controls ---------- */
  var progs = document.getElementById('progs'), fundEls = {};
  FUND_ORDER.forEach(function(p, i){
    var id = 'fund-' + i;
    var l = document.createElement('label');
    l.className = 'opt'; l.setAttribute('for', id);
    l.innerHTML = '<input type="checkbox" id="' + id + '" checked>' +
      '<span class="nm">' + esc(p) + '</span><span class="ct">0</span>';
    var box = l.querySelector('input');
    box.addEventListener('change', function(){
      f.funds = FUND_ORDER.filter(function(q){ return fundEls[q].box.checked; });
      if(!f.funds.length){ f.funds = FUND_ORDER.slice(); FUND_ORDER.forEach(function(q){ fundEls[q].box.checked = true; }); }
      render();
    });
    progs.appendChild(l);
    fundEls[p] = { label:l, box:box, ct:l.querySelector('.ct') };
  });
  document.getElementById('prog-n').textContent = FUND_ORDER.length;

  var regSel = document.getElementById('f-region'), qIn = document.getElementById('f-q');
  uniq(recs.map(function(r){ return r.region; }))
    .sort(function(a,b){ if(!a) return 1; if(!b) return -1; return cnt('region',b) - cnt('region',a); })
    .forEach(function(g){
      var o = document.createElement('option');
      o.value = g || '__none';
      o.textContent = (regions[g] || g) + ' (' + cnt('region',g) + ')';
      regSel.appendChild(o);
    });
  function cnt(k,v){ return recs.filter(function(r){ return r[k]===v; }).length; }

  regSel.addEventListener('change', function(){ f.region = regSel.value; render(); });
  var t;
  qIn.addEventListener('input', function(){
    clearTimeout(t);
    t = setTimeout(function(){ f.q = qIn.value.trim().toLowerCase(); render(); }, 130);
  });
  document.getElementById('f-reset').addEventListener('click', function(){
    regSel.value = ''; qIn.value = '';
    FUND_ORDER.forEach(function(p){ fundEls[p].box.checked = true; });
    f = { funds: FUND_ORDER.slice(), region:'', q:'' }; sel = null; render();
  });

  var side = document.getElementById('side'), toggle = document.getElementById('toggle');
  function setSide(open){
    side.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.textContent = open ? 'Hide filters' : 'Filters';
  }
  toggle.addEventListener('click', function(){ setSide(side.hidden); });
  var narrow = window.matchMedia('(max-width:900px)');
  if(narrow.matches) setSide(false);
  narrow.addEventListener('change', function(e){ setSide(!e.matches); });

  /* Offices list: one entry per office, each opening its marker. */
  var offlist = document.getElementById('offlist'), offEls = {};
  var offUnits = units.filter(function(u){ return u.kind === 'office'; })
                      .sort(function(a,b){ return b.n - a.n || a.name.localeCompare(b.name); });
  document.getElementById('off-n').textContent = offUnits.length;
  offUnits.forEach(function(u){
    var li = document.createElement('li'), b = document.createElement('button');
    b.type = 'button';
    b.innerHTML = esc(u.name) + ' <span class="ct">0</span>';
    b.addEventListener('click', function(){ pick(markOf[u.code], true); });
    li.appendChild(b); offlist.appendChild(li);
    offEls[u.code] = b;
  });
  var noneBtn = document.getElementById('nolink');
  if(byUnit[NONE]) noneBtn.addEventListener('click', function(){ pick(NONE, true); });
  else noneBtn.hidden = true;

  document.getElementById('dl-note').textContent =
    'All ' + recs.length.toLocaleString('en-US') + ' records, including coordinates, the full description, and how each location was assigned';

  /* ---------- filtering ---------- */
  function matches(r){
    if(f.funds.indexOf(r.fund) === -1) return false;
    if(f.region){
      if(f.region === '__none'){ if(r.region) return false; }
      else if(r.region !== f.region) return false;
    }
    if(f.q){
      var u = byUnit[r.unit] || {};
      var hay = (r.title + ' ' + r.desc + ' ' + r.unit + ' ' + (u.name||'') + ' ' + (u.place||'') +
                 ' ' + r.fund).toLowerCase();
      if(hay.indexOf(f.q) === -1) return false;
    }
    return true;
  }
  function keyOf(r){ return r.unit === NONE ? NONE : markOf[r.unit]; }
  function visible(){ return recs.filter(matches); }
  function visibleFor(key){ return recs.filter(function(r){ return keyOf(r) === key && matches(r); }); }

  function pick(key, force){
    sel = (sel === key && !force) ? null : key;
    render();
    if(sel && window.innerWidth <= 900){
      document.getElementById('detail').scrollIntoView({ behavior:'smooth', block:'start' });
    }
  }

  /* ---------- render ---------- */
  function render(){
    var vis = visible(), per = {}, perUnit = {};
    vis.forEach(function(r){
      var k = keyOf(r);
      per[k] = (per[k]||0) + 1;
      perUnit[r.unit] = (perUnit[r.unit]||0) + 1;
    });
    lastPer = per;

    var nloc = Object.keys(perUnit).filter(function(c){ return c !== NONE; }).length;
    document.getElementById('tally').textContent =
      (vis.length === recs.length ? vis.length.toLocaleString('en-US')
                                  : vis.length.toLocaleString('en-US') + ' of ' + recs.length.toLocaleString('en-US')) +
      ' project' + (vis.length === 1 ? '' : 's') +
      ' · ' + nloc + ' location' + (nloc === 1 ? '' : 's');

    FUND_ORDER.forEach(function(p){
      fundEls[p].ct.textContent = vis.filter(function(r){ return r.fund === p; }).length;
      fundEls[p].label.classList.toggle('off', !fundEls[p].box.checked);
    });

    Object.keys(bndLayers).forEach(function(code){
      var poly = bndLayers[code], on = (perUnit[code] || 0) > 0;
      if(on && !map.hasLayer(poly)) poly.addTo(map);
      if(!on && map.hasLayer(poly)) map.removeLayer(poly);
      var el = poly.getElement && poly.getElement();
      if(el) el.classList.toggle('sel', markOf[code] === sel);
    });

    markList.forEach(function(m){
      var lay = layers[m.key], n = per[m.key] || 0;
      if(n === 0){ if(map.hasLayer(lay)) map.removeLayer(lay); return; }
      if(!map.hasLayer(lay)) lay.addTo(map);
      draw(m, n); label(m);
      var el = span(lay);
      if(el) el.classList.toggle('sel', m.key === sel);
    });
    offUnits.forEach(function(u){
      var n = perUnit[u.code] || 0, b = offEls[u.code];
      b.querySelector('.ct').textContent = n;
      b.classList.toggle('off', n === 0);
    });
    document.getElementById('none-n').textContent = perUnit[NONE] || 0;

    if(sel && !per[sel]) sel = null;

    var detail = document.getElementById('detail');
    if(!sel){ detail.hidden = true; return; }

    var list = visibleFor(sel), head, groups;
    if(sel === NONE){
      head = { code: 'Not mapped', name: 'No location given',
               meta: 'These records name no park or office, and none could be identified from their own text.' };
    } else {
      var m = marks[sel], u0 = byUnit[m.codes[0]];
      head = { code: (m.codes.length > 1 ? m.codes.length + ' offices' : u0.code) + ' · ' + (regions[u0.region] || u0.region),
               name: m.name,
               meta: m.place ? 'mapped at ' + m.place : (m.codes.length > 1 ? 'offices sharing one published address' : '') };
    }
    detail.hidden = false;
    document.getElementById('dhead').innerHTML =
      '<button class="close" id="dclose" type="button" aria-label="Close details">&times;</button>' +
      '<div class="code">' + esc(head.code) + '</div>' +
      '<h3>' + esc(head.name) + '</h3>' +
      '<div class="meta">' + list.length + ' project' + (list.length === 1 ? '' : 's') +
        (head.meta ? '<br>' + esc(head.meta) : '') + '</div>';
    document.getElementById('dclose').addEventListener('click', function(){ sel = null; render(); });

    /* Group by office when a marker holds more than one. */
    groups = {};
    list.forEach(function(r){ (groups[r.unit] = groups[r.unit] || []).push(r); });
    var codes = Object.keys(groups).sort(function(a,b){ return groups[b].length - groups[a].length; });
    var many = codes.length > 1;
    document.getElementById('dbody').innerHTML = codes.map(function(c){
      return (many ? '<div class="grp">' + esc(byUnit[c].name) + ' <span>' + groups[c].length + '</span></div>' : '') +
        groups[c].map(card).join('');
    }).join('');
  }

  function card(r){
    var desc = r.desc && r.desc.toLowerCase() !== r.title.toLowerCase() ? r.desc : '';
    return '<article class="agr">' +
      '<h4>' + esc(r.title) + '</h4>' +
      '<div class="badges"><span class="badge fund">' + esc(r.fund) + '</span></div>' +
      (desc ? '<p class="desc">' + esc(desc) + '</p>' : '') +
      '<p class="rec">Record ' + r.id + (r.how !== 'as listed' ? ' &middot; location inferred from the record’s text' : '') +
        (r.region ? '' : ' &middot; no region given') + '</p>' +
    '</article>';
  }

  /* ---------- helpers ---------- */
  function uniq(a){ return a.filter(function(v,i){ return a.indexOf(v)===i; }); }
  function esc(s){
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){
      return { '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c];
    });
  }

  /* ---------- embed helper: report height to the parent frame ---------- */
  if(embedded){
    var last = 0;
    var report = function(){
      var h = Math.ceil(document.documentElement.scrollHeight);
      if(Math.abs(h - last) > 8){
        last = h;
        window.parent.postMessage({ type:'cwp:resize', id:'nps-low-priority', height:h }, '*');
      }
    };
    window.addEventListener('load', report);
    window.addEventListener('resize', report);
    if(window.ResizeObserver) new ResizeObserver(report).observe(document.documentElement);
    setInterval(report, 1000);
  }

  render();
})();
