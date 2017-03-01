# nwc2ly
A line by line converter from NoteWorthy Composer's nwctxt file to lilypond

### Currently handles (nwc version 2.75):
* notes and rests (except multi voice chords and special note heads)
* all bar types (including EndingBar)
* key and time signatures
* clefs
* text
* all dynamics and dynamic variance (cresc., rfz, etc.)
* all tempo variance (rall., string., etc.) and tempo marking
* sustain pedal marks
* all performance styles (sostenuto, maestoso, etc.)

### Still working on:
* Flow markings (coda, D.C., etc.)
* lyrics
* special endings
* multivoice chords and 'rest cords'

### Usage
save to file:
`python ./nwc2ly.py nwctextfile.nwctxt > lilypondfile.ly`

pipe directly into lilypond:
`python ./nwc2ly.py nwctextfile.nwctxt | lilypond --pdf -o pdfout.pdf -`
