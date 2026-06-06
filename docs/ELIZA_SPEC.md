# ELIZA_SPEC.md — a hand-runnable ELIZA, in a book

*Working title: **THE PAPER THERAPIST** (GCU Field Kit, "operate-the-machine" line).
Provisional; this is a design sketch, not yet built.*

A book you **operate** with a pencil and a notepad. The book is the program; the
pad is the memory; **you are the processor.** You write a sentence, follow the
printed rules, and the book talks back — reproducing Weizenbaum's 1966 ELIZA
(the DOCTOR script) closely enough to run his *actual* published conversation by
hand. You converse with it, feel it "understand" you, and — because you ran every
step yourself — know exactly how hollow the trick is. That gap is the book.

---

## 0. Why this one (the thesis)

ELIZA is the inverse of *The Book That Plays Back*:

| | playback / Quire | ELIZA-by-hand |
|---|---|---|
| precomputed? | everything, frozen | **nothing** |
| reader does | navigates (flips) | **executes** (transforms + holds state) |
| arbitrary input? | no (can't freeze the infinite) | **yes** (conditioning happens at read-time, in your pencil) |

The "you can't ask a book arbitrary questions" wall (that playback hits) is walked
straight through here, because **the reader is the CPU.** This is the CARDIAC /
paper-computer lineage, not the phrasebook lineage. And it lands the oldest
question in the field — does symbol-manipulation constitute understanding? — by
making the reader *become* the symbol-manipulator and decide for themselves.

ELIZA was *already* "ELIZA Lite": Weizenbaum's whole point was that a trivially
simple program triggered profound projection of understanding. A version honest
about its own triviality is **more** faithful to his thesis, not less.

---

## 1. The core loop (one flip, one tick per turn)

```
1. Write your sentence on the PAD.
2. Scan the SPOTTER (inside front cover) top→bottom. First keyword
   present in your sentence wins.                    ← ranking, free
3. Flip to that keyword's page.                      ← the only flip
4. On the page: GRAB the right words (mat) → SWAP them (table, inside
   back cover) → drop into the next un-ticked TEMPLATE → tick it.
5. Write the Doctor's reply on the PAD. → back to 1.
```

Design invariant: **one glance at a fixed card + one flip + a couple of items held
in working memory, per turn.** Everything below serves that.

---

## 2. The two always-open cards (inside covers — never a "flip")

**Inside front — THE SPOTTER.** Priority order = ELIZA's keyword ranking, run as
"first hit wins". (Roster + priorities in §4.)

**Inside back — THE SWAP TABLE** (you only ever swap the short grabbed fragment):
```
 I / me ↔ you      my ↔ your      am ↔ are
 myself ↔ yourself      I'm ↔ you're      mine ↔ yours
```

---

## 3. Mats — the user interface of the computer

A **mat** is a printed cut-here diagram for one keyword's pattern: it turns ELIZA's
wildcard decomposition into "copy your words into labeled boxes." The mat *is* the
craft of the book — good mats = a machine that's a pleasure to run; clumsy mats =
a tax form. Three difficulty tiers:

- **🟢 grab-after (one anchor):** underline everything after the keyword. Trivial.
  *e.g. `my` → "my ⟨GRAB⟩" → "Your ⟨GRAB⟩."*
- **🟡 two-anchor:** find two landmarks, grab between/after them. The edge of
  pleasant; the showcase pages where the uncanny mirror happens.
  *e.g. `you…me` → "...YOU │⟨GRAB⟩│ ME..." → "What makes you think I ⟨GRAB⟩ you?"*
- **🔵 spot-only (no anchor):** keyword present → canned/cycling reply, no grab.

**Hard rule (see §7): never exceed two anchors.** Three captured fragments + their
swaps + template order exceeds human working memory (~4 chunks) and the machine
becomes unrunnable.

### Worked 🟡 page — `I am`
```
 ┌─ MATCH MAT ─ I AM ──────────────────────────┐
 │  your sentence:  "i think i am pretty tired" │
 │  ① find  I AM                                │
 │  ② everything AFTER it → THE GRAB:           │
 │        ...... I AM │⟨═══ GRAB ═══⟩           │
 │                    │  pretty tired           │
 │  ③ write the grab: [ ________________ ]      │
 └──────────────────────────────────────────────┘
  templates (pick leftmost un-ticked, then tick):
    ☐ How long have you been ⟨grab⟩?
    ☐ Do you believe it is normal to be ⟨grab⟩?
    ☐ Do you enjoy being ⟨grab⟩?
  ★ copy the swapped grab to a MEMORY line on the pad.
  ⚠ doesn't fit cleanly? say "Tell me more about that." → next turn.
```

---

## 4. The roster — "+3 = reproduces the 1966 session"

19 keywords. The base 16 carry ordinary conversation; the **+3** (`alike`, `like`,
`everyone`) are what let the book run Weizenbaum's *actual* published transcript —
they fire on its pivotal "[group] are all alike" / "you are like my [relative]" /
"everybody …" turns, which otherwise deflect to the fallback. Pinning the book to a
verifiable historical target doubles as the correctness test (§6).

| Keyword | Type | Reply gist | Pri |
|---|---|---|---|
| sorry | 🔵 | "Please don't apologise." | hi |
| **alike** | 🔵 | "In what way?" | hi |
| **like** (X like Y) | 🟡 | "What resemblance do you see?" | hi |
| I am / I'm | 🟡 | "How long have you been ⟨X⟩?" | hi |
| I feel | 🟢 | "Tell me more about feeling ⟨X⟩." | hi |
| I want / need | 🟡 | "What would it mean to you if you got ⟨X⟩?" | |
| I think | 🟢 | "Do you really think so?" | |
| I can't | 🟡 | "Maybe you could ⟨X⟩ now." | |
| because | 🔵 | "Is that the real reason?" | |
| why | 🔵 | "Why do you ask?" | |
| my | 🟢 | "Your ⟨X⟩." (the canonical echo) | |
| you (…me) | 🟡 | "What makes you think I ⟨X⟩ you?" | |
| **everyone** / everybody | 🔵 | "Who in particular are you thinking of?" | |
| mother/father → family | 🔵→ | "Tell me about your family." | |
| dream | 🔵 | "What does that suggest to you?" | |
| computer / machine | 🔵 | "Do machines worry you?" | |
| always | 🔵 | "Can you think of a specific example?" | |
| yes / no | 🔵 | "You seem quite certain." | |
| **(none found)** | 🔵 | cycling continuers + MEMORY recall | lo |

Tally: 🟢×3, 🟡×5, 🔵×11. Most turns hit a fast 🟢/🔵; the five 🟡 carry the magic.

**`mother→family`** demonstrates ELIZA's keyword-substitution trick (one word
redirects to another's rules) — a nice "look how sneaky the script is" beat.

---

## 5. The pad (printed session sheet — the only state)

```
 SESSION №___                 fallback seed: ___
 YOU ► ________________________________________
 DR  ◄ ________________________________________
 … (repeat) …
 ─ ★ MEMORY (bring these back when stuck) ──────
  1 ________________   2 ________________
```

The pad is RAM. The transcript is write-only (no burden); the 2-line MEMORY shelf
is the *only* state the reader maintains, and it's **passive** — read back solely
when the (none) page says so. (This is exactly the "reader logbook" from
GAMEBOOK_SPEC's state-machine mode. It's also why MEMORY stays on the ridge — see
§7.)

---

## 6. Correctness — the built-in oracle

Every keyword here appears in Weizenbaum's published 1966 DOCTOR transcript (CACM
9(1)). **Conformance test:** run that exact conversation through the book by hand;
each Doctor line must match (modulo the documented Lite divergences). This is the
ELIZA analogue of playback's navigation play-test — a historical ground truth, not
a vibe. Keyword **priorities** must match the published weights (first-hit-down-the-
Spotter = ELIZA's ranking); getting the order wrong makes replies feel "off".

**Known residual divergences** (acceptable, and material for the foot-essay): no
MEMORY *stack* (we fake a lite recall on the (none) page); generic rather than
hyper-specific reassembly on a couple of distress-flavoured lines (same mechanism,
plainer flavour); any multi-anchor decomposition beyond two anchors is simplified.

---

## 7. The limits — staying on the ridge (do NOT "upgrade")

The binding constraint is **human working memory per turn (~4 chunks)**, not pages.
The book may be arbitrarily long; each *turn* must stay small. Two cliffs bound the
pleasant zone — and they are the same two walls this whole line of books keeps
hitting:

| Axis | Comfortable | Wall — and why |
|---|---|---|
| Keywords | ≤20 | ~40+: Spotter scan slows (soft, just bulk) |
| **Anchors / pattern** | 1–2 | **3: exceeds working memory (HARD)** |
| Steps / turn | ~5 | flip-storms: rhythm dies, feels like compiling |
| Live state | 2 passive lines | conditioning on memory = reader hand-executes a join (miserable) |

**The trap, named:** the things that make ELIZA "more" (a MEMORY stack,
multi-anchor decompositions, rules that condition on history) are *exactly* the
things that make it un-hand-runnable. Precompute (Quire) hits combinatorial
explosion; hand-execution (this) hits working-memory explosion. **The pleasant zone
is a narrow ridge between two cliffs, and ELIZA-v1 sits almost on the peak** — that
is *why* it's the sweet spot, not a compromise short of one. Do not emulate upward;
that is not a bigger book, it is a worse one.

---

## 8. The philosophical payload (foot-essay + colophon)

- **Foot-essay**, page by page along the bottom (the playback timeline trick):
  ELIZA's origin (1966), the **ELIZA effect** (users projecting understanding onto a
  program Weizenbaum knew was hollow), his subsequent horror and *Computer Power and
  Human Reason* (1976), and the Chinese-Room connection (you, running rules over
  symbols you don't "understand," nonetheless conducting a conversation).
- **The honest-limit colophon** (the GCU signature move): *"The real DOCTOR could
  resurface your words from minutes ago. This one can't — notice how little you miss
  it. That gap is how much 'memory' you were imagining into a machine that had almost
  none."* And the meta-twist: *"Co-written by a symbol-manipulating machine. Whether
  the second author understood any of it is the subject of this book."*
- **Field anecdote worth including:** while drafting this, an automated content
  filter blocked ELIZA's own therapy-transcript lines — mistaking 1966 demo syntax
  for genuine present-day distress. A modern machine reacting to ELIZA's *surface
  form* without grasping its *context* is the Chinese Room happening to us, live.

---

## 9. Page budget

Square Field Kit format (~one idea per spread), v1 = 19 keywords:

| Section | Pages |
|---|---|
| Front matter (title, verso, dedication) | 4 |
| How to operate (tutorial, one fully-walked turn) | 8 |
| Inside-cover cards (Spotter + Swap) | 0 *(on the covers)* |
| 🟢 keywords ×3 | 3 |
| 🟡 keywords ×5 (the careful mats) | 5 |
| 🔵 keywords ×11 (two-up; small) | 6 |
| (none) fallback page | 1 |
| Worked full conversation (the 1966 session) | 6 |
| Foot-essay payload | 0 *(runs along the foot)* |
| Glossary + further reading + colophon | 5 |
| **Total** | **~38 pp** → round to **40** |

Comfortably Field-Kit scale; same proven pipeline, binding, and prepress
(`make_pdfx.sh`, `[bleed]`, CMYK) as the rest of the house. **Page count is a knob,
not a discovery** — ship the smallest machine that still feels alive.

---

## 10. Build order (de-risk before committing)

1. **Prototype ONE 🟡 page** (`I am`) end-to-end — mat, swap, templates, tally,
   escape line. If the hardest-tier page reads as *pleasant*, the book works. (Same
   "build the engine on one case first" discipline as playback.)
2. Then the tutorial + the (none) page (the two pieces that make it never-stuck).
3. Then the 1966 conformance run as the acceptance test.
4. Then fan out the remaining keywords.

Risks, ranked: (1) the 🟡 mats' legibility *is* the product; (2) keyword priority
must match the published weights; (3) two-anchor matching is the only non-mechanical
reader step — bias v1 toward single-anchor patterns, reserve two-anchor for
showcases.

---

*GCU. If built: code MIT, text/figures CC0 — like the rest of the house. Engine is
GAMEBOOK_SPEC's state-machine mode with the reader as executor rather than
navigator. Not yet built.*
