# Affinity MCP — experiments & notes

Notes from wiring the **official "Affinity by Canva" MCP connector** into this
project and driving it from Claude Code. Written up because the findings were
genuinely useful — both about the connector's plumbing and about what it can (and
can't) do for a project like this one.

TL;DR: it works, it's surprisingly capable, and **we don't use it for the book** —
because the book is a deterministic LaTeX→PDF pipeline and routing it through a GUI
app would trade away reproducibility for nothing we don't already have. Kept
installed for tinkering and for *future* Affinity-native work.

---

## 1. What it is

"Affinity by Canva" is one of the nine creative connectors in Anthropic's
**Claude for Creative Work** (released 2026-04-28). It is installed through the
**Claude Desktop** UI, not as a file you hand-edit — it lands as a Desktop
Extension bundle:

```
%APPDATA%\Claude\Claude Extensions\ant.dir.gh.canva.affinity\
  manifest.json          <- the interesting bit
  server/index.js        <- a thin stdio<->SSE bridge
  node_modules/ ...
```

### The architecture (reverse-engineered from manifest.json)

The `.mcpb` bundle is **not** the real server. It's a thin bridge:

```
Claude  ──stdio──▶  server/index.js  ──HTTP/SSE──▶  http://localhost:6767/sse  ──▶  Affinity app
         (bundle)                     (SSE_URL in manifest env)        (the REAL server, hosted INSIDE Affinity)
```

So the actual MCP server **runs inside the Affinity desktop app itself** and only
exists while Affinity is open with its MCP server enabled
(Affinity → Settings → MCP Server). Auth is handled by Canva via your logged-in
desktop session.

---

## 2. Claude Desktop vs Claude Code — the key finding

**Question we set out to answer:** a connector installed via *Claude Desktop's*
interface lives in Desktop's config, not Claude Code's. Can Claude Code use it?

**Answer: yes — *if* the connector's server is a reachable local endpoint.**
Because the real server is just an HTTP/SSE socket on `localhost:6767`, Claude Code
can attach to the *same* endpoint Desktop uses. We verified the port was open and
unauthenticated (no Desktop-token gate — it returned a `session_id` immediately
with `Access-Control-Allow-Origin: *`), then:

```sh
claude mcp add --transport sse affinity "http://localhost:6767/sse"
# -> affinity: http://localhost:6767/sse (SSE) - ✓ Connected
```

The entry is stored in `~/.claude.json`, scoped to this project. It shows
"disconnected" whenever Affinity is closed — harmless. The tools only load at
**session start**, so after `claude mcp add` you must restart Claude Code for the
`mcp__affinity__*` tools to appear.

Note the server binds **IPv6 `[::1]:6767`** (use `localhost`, which resolves to
`::1` here, or explicit `[::1]`).

### General lesson
A Desktop-installed connector is reusable from Claude Code when it's backed by a
local stdio command or a localhost URL you can point at. Connectors that are
purely hosted claude.ai OAuth integrations (interactive browser login) are the
ones that typically *won't* carry over to a headless/CLI context.

---

## 3. Driving the SDK — the working pattern

The server is a **JavaScript scripting bridge into the live Affinity document**.
Its tools: `execute_script`, `render_spread`, `render_selection`,
`list_/read_sdk_documentation`, `search_sdk_hints`, `add_sdk_hint`,
`list_/read_/save_script_to_library`, `report_sdk_issue`.

What worked well, in order:

1. **Read the `preamble` doc first** (the server insists on it). It documents the
   rules: `require('/document')` style includes, scripts return nothing so use
   `console.log()`, set the current spread before editing it (but not if it's
   already current — that clears the selection), prefer the SDK's own AI/Dialog
   APIs over external ones.
2. **`search_sdk_hints` BEFORE experimenting.** This is the big time-saver: a
   global pool of solutions from prior sessions. It handed us exact constructor
   names and module paths, so we never had to read the giant SDK source files
   (`document.js` alone is ~86k chars — it overflows the tool output; grep or
   chunk it if you ever must).
3. **`execute_script`** to act, **`render_spread`** to *see* the result and verify.
4. **`add_sdk_hint`** after solving something by experiment, to help future runs.

### Gotchas we hit
- A spread has **no `.bounds`** — use `spread.getSpreadExtents()` →
  `{x,y,width,height}` in **px**. Units are **11.811 px/mm** (300 dpi). Our "A4"
  test doc actually reported 1748×2480 px = **148×210 mm** (A5).
- Add shapes via **`AddChildNodesCommandBuilder`** (one undoable command for many
  shapes), not `doc.addNode()` per shape.
- Ring/outline = `ShapeEllipse` with `brushFill = FillDescriptor.createNone()` and
  `lineFill = createSolid(...)` + `LineStyleDescriptor.createDefault(weight)`.

### The demo (fittingly on-theme)
We drew, live, a **tic-tac-toe grid** in Forme's slate ink (`#1B2A33`) with a
**signal-red ringed O** (`#DC424C`) in the top-left cell — the book's "ringed
move" motif — and rendered it back to confirm. Full round trip proven:
Claude Code → localhost:6767 → Affinity → render → back.

---

## 4. Is it deep enough for real prepress? (Yes, mostly)

Asked the hints pool whether it could do the production steps this book needs.
It's more capable than expected — operating **on an Affinity document**:

| Task | SDK support | How |
|---|---|---|
| Text → curves | ✅ | `doc.convertToCurves()` on a Selection of all text nodes |
| Units | ✅ | `units.js` |
| Convert doc to CMYK | ✅ | `doc.format = RasterFormat.CMYKA8` (auto-assigns SWOP v2) |
| **Specific** ICC profile | ⚠️ creation-only | `NewDocumentOptions.colourProfile` at doc creation; **read-only after** |
| PDF/X export | ✅ | `FileExportOptions.createWithPresetName('PDF/X-1a:2003' / 'PDF/X-4')` — enumerate via `allPresetNames` (names are localized!) |
| Bleed + box hierarchy | ✅ | `DocumentProperties` bleed (LTRB); press preset sets `MediaBox=BleedBox`, `TrimBox=canvas` |
| Trim/crop marks | ⚠️ | preset-driven; no direct API, manual paths for custom marks |
| Export to file | ✅ | `doc.export(path, options, area)` — **Desktop only** (`app.getUserDesktopPath`) |

---

## 5. Why we DON'T use it for this book

Everything above acts on an **Affinity document**. This book is a
**LaTeX-generated PDF**, rebuildable byte-identically from `book.py` + seed 43.
Using the MCP would mean: our PDF → import/place into Affinity → convert → export.
That import step:

1. **Breaks reproducibility** — a manual GUI-state round-trip that can't be
   regenerated from source. That's the project's whole ethos.
2. **Is lossy/fiddly** for a 310-page vector PDF (placing ≠ keeping crisp pages).
3. **Buys us nothing** — our output is **already** CMYK (verified at the
   content-stream level: CMYK ops present, zero RGB), **already** has 5 mm bleed
   with the correct trim, and fonts are embedded+subset (Futura accepts that).

The only genuinely-missing prepress step is **PDF/X-1a wrapping**, and that's
better done in the deterministic pipeline (see below) than via a GUI app.

**Where the MCP *would* shine:** a project authored in Affinity to begin with —
batch text-to-curves, CMYK setup, and PDF/X export across many `.afpub` files.
Worth remembering for the next thing, not this one.

---

## 6. The deterministic alternative — Ghostscript (recommended path)

The two things people reach for Affinity to do — **PDF/X wrapping** and
**text→curves** — both have one-line Ghostscript equivalents that keep us in the
reproducible CLI pipeline. (Ghostscript is **not currently installed** on this
machine — `gs`/`gswin64c` absent from PATH — so these are the documented path for
when/if Futura requires them.)

PDF/X-1a (needs a small ICC + def file, but the core is):
```sh
gswin64c -dPDFX -dBATCH -dNOPAUSE -sColorConversionStrategy=CMYK \
  -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
  -sOutputFile=miolo_X1a.pdf PDFX_def.ps the_book_compact_bw_bleed.pdf
```

Text → curves (outline all fonts, no font embedding needed):
```sh
gswin64c -o outlined.pdf -sDEVICE=pdfwrite -dNoOutputFonts cover.pdf
```
`-dNoOutputFonts` re-emits every glyph as vector outlines. Verify afterwards with
`pdffonts outlined.pdf` (should list **no** fonts).

---

## 7. Housekeeping

- The `affinity` MCP entry is in `~/.claude.json` (project-scoped). Remove with
  `claude mcp remove affinity` if you ever want it gone.
- Tools only appear after a Claude Code restart, with Affinity running + its MCP
  server enabled in Settings.
- The tic-tac-toe demo was drawn into a scratch Affinity doc — not saved; just Undo
  or close without saving.
