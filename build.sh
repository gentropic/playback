#!/usr/bin/env sh
# Build all four editions of "The Book That Plays Back".
#
# Requires:
#   - python3
#   - xelatex (TeX Live / MiKTeX)
#   - the fonts Barlow and Space Mono (both OFL); forme.sty expects them
#     under fonts/ — adjust the Path= entries there if yours live elsewhere.
#
# Two XeLaTeX passes are needed per file: the foot-timeline uses
# remember-picture overlays that only settle on the second pass.

set -e

python3 book.py

for f in the_book_color the_book_bw the_book_compact_color the_book_compact_bw; do
    xelatex -interaction=nonstopmode -halt-on-error "$f.tex"
    xelatex -interaction=nonstopmode -halt-on-error "$f.tex"
done

echo "Done."
echo "  wide:    the_book_color.pdf / the_book_bw.pdf      (547 pp)"
echo "  compact: the_book_compact_color.pdf / ..._bw.pdf   (310 pp)"
