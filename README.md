# nwc2ly
A line by line converter from NoteWorthy Composer's nwctxt file to lilypond

### Currently handles (nwc version 2.75):
* notes and rests (except chords)
* all bar types
* key and time signatures
* clefs (except percussion)

### Usage
save to file:
`python ./nwc2ly.py nwctextfile.nwctxt > lilypondfile.ly`

pipe directly into lilypond:
`python ./nwc2ly.py nwctextfile.nwctxt | lilypond --pdf - -o pdfout.pdf`
