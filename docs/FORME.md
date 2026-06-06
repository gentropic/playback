# Forme

*A print companion to Switchboard.*

Forme is the print side of the GCU design language. Where Switchboard dresses
screens, Forme sets ink on paper: a small LaTeX package for books and booklets
that share the flight-deck character — Barlow and Space Mono, a slate ink, a
single signal red, and information carried by structure rather than decoration.

It is deliberately tiny. One trim size, one ink, one signal, three components.
The constraint is the point: a Forme book reads the same whether it is printed
in full colour or photocopied in black and white.

---

## Principle

> Information lives in shape, weight, position and label.
> Colour is a removable garnish: `[bw]` drops it without losing meaning.

Every Forme decision answers to that line. The signal colour never carries
meaning *alone* — a thing picked out in red is always also picked out by a ring,
a stamp, a weight, or a position, so the black-and-white edition loses nothing
but the warmth. This is what lets one source produce both a colour master and a
laser/photocopy master from the same file.

---

## Tokens

### Palette

Three roles, never more.

| Token | Role | Hex (sRGB) | RGB | CMYK build |
|---|---|---|---|---|
| `paper` | the ground | `#FFFFFF` | `255, 255, 255` | `0, 0, 0, 0` |
| `ink` | text, rules, structure | `#1B2A33` | `27, 42, 51` | `47, 18, 0, 80` |
| `signal` | the one thing to look at | `#DC424C` | `220, 66, 76` | `0, 70, 65, 14` |

In `[bw]` mode `signal` collapses onto `ink`, and `ink` darkens from slate to
true black for clean toner reproduction. Nothing else changes.

The hex/sRGB values are authoritative; the CMYK figures are a calculated build
(a reasonable FOGRA-ish starting point) — your press's own profile is the final
word, so hand the printer the hex and let them match.

**`signal` is a real Risograph ink.** It is *vermelho vivo* — the workhorse red
of Risotrip (the Rio de Janeiro Riso studio), cross-referenced to **Pantone
185 U**. This is deliberate: rather than approximate the indie-print world with an
offset red, Forme's signal *is* an actual drum you can walk a file into. A
Risograph edition therefore needs no palette shift on the red at all — `signal`
prints natively.

No Pantone number is *anchored* here (Pantone is closed, and 185 U is a waypoint,
not a dependency). If a job needs the colour matched in software against an open
deck, Stuart Semple's **Freetone** or the **Spot Matching System / Swatchos**
(free ASE downloads, ISO 12647-2) are the references — pick the nearest vivid red.

**Forme on Riso.** Because `signal` is already a Riso ink, a Risograph edition is
mostly a clean translation, with one caveat — the dark:

| Token | Riso drum | Note |
|---|---|---|
| `signal` `#DC424C` | **vermelho vivo** | Native — this *is* the ink (≈ Pantone 185 U). |
| `ink` `#1B2A33` | **black** `#000000` | Riso has no dark slate, so the slate gives way to true black. |
| `paper` | the stock | Riso is semi-transparent; the paper colour shows through. |

So a Riso edition keeps the red exactly and trades slate for black — a small,
honest shift, not a redesign. (Riso inks are semi-transparent and paper-dependent;
treat the dark as black-on-whatever-stock.)

### Type

| Role | Family | Used for |
|---|---|---|
| text | **Barlow** | running prose, headings, labels |
| data | **Space Mono** (`\fmdata`) | move lists, coordinates, folios, the timeline, the colophon |

Both are OFL. Barlow justifies cleanly at small measures; Space Mono's fixed
advance is doing real work, not styling — it tabulates page references and
coordinates into columns the eye can scan. The split is semantic: prose is
Barlow, *data is mono*.

### Trim & margins

A6, portrait, two-sided, with the binding allowance on the inner edge.

```
paperwidth   105 mm        inner (gutter)  14   mm
paperheight  148 mm        outer            8.5 mm
                           top              8.5 mm
                           bottom          12   mm
                           footskip         5.5 mm
```

The asymmetric inner/outer margins mirror on odd/even pages, so the gutter is
always the bound edge. The generous bottom margin is not slack — it houses the
timeline and the folio.

---

## Components

### 1. Mark — `\pmark{·}` / `\bookmark{·}`

The pieces on a board. `\pmark` is the reader's mark in `ink`; `\bookmark` is the
book's reply in `signal`. Both are `\Huge` and bold — sized for board cells, **not
for inline use** (a `\bookmark` dropped into a sentence will tower over it; use
`\textbf{}` in prose). Crucially, the book's move is *also* circled by a ring
drawn in the board code, so in `[bw]` the reply still reads even with the colour
gone.

### 2. Stamp — `\fmlabel{TEXT}`

A centred, ink-filled box with reversed (`paper`) mono text — an outcome or a
section tag, struck onto the page like a rubber stamp. Reads identically in
colour and b/w because it is built from `ink` + `paper`, never from `signal`.

```latex
\fmlabel{THE BOOK WINS}
\fmlabel{A DRAW}
```

### 3. Timeline + folio — `\fmtimeline`, driven by `\pagebeat` and `\fmticks`

The signature Forme component: a quiet second track running along the foot of
every page. A thin ink rule spans the bottom margin; `\fmticks` (a comma-list of
fractions in `[0,1]`) places tick marks along it; `\pagebeat{frac}{label}` per
page sets a `signal` dot at the current position and an optional caption beneath.
Read the book by hopping where it sends you; read the foot straight through, and
a parallel story unfolds at reading pace.

The **folio** rides just above the timeline, in bold mono, pushed to the outer
corner — bottom-right on recto, bottom-left on verso — and raised clear of the
rule so it never collides with the ticks, even at three digits.

A **fore-edge staircase index** is drawn in the same overlay: a small ink tab on
the outer edge whose vertical position descends as the page fraction advances.
Closed, the book shows a diagonal staircase down its fore-edge — a flip-aid and a
quiet bit of object-craft, free because the overlay already knows the fraction.

The timeline, folio, and fore-edge tab are all drawn in a `remember picture`
TikZ overlay, so they are **layout-neutral**: they never push text or change the
page count. (They do require **two XeLaTeX passes** to settle.)

### 4. Hatches — `\fmhatch{style}{w}{h}`, or `\draw[style]`

Tone and texture without colour. Four named fills, all drawn in `ink` so they
survive `[bw]` exactly as they look in colour — a hatch reads in pure black on a
photocopier where a grey tint would wash out. Use them for panels, callout
backgrounds, chart fills, or to weight a region of a page.

| Style | Pattern |
|---|---|
| `fmlines` | 45° single hatch (the default tone) |
| `fmgrid` | fine square grid |
| `fmdots` | dotted field (the lightest) |
| `fmcross` | crosshatch (the heaviest) |

Inline as a stamped rectangle, `\fmhatch{fmlines}{3cm}{1.2cm}`, or as a TikZ
style on any path: `\fill[fmgrid] (a) rectangle (b);` with an `ink` outline. As
with everything in Forme, the meaning is in the pattern, not the colour — so they
are safe to use anywhere the `[bw]` master has to hold.

---

## Options

```latex
\usepackage[color]{forme}      % slate ink + signal red (the colour master)
\usepackage[bw]{forme}         % true black, signal→ink (the print master)
\usepackage[bw,cropmarks]{forme}  % adds camera/registration marks (needs crop.sty + a larger sheet)
\usepackage[bw,bleed]{forme}   % +5mm print bleed on every side for the press
```

Colours are defined in **CMYK** (the press wants CMYK, not RGB); the hex/sRGB
values in the table above remain authoritative for screen, and the CMYK builds
here are what the package emits.

`bleed` grows the sheet by 5 mm on every side **and** adds 5 mm to every margin,
so the text block — and therefore line breaks and the page count — is identical
to the no-bleed build; only extra paper appears outside the trim. The foot
timeline, folio, and fore-edge tab are anchored to page edges, so `bleed` shifts
each of them back inward by 5 mm to stay on the trimmed page. Use it for the file
you hand the printer; use the plain build for screen/proof.

`color` (or `colour`) is the default. `bw` is the one you send to a mono press or
a photocopier. `cropmarks` overlays registration marks on an oversized sheet for
a bindery.

---

## Using Forme

A minimal document:

```latex
\documentclass[11pt]{article}
\usepackage[bw]{forme}
\begin{document}
\def\fmticks{0.1,0.3,0.5,0.7,0.9}   % where ticks sit along the foot
\pagebeat{0.42}{a caption for this page}
Body text in Barlow. Data — like coordinates or page refs — in {\fmdata 42}.
\fmlabel{A STAMPED OUTCOME}
\end{document}
```

Per-page, call `\pagebeat{frac}{label}` to advance the timeline dot; set
`\fmticks` once for the whole run. Everything else is ordinary LaTeX — Forme only
adds the trim, the palette, the two font roles, and the three components above.

---

## Relationship to Switchboard

Forme and Switchboard share a palette, a type pairing (Barlow + Space Mono), and
a temperament — cool, instrument-panel, information-first. They differ where the
medium demands it: Switchboard has hover, focus, and motion; Forme has gutters,
folios, fore-edges, and a `[bw]` press master. Think of them as the same voice
speaking on a screen and on paper.

---

*Forme is part of the Geoscientific Chaos Union toolkit. MIT-licensed. Barlow and
Space Mono are under the SIL Open Font License.*
