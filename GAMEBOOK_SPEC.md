# GAMEBOOK_SPEC.md — a reusable gamebook engine

*Provisional name: **Quire** — a gathering of leaves. Forme is the print **style**;
Quire is the **binder** that numbers, orders, and validates the leaves.*

Status: **design sketch**, not yet built. Extracted from the patterns proven in
`book.py` (*The Book That Plays Back*), generalised so the same compiler can emit
ordinary branching gamebooks, computed-reply books like ours, and parser-IF
adventures compiled to print.

---

## 1. Motivation

`book.py` secretly contains a *general* gamebook compiler — it's just fused to one
domain (five solved games) and one output mode (one board per physical page). The
genuinely reusable, genuinely hard part — number the nodes, shuffle them so you
can't peek, resolve every "turn to N", and **prove nothing drifted** — is the part
no off-the-shelf tool packages. ink/Twine/Twee model the *branching*; they stop at
the screen. Quire is the missing last mile: **branching graph → validated,
deterministic, print-ready numbered book.**

Design goals, in priority order:

1. **Correctness is mechanical, not manual.** The off-by-one catastrophe (a single
   overflowing line shifting every downstream reference) must be caught by the
   build, never by a human reading proofs.
2. **Deterministic.** Same source + same seed → byte-identical output. (Carried
   over from `book.py`: seed 43, SHA of sources in the colophon.)
3. **Domain-agnostic core.** The compiler never knows if a node is a tic-tac-toe
   board, a paragraph, or a cave room.
4. **Swappable renderer.** Forme/LaTeX first; HTML, InDesign/IDML, plain PDF later.

---

## 2. Architecture — three layers

```
┌─ Layer 1: GRAPH ────────── domain-specific (the user writes / generates this)
│    nodes + the references between them
├─ Layer 2: COMPILER ─────── THE ENGINE (reusable — the real value)
│    numbering · seeded shuffle · constraints · ref resolution · validation
└─ Layer 3: RENDERER ─────── swappable backend
     Forme/LaTeX, HTML, IDML, …
```

Only Layer 2 is "Quire". Layers 1 and 3 are interfaces the user plugs into.

---

## 3. The node model (the one interface that unifies everything)

```python
Node = {
  "key":    Hashable,                    # stable identity (survives reshuffles)
  "type":   "section" | "terminal",      # terminal = an ending, points nowhere
  "refs":   Callable[[], list[Key]],     # outgoing edges (for constraints + validation)
  "render": Callable[[RefFn], str],      # content; ref(key) -> printed reference string
  "span":   int | "flow",                # fixed page count, or free-flowing
  "tags":   set[str],                    # optional: "entry", "decoy", volume id, …
}
RefFn = Callable[[Key], str]             # key -> "142" / "142U" / "Book II §17"
```

The whole design rests on `render` receiving a `ref` function rather than baking in
numbers. The node says *"turn to {ref(target)}"*; the engine decides what that
string is. Authoring never touches a number.

---

## 4. The pivotal decision: section number ≠ page number

`book.py` references **physical page numbers**, which forces "1 node = 1 page" and
makes pagination terrifying. Classic gamebooks reference **logical section
numbers**, assigned by the compiler and printed verbatim, while sections *flow*
across pages freely.

Quire supports both via a `numbering` mode:

| Mode | Refs are | Node `span` | Drift risk | Use for |
|---|---|---|---|---|
| **`section`** *(default)* | logical numbers (`§142`) | `"flow"` | **none** — assigned ≠ printed are decoupled | 99% of gamebooks |
| **`page`** | physical PDF pages | `1` (or two-up) | high — needs the page-count invariant | the "flip to that exact page and the reply is already there" effect (*our* book) |

**Why `section` mode kills the off-by-one problem:** the engine assigns section
*N*, prints "**N**" wherever that section is, and prints the cross-references to it
as "**N**" too. A section spilling onto the next leaf renumbers *nothing*, because
references are to the logical number, not the location. Page mode is the rare, hard
special case — our book — kept as an option, not the baseline.

---

## 5. The compiler (Layer 2) — what it does

### 5.1 Slot assignment
- Fixed **entry** nodes get reserved low numbers (e.g. start = §1, or the menu page).
- The rest are ordered by `random.Random(seed).shuffle(...)` — reproducible.
- Optional **decoys**: nodes nothing references, hidden in the shuffle. (Generalises
  `book.py`'s single `('orphan',)` "You were not sent here." page.)

### 5.2 Constraints (pluggable predicates)
Built-ins, each a `(a, b) -> bool` or a global checker:
- `non_adjacent(linked)` — a node and a node it links to may not land on the same
  page/spread (so a reader can't see the reply to a move). This is `book.py`'s
  `linked()` rule, promoted to a reusable constraint.
- `entries_fixed` — entry nodes at their reserved numbers.
- `terminals_spread` — endings not clustered (optional aesthetic).
- `partners_unlinked` — for two-up layouts, paired nodes must not be linked.

The assigner is constraint-aware: it places nodes so all predicates hold, and
**fails loudly** if it can't (rather than emitting a subtly broken book).

### 5.3 Reference resolution
`REF(key) -> str`, with decorations:
- plain: `"142"`
- slot marker: `"142U"` / `"142L"` (our two-up upper/lower — generalised slot tags)
- cross-volume: `"Book II, 142"` (see §7)

### 5.4 Assembly
Order the rendered blocks, interleave front/back matter, hand to the renderer.

---

## 6. Validation suite — the engine's real value

Run after compile, before render. **Any failure aborts the build.** This is the
play-testing and invariant-checking we did *by hand* this session, promoted to a
library:

- ✅ **Refs resolve** — no dangling "turn to N" (every target key exists & is placed).
- ✅ **No self-reveal** — no choice shares a page/spread with its target.
- ✅ **Reachability** — every node reachable from an entry, OR tagged `decoy`.
  (Catches orphaned content and typo'd keys.)
- ✅ **Constraints hold** — zero violations of the active predicate set.
- ✅ **Page-count invariant** *(page mode only)* — rendered PDF page count == computed N.
- ✅ **Determinism** — rebuild, hash sources + output, must match the recorded hash.

> **Hard-won lesson, baked in:** a node that overflows its reserved page spills past
> `\clearpage` with **no `Overfull` warning** — so `grep Overfull` is blind to it.
> In page mode, Quire checks the **actual PDF page count**, never the overfull
> count. (See the `playback` repo's memory on this.) Build outputs are produced
> **sequentially**, never concurrently — overlapping LaTeX runs corrupt the
> remember-picture overlays and aux files.

---

## 7. Multiplayer & multi-volume

The historical ambitious gamebooks (*Clash of the Princes* — two duelling books;
*Fabled Lands* — a persistent world across volumes) are modelled as:

- **One graph, nodes tagged by volume.** The compiler emits **N output documents**
  that **share one keyspace**, so a reference can cross volumes
  (`ref(k)` → `"Book II, 142"` when `k` lives in another volume).
- **Per-volume entry points** and per-volume validation, plus a global cross-volume
  reachability pass.
- State that persists across volumes (inventory, gold, flags) is **not** the
  engine's concern — it lives on the player's **logbook/character sheet**, which is
  Layer-1 content (a printed form + conditional inline references). See §8.

---

## 8. The three kinds of gamebook (how Layer 1 differs)

| Kind | Who fills `refs`/`render` | Mode | Engine additions needed |
|---|---|---|---|
| **Choice tree** (CYOA / ink / Twine) | import a narrative graph | `section` | importer (ink JSON / Twee) → nodes |
| **Computed-reply** (*our* book) | a solver emits the tree | `page` | none — this is the proven path |
| **State machine** (parser IF, e.g. Colossal Cave) | parse the game's data tables | `section` | **conditional inline refs** (§8.1) |

### 8.1 State-machine support (the one real engine addition)
Parser IF (Colossal Cave) has millions of reachable states — infeasible as
"one section per state". The classic gamebook tames this exactly as Fighting
Fantasy did:

- A **section = a room + an event**, not a full state.
- **Conditional inline references:** *"If your lamp is lit, read on; otherwise turn
  to {ref(dark_room)}."* The engine must treat **each conditional branch as an
  edge** (so validation & reachability still work), while the **condition logic and
  the player logbook design stay in Layer 1.**
- **RNG folds into player dice rolls** (*"roll a die: 1–2, a dwarf attacks, turn to
  {ref(...)}"*), keeping randomness out of the state count.

This collapses millions of states into low-thousands of sections — a chunky but
real volume. The source data (Crowther–Woods room/travel/object tables) is already
a machine-readable directed graph, so it'd be a **compile**, not an authoring job —
the same shape as `book.py`, swapping "solved game tree" for "parsed adventure
graph". (Whether anyone has *published* a Colossal Cave gamebook: unknown — worth a
search before attempting.)

---

## 9. Renderer interface (Layer 3)

```python
class Renderer(Protocol):
    def begin(self, meta: BookMeta) -> None: ...
    def block(self, number: str, content: str, span: Span) -> None: ...
    def matter(self, name: str, content: str) -> None: ...   # title/verso/toc/…
    def finish(self) -> bytes | str: ...                     # .tex / .html / .idml
```

- **FormeRenderer** (first target): wraps the existing `forme.sty` — A6, palette,
  foot-timeline, fore-edge index, `[bleed]`, CMYK. Reuses everything we built.
- Future: **HtmlRenderer** (web gamebook), **IdmlRenderer** (InDesign hand-off).
- A separate **PdfxStep** wraps output as PDF/X-1a (the `make_pdfx.sh` recipe:
  curves via `-dNoOutputFonts`, CMYK, `-dPDFXTrimBoxToMediaBoxOffset`).

### 9.1 Trim/bleed profiles (one renderer, many printers)
A renderer takes a **trim profile**: `{trim_w, trim_h, bleed, safety, spine_fn}`.
The same node graph then targets different printers by swapping the profile —
`forme.sty`'s `[bleed]` option already parameterises this; generalise it from a
single 5 mm value to arbitrary trim + bleed. Concrete planned profiles:
- **Futura Cod. 73** — A6 105×148, bleed 5 mm, spine 17 mm *(the current build)*.
- **Lulu Pocket** — 108×174, bleed 3.175 mm, safety 12.7 mm, Lulu spine formula
  *(a sibling edition — different trim ⇒ text reflows ⇒ re-verify the page-count
  invariant, and the ghost-grid/two-up layout needs an eyeball, not just a reflow)*.

This re-target is the concrete near-term motivation for keeping trim swappable. See
**`DISTRIBUTION.md`** for the full Lulu plan, rationale (free listing, zero markup,
no inventory/tax), and the step-by-step re-target checklist.

---

## 10. API sketch

```python
from quire import Gamebook, non_adjacent
from quire.render import FormeRenderer
from quire.prepress import pdfx1a

book = Gamebook(seed=43, numbering="section")
book.add_nodes(my_nodes)                 # Layer-1 list of Node
book.entries     = [start_key]
book.decoys      = 1                      # orphan / easter-egg sections
book.constraints = [non_adjacent(linked)]

doc = book.compile()                     # assign numbers, resolve refs
book.validate()                          # raises on ANY §6 failure
tex = doc.render(FormeRenderer(trim="A6", bleed=5, cmyk=True))
open("book.tex","w",encoding="utf-8").write(tex)   # NB utf-8 (cp1252 bit us once)
# build sequentially (never concurrent), 2x xelatex, then:
pdfx1a("book.pdf", trim_inset_mm=5)
```

**Rebuilding *The Book That Plays Back* on Quire** would be the conformance test:
`numbering="page"`, `span=1`/two-up, the five game engines as Layer-1 node
producers, `non_adjacent(linked)` as the only constraint, FormeRenderer as backend.
If Quire can reproduce our 310-page book byte-for-byte, the abstraction is right.

---

## 11. What to reuse vs. build

**Reuse from `book.py` (proven):**
- the order / seeded-shuffle logic, `REF`, `linked`/`non_adjacent`
- the `len(pages_seq) == N` assertion and page-count verification
- SHA-of-source determinism (colophon)
- the Forme renderer incl. `[bleed]` + CMYK + the foot-timeline overlay math
- the PDF/X-1a recipe (`make_pdfx.sh`) and its gotchas (MSYS_NO_PATHCONV, local ICC)

**Build new:**
- the Layer 1/2/3 interfaces (Node, Constraint, Renderer)
- `numbering="section"` **flow layout** (sections pack onto pages while staying
  numbered) — the biggest genuinely new piece
- the validation suite as first-class, reusable API
- multi-volume / cross-volume references
- conditional inline references (state-machine support)
- importers: ink (compiled JSON) and Twine/Twee → nodes

---

## 12. Open questions

- **Flow layout numbering display:** print the section number as a run-in header
  (`**142** You enter a cave…`) — confirm it survives column/page breaks cleanly.
- **Constraint solver:** is greedy placement + backtracking enough, or do dense
  non-adjacency graphs need a real CSP/SAT pass? (Our compact pairing was greedy
  and fine; bigger books may not be.)
- **Importer fidelity:** ink supports logic/variables that don't map to static
  print — define the supported subset, and fail loudly on the rest.
- **Two-up / N-up generality:** `book.py` hard-codes two-up upper/lower; generalise
  to arbitrary slots-per-page with slot markers.
- **Section mode + page-accurate ToC:** a contents that lists page numbers needs a
  second pass after flow layout settles (LaTeX `\label`/`\ref` territory).

---

*Part of the Geoscientific Chaos Union toolkit. If built: code MIT, like Forme.*
