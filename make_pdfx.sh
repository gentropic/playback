#!/usr/bin/env bash
# Wrap the press files as PDF/X-1a for Futura (Cod.73), per their instructions:
#   text -> curves, CMYK, PDF/X-1a, with correct Trim/Bleed boxes.
#
# Inputs (built by build.sh / book.py / cover.py):
#   the_book_compact_bw_bleed.pdf  (miolo, 115x158mm = A6 105x148 + 5mm bleed)
#   cover.pdf                      (capa,  273x188mm = 243x158 trim + 15mm bleed)
# Outputs:
#   miolo_x1a.pdf, cover_x1a.pdf   (these are what you upload)
#
# Requires Ghostscript. On this machine it's at the path below (not on PATH).
set -euo pipefail
export MSYS_NO_PATHCONV=1   # stop Git-Bash mangling /Name PostScript args

GS="${GS:-/c/Program Files/gs/gs10.07.1/bin/gswin64c.exe}"
ICC_SRC="$(dirname "$GS")/../iccprofiles/default_cmyk.icc"

# pdfwrite's PostScript 'file' op can't read a path with spaces ("Program Files"),
# so stage the ICC locally with a space-free name.
cp "$ICC_SRC" ./_cmyk.icc

# PDF/X output-intent definition (the embedded CMYK profile required by X-1a).
cat > _pdfx_def.ps <<'PS'
%!
[ /_objdef {icc_PDFX} /type /stream /OBJ pdfmark
[ {icc_PDFX} << /N 4 >> /PUT pdfmark
[ {icc_PDFX} (_cmyk.icc) (r) file /PUT pdfmark
[ /_objdef {OI} /type /dict /OBJ pdfmark
[ {OI} << /Type /OutputIntent /S /GTS_PDFX
   /OutputConditionIdentifier (Custom CMYK)
   /Info (default_cmyk.icc) /DestOutputProfile {icc_PDFX} >> /PUT pdfmark
[ {Catalog} << /OutputIntents [ {OI} ] >> /PUT pdfmark
PS

# $1 in, $2 out, $3 bleed-inset in pt (TrimBox = MediaBox shrunk by this on all sides).
x1a () {
  "$GS" -dPDFX -dBATCH -dNOPAUSE --permit-file-read=_cmyk.icc \
    -sColorConversionStrategy=CMYK -dNoOutputFonts \
    -dPDFXTrimBoxToMediaBoxOffset="{$3 $3 $3 $3}" \
    -dPDFXSetBleedBoxToMediaBox=true \
    -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress \
    -sOutputFile="$2" _pdfx_def.ps "$1"
}

# 5mm = 14.173pt (miolo bleed) ; 15mm = 42.520pt (cover bleed)
x1a the_book_compact_bw_bleed.pdf miolo_x1a.pdf 14.173
x1a cover.pdf                     cover_x1a.pdf  42.520

rm -f _cmyk.icc _pdfx_def.ps
echo "Wrote miolo_x1a.pdf and cover_x1a.pdf (PDF/X-1a, curves, CMYK)."
echo "Verify: pdffonts (expect none) + pdfinfo -box (TrimBox inset from MediaBox)."
