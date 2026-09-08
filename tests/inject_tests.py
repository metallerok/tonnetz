#!/usr/bin/env python3
"""
Generates headless test pages from ../index.html into ../tmp/ (gitignored).

Outputs:
  tmp/index-test.html      - copy of index.html + smoke-test script (results panel top-left)
  tmp/index-scenario.html  - copy of index.html + scenario script (Guitar on, focus on b2)

Run tests/inject_tests.sh afterwards to capture screenshots with headless Firefox.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'index.html')
DST_DIR = os.path.join(ROOT, 'tmp')
os.makedirs(DST_DIR, exist_ok=True)

TEST_JS = r"""
(function(){
  document.head.insertAdjacentHTML('beforeend', '<style>*{transition:none!important}#testres{position:fixed;top:8px;left:8px;z-index:999;background:#10141eee;border:1px solid #444;padding:8px 12px;font:12px monospace;color:#d5dbe6;max-width:52ch;white-space:pre-wrap}</style>');
  const out = [];
  const ok = (name, cond) => out.push((cond ? 'PASS ' : 'FAIL ') + name);
  try {
    const netSvg = document.getElementById('net');
    const dispBtns = [...document.querySelectorAll('#displayRow button')];
    ok('display buttons exact', JSON.stringify(dispBtns.map(b => b.textContent)) === JSON.stringify(['Functions','Intervals','Voicing','Letters']));
    ok('degrees always visible', [...document.querySelectorAll('.node .deg')].every(t => t.style.display !== 'none'));
    ok('edges always visible', document.getElementById('gEdges').style.display !== 'none');
    ok('no legacy show keys', state.show.deg === undefined && state.show.links === undefined);
    ok('initial tonic label', document.getElementById('tonicPc').textContent === '= C');

    const voiceBtn = dispBtns.find(b => b.textContent === 'Voicing');
    voiceBtn.click();
    ok('voicing off hides badges', [...document.querySelectorAll('.badge')].every(b => b.style.display === 'none'));
    voiceBtn.click();
    ok('voicing on shows badges', [...document.querySelectorAll('.badge')].every(b => b.style.display !== 'none'));

    [...document.querySelectorAll('#modeRow button')].find(b => b.textContent === 'Guitar').click();
    ok('guitar panel visible', !document.getElementById('guitarPanel').hidden);
    const cm = document.querySelector('.g-mark.chord circle');
    ok('chord marker r=8.5', !!cm && cm.getAttribute('r') === '8.5');
    const chordCount0 = document.querySelectorAll('.g-mark.chord').length;

    toggleFocusPc(1, null);
    const foc = document.querySelector('.node.focused .deg');
    ok('lattice focus deg', !!foc && foc.textContent === '♭2');
    const gm = [...document.querySelectorAll('.g-mark.focus')];
    ok('guitar focus marks exist', gm.length >= 1);
    ok('guitar focus label', gm.length > 0 && gm.every(g => g.querySelector('.g-lbl').textContent === '♭2'));
    ok('guitar focus ring', gm.every(g => !g.querySelector('.g-focus')));
    toggleFocusPc(0, null);
    const ringed = [...document.querySelectorAll('.g-mark.chord')].filter(g => g.querySelector('.g-focus'));
    ok('ring on focused chord tone', ringed.length >= 1);
    ok('focus ring stays hollow', ringed.length > 0 &&
      [...document.querySelectorAll('.g-mark.chord .g-focus')].every(r => getComputedStyle(r).fill === 'none'));
    toggleFocusPc(1, null);
    ok('chord marks unchanged', document.querySelectorAll('.g-mark.chord').length === chordCount0);

    // wiring: synthetic DOM click on the ♭7 vertex (nearest to center)
    const cands = [...document.querySelectorAll('.node')].filter(g => g.querySelector('.deg').textContent === '♭7');
    cands.sort((a, b) => {
      const p = g => g.getAttribute('transform').match(/translate\((-?[\d.]+),(-?[\d.]+)\)/).slice(1).map(Number);
      const A = p(a), B = p(b);
      return (A[0]*A[0] + A[1]*A[1]) - (B[0]*B[0] + B[1]*B[1]);
    });
    const g7 = cands[0];
    const tr = g7.getAttribute('transform').match(/translate\((-?[\d.]+),(-?[\d.]+)\)/);
    const r = netSvg.getBoundingClientRect();
    const vb = netSvg.viewBox.baseVal;
    const scale = Math.min(r.width / vb.width, r.height / vb.height);
    const ox = (r.width - vb.width * scale) / 2, oy = (r.height - vb.height * scale) / 2;
    const cx = r.left + ox + ((+tr[1]) - vb.x) * scale;
    const cy = r.top + oy + ((+tr[2]) - vb.y) * scale;
    netSvg.dispatchEvent(new MouseEvent('click', { clientX: cx, clientY: cy, bubbles: true }));
    const f2 = document.querySelector('.node.focused .deg');
    ok('vertex click focuses', !!f2 && f2.textContent === '♭7');
    ok('guitar focus relabeled', [...document.querySelectorAll('.g-mark.focus .g-lbl')].every(t => t.textContent === '♭7'));

    [...document.querySelectorAll('#tonicRow button')].find(b => b.textContent === '5').click();
    ok('tonic pc label', document.getElementById('tonicPc').textContent === '= G');
    ok('tonic chip active', [...document.querySelectorAll('#tonicRow button')].find(b => b.textContent === '5').classList.contains('on'));
    ok('focus survives tonic change', [...document.querySelectorAll('.g-mark.focus .g-lbl')].every(t => t.textContent === '♭7'));

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    ok('escape clears focus', !document.querySelector('.node.focused') && !document.querySelector('.g-mark.focus'));

    dispBtns.find(b => b.textContent === 'Letters').click();
    ok('letters toggle works', [...document.querySelectorAll('.node .letter')].every(t => t.style.display !== 'none'));
  } catch (err) {
    out.push('ERROR ' + (err && err.message));
  }
  const pass = out.filter(s => s.startsWith('PASS')).length;
  document.title = 'TESTS ' + pass + '/' + out.length;
  const d = document.createElement('div');
  d.id = 'testres';
  d.textContent = out.join('\n');
  document.body.appendChild(d);
  document.getAnimations().forEach(a => a.finish());
})();
"""

SCEN_JS = r"""
(function(){
  document.head.insertAdjacentHTML('beforeend', '<style>*{transition:none!important}</style>');
  [...document.querySelectorAll('#modeRow button')].find(b => b.textContent === 'Guitar').click();
  toggleFocusPc(1, null);
  document.getAnimations().forEach(a => a.finish());
})();
"""

def inject(path, js):
    html = open(SRC).read()
    assert html.count('</body>') == 1
    html = html.replace('</body>', '<script>' + js + '</script>\n</body>')
    open(path, 'w').write(html)

inject(os.path.join(DST_DIR, 'index-test.html'), TEST_JS)
inject(os.path.join(DST_DIR, 'index-scenario.html'), SCEN_JS)
print('written:', DST_DIR)
