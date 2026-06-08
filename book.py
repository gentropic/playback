#!/usr/bin/env python3
"""The Book That Plays Back -- tic-tac-toe (unbeatable, either side),
hexapawn (unbeatable), nim (BEATABLE), plus a build-the-learning-machine essay.
One PDF, master menu on page 1, fixed entry pages, the rest shuffled."""
import random
from functools import lru_cache
def place(b,i,m): return b[:i]+(m,)+b[i+1:]
def other(m): return 'O' if m=='X' else 'X'
EMPTY=('.',)*9

# ===================== TIC-TAC-TOE =====================
WIN=[(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
NAMES=["top-left","top-centre","top-right","middle-left","centre",
       "middle-right","bottom-left","bottom-centre","bottom-right"]
def twin(b):
    for a,c,d in WIN:
        if b[a]!='.' and b[a]==b[c]==b[d]: return b[a]
    return None
def full(b): return '.' not in b
def emp(b):  return [i for i,v in enumerate(b) if v=='.']
@lru_cache(maxsize=None)
def tmm(b,t):
    w=twin(b)
    if w=='X': return 1
    if w=='O': return -1
    if full(b): return 0
    v=[tmm(place(b,i,t),other(t)) for i in emp(b)]
    return max(v) if t=='X' else min(v)
def tbook(board,book):
    sign=1 if book=='X' else -1; best=ch=None
    for i in emp(board):
        nb=place(board,i,book); val=tmm(nb,other(book))
        if twin(nb)==book: trap=999
        elif full(nb): trap=-1
        else: trap=sum(1 for o in emp(nb) if tmm(place(nb,o,other(book)),book)==sign)
        key=(sign*val,trap,-i)
        if best is None or key>best: best,ch=key,i
    return ch
ttt={}
def tterm(b,book,oc,last):
    k=('ttt',b,book)
    if k not in ttt: ttt[k]={'board':b,'book':book,'type':'end','last':last,'oc':oc}
    return k
def texplore(b,book,last):
    k=('ttt',b,book)
    if k in ttt: return
    pl=other(book); node={'board':b,'book':book,'type':'play','last':last,'moves':{}}
    ttt[k]=node
    for s in emp(b):
        pb=place(b,s,pl)
        if twin(pb)==pl: node['moves'][s]=tterm(pb,book,'lose',s); continue
        if full(pb): node['moves'][s]=tterm(pb,book,'draw',s); continue
        bm=tbook(pb,book); xb=place(pb,bm,book)
        if twin(xb)==book: node['moves'][s]=tterm(xb,book,'win',bm)
        elif full(xb): node['moves'][s]=tterm(xb,book,'draw',bm)
        else: texplore(xb,book,bm); node['moves'][s]=('ttt',xb,book)
ttt_A=('ttt',place(EMPTY,0,'X'),'X'); texplore(place(EMPTY,0,'X'),'X',0)  # book opens corner
ttt_B=('ttt',EMPTY,'O');             texplore(EMPTY,'O',None)             # you open
assert not any(n['type']=='end' and n['oc']=='lose' for n in ttt.values()), "TTT book can lose!"

# ===================== HEXAPAWN =====================
def hmoves(board,side):
    opp='B' if side=='W' else 'W'; out=[]
    for i,v in enumerate(board):
        if v!=side: continue
        r,c=divmod(i,3); nr=r-1 if side=='W' else r+1
        if 0<=nr<=2:
            fi=nr*3+c
            if board[fi]=='.': out.append((i,fi,place(place(board,i,'.'),fi,side)))
            for nc in (c-1,c+1):
                if 0<=nc<=2 and board[nr*3+nc]==opp:
                    ci=nr*3+nc; out.append((i,ci,place(place(board,i,'.'),ci,side)))
    return out
def hwin(nb,side,to):
    if side=='W' and to//3==0: return True
    if side=='B' and to//3==2: return True
    return ('B' if side=='W' else 'W') not in nb
def osd(s): return 'B' if s=='W' else 'W'
@lru_cache(maxsize=None)
def hval(board,side):
    mv=hmoves(board,side)
    if not mv: return -1
    for frm,to,nb in mv:
        if hwin(nb,side,to) or hval(nb,osd(side))==-1: return 1
    return -1
HP_START=('B','B','B','.','.','.','W','W','W')
def hbook(board):
    mv=hmoves(board,'B'); win=[]
    for frm,to,nb in mv:
        if hwin(nb,'B',to): win.append((frm,to,nb,True))
        elif hval(nb,'W')==-1: win.append((frm,to,nb,False))
    pool=win if win else [(f,t,nb,False) for f,t,nb in mv]
    pool.sort(key=lambda x:(1 if x[3] else 0,-x[2].count('W'),-x[1]),reverse=True)
    return pool[0]
hp={}
def hterm(b,oc,last):
    k=('hp',b)
    if k not in hp: hp[k]={'board':b,'type':'end','last':last,'oc':oc}
    return k
def hexplore(board,last):
    k=('hp',board)
    if k in hp: return
    mv=hmoves(board,'W')
    if not mv: hp[k]={'board':board,'type':'end','last':last,'oc':'lose'}; return
    node={'board':board,'type':'play','last':last,'moves':{}}; hp[k]=node
    for frm,to,nb in mv:
        if hwin(nb,'W',to): node['moves'][(frm,to)]=hterm(nb,'humanwin',None); continue
        bfrm,bto,bnb,bw=hbook(nb)
        if bw: node['moves'][(frm,to)]=hterm(bnb,'lose',bto)
        else: hexplore(bnb,bto); node['moves'][(frm,to)]=('hp',bnb)
hexplore(HP_START,None)
assert not any(n['type']=='end' and n['oc']=='humanwin' for n in hp.values()), "HP book can lose!"

# matchbox count: reachable Black-to-move positions with a real choice, mirror-reduced
def mirror(b): return tuple(b[r*3+(2-c)] for r in range(3) for c in range(3))
bpos=set(); seen=set()
def enum_all(board,side):
    if (board,side) in seen: return
    seen.add((board,side)); mv=hmoves(board,side)
    if side=='B' and len(mv)>=2: bpos.add(board)
    for frm,to,nb in mv:
        if hwin(nb,side,to): continue
        enum_all(nb,osd(side))
enum_all(HP_START,'W')
BOXES=len(set(min(b,mirror(b)) for b in bpos))

# ===================== NIM (beatable) =====================
NIM_START=(3,5,7)
def nbook(h):
    x=0
    for v in h: x^=v
    if x!=0:
        for i,v in enumerate(h):
            t=v^x
            if t<v: nh=list(h); nh[i]=t; return tuple(nh),i,v-t
    i=max(range(len(h)),key=lambda j:h[j]); nh=list(h); nh[i]-=1; return tuple(nh),i,1
nim={}
def nterm(h,oc,act):
    k=('nim',h)
    # terminals share board (0,0,0); namespace by outcome to keep both messages
    k=('nim',h,oc)
    if k not in nim: nim[k]={'heaps':h,'type':'end','oc':oc,'act':act}
    return k
def nexplore(h,act):
    k=('nim',h)
    if k in nim: return
    node={'heaps':h,'type':'play','act':act,'moves':{}}; nim[k]=node
    for i,v in enumerate(h):
        for take in range(1,v+1):
            nh=list(h); nh[i]-=take; nh=tuple(nh)
            if sum(nh)==0: node['moves'][(i,take)]=nterm(nh,'humanwin',None); continue
            bb,bi,bt=nbook(nh)
            acttxt=f"The book took {bt} from Row {chr(65+bi)}."
            if sum(bb)==0: node['moves'][(i,take)]=nterm(bb,'lose',acttxt)
            else: nexplore(bb,acttxt); node['moves'][(i,take)]=('nim',bb)
nexplore(NIM_START,None)
assert any(n['type']=='end' and n['oc']=='humanwin' for n in nim.values()), "Nim must be winnable!"
NIM_KEY=('nim',NIM_START)

# ===================== NOTAKTO (misere TTT, both play X) =====================
def nk_line(b,i):                          # does placing X at i complete a line?
    bb=place(b,i,'X')
    return any(bb[a]==bb[c]==bb[d]=='X' for a,c,d in WIN)
@lru_cache(maxsize=None)
def nk_win(b):                             # True if player to move wins (misere)
    safe=[i for i in emp(b) if not nk_line(b,i)]
    if not safe: return False              # every move makes a line -> mover loses
    return any(not nk_win(place(b,i,'X')) for i in safe)
def nk_book(b):                            # book to move, winning: pick trappiest safe win
    safe=[i for i in emp(b) if not nk_line(b,i)]
    best=ch=None
    for i in safe:
        nb=place(b,i,'X')
        if nk_win(nb): continue            # leaves opponent winning -> skip
        opp_safe=[j for j in emp(nb) if not nk_line(nb,j)]
        traps=sum(1 for j in opp_safe if not nk_win(place(nb,j,'X')))  # opp losing replies
        # fewer escapes for opponent is better; here all of opp's safe moves lose anyway
        key=(-len(opp_safe),-i)
        if best is None or key>best: best,ch=key,i
    if ch is None: ch=safe[0]              # losing position (shouldn't happen for book)
    return ch
NK_FIRST = nk_win(EMPTY)                    # does the first player win?
notakto={}
def nk_term(b,oc,last):
    k=('nk',b,oc)
    if k not in notakto: notakto[k]={'board':b,'type':'end','oc':oc,'last':last}
    return k
def nk_explore(b,last):
    k=('nk',b)
    if k in notakto: return
    node={'board':b,'type':'play','last':last,'moves':{}}; notakto[k]=node
    for s in emp(b):
        if nk_line(b,s):                   # human completes a line -> human loses
            node['moves'][s]=nk_term(place(b,s,'X'),'lose',s); continue
        hb=place(b,s,'X')
        # book to move; if book has no safe move it must complete a line -> human wins
        if not [j for j in emp(hb) if not nk_line(hb,j)]:
            node['moves'][s]=nk_term(place(hb,nk_book_forced(hb),'X'),'humanwin',None); continue
        bm=nk_book(hb); xb=place(hb,bm,'X')
        node['moves'][s]=('nk',xb); nk_explore(xb,bm)
def nk_book_forced(b):
    return emp(b)[0]
# If book is FIRST, book opens; the start page is after book's first move.
if NK_FIRST:
    _bm=nk_book(EMPTY); NK_START_BOARD=place(EMPTY,_bm,'X'); _bl=_bm
else:
    NK_START_BOARD=EMPTY; _bl=None
nk_explore(NK_START_BOARD,_bl)
assert not any(n['type']=='end' and n['oc']=='humanwin' for n in notakto.values()), "Notakto book can lose!"
NK_KEY=('nk',NK_START_BOARD)

# ===================== TWENTY-ONE (subtraction 1-3, misere: last loses) =====================
SUB_START=21; SUB_MAX=3
@lru_cache(maxsize=None)
def sub_win(n):                            # True if player to move wins; misere: taking last loses
    if n==0: return True                   # opponent took the last -> they lost -> mover already won
    if n==1: return False                  # must take the last -> mover loses
    return any(not sub_win(n-k) for k in range(1,SUB_MAX+1) if n-k>=0)
def sub_book(n):                           # book to move, winning take
    for k in range(1,SUB_MAX+1):
        if n-k>=0 and not sub_win(n-k): return k
    return 1
SUB_FIRST = sub_win(SUB_START)
sub={}
def sub_term(n,oc,act):
    k=('sub',n,oc)
    if k not in sub: sub[k]={'n':n,'type':'end','oc':oc,'act':act}
    return k
def sub_explore(n,act):
    k=('sub',n)
    if k in sub: return
    node={'n':n,'type':'play','act':act,'moves':{}}; sub[k]=node
    for take in range(1,SUB_MAX+1):
        if n-take<0: continue
        m=n-take
        if m==0: node['moves'][take]=sub_term(0,'lose',None); continue   # human took last -> loses
        bk=sub_book(m); m2=m-bk
        act2=f"The book takes {bk}."
        if m2==0: node['moves'][take]=sub_term(0,'humanwin',act2)        # book took last -> book loses
        else: node['moves'][take]=('sub',m2); sub_explore(m2,act2)
if SUB_FIRST:
    _bk=sub_book(SUB_START); SUB_START_N=SUB_START-_bk; _sa=f"The book takes {_bk}."
else:
    SUB_START_N=SUB_START; _sa=None
sub_explore(SUB_START_N,_sa)
assert not any(n['type']=='end' and n['oc']=='humanwin' for n in sub.values()), "21 book can lose!"
SUB_KEY=('sub',SUB_START_N)

# ===================== PAGE ASSIGNMENT =====================
import math
allgame={}
for d in (ttt,hp,nim,notakto,sub): allgame.update(d)
fixed=[ttt_B, ttt_A, ('hp',HP_START), NK_KEY, NIM_KEY, SUB_KEY]
rest=[k for k in allgame if k not in fixed]
rest.append(('orphan',))                     # one page no move points to; hides in the shuffle
random.Random(43).shuffle(rest)
order=fixed+rest
ESSAY=[('essay',i) for i in range(3)]
canon={}
for b in bpos:
    key=min(b,mirror(b))
    if key not in canon: canon[key]=hmoves(key,'B')
KIT_POSITIONS=sorted(canon.items())
KIT_PER=6; KIT_N=math.ceil(len(KIT_POSITIONS)/KIT_PER)
# ---- layout helpers, shared by both editions ----
def children(k):
    n=allgame.get(k)
    if not n or n.get('type')!='play': return set()
    return set(n['moves'].values())
def linked(a,b): return (b in children(a)) or (a in children(b))
_pageof={}; _compact=False; _FIRSTGRID=set()
def REF(k):
    pg,slot=_pageof[k]
    if slot is None: return str(pg)
    return f"{pg}"+("U" if slot==0 else "L")
# history-of-machines track, distributed across physical pages
MILESTONES=[
 r"1834 --- Babbage imagines a\\noughts-and-crosses engine",
 r"1940 --- the Nimatron plays Nim\\at the New York World's Fair",
 r"1950 --- Bertie the Brain:\\tic-tac-toe in light bulbs",
 r"1950 --- Shannon's blueprint\\for a chess machine",
 r"1951 --- the Nimrod computer\\plays Nim before crowds",
 r"1952 --- Turing's paper machine\\plays a full game of chess",
 r"1959 --- Samuel's draughts\\program learns from itself",
 r"1961 --- Michie's MENACE:\\304 matchboxes learn noughts",
 r"1962 --- Gardner's hexapawn box\\--- the one this book builds",
 r"1992 --- TD-Gammon teaches\\itself world-class backgammon",
 r"1994 --- Chinook takes the\\checkers crown from humans",
 r"1997 --- Deep Blue defeats\\Kasparov over the board",
 r"2016 --- AlphaGo beats\\Lee Sedol four games to one",
 r"2017 --- AlphaZero learns chess,\\shogi and Go from only the rules"]

# ===================== RENDERERS =====================
def cell_name(i): return f"{chr(97+i%3)}{3-i//3}"
def ttt_tikz(b,last,sc=0.95):
    r=[rf"\begin{{tikzpicture}}[scale={sc}]",
       r"\draw[line width=1.2pt] (1,0)--(1,3) (2,0)--(2,3) (0,1)--(3,1) (0,2)--(3,2);"]
    for i,v in enumerate(b):
        if v=='.': continue
        cx,cy=i%3+0.5,3-i//3-0.5
        if i==last:
            r.append(rf"\draw[ink,line width=1pt] ({cx},{cy}) circle (0.42);")
            r.append(rf"\node at ({cx},{cy}) {{\bookmark{{{v}}}}};")
        else:
            r.append(rf"\node at ({cx},{cy}) {{\pmark{{{v}}}}};")
    r.append(r"\end{tikzpicture}"); return "\n".join(r)
def ttt_nav(b,last,cellpages,sc=1.05):
    cf=r"\footnotesize" if sc>=1 else r"\scriptsize"
    r=[rf"\begin{{tikzpicture}}[scale={sc}]",
       r"\draw[line width=1.2pt] (1,0)--(1,3) (2,0)--(2,3) (0,1)--(3,1) (0,2)--(3,2);"]
    for i,v in enumerate(b):
        cx,cy=i%3+0.5,3-i//3-0.5
        if v!='.':
            if i==last:
                r.append(rf"\draw[ink,line width=1pt] ({cx},{cy}) circle (0.42);")
                r.append(rf"\node at ({cx},{cy}) {{\bookmark{{{v}}}}};")
            else:
                r.append(rf"\node at ({cx},{cy}) {{\pmark{{{v}}}}};")
        elif i in cellpages:
            r.append(rf"\node[text=signal,font=\fmdata{cf}] at ({cx},{cy}) {{{cellpages[i]}}};")
    r.append(r"\end{tikzpicture}"); return "\n".join(r)
def hp_tikz(b,last,sc=0.95):
    r=[rf"\begin{{tikzpicture}}[scale={sc}]",
       r"\draw[line width=1pt] (0,0) rectangle (3,3);",
       r"\draw[line width=1pt] (1,0)--(1,3) (2,0)--(2,3) (0,1)--(3,1) (0,2)--(3,2);"]
    for i,v in enumerate(b):
        if v=='.': continue
        x=i%3+0.5; y=2-i//3+0.5
        if v=='W':
            r.append(rf"\draw[line width=1.4pt,fill=white] ({x},{y}) circle (0.33);")
            r.append(rf"\node at ({x},{y}) {{\small W}};")
        else:
            fc="signal" if i==last else "ink"
            r.append(rf"\draw[line width=1.4pt,fill={fc}] ({x},{y}) circle (0.33);")
            if i==last:
                r.append(rf"\draw[ink,line width=1pt] ({x},{y}) circle (0.46);")
            r.append(rf"\node at ({x},{y}) {{\small\textcolor{{white}}{{B}}}};")
    for c in range(3): r.append(rf"\node[gray,font=\tiny] at ({c+0.5},-0.3) {{{chr(97+c)}}};")
    for rr in range(3): r.append(rf"\node[gray,font=\tiny] at (-0.3,{2-rr+0.5}) {{{3-rr}}};")
    r.append(r"\end{tikzpicture}"); return "\n".join(r)
def nim_tikz(h):
    r=[r"\begin{tikzpicture}[scale=0.62]"]
    for ri,cnt in enumerate(h):
        y=(len(h)-1-ri)*1.1
        r.append(rf"\node[font=\small,anchor=east] at (-0.6,{y}) {{Row {chr(65+ri)}}};")
        for j in range(cnt): r.append(rf"\fill[ink] ({j*0.95},{y}) circle (0.3);")
        if cnt==0: r.append(rf"\node[gray,font=\footnotesize,anchor=west] at (0,{y}) {{taken}};")
    r.append(r"\end{tikzpicture}"); return "\n".join(r)
def sub_tikz(n):
    r=[r"\begin{tikzpicture}[scale=0.5]"]; per=11
    for idx in range(n):
        r.append(rf"\fill[ink] ({(idx%per)*0.9},{-(idx//per)*0.9}) circle (0.3);")
    r.append(r"\end{tikzpicture}"); return "\n".join(r)

def render(k):
    g=k[0]
    if g=='ttt':
        n=ttt[k]; b=n['board']; pl=other(n['book'])
        if n['type']=='end':
            sc=0.82 if _compact else 0.95
            o=[r"\begin{center}"+("" if _compact else r"\vspace*{0.4cm}"),ttt_tikz(b,n['last'],sc),
               (r"\vspace{0.15cm}" if _compact else r"\vspace{0.5cm}")+r"\end{center}"]
            if n['oc']=='win':
                o.append(r"\fmlabel{THE BOOK WINS}")
                o.append(r"\begin{center}\itshape Three in a row. Your game ends here.\end{center}")
            else:
                o.append(r"\fmlabel{A DRAW}")
                o.append(r"\begin{center}\itshape The grid is full --- you held the book to a tie. Nobody does better.\end{center}")
        else:
            cellpages={s:REF(n['moves'][s]) for s in n['moves']}
            sc=0.82 if _compact else 1.05
            o=[r"\begin{center}"+("" if _compact else r"\vspace*{0.6cm}"),ttt_nav(b,n['last'],cellpages,sc),
               (r"\vspace{0.1cm}" if _compact else r"\vspace{0.6cm}")+r"\end{center}"]
            if _compact:
                o.append(r"\begin{center}\small\textbf{Tic-tac-toe} --- play a square, turn to its number.\end{center}" if b==EMPTY
                         else rf"\begin{{center}}\small You play \pmark{{{pl}}}; turn to the number you choose.\end{{center}}")
            elif b==EMPTY:
                o.append(r"\begin{center}\large\textbf{Tic-tac-toe.} You move first. Play any square --- then turn to the page printed in it.\end{center}")
            else:
                o.append(rf"\begin{{center}}\large Your move --- you play \pmark{{{pl}}}.\\[2pt]\normalsize Play a square; turn to its number.\end{{center}}")
    elif g=='hp':
        n=hp[k]; b=n['board']
        o=[r"\begin{center}\vspace*{0.2cm}",hp_tikz(b,n['last']),r"\vspace{0.35cm}\end{center}"]
        if n['type']=='end':
            o.append(r"\fmlabel{THE BOOK WINS}")
            o.append(r"\begin{center}\itshape Your game ends here.\end{center}")
        else:
            if b==HP_START:
                o.append(rf"\begin{{center}}\large\textbf{{Hexapawn.}} You are \textbf{{W}} (bottom), moving up; you move first.\\[2pt]\small Pawns step straight forward or capture diagonally forward. Reach the top row, take all the book's pawns, or leave it stuck --- and you win. \emph{{Good luck: you cannot.}} (Machine to learn it: page \textbf{{{REF(ESSAY[0])}}}.)\end{{center}}")
            else:
                o.append(r"\begin{center}\large Your move (\textbf{W}).\end{center}")
            o.append(r"\vspace{0.1cm}\begin{center}{\fmdata\small\begin{tabular}{rl}")
            for (frm,to) in sorted(n['moves']):
                cap=" (capture)" if frm%3!=to%3 else ""
                o.append(rf"{cell_name(frm)}\,$\to$\,{cell_name(to)}{cap} & $\rightarrow$ page \textbf{{{REF(n['moves'][(frm,to)])}}}\\")
            o.append(r"\end{tabular}}\end{center}")
    elif g=='nim':
        n=nim[k]; h=n['heaps']
        o=[r"\begin{center}\vspace*{0.3cm}",nim_tikz(h),r"\vspace{0.3cm}\end{center}"]
        if n.get('act'): o.append(rf"\begin{{center}}\small\emph{{{n['act']}}}\end{{center}}")
        if n['type']=='end':
            if n['oc']=='humanwin':
                o.append(r"\fmlabel{YOU WIN}")
                o.append(r"\begin{center}\itshape You took the last token. The book has been beaten --- few pages can say that.\end{center}")
            else:
                o.append(r"\fmlabel{THE BOOK WINS}")
                o.append(r"\begin{center}\itshape The book took the last token. This one was winnable --- try again.\end{center}")
        else:
            if h==NIM_START:
                o.append(r"\begin{center}\large\textbf{Nim.} Take any number of tokens from a single row. Take the last token and you win.\\[2pt]\small\emph{This book can be beaten --- there is one perfect line. You move first.}\end{center}")
            else:
                o.append(r"\begin{center}\large Your move.\end{center}")
            o.append(r"\vspace{0.1cm}\begin{center}{\fmdata\footnotesize\begin{tabular}{rl}")
            for (i,take) in sorted(n['moves']):
                o.append(rf"take \textbf{{{take}}} from Row \textbf{{{chr(65+i)}}} & $\rightarrow$ page \textbf{{{REF(n['moves'][(i,take)])}}}\\")
            o.append(r"\end{tabular}}\end{center}")
    elif g=='nk':
        n=notakto[k]; b=n['board']
        if n['type']=='end':
            sc=0.82 if _compact else 0.95
            o=[r"\begin{center}"+("" if _compact else r"\vspace*{0.4cm}"),ttt_tikz(b,n['last'],sc),
               (r"\vspace{0.15cm}" if _compact else r"\vspace{0.5cm}")+r"\end{center}"]
            o.append(r"\fmlabel{YOU LOSE}")
            o.append(r"\begin{center}\itshape You completed three in a row --- and in this game, that loses.\end{center}")
        else:
            cellpages={s:REF(n['moves'][s]) for s in n['moves']}
            sc=0.82 if _compact else 1.05
            o=[r"\begin{center}"+("" if _compact else r"\vspace*{0.6cm}"),ttt_nav(b,n['last'],cellpages,sc),
               (r"\vspace{0.1cm}" if _compact else r"\vspace{0.6cm}")+r"\end{center}"]
            if _compact:
                o.append(r"\begin{center}\small\textbf{Notakto} --- three in a row \emph{loses}; play a square, turn to its number.\end{center}")
            elif b==EMPTY:
                o.append(r"\begin{center}\large\textbf{Notakto.} Both play \pmark{X}; three in a row \emph{loses}.\\[2pt]\normalsize You move first --- play a square, turn to its number.\end{center}")
            elif b==NK_START_BOARD:
                o.append(r"\begin{center}\large\textbf{Notakto.} Both play \pmark{X}; three in a row \emph{loses}.\\[2pt]\normalsize The book opened (ringed). Play a square; turn to its number.\end{center}")
            else:
                o.append(r"\begin{center}\large Your move --- play an open square (avoid three in a row).\\[2pt]\normalsize Turn to its number.\end{center}")
    elif g=='sub':
        n=sub[k]
        o=[r"\begin{center}\vspace*{0.4cm}",sub_tikz(n['n']),r"\vspace{0.3cm}\end{center}"]
        if n.get('act'): o.append(rf"\begin{{center}}\small\emph{{{n['act']}}}\end{{center}}")
        if n['type']=='end':
            o.append(r"\fmlabel{YOU LOSE}")
            o.append(r"\begin{center}\itshape You took the last token --- and in this game, that loses.\end{center}")
        else:
            if n['n']==SUB_START_N:
                o.append(r"\begin{center}\large\textbf{Twenty-one.} Take 1, 2 or 3 tokens. Whoever takes the \emph{last} token loses. You move first.\end{center}")
            else:
                o.append(r"\begin{center}\large Your move --- take 1, 2 or 3 tokens.\end{center}")
            o.append(r"\vspace{0.1cm}\begin{center}{\fmdata\small\begin{tabular}{rl}")
            for take in sorted(n['moves']):
                o.append(rf"take \textbf{{{take}}} & $\rightarrow$ page \textbf{{{REF(n['moves'][take])}}}\\")
            o.append(r"\end{tabular}}\end{center}")
    elif g=='orphan':
        o=[r"\thispagestyle{fancy}\vspace*{2.4cm}\begin{center}",
           r"{\bfseries\large You were not sent here.}\\[14pt]",
           r"\begin{minipage}{0.82\linewidth}\itshape ",
           r"No move points to this page; the shuffle simply let you fall through a crack "
           r"between two games. Hello.\\[6pt]",
           r"Everything in this book was decided before it was printed. Every reply you "
           r"will ever provoke is already here, in ink that will not change its mind --- so "
           r"in a sense the book has already finished every game it will ever play, and is "
           r"only waiting for you to catch up.\\[6pt]",
           r"There is nothing to win on this page. Turn back, choose a square, and lose "
           r"gracefully --- or, at Nim, don't.",
           r"\end{minipage}\\[16pt]",
           r"\begin{tikzpicture}\draw[signal,line width=1.2pt](0,0) circle (5mm);\end{tikzpicture}",
           r"\end{center}"]
    if _compact and _pageof.get(k,(0,None))[1] is not None:
        slot=_pageof[k][1]
        if _pageof[k][0] in _FIRSTGRID:             # first page of each grid game: spell it out
            init,rest=("U","pper") if slot==0 else ("L","ower")
            mk=rf"{{\large\bfseries{{\color{{signal}}{init}}}{rest}}}"
        else:
            mk=rf"{{\color{{signal}}\large\bfseries {'U' if slot==0 else 'L'}}}"
        o=[rf"\begin{{center}}{mk}\end{{center}}"]+o
    return "\n".join(o)

def render_essay(k):
    idx=k[1]
    if idx==0:
        body=rf"""\section*{{The matchbox that learns}}
The hexapawn book never loses because every reply was computed in advance. But
in 1962 Martin Gardner described something stranger: a pile of matchboxes, with
no computation inside, that \emph{{teaches itself}} to play hexapawn perfectly,
just by being punished when it loses.

\medskip\noindent\textbf{{What you need.}} About {BOXES} matchboxes (one for each
position the machine can face --- mirror-image positions share a box), and a
supply of coloured beads. The machine always plays \textbf{{Black}} (the side
that, with perfect play, wins). You play White and move first.

\medskip\noindent\textbf{{Set-up.}} On the lid of each box, draw the board
position that box stands for. Inside, drop one bead per legal Black move from
that position, using a fixed colour code (say: red = ``left pawn forward'',
blue = ``capture left'', and so on). A box with three legal moves starts with
three beads, one of each relevant colour."""
    elif idx==1:
        body=r"""\section*{The matchbox that learns \emph{(continued)}}
\noindent\textbf{Playing a game.} You move first. Then find the box whose lid
matches the current board, shake it, and draw one bead \emph{without looking}.
The colour you drew is the machine's move --- make it on the real board. Leave
that box open with its drawn bead sitting on top, so you can find it again at
the end. Repeat until someone wins.

\medskip\noindent\textbf{The one rule that does all the work.} When the game
ends:

\smallskip\noindent\emph{If the machine won}, return every drawn bead to its own
box. Nothing changes.

\smallskip\noindent\emph{If the machine lost}, punish it: take the \textbf{last}
bead it drew --- the move that walked into the loss --- and throw that bead away.
Return the others. That losing option can never be chosen again from that
position."""
    else:
        body=r"""\section*{The matchbox that learns \emph{(continued)}}
\noindent\textbf{What happens.} At first the machine plays at random and loses
often. But each loss permanently removes one bad move from one box. Bad moves
cannot come back, good moves survive --- so the bead population drifts, game by
game, toward perfect play. After a couple of dozen games the machine stops
losing entirely: it has discovered the same winning strategy this book has
printed, with no arithmetic and no instructions, only reward and punishment.

\medskip\noindent That is reinforcement learning, in beads. Donald Michie built
the same idea for tic-tac-toe in 1961 (a 304-box machine he called MENACE), and
the principle --- keep what wins, discard what loses --- is still, in spirit, how
modern game-playing programs are trained.

\medskip\noindent\emph{A nice touch:} if a box ever empties completely, it means
\emph{every} move from that position loses. Throw the box away too --- and remove
the bead that led \emph{into} it from the previous box. The punishment flows
backward through the game."""
    return r"\thispagestyle{fancy}"+body+r"\clearpage"

# ===================== STATIC MATTER + PER-EDITION ASSEMBLY =====================
def kit_card(board,moves):
    labs=[]
    for n,(frm,to,nb) in enumerate(moves):
        cap=r"\,$\times$" if frm%3!=to%3 else ""
        labs.append(rf"{chr(97+n)})~{cell_name(frm)}$\to${cell_name(to)}{cap}")
    return (r"\begin{minipage}[t]{0.47\linewidth}\centering\vspace{3pt}"
            r"\scalebox{0.52}{"+hp_tikz(board,None)+r"}\\[1pt]"
            r"{\fmdata\fontsize{6.5}{8}\selectfont "+r"\quad ".join(labs)+r"}\\[4pt]\end{minipage}")

def build_kit(hp_ref, essay_ref):
    cards=[kit_card(b,m) for b,m in KIT_POSITIONS]
    hdr=(r"\thispagestyle{fancy}{\bfseries\large Build the machine}\\[2pt]"
         r"{\color{signal}\rule{3cm}{1pt}}\\[6pt]"
         r"{\small Photocopy these pages, cut out the %d cards and glue each onto a matchbox "
         r"lid. In every box put one bead per lettered move --- one bead colour per letter. "
         r"Then play hexapawn (page \textbf{%s}), letting the boxes choose the machine's "
         r"moves, and punish a loss as page \textbf{%s} describes.}\\[8pt]"
         % (len(cards),hp_ref,essay_ref))
    pages=[]
    for pi in range(KIT_N):
        chunk=cards[pi*KIT_PER:(pi+1)*KIT_PER]
        s=hdr if pi==0 else r"\thispagestyle{fancy}\vspace*{2pt}"
        rows=[(c0+(r"\hfill"+c1 if c1 else "")) for c0,c1 in
              [(chunk[j],chunk[j+1] if j+1<len(chunk) else "") for j in range(0,len(chunk),2)]]
        s+=(r"\par\vspace{6pt}").join(rows)+r"\clearpage"
        pages.append(s)
    return pages

CERT = (r"\thispagestyle{fancy}\vspace*{1.0cm}\begin{center}"
        r"{\color{signal}\rule{2.4cm}{1pt}}\\[8pt]"
        r"{\bfseries\fontsize{22}{26}\selectfont Certificate}\\[3pt]"
        r"{\fmdata\small OF A GAME WELL PLAYED}\\[16pt]"
        r"{\large This certifies that}\\[12pt]"
        r"{\fmdata \underline{\hspace{6.5cm}}}\\[14pt]"
        r"{\large held \emph{The Book That Plays Back} to a \textbf{draw} at tic-tac-toe,\\[2pt]"
        r"or \textbf{beat} it at Nim --- a feat the book\\[2pt]concedes is possible, and rare.}\\[18pt]"
        r"{\fmdata\small signed \underline{\hspace{3.2cm}}\quad date \underline{\hspace{2.4cm}}}\\[18pt]"
        r"\begin{tikzpicture}\draw[signal,line width=1.4pt] (0,0) circle (8mm);"
        r"\node[signal,font=\bfseries] at (0,0) {GCU};\end{tikzpicture}"
        r"\end{center}\clearpage")

POS_TOTAL=sum(len(d) for d in (ttt,hp,nim,notakto,sub))
import hashlib
_src=open(__file__,'rb').read()
try: _src+=open('forme.sty','rb').read()
except FileNotFoundError: pass
SRC_HASH="sha256:"+hashlib.sha256(_src).hexdigest()[:12]

SOURCES = (r"\thispagestyle{fancy}\vspace*{0.4cm}"
  r"{\bfseries\large Sources \& further reading}\\[2pt]"
  r"{\color{signal}\rule{3.4cm}{1pt}}\\[8pt]"
  r"{\small "
  r"\textbf{The learning machine.} Martin Gardner, ``How to build a game-learning machine "
  r"and teach it to play and win,'' \emph{Scientific American} \textbf{206}(3), 1962, "
  r"138--154 (reprinted in \emph{The Unexpected Hanging}, 1969). The reinforcement idea is "
  r"Donald Michie's 304-box MENACE: \emph{The Computer Journal} \textbf{6}(3), 1963, "
  r"232--236.\par\smallskip "
  r"\textbf{The games.} Hexapawn: Gardner (1962, above); his 24 boxes reduce, by merging "
  r"mirror-images, to the %d here. Nim: C.\,L.\,Bouton, \emph{Annals of Mathematics} "
  r"\textbf{3} (1901--02), 35--39. Notakto: T.\,Plambeck \& G.\,Whitehead, ``The Secrets of "
  r"Notakto'' (2013). Twenty-one and the general theory of who-wins: Berlekamp, Conway \& "
  r"Guy, \emph{Winning Ways} (1982).\par\smallskip "
  r"\textbf{Kindred \& credits.} \emph{Tic Tac Tome} (Willy Yonkers, Quirk Books, 2014) is a "
  r"published predecessor in the same spirit; this book was conceived independently and "
  r"shares none of its text, code or page numbers. Engine, layout and text: Geoscientific "
  r"Chaos Union, rebuildable from book.py.\par}"
  r"\clearpage") % len(KIT_POSITIONS)

SG1 = (r"\thispagestyle{fancy}\vspace*{0.3cm}"
  r"{\bfseries\large Every game is Nim in disguise}\\[2pt]"
  r"{\color{signal}\rule{4.2cm}{1pt}}\\[8pt]"
  r"{\small "
  r"Nim looks like the slightest game in this book --- a few rows of tokens, take as many as "
  r"you please from a single row, last to take wins. It hardly seems to need a theory. Yet "
  r"Nim is the hidden skeleton of an entire family of games, and once you can see the "
  r"skeleton, games that look nothing alike reveal themselves as the same game wearing "
  r"different masks.\par\smallskip "
  r"\textbf{Impartial games.} The family is the games in which both players have exactly the "
  r"same moves available, so that only the position matters, never whose turn it is. Nim is "
  r"such a game; so is Twenty-one, where either player may take one, two or three; and so, in "
  r"spirit, is Notakto, where both hands draw the same \textbf{X}. Tic-tac-toe and hexapawn "
  r"are \emph{not} --- there you own your marks, your pawns, your one direction of travel. "
  r"Those are \emph{partisan} games, and they yield only to the patience of \emph{minimax}, "
  r"which is exactly how this book solved them.}"
  r"\clearpage")

SG2 = (r"\thispagestyle{fancy}\vspace*{0.3cm}"
  r"{\bfseries\large Every game is Nim in disguise \emph{(ii)}}\\[2pt]"
  r"{\color{signal}\rule{4.2cm}{1pt}}\\[10pt]"
  r"{\small "
  r"\textbf{A number for every position.} For impartial games under the \emph{normal} "
  r"convention --- last to move wins --- something remarkable holds. Give each position a "
  r"single whole number, its \emph{Grundy value}. The claim is audacious: a position whose "
  r"value is $n$ behaves \emph{exactly} like one Nim row of $n$ tokens --- same threats, same "
  r"replies, same fate. And a position whose value is \textbf{zero} is a loss for whoever "
  r"must move next, against perfect play. Find the zeros and you have found the losing "
  r"seats.\par\medskip "
  r"\textbf{Finding the number.} The rule is short and self-referential. Look at every "
  r"position you could move to, gather their Grundy values, and take the \emph{mex} --- the "
  r"\emph{minimum excludant}, the smallest of $0,1,2,\dots$ that is \emph{not} among them. "
  r"That is your value. A finished position offers no moves and so excludes nothing; its "
  r"value is $0$ --- a loss for the player who faces it, precisely as it should be.}"
  r"\clearpage")

SG3 = (r"\thispagestyle{fancy}\vspace*{0.3cm}"
  r"{\bfseries\large Every game is Nim in disguise \emph{(iii)}}\\[2pt]"
  r"{\color{signal}\rule{4.2cm}{1pt}}\\[10pt]"
  r"{\small "
  r"\textbf{Adding games together.} A Nim board is several rows at once; many a real game is "
  r"several smaller games at once. To combine them you do not add their Grundy values in the "
  r"ordinary way --- you add them in binary \emph{without carrying}, an operation called the "
  r"\emph{nim-sum} and written $\oplus$. The combined game is a loss for the mover exactly "
  r"when the nim-sum of its parts is zero; and whenever that sum is not zero, some move "
  r"always drives it to zero, handing the opponent a dead position. That is the whole secret "
  r"of Nim --- and the one perfect line by which you can beat the Nim in this book."
  r"\par\medskip "
  r"\textbf{The theorem.} Gathered together, these facts are the \emph{Sprague--Grundy "
  r"theorem}, found independently by Roland Sprague in 1935 and Patrick Grundy in 1939: "
  r"every impartial game under normal play is equal to a single Nim row. That is the precise "
  r"sense in which every impartial game is Nim in disguise.}"
  r"\clearpage")

SG4 = (r"\thispagestyle{fancy}\vspace*{0.3cm}"
  r"{\bfseries\large Every game is Nim in disguise \emph{(iv)}}\\[2pt]"
  r"{\color{signal}\rule{4.2cm}{1pt}}\\[10pt]"
  r"{\small "
  r"\textbf{Two complications, two doors.} First, \emph{mis\`ere} play, where the last move "
  r"\emph{loses} --- the rule in Notakto, and in Twenty-one as printed here. The tidy theory "
  r"cracks: mis\`ere games can be far subtler than their normal-play cousins, and Notakto "
  r"demanded an analysis of its own. Second, the \emph{partisan} games, which carry no single "
  r"nimber at all. For them John Conway showed that games themselves can be treated as a new "
  r"kind of \emph{number}, with their own arithmetic --- the surreal numbers --- a theory set "
  r"out in \emph{On Numbers and Games} and \emph{Winning Ways}. Tic-tac-toe and hexapawn live "
  r"in that wider country, and this book reached their verdicts the long way, by exhausting "
  r"every line.\par\medskip "
  r"\textbf{Either way.} So the book carries two kinds of certainty at once: impartial games "
  r"that are Nim in costume, and partisan games pinned down by sheer foresight. However "
  r"different the masks, the reply you will meet was always already here.}"
  r"\clearpage")

GLOSSARY = (r"\thispagestyle{fancy}\vspace*{0.3cm}"
  r"{\bfseries\large A small glossary}\\[2pt]"
  r"{\color{signal}\rule{3cm}{1pt}}\\[8pt]"
  r"{\footnotesize "
  r"\textbf{Impartial game.} Both players share the same moves; only the position matters. (Nim, Twenty-one, Notakto.)\par\smallskip "
  r"\textbf{Partisan game.} The players command different pieces or moves. (Tic-tac-toe, hexapawn.)\par\smallskip "
  r"\textbf{Normal play.} The last player able to move \emph{wins}; in \textbf{mis\`ere play} the last to move \emph{loses}.\par\smallskip "
  r"\textbf{P-position.} Losing for the player to move (the \emph{previous} player wins); Grundy value zero. \textbf{N-position}: winning for the player to move.\par\smallskip "
  r"\textbf{Grundy value (nimber).} The number an impartial position carries; it plays like a Nim row of that size.\par\smallskip "
  r"\textbf{mex.} The \emph{minimum excludant} --- the smallest non-negative integer absent from a set; it yields Grundy values.\par\smallskip "
  r"\textbf{Nim-sum ($\oplus$).} Addition in binary without carrying (XOR); how independent games combine.\par\smallskip "
  r"\textbf{Sprague--Grundy theorem.} Every impartial normal-play game equals a single nimber.\par\smallskip "
  r"\textbf{Minimax.} Exhaustive best-play search --- how the partisan games here were solved.\par\smallskip "
  r"\textbf{Zugzwang.} When merely being obliged to move is itself the disadvantage. \textbf{Fork}: one move making two winning threats at once.}"
  r"\clearpage")

TITLE = (r"\thispagestyle{empty}\vspace*{1.4cm}\begin{center}"
  r"{\bfseries\fontsize{30}{35}\selectfont The Book\\[2pt]That Plays Back}\\[10pt]"
  r"{\color{signal}\rule{4cm}{1.2pt}}\\[10pt]"
  r"{\large\itshape an unbeatable game of tic-tac-toe\\---\,and other games\,---}\\[16pt]"
  r"{\large Arthur Endlein Correia}\\[0.9cm]"
  r"\scalebox{0.66}{"+ttt_tikz(('O','O','O','.','X','.','X','.','X'),1)+r"}\\[0.9cm]"
  r"{\fmdata GEOSCIENTIFIC CHAOS UNION}\\[5pt]"
  r"{\fmdata\small Belo Horizonte $\cdot$ 2026}"
  r"\end{center}\clearpage")

VERSO = (r"\thispagestyle{empty}\vspace*{0.5cm}"
  r"\begin{center}\itshape\footnotesize "
  r"For Martin Gardner, who built machines from matchboxes;\\[2pt] "
  r"Claude Shannon, who taught machines to play;\\[2pt] "
  r"and John Conway, who turned games into numbers.\par"
  r"\end{center}"
  r"\vspace*{0.5cm}"
  r"{\fmdata\footnotesize\raggedright "
  r"First edition --- Belo Horizonte, 2026.\\ Geoscientific Chaos Union.\par\smallskip "
  r"ISBN 978-65-02-14290-5\par\smallskip "
  r"This book is free --- code MIT, text \& figures CC0: copy it, print it, remix it, "
  r"sell it (just keep the MIT notice on the code). Set in Barlow \& Space Mono (SIL OFL), "
  r"typeset with Forme; rebuilds identically from book.py and random seed 43.\par}"
  # --- ficha catalografica (CIP), Camara Brasileira do Livro, CIP 26-366952.0.
  #     ASCII LaTeX accents (\c{c} \~a \'i ...) so it is encoding-proof in print. ---
  r"\vspace*{0.3cm}"
  r"{\fmdata\fontsize{6.5}{7.8}\selectfont"
  r"\begin{center}Dados Internacionais de Cataloga\c{c}\~ao na Publica\c{c}\~ao (CIP)\\"
  r"(C\^amara Brasileira do Livro, SP, Brasil)\end{center}\vspace*{-3pt}"
  r"\setlength{\fboxsep}{4pt}\noindent\fbox{\parbox{\dimexpr\linewidth-10pt\relax}{\raggedright "
  r"Correia, Arthur Endlein\\"
  r"\hspace*{1.4em}The book that plays back : an unbeatable game of tic-tac-toe : and other "
  r"games / Arthur Endlein Correia. -- 1.~ed. -- Belo Horizonte, MG : Ed. do Autor, 2026.\\[2pt]"
  r"\hspace*{1.4em}ISBN 978-65-02-14290-5\\[2pt]"
  r"\hspace*{1.4em}1.~Educa\c{c}\~ao 2.~Jogos educativos 3.~Jogos educativos - Atividades I.~T\'itulo.\\[2pt]"
  r"26-366952.0\hfill CDD-371.397}}\\[1pt]"
  r"\begin{center}\'Indices para cat\'alogo sistem\'atico:\end{center}\vspace*{-5pt}"
  r"\hspace*{1.4em}1.~Jogos educativos : Educa\c{c}\~ao\quad 371.397\hfill{}"
  r"Livia Dias Vaz --- Bibliotec\'aria --- CRB-8/9638\par}"
  r"\clearpage")

INTRO = (r"\thispagestyle{fancy}\vspace*{0.2cm}"
  r"{\bfseries\large How this book plays}\\[2pt]"
  r"{\color{signal}\rule{3cm}{1pt}}\\[6pt]"
  r"{"
  r"This is a book you play against. You make a move, turn to the page the book sends you "
  r"to, and find it has already replied. Every answer here was worked out in advance, so the "
  r"book never thinks and never hesitates --- it simply knows.\par\smallskip "
  r"At tic-tac-toe, hexapawn and notakto it cannot lose, however well you play; the most you "
  r"can take is a draw. At Nim it has left one crack --- play perfectly and you can beat it. "
  r"Twenty-one it always wins. Which game is which, and where to start, is overleaf.\par\smallskip "
  r"Along the foot of every page runs a second, quieter thread: a history of the machines "
  r"that learned to play, from Babbage's daydream to AlphaZero. Play the book by hopping where "
  r"it sends you; read the foot straight through, cover to cover.\par\smallskip "
  r"Nothing here is hidden. Every move and page number was generated by a short program "
  r"from a single seed, and rebuilds identically. Turn the page to begin.\par}"
  r"\clearpage")

def emit(compact, suffix):
    global _pageof,_compact,_FIRSTGRID
    _compact=compact
    pageof={}; p=5; game_pages=[]
    if not compact:
        for k in order: pageof[k]=(p,None); game_pages.append([k]); p+=1
    else:
        grids =[k for k in order if k[0] in ('ttt','nk')]
        others=[k for k in order if k[0] not in ('ttt','nk')]
        used=[False]*len(grids)
        for i in range(len(grids)):
            if used[i]: continue
            used[i]=True; partner=None
            for j in range(i+1,len(grids)):
                if (not used[j]) and (not linked(grids[i],grids[j])): partner=j; break
            if partner is None:
                pageof[grids[i]]=(p,None); game_pages.append([grids[i]]); p+=1
            else:
                used[partner]=True
                pageof[grids[i]]=(p,0); pageof[grids[partner]]=(p,1)
                game_pages.append([grids[i],grids[partner]]); p+=1
        for k in others: pageof[k]=(p,None); game_pages.append([k]); p+=1
    ESSAY_P0=p
    for k in ESSAY: pageof[k]=(p,None); p+=1
    SG_P0=p; p+=4
    GLOSS_P=p; p+=1
    SOURCES_P=p; p+=1
    KIT_P0=p; p+=KIT_N
    CERT_P=p; p+=1
    COLO_P=p; p+=1
    N=p-1
    _pageof=pageof
    _firstof={}                                   # first page each grid family appears on
    for kk,(pg,slot) in pageof.items():
        if slot is not None and (kk[0] not in _firstof or pg<_firstof[kk[0]]):
            _firstof[kk[0]]=pg
    _FIRSTGRID=set(_firstof.values())
    msp=[round((i+1)*N/(len(MILESTONES)+1)) for i in range(len(MILESTONES))]
    MS_AT=dict(zip(msp,MILESTONES)); MS_TICKS=",".join(f"{x/N:.4f}" for x in msp)
    note_tail=(r" Some pages hold two boards: a page number with \textbf{U} or \textbf{L} (e.g.\ \textbf{12L}) means the upper or lower board there." if compact else "")
    MENU = (r"""\begin{center}\vspace*{0.4cm}
{\bfseries\fontsize{22}{26}\selectfont The Book\\That Plays Back}\\[4pt]
{\color{signal}\rule{3.6cm}{1.2pt}}\\[10pt]
\begin{minipage}{0.94\linewidth}\small
\textbf{Tic-tac-toe} --- cannot lose\\
\hspace*{1.4em}you open\dotfill\textbf{%s}\\
\hspace*{1.4em}the book opens\dotfill\textbf{%s}\\[4pt]
\textbf{Hexapawn} --- cannot lose\dotfill\textbf{%s}\\[4pt]
\textbf{Notakto} --- mis\`ere; cannot lose\dotfill\textbf{%s}\\[4pt]
\textbf{Nim} --- \emph{you can beat this one}\dotfill\textbf{%s}\\[4pt]
\textbf{Twenty-one} --- cannot lose\dotfill\textbf{%s}\\[8pt]
\textbf{How the machine learns}\dotfill\textbf{%s}\\[3pt]
\textbf{Every game is Nim in disguise}\dotfill\textbf{%s}\\[3pt]
\textbf{A small glossary}\dotfill\textbf{%s}\\[3pt]
\textbf{Sources \& further reading}\dotfill\textbf{%s}\\[3pt]
\textbf{Build it} --- matchbox kit\dotfill\textbf{%s}\\[3pt]
\textbf{Certificate}\dotfill\textbf{%s}\\[3pt]
\textbf{Colophon}\dotfill\textbf{%s}
\end{minipage}\\[10pt]
\begin{minipage}{0.9\linewidth}\footnotesize\centering
After each move, turn to the page shown --- the book has already replied, its move
\textbf{ringed}.%s
\end{minipage}
\end{center}\clearpage
""" % (REF(ttt_B),REF(ttt_A),REF(('hp',HP_START)),REF(NK_KEY),REF(NIM_KEY),REF(SUB_KEY),
       str(ESSAY_P0),str(SG_P0),str(GLOSS_P),str(SOURCES_P),str(KIT_P0),str(CERT_P),str(COLO_P),note_tail))
    KIT_PAGES=build_kit(REF(('hp',HP_START)), str(ESSAY_P0))
    COLO = (r"""\thispagestyle{fancy}\vspace*{0.15cm}
{\ttfamily\bfseries\Large Colophon}\\[5pt]
{\color{signal}\rule{3cm}{1pt}}\\[8pt]
{\ttfamily\small
{\raggedright\textbf{The Book That Plays Back}\par\smallskip
Every reply was precomputed by minimax, with a trap-maximising tie-break, then laid
out by book.py. The result is fully deterministic --- this exact book rebuilds from
the seed below.\par}
\smallskip
random seed \dotfill 43\\
pages \dotfill %d\\
games \dotfill 5\\
positions \dotfill %d\\
matchboxes \dotfill %d\\
source \dotfill %s\\
github \dotfill gentropic/playback\\[7pt]
{\raggedright Typeset with \textbf{Forme}, a print companion to Switchboard. Barlow \&
Space Mono, both OFL. Code MIT; text \& figures CC0.\par}
\smallskip
{\raggedright Printed by Futura Express, Belo Horizonte, 2026.\\
Miolo P\'olen 90\,g; capa dura, couch\'e fosco.\par}
\smallskip
reproduce: clone the repo,\\ then python3 book.py
}
""" % (N, POS_TOTAL, len(KIT_POSITIONS), SRC_HASH))
    DIV="\n"+r"\begin{center}{\color{signal}\rule{0.55\linewidth}{0.4pt}}\end{center}"+"\n"
    game_blocks=[]
    for grp in game_pages:
        if len(grp)==2: game_blocks.append(render(grp[0])+DIV+render(grp[1])+r"\clearpage")
        else: game_blocks.append(render(grp[0])+r"\clearpage")
    pages_seq=[TITLE,VERSO,INTRO,MENU]+game_blocks+[render_essay(k) for k in ESSAY]+[SG1,SG2,SG3,SG4,GLOSSARY]+[SOURCES]+KIT_PAGES+[CERT,COLO]
    assert len(pages_seq)==N, f"{suffix or 'wide'}: {len(pages_seq)} != {N}"
    body_parts=[]
    for idx,ps in enumerate(pages_seq,start=1):
        lab=MS_AT.get(idx,"")
        body_parts.append(rf"\pagebeat{{{idx/N:.4f}}}{{{lab}}}"+"\n"+ps)
    body="\n".join(body_parts)
    builds=[("color",f"the_book_{suffix}color.tex"),("bw",f"the_book_{suffix}bw.tex")]
    # print master: compact bw WITH 5mm bleed (Futura miolo gabarito wants it).
    # Same body -> must yield the same N; [bleed] grows paper+margins equally so
    # the text block (line breaks, pagination) is unchanged. Verified in build.
    if compact: builds.append(("bw,bleed",f"the_book_{suffix}bw_bleed.tex"))
    for mode,fn in builds:
        doc=("\\documentclass[11pt]{article}\n\\usepackage[%s]{forme}\n"%mode
             +"\\begin{document}\n\\def\\fmticks{%s}\n"%MS_TICKS+body+"\n\\end{document}\n")
        open(fn,"w",encoding="utf-8").write(doc)
    print(f"[{(suffix or 'wide_')[:-1] or 'wide'}] N={N}  game_pages={len(game_pages)}  "
          f"refs: ttt {REF(ttt_B)}/{REF(ttt_A)}  nk {REF(NK_KEY)}  hp {REF(('hp',HP_START))}")
    return N

emit(False, "")
emit(True, "compact_")
