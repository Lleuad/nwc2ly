# nwc2ly
A line by line converter from NoteWorthy Composer's nwctxt file to lilypond

### Currently handles (nwc version 2.75):
* notes and (multibar)rests (except multi voice chords and special note heads)
* all bar types (including EndingBar)
* key and time signatures
* clefs
* text
* all dynamics and dynamic variance (cresc., rfz, etc.)
* all tempo variance (rall., string., etc.) and tempo marking
* sustain pedal marks
* all performance styles (sostenuto, maestoso, etc.)
* Flow markings (coda, D.C., etc.)

### Still working on:
see [issues](../../issues?q=is%3Aopen+is%3Aissue+label%3A%22new+feature%22 "issues")

### Usage
#### without CLI
run `nwc2ly.py`
#### with CLI
save to file:
<code>python nwc2ly.py <i>nwctextfile</i>.nwctxt > <i>lilypondfile</i>.ly</code>

pipe directly into lilypond:
<code>python nwc2ly.py <i>nwctextfile</i>.nwctxt | lilypond --pdf -o <i>pdfout</i>.pdf -</code>

### License ###

This project is licensed under the BSD 3-Clause License
