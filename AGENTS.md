# AGENTS.md — Tonnez

## What this is

`index.html` — a single self-contained interactive Tonnetz visualization for
scale-degree thinking (1, ♭2, 2, ♭3, 3, 4, ♯4/♭5, 5, ♭6, 6, ♭7, 7), not note
names. HTML + CSS + vanilla JS + SVG, **no build step, no dependencies**.
All UI text and code comments are in English. Deployed via GitHub Pages
(file must stay named `index.html`).

## Verifying changes

1. Syntax-check the inline script:

   ```bash
   python3 -c "import re;open('/tmp/opencode/t.js','w').write(re.search(r'<script>\n(.*)\n</script>',open('index.html').read(),re.S).group(1))" && node --check /tmp/opencode/t.js
   ```

2. Smoke tests + screenshots (self-contained):

   ```bash
   tests/run_tests.sh
   ```

   - `tests/inject_tests.py` generates `tmp/index-test.html` (23 assertions,
     results panel drawn top-left) and `tmp/index-scenario.html` (Guitar panel
     open + local center on ♭2) from `index.html` into `tmp/` (gitignored).
   - Then headless Firefox captures `tmp/tt-test.png`, `tmp/tt-scenario.png`,
     `tmp/tt-default.png`.
   - **Read `tmp/tt-test.png` and check every line is PASS** (the panel is in
     the top-left corner). `document.title` also becomes `TESTS n/m`.

### Firefox on this machine is a SNAP

- The `--profile <dir>` directory must **already exist** (hence the `mkdir -p`).
- Input/output paths must be **absolute and under `$HOME`** — the project dir
  works; `/tmp` does **not** (snap-private tmp namespace).
- Use `--no-remote --headless --window-size=WxH --screenshot OUT file://...`.
- For deterministic screenshots the test pages freeze CSS transitions
  (`*{transition:none!important}`) and finish Web-Animation-API animations
  (`document.getAnimations().forEach(a => a.finish())`).

## Architecture cheat sheet

The lattice lives in **degree space**: every node is an offset from the tonic.
Changing the tonic therefore does **not** move the grid by design — it only
remaps guitar markers, optional letters, and the `= X` pitch indicator next to
the tonic chips.

- Node `(i,j)`: `pc = ((7i + 4j) % 12 + 12) % 12` (+7 = P5 right, +4 = M3 up).
- Hex patch `RADIUS = 3` (37 nodes); `posOf(i,j) = (SP*(i + j/2), -HP*j)`,
  `SP = 92`, `HP = SP*√3/2`; SVG viewBox `-405 -335 810 670`.
- Triad qualities `QUALITIES = {maj:[0,4,7], min:[0,3,7], dim:[0,3,6],
  aug:[0,4,8], off:null}`; semitone step → lattice delta `STEP_DELTA`
  (`0:[0,0], 3:[1,-1], 4:[0,1], 6:[2,-2], 7:[1,0], 8:[0,2]`).
- Clicking inside a triangle selects that triad via inverse transform:
  `β = -py/HP`, `α = px/SP - β/2`; `α+β ≤ i0+j0+1` → major rooted at `(i0,j0)`,
  else minor rooted at `(i0,j0+1)`.
- Vertex click = local center (relative-interval labels on every node + cyan
  ring on the chosen node). Escape / "clear" resets. Inversions move only the
  bass ring + voice badges; the triad shape stays.
- Blues mode: `BLUE_NOTES = {3,6,10}` violet, `BLUE_SCALE = {0,3,4,5,6,7,10,11}`
  as soft support tint.
- Guitar: standard tuning, high-e first `OPEN_STRING_PCS = [4,11,7,2,9,4]`,
  12 frets, `NUT_X=64, FRET_SP=44, STR_TOP=28, STR_GAP=31`. Marker kinds:
  chord (gold), blue (violet), supp (hollow violet), focus (cyan disc, no ring);
  a cyan `.g-focus` ring (r 11.5) is added only on non-focus marks matching the
  focused pitch. Chord/blue/focus marker radius is 8.5.
- Display toggles are only `Functions / Intervals / Voicing / Letters`
  (`state.show = {fn, int, voice, letters}`). Degrees and edge links are always
  on — there are deliberately no toggles for them.

## Known traps

- `#net * { pointer-events: none }` — hit-testing is done manually on the two
  `<svg>` elements (`net`, `guitar`) from event coordinates, not via DOM events
  on shapes.
- CSS specificity: `.g-mark.chord circle` / `.g-mark.blue circle` /
  `.g-mark.focus circle` all beat a bare `.g-focus { fill:none }`, so a focus
  ring inside a marked dot once got filled solid and painted over the degree
  label. Fix: the ring rule is `.g-mark circle.g-focus` (equal specificity,
  later source order). Focus-kind marks get no ring at all (the cyan disc *is*
  the focus indication).
- Snap Firefox quirks, see above.

## Conventions

- `tmp/` is gitignored: scratch pages, screenshots, profiles live there.
  Reusable test code lives in `tests/`.
- Do not commit unless explicitly asked; the repo currently has staged rename
  `tonnetz.html → index.html` plus untracked `.gitignore`, `tests/`, `AGENTS.md`.
