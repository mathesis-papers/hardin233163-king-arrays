# Extending Orrick's rectangle count to Barker's king-strip conjectures

Haobo Ma (ChronoAI Pte Ltd, Singapore), then Wenlin Zhang (National University
of Singapore; ChronoAI Pte Ltd, Singapore). November 16, 2026.

## Result

For every height `n >= 2` and width `k >= 2`, the literal normalized
eight-colour king-array count is

```
T(n,k) = 2^(n*k-4) * (2^(n-2) + 2^(k-2) - 1).
```

At width three this proves Colin Barker's generating-function and closed-form
conjectures in OEIS A233163, revision 8, FORMULA block dated October 9, 2018.
The rectangle and path proofs establish all twelve closed-form and
generating-function conjectures in A233162–A233167 and every empirical FORMULA
recurrence at widths 1 through 7 in A233168, revision 8.

Will Orrick proves the four-colour count for every rectangle in answer 2088242,
first posted January 8, 2017, expanded in revision 5 on January 9:
https://math.stackexchange.com/revisions/2088242/5 .
Britnell and Wildon prove the paired-colour path count in Proposition 8.1,
with its generating functions in Section 6.5:
https://arxiv.org/abs/1507.04803v1 .
David Eppstein's *Coloring kinggraphs* (April 11, 2019), final two paragraphs,
gives the labelled square-board count and zone construction:
https://11011110.github.io/blog/2019/04/11/coloring-kinggraphs.html .
Chang and Shrock's earlier chromatic-polynomial formulas supply the labelled
free-strip counts at widths two through four:
https://arxiv.org/abs/cond-mat/0005236v1 , Section II, equations (2.1), (2.10)
and (2.14)–(2.22).
The note gives the exact normalization fibres connecting the labelled counts to
the OEIS arrays, and a weighted-partition proof of the known path count.

## Build

Use Tectonic 0.17.0:

```
tectonic note.tex
```

Alternatively use a conventional LaTeX distribution:

```
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded; no external bibliography database is needed.
Run the standard-library Python 3 checker with:

```
python3 verify.py > verification.new.json
cmp verification.json verification.new.json
```

## Scientific scope

- `note.tex` proves the rectangle, path and all-width generating-series formulas
  for every stated size, and explicitly specializes the six Barker entries.
- `verify.py` independently counts literal eight-colour arrays at widths 1--3
  and heights 1--12, canonical four-pair and named four-colour rectangles at
  heights and widths 2--6,
  and canonical paths of lengths 1--12. It checks all 36 proper three-column
  pair boundaries against all 512 colour rows, and the eight normalized
  two-row seeds. Additional exact algebra checks cover the three-column
  series and closed forms for widths 3--7 through degree/height 210, recurrence
  identities at heights 4--30, geometric coefficients for widths 2--12 at heights
  2--30, square sizes 2--30, and path lengths 5--30.
  The path closed form and full series are checked through height/degree 210;
  Chang–Shrock's four-colour series are checked through degree 208.
  These are finite checks, not all-size enumeration. Full literal-count vectors
  are represented by SHA-256 digests alongside their first six values.
- The pinned Lean file
  https://github.com/the-omega-institute/trureturing/blob/0a197c5f83db6039a3c1177b20d31df4bfe95cd9/D5/S3/Combinatorics/TraceAvoidingArrays/HardinA233163KingStrip.lean
  defines the literal count in declaration `a` and proves the complete
  three-column rational series in declaration `result`, both in namespace
  `D5.S3.Combinatorics.TraceAvoidingArrays.HardinA233163KingStrip`.
  The wider rectangle and path statements are the written proofs in the note.
  Its imported `HardinA233196Strip.width_counting_bridge` identifies literal
  normalized cardinalities with finite row-transition sums at a fixed positive
  width; it is not the rectangle formula:
  https://github.com/the-omega-institute/trureturing/blob/0a197c5f83db6039a3c1177b20d31df4bfe95cd9/D5/S3/Combinatorics/TraceAvoidingArrays/HardinA233196Strip.lean .

The posing lines are 8--10 of
https://raw.githubusercontent.com/oeis/oeisdata/571197984aeda7b8b680fe3a1f6a43f9898cd441/seq/A233/A233163.seq .
Hardin is the sequence author; Barker is credited with the conjectures.
The linked rectangle source is https://oeis.org/A233168 .
The sibling conjectures have the same FORMULA line numbers 8--10 in
A233164, A233165 and A233166 revision 8, and A233167 revision 14:
https://oeis.org/A233164 , https://oeis.org/A233165 ,
https://oeis.org/A233166 , https://oeis.org/A233167 .
For the path, Barker's February 18, 2018 conjectures are at lines 10--12 of
A233162 revision 21: https://oeis.org/A233162 .

## Files and license

The source archive contains `note.tex`, `README.md`, `metadata.json`,
`verify.py`, and `verification.json`. The readable typeset note is `note.pdf`.
All original text and code in this package are licensed under CC BY 4.0
(`cc-by-4.0`): https://creativecommons.org/licenses/by/4.0/ .
