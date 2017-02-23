# nwc2ly
A line by line converter from NoteWorthy Composer's nwctxt file to lilypond

### Currently handles (nwc version 2.75):
* notes and rests (except chords, multimeasure rest and special note heads)
* all bar types (including EndingBar)
* key and time signatures
* clefs
* text

### Usage
save to file:
`python ./nwc2ly.py nwctextfile.nwctxt > lilypondfile.ly`

pipe directly into lilypond:
`python ./nwc2ly.py nwctextfile.nwctxt | lilypond --pdf -o pdfout.pdf -`
