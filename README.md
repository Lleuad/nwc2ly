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
see [issues](/issues?q=is%3Aopen+is%3Aissue+label%3A%22new+feature%22 "issues")

### Usage
save to file:
`python ./nwc2ly.py nwctextfile.nwctxt > lilypondfile.ly`

pipe directly into lilypond:
`python ./nwc2ly.py nwctextfile.nwctxt | lilypond --pdf -o pdfout.pdf -`

### License ###

This project is licensed under the BSD 3-Clause License
