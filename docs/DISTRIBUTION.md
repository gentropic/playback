# DISTRIBUTION.md — how *The Book That Plays Back* reaches people

Channels for getting the book (and its source) to readers, with the decisions and
the open follow-ons. The book is **MIT (code) / CC0 (content)**, so the bias is
toward "free and frictionless to obtain" over revenue.

---

## Current state

| Channel | Status | Notes |
|---|---|---|
| **Source** (GitHub) | ✅ live | `github.com/gentropic/playback` — rebuilds byte-identically from `book.py` + seed 43 |
| **Built PDFs** | shipped via GitHub **Release** (not committed) | `*.pdf` is gitignored; attach the masters to a tagged release |
| **Futura hardcover** (físico) | ✅ ordered (proof) | A6 capa dura, Cod. 73, Pólen 90 g, 17 mm spine. The **gift run** lives here — local, cheaper, hand-delivered. ISBN 978-65-02-14290-5 |

**Decided against:**
- **Kindle / KDP** — can't easily be free ($0.99 floor), reflowable Kindle fights
  the design, PD/CC0 content gets extra scrutiny, account + tax-interview friction.
  Poor fit; dropped.
- **EPUB / HTML reader** — technically easy (it's `numbering="section"` from the
  gamebook spec: each board an XHTML page, moves become hyperlinks), but it loses
  *playback*'s whole point. The "flip the page and the reply is already there" trick
  is **paper magic**; as taps it's just an ordinary hyperlinked CYOA, and the
  seed-43 anti-peek shuffle becomes meaningless when you can't flip ahead. A *good*
  digital gamebook, but a **different artifact** — not this book. Revisit only as a
  deliberate companion edition, never as the primary form. (Never PDF→EPUB
  conversion — always emit XHTML from the node graph via a Layer-3 `EpubRenderer`.)

---

## Planned follow-on: **Lulu Pocket edition** (the "anyone, anywhere" tail)

**Goal:** anyone in the world can order a physical copy at **cost**, with **zero
inventory, fulfilment, or tax burden** on the author. Gift runs stay with Futura;
Lulu is purely the standing "someone might want one someday" option.

**Why Lulu fits (verified ~2026, re-check before acting — policies move):**
- **Free Lulu Bookstore listing** — public marketplace, **no upfront cost, no
  distribution fee**; Lulu prints + ships white-label. Buyer finds it, author
  touches nothing.
- **Zero markup** — minimum price = manufacturing cost; set revenue to 0 so the
  buyer pays only print + shipping. **No royalties ⇒ essentially nothing to
  report** (structural; Brazil-specific tax treatment NOT promised — verify).
- **CC0-friendly** — Lulu is relaxed about public-domain / openly-licensed content
  (unlike KDP).
- No inventory, ever (print-on-demand).

**Plan:** list free on the Lulu Bookstore at zero markup, link it from the README.

### The catch — it's a *re-target*, not a re-upload
Our files are built to **Futura Cod. 73 A6** exactly. Lulu's specs differ on every
axis, so a Lulu edition is a **sibling**, regenerated from source:

| | Futura (current) | Lulu (≈, verify) |
|---|---|---|
| Trim | A6 105×148 mm | **Pocket 108×174 mm** (4.25×6.875″) — *no true A6* |
| Bleed | 5 mm miolo / 15 mm cover | **3.175 mm** (0.125″) |
| Safety | 10 mm | **12.7 mm** (0.5″) |
| Cover | Futura gabarito, 17 mm spine | Lulu template + Lulu spine formula |
| Output | PDF/X-1a (`make_pdfx.sh`) | per Lulu upload reqs |

### Re-target checklist (when we circle back)
1. **Re-verify Lulu's current** Pocket (and hardcover?) spec + download their cover
   template from the pricing calculator (numbers above may have moved).
2. Add a **trim/bleed profile** to `forme.sty` (the `[bleed]` option already
   parameterises this — generalise to arbitrary trim + Lulu's 3.175 mm bleed).
3. **Regenerate the interior** at Lulu trim → **re-verify the 310-page invariant**
   (different trim reflows text; pages may shift — same situation as the 20 mm
   gutter experiment; claw back via prose trims if needed). Build **sequentially**,
   check **page count not overfull**.
4. **Rebuild `cover.py`** to Lulu's template + spine formula. Proportions change
   (108×174 is taller/wider than A6) → **eyeball the ghost-grid + two-up layout**,
   not just reflow. Keep the full-bleed ink overshoot fix.
5. **Order one Lulu proof** before listing publicly.
6. **List free, zero markup**, link from README.

**Sequencing:** do this *after* the Futura proof is confirmed good — no point
re-targeting a base that hasn't been validated in hand.

---

## Quick "get the book" summary (for the README, eventually)

- **Read/print it yourself, free:** clone the repo, `./build.sh` (or grab the PDFs
  from Releases). CC0 — do anything.
- **Order a copy at cost:** Lulu Bookstore link *(pending the Pocket edition)*.
- **Hardcover gift copies:** Futura, local *(author-run, not public)*.
