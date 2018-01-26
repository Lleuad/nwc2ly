# nwc2ly
A line by line converter from [NoteWorthy Composer](https://noteworthycomposer.com/)'s filetypes to [LilyPond](http://lilypond.org/).

The goal is not to produce an exact copy of the score, NoteWorthy Composer isn't known for its pretty output after all. The main priority is to produce an easily editable file (relative mode, bar checks, etc.) and do any final tweaks in LilyPond, while still being able to do most of the grunt work in NoteWorthy.

### Currently handles (nwc version 2.75):
* notes and (multibar)rests (except special note heads)
* all bar types (including EndingBar)
* key and time signatures
* clefs
* text
* all dynamics and dynamic variance (cresc., rfz, etc.)
* all tempo variance (rall., string., etc.) and tempo marking
* sustain pedal marks
* all performance styles (sostenuto, maestoso, etc.)
* Flow markings (coda, D.C., etc.)
* Song info (Title, Author, etc.)

### Still working on:
* Multiple voices. It'll accept them, but it is still quite buggy and will require some cleanup.
* see [issues](../../issues?q=is%3Aopen+is%3Aissue+label%3A%22new+feature%22 "issues")

### Requirements
* python 3.2 or later

### Usage
#### without CLI
run `nwc2ly.py` and select the input file from the filedialog.
#### with CLI
save to file:<br>
<code>python nwc2ly.py <i>nwctextfile</i>.nwctxt <i>lilypondfile</i>.ly</code><br>
<code>python nwc2ly.py <i>nwcfile</i>.nwc <i>lilypondfile</i>.ly</code>

pipe directly into lilypond:<br>
<code>python nwc2ly.py <i>nwctextfile</i>.nwctxt - | lilypond --pdf -o <i>pdfout</i>.pdf -</code><br>
<code>python nwc2ly.py <i>nwcfile</i>.nwc - | lilypond --pdf -o <i>pdfout</i>.pdf -</code>

### License ###

This project is licensed under the [BSD 3-Clause License](./LICENSE)
