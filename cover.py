#!/usr/bin/env python3
"""Hardcover wrap for 'The Book That Plays Back' (Futura cod.73, A6 capa dura).
Geometry read from the gabarito: bleed 15mm/side, safety 10mm/side, hinge gap 8mm,
total width = 256 + spine.  Spine is PARAMETRIC -- set SPINE_MM from Futura's
calculadora de lombada (474 pages, Sulfite 90g, capa dura) for the final file.
Outputs a clean wrap and a proof with guide lines."""

SPINE_MM   = 22.0     # <-- ESTIMATE for 310 pp capa dura (~17.8mm block + boards/joints).
                      #     Replace with Futura's lombada calculator output before printing.
BLEED, SAFE, GAP, TRIM, H = 15.0, 10.0, 8.0, 105.0, 188.0
S = SPINE_MM
TOTAL_W = 2*BLEED + 2*TRIM + 2*GAP + S        # = 256 + S

# --- EAN-13 (Bookland) barcode reserve, sized to GS1 spec ---------------------
# GS1 nominal (100%) symbol, quiet zones INCLUDED: 37.29 x 25.93 mm.
# Allowed magnification 80-200%; printed here at 100% (nominal) for max scannability.
EAN_MAG  = 1.00
EAN_W    = 37.29 * EAN_MAG       # 37.29 mm  (bars + left 3.63 + right 2.31 quiet zones, scaled)
EAN_H    = 25.93 * EAN_MAG       # 25.93 mm  (bars + EAN digits)
EAN_TEXT = 3.2                   # ISBN human-readable line printed above the bars
EAN_PAD  = 1.5                   # extra white safety margin so dark artwork never touches a quiet zone
BOX_W    = EAN_W + 2*EAN_PAD             # ~40.3 mm  white reserve, full quiet zone
BOX_H    = EAN_H + EAN_TEXT + 2*EAN_PAD  # ~32.1 mm

back_x0, back_x1 = BLEED, BLEED+TRIM                       # back cover (CONTRACAPA)
sp_x0,   sp_x1   = back_x1+GAP, back_x1+GAP+S              # spine (lombada)
front_x0, front_x1 = sp_x1+GAP, sp_x1+GAP+TRIM            # front cover (CAPA)
back_cx, front_cx, sp_cx = (back_x0+back_x1)/2, (front_x0+front_x1)/2, (sp_x0+sp_x1)/2

FONTS="fonts/"   # relative to repo root, where cover.tex is compiled

ISBN13="978-65-02-14290-5"

# --- EAN-13 encoder (verified by round-trip + check digit; see git history) ----
_L={'0':'0001101','1':'0011001','2':'0010011','3':'0111101','4':'0100011',
    '5':'0110001','6':'0101111','7':'0111011','8':'0110111','9':'0001011'}
_G={'0':'0100111','1':'0110011','2':'0011011','3':'0100001','4':'0011101',
    '5':'0111001','6':'0000101','7':'0010001','8':'0001001','9':'0010111'}
_R={'0':'1110010','1':'1100110','2':'1101100','3':'1000010','4':'1011100',
    '5':'1001110','6':'1010000','7':'1000100','8':'1001000','9':'1110100'}
_PARITY={'0':'LLLLLL','1':'LLGLGG','2':'LLGGLG','3':'LLGGGL','4':'LGLLGG',
         '5':'LGGLLG','6':'LGGGLL','7':'LGLGLG','8':'LGLGGL','9':'LGGLGL'}
def _ean_checkdigit(d12):
    s=sum((1 if i%2==0 else 3)*int(c) for i,c in enumerate(d12))
    return str((10-s%10)%10)
def ean13_bits(isbn):
    d="".join(c for c in isbn if c.isdigit())
    assert len(d)==13 and _ean_checkdigit(d[:12])==d[12], f"bad EAN-13: {isbn}"
    bits="101"
    for ch,par in zip(d[1:7],_PARITY[d[0]]): bits+=(_L[ch] if par=='L' else _G[ch])
    bits+="01010"
    for ch in d[7:]: bits+=_R[ch]
    bits+="101"
    assert len(bits)==95
    return bits
def ean13_tikz(x0,y0,bar_w,bar_h,isbn,digit_h=2.6):
    """Draw EAN-13 with (x0,y0) the bottom of the DIGIT strip; bars sit above it.
    Guard bars (start/centre/end) extend down THROUGH the digit strip for the
    classic look; data bars stop at the strip top. Digits sit in the strip."""
    bits=ean13_bits(isbn); d="".join(c for c in isbn if c.isdigit())
    out=[]; guards={0,1,2,45,46,47,48,49,92,93,94}
    by0=y0+digit_h                                   # data-bar bottom = top of digit strip
    i=0
    while i<95:
        if bits[i]=='1':
            j=i
            while j<95 and bits[j]=='1': j+=1
            run_guard = all(k in guards for k in range(i,j))
            bottom = y0 if run_guard else by0           # guards drop to digit baseline
            out.append(rf"\fill[ink] ({x0+i*bar_w},{bottom}) rectangle ({x0+j*bar_w},{by0+bar_h});")
            i=j
        else: i+=1
    # human-readable, baseline centred in the digit strip
    ty=y0+0.5
    out.append(rf"\node[ink,font=\mono,anchor=base east,inner sep=0pt] at ({x0-0.4},{ty}) {{{d[0]}}};")
    out.append(rf"\node[ink,font=\mono,anchor=base,inner sep=0pt] at ({x0+(3+21)*bar_w},{ty}) {{{d[1:7]}}};")
    out.append(rf"\node[ink,font=\mono,anchor=base,inner sep=0pt] at ({x0+(50+21)*bar_w},{ty}) {{{d[7:]}}};")
    return "\n".join(out)

def doc(show_guides):
    # real motif sized to NEST inside the centre cell of the ghost grid below;
    # board = 3*c must sit clear inside one ghost cell (GC).
    motif_cx, motif_cy, c = front_cx, 80, 7.5       # tic-tac-toe motif, cell 7.5mm -> 22.5mm board
    gx0, gy0 = motif_cx-1.5*c, motif_cy-1.5*c
    def cell(col,row): return (gx0+col*c+c/2, gy0+(2-row)*c+c/2)
    marks=[]
    grid_lines = (rf"\draw[paper,line width=0.7pt] "
                  rf"({gx0+c},{gy0})--({gx0+c},{gy0+3*c}) ({gx0+2*c},{gy0})--({gx0+2*c},{gy0+3*c}) "
                  rf"({gx0},{gy0+c})--({gx0+3*c},{gy0+c}) ({gx0},{gy0+2*c})--({gx0+3*c},{gy0+2*c});")
    # a small finished position: book (O) just won across the top, its last move ringed
    board={0:'O',1:'O',2:'O',4:'X',6:'X',8:'X'}; last=1
    for i,v in board.items():
        cx,cy=cell(i%3,i//3)
        col = "signal" if i==last else "paper"
        if i==last:
            marks.append(rf"\draw[signal,line width=0.7pt] ({cx},{cy}) circle ({c*0.35}mm);")
        marks.append(rf"\node[{col},font=\bfseries] at ({cx},{cy}) {{{v}}};")
    marks="\n".join(marks)

    # --- ghost grid: a faint 3x3 behind the motif; the real board nests in the
    #     centre cell, the 8 others hold real, legally-reachable final positions
    #     ("every game already played"). Front panel only. ---
    GC=26.0                                   # ghost cell; frames the 22.5mm motif with margin
    GCW="ink!84!paper"; GMK="ink!82!paper"; GLN="ink!86!paper"   # tuning B (faint)
    ggx0,ggy0=motif_cx-1.5*GC, motif_cy-1.5*GC
    # just the tic-tac-toe "#" (no outer border) -- the four interior lines, full span
    ghost_grid=(rf"\draw[{GCW},line width=0.18pt] "
                rf"({ggx0+GC},{ggy0})--({ggx0+GC},{ggy0+3*GC}) ({ggx0+2*GC},{ggy0})--({ggx0+2*GC},{ggy0+3*GC}) "
                rf"({ggx0},{ggy0+GC})--({ggx0+3*GC},{ggy0+GC}) ({ggx0},{ggy0+2*GC})--({ggx0+3*GC},{ggy0+2*GC});")
    # real, legal final positions (3 X-wins, 3 O-wins, 2 draws) from the ttt tree
    GHOST_POS=["....OOXXX","OO.OX.XXX","XO.OXOX.X","..O.OXOXX",
               "OOO.XXXOX","X.O.OXO.X","OOXXXOOXX","XOXOOXXXO"]
    GHOST_CELLS=[(0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2)]  # all but centre
    gc=4.4                                     # ghost board cell -> ~13mm board in a 26mm cell
    ghost_games=[]
    for (col,row),pos in zip(GHOST_CELLS,GHOST_POS):
        bcx=motif_cx+(col-1)*GC; bcy=motif_cy+(1-row)*GC
        bx0,by0=bcx-1.5*gc,bcy-1.5*gc
        ghost_games.append(rf"\draw[{GLN},line width=0.15pt] "
            rf"({bx0+gc},{by0})--({bx0+gc},{by0+3*gc}) ({bx0+2*gc},{by0})--({bx0+2*gc},{by0+3*gc}) "
            rf"({bx0},{by0+gc})--({bx0+3*gc},{by0+gc}) ({bx0},{by0+2*gc})--({bx0+3*gc},{by0+2*gc});")
        for i,ch in enumerate(pos):
            if ch not in "XO": continue
            mx=bx0+(i%3)*gc+gc/2; my=by0+(2-i//3)*gc+gc/2
            ghost_games.append(rf"\node[{GMK},font=\scriptsize] at ({mx},{my}) {{{ch}}};")
    # clip the whole ghost layer to the front panel so nothing spills onto spine/back
    ghost=(rf"\begin{{scope}}\clip ({front_x0},0) rectangle ({front_x1},{H});"
           +"\n"+"\n".join([ghost_grid]+ghost_games)+"\n"+r"\end{scope}")

    # --- EAN-13 barcode rendered inside the white reserve box ---
    box_x0=back_x1-SAFE-BOX_W; box_y0=BLEED+SAFE
    bar_w=EAN_W/95.0                              # 37.29mm over 95 modules
    bar_x0=box_x0+EAN_PAD                         # left quiet zone = EAN_PAD
    dig_y0=box_y0+EAN_PAD                         # digit-strip bottom (above bottom pad)
    bar_h=EAN_H-EAN_TEXT                          # bar height above the digit strip
    barcode=ean13_tikz(bar_x0,dig_y0,bar_w,bar_h,ISBN13,digit_h=EAN_TEXT)

    guides=""
    if show_guides:
        cut0,cut1x,cut1y = BLEED, TOTAL_W-BLEED, H-BLEED
        guides=rf"""
\draw[cyan,dashed,line width=0.4pt] ({BLEED},{BLEED}) rectangle ({TOTAL_W-BLEED},{H-BLEED});
\draw[cyan,dashed,line width=0.3pt] ({BLEED+SAFE},{BLEED+SAFE}) rectangle ({TOTAL_W-BLEED-SAFE},{H-BLEED-SAFE});
\draw[magenta,dashed,line width=0.4pt] ({sp_x0},{BLEED})--({sp_x0},{H-BLEED}) ({sp_x1},{BLEED})--({sp_x1},{H-BLEED});
\node[cyan,font=\ttfamily\tiny] at ({TOTAL_W/2},{H-7}) {{wrap {TOTAL_W:.0f} x {H:.0f} mm  |  spine {S:.0f} mm  |  bleed {BLEED:.0f}  |  safe {SAFE:.0f}}};
"""
        bcx=back_x1-SAFE-BOX_W/2          # centre of the reserve box
        eanpct=int(round(EAN_MAG*100))    # avoid a literal % (starts a LaTeX comment)
        guides += rf"""\draw[magenta,dashed,line width=0.3pt] ({back_x1-SAFE-BOX_W},{BLEED+SAFE}) rectangle ({back_x1-SAFE},{BLEED+SAFE+BOX_H});
\node[ink,font=\ttfamily\tiny,align=center] at ({bcx},{BLEED+SAFE+BOX_H/2}) {{EAN-13 @ {eanpct}\%\\{BOX_W:.1f}x{BOX_H:.1f}mm\\ISBN pending}};
"""
    return rf"""\documentclass{{article}}
\usepackage[paperwidth={TOTAL_W}mm,paperheight={H}mm,margin=0mm]{{geometry}}
\usepackage{{fontspec}}\usepackage{{xcolor}}\usepackage{{tikz}}
\definecolor{{ink}}{{HTML}}{{1B2A33}}\definecolor{{signal}}{{HTML}}{{DC424C}}\definecolor{{paper}}{{HTML}}{{FFFFFF}}
\setmainfont{{Barlow}}[Path={FONTS},UprightFont=Barlow-Regular.ttf,BoldFont=Barlow-Bold.ttf,ItalicFont=Barlow-Italic.ttf,BoldItalicFont=Barlow-BoldItalic.ttf]
\newfontfamily\mono{{Space Mono}}[Path={FONTS},UprightFont=SpaceMono-Regular.ttf,BoldFont=SpaceMono-Bold.ttf,ItalicFont=SpaceMono-Italic.ttf,BoldItalicFont=SpaceMono-BoldItalic.ttf]
\pagestyle{{empty}}\setlength{{\parindent}}{{0pt}}
\begin{{document}}
\begin{{tikzpicture}}[x=1mm,y=1mm,remember picture,overlay,shift={{(current page.south west)}}]
\fill[ink] (0,0) rectangle ({TOTAL_W},{H});

% ---------- GHOST GRID (faint, behind the front motif) ----------
{ghost}

% ---------- FRONT COVER (CAPA, right panel) ----------
\node[paper,align=center] at ({front_cx},150)
  {{\bfseries\fontsize{{34}}{{37}}\selectfont The Book\\[1pt]\fontsize{{17}}{{19}}\selectfont That Plays Back}};
\draw[signal,line width=1.2pt] ({front_cx-22},134)--({front_cx+22},134);
\node[paper,align=center,font=\mono\small] at ({front_cx},126)
  {{an unbeatable game of tic-tac-toe\\--- and other games ---}};
{grid_lines}
{marks}
\node[paper,align=center,font=\mono\scriptsize] at ({front_cx},34)
  {{GEOSCIENTIFIC CHAOS UNION}};

% ---------- SPINE (LOMBADA) ----------
\node[paper,rotate=90,font=\bfseries\Large] at ({sp_cx},{H/2})
  {{The Book That Plays Back}};
\fill[signal] ({sp_cx-2},{H-22}) rectangle ({sp_cx+2},{H-18});
\fill[signal] ({sp_cx-2},18) rectangle ({sp_cx+2},22);
% publisher at the foot of the spine (convention: title centre, publisher foot)
\node[paper,rotate=90,font=\mono\small] at ({sp_cx},32)
  {{GCU}};

% ---------- BACK COVER (CONTRACAPA, left panel) ----------
% blurb vertically centred in the panel (optical balance between top air and the
% footer/barcode row); anchor=west pins its mid-height to the panel centre line.
\node[paper,align=left,font=\mono\footnotesize,text width=82mm,anchor=west] at ({back_x0+SAFE},{H/2})
  {{A book you play against. It moves; you reply by turning to the page it names ---
    where it has already answered.\\[4pt]
    Five games live inside. At tic-tac-toe, hexapawn and notakto it
    \textbf{{cannot lose}}; at twenty-one it always wins. But at nim it has left one
    crack --- play perfectly and you can \textbf{{beat it}}.\\[4pt]
    310 pages, 229 decisions, every reply precomputed by minimax --- and a matchbox
    machine that teaches itself to play.}};
% EAN-13 barcode in its white quiet-zone box, GS1 {EAN_MAG:.0%} ({BOX_W:.1f}x{BOX_H:.1f}mm),
% bottom-right of the back panel. Bars encoded from ISBN {ISBN13} (round-trip verified).
\fill[paper] ({back_x1-SAFE-BOX_W},{BLEED+SAFE}) rectangle ({back_x1-SAFE},{BLEED+SAFE+BOX_H});
{barcode}
% footer bottom-left; lines pre-broken so the long URL can't overflow into the
% barcode box. text width caps short of the box's left edge with clearance.
\node[paper,align=left,font=\mono\scriptsize,text width=40mm,anchor=south west] at ({back_x0+SAFE},{BLEED+SAFE})
  {{gentropic.org\\github.com/\\\hspace*{{1em}}gentropic/playback\\Typeset with Forme.\\CC0 / MIT.}};
{guides}
\end{{tikzpicture}}
\end{{document}}
"""

open("cover.tex","w",encoding="utf-8").write(doc(False))
open("cover_proof.tex","w",encoding="utf-8").write(doc(True))
print(f"spine={S}mm  total wrap = {TOTAL_W:.0f} x {H:.0f} mm")
print(f"back {back_x0:.0f}-{back_x1:.0f} | spine {sp_x0:.0f}-{sp_x1:.0f} | front {front_x0:.0f}-{front_x1:.0f}")
