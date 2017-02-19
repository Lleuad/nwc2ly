# nwc2ly
A line by line converter of NoteWorthy Composer's nwctxt file to lilypond

### Currently handles (nwc version 2.0):
* notes and rests (except chords, slurs and articulation)
* all bar types
* key signatures

### Usage
save to file:
`python ./nwc2ly.py nwctextfile.nwctxt > lilypondfile.ly`

pipe directly into lilypond:
`python ./nwc2ly.py nwctextfile.nwctxt | lilypond --pdf - -o pdfout.pdf`
