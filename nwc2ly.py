#!/bin/python
import table, sys, os, tempfile
from itertools import chain
from functools import partial
from fractions import Fraction

CurPage = None
CurStaff = None
CurMultiVoice = None

#IF = ["NWCTXT/SONG1",
#      "NWCTXT/RegressionTests/Bar",
#      "NWCTXT/RegressionTests/TempoVariance",
#      "NWCTXT/RegressionTests/Rest",
#      "NWCTXT/RegressionTests/Time",
#      "NWCTXT/RegressionTests/Clef",
#      "NWCTXT/RegressionTests/Upbeat",
#      "NWCTXT/RegressionTests/Key",
#      "NWCTXT/RegressionTests/RestMultiBar",
#      "NWCTXT/RegressionTests/DynamicVar",
#      "NWCTXT/RegressionTests/Flow",
#      "NWCTXT/RegressionTests/PerformanceStyle",
#      "NWCTXT/RegressionTests/Tempo",
#      "NWCTXT/RegressionTests/Text",
#      "NWCTXT/RegressionTests/Note",
#      "NWCTXT/RegressionTests/Blaaskwintet",
#      "NWCTXT/RegressionTests/Chord",
#][-1] + ".nwctxt"
#OF = sys.stdout

#FIXME cleanup
if sys.argv.__len__() > 1:
    IF = sys.argv[1]
else:
    import tkinter
    from tkinter import filedialog
    tkinter.Tk().withdraw()

    IF = filedialog.askopenfilename(filetypes=[("NWC Text File", "*.nwctxt")])

if sys.argv.__len__() > 2:
    OF = sys.argv[2]
else:
    OF = os.path.splitext(IF)[0]

if OF == "-":
    OF = sys.stdout
else:
    OF = os.path.abspath(OF)

    if os.path.exists(OF + ".ly"):
        OF = open(tempfile.mkstemp(prefix=OF + "-", suffix=".ly", text=True)[0], "w")
    else:
        OF = open(OF + ".ly", "w")

GRACE = ["acciaccatura", "appoggiatura"][0]
CLEFDIFF = {"treble": 0, "bass": 12, "tenor": 8, "alto": 6, "percussion": 6}

NOTES = {"treble":     ['b', 'c', 'd', 'e', 'f', 'g', 'a'],
         "bass":       ['d', 'e', 'f', 'g', 'a', 'b', 'c'],
         "tenor":      ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
         "alto":       ['c', 'd', 'e', 'f', 'g', 'a', 'b'],
         "percussion": ['c', 'd', 'e', 'f', 'g', 'a', 'b']}

def Tokenise(s): return {a[0]:a[1].split(',') for a in (a.split(':') for a in (':' + str(s)[1:]).split('|')) }
def Direction(p): return 1 if float(p) > -1 else -1
def CloseMultiVoice():
    global CurMultiVoice
    if CurMultiVoice:
        CurMultiVoice.fill(CurStaff.Progress)
        CurStaff.append(CurMultiVoice)
        CurMultiVoice = None

def Pitch(pos):
	pitch = {'accidental': '', 'pitch': 0, 'head': 'o', 'tie': False}
	if not pos[0].isdigit() and pos[0] != '-':
		pitch['accidental'] = pos[0]
		pos = pos[1:]
	if not pos[-1].isdigit() and pos[-1] == '^':
		pitch['tie'] = True
		pos = pos[:-1]
	if not pos[-1].isdigit():
		pitch['head'] = pos[-1]
		pos = pos[:-1]
	if pos.replace('-','',1).isdigit():
		pitch['pitch'] = int(pos)
	else:
		printErr("%s is not a number" % (pos,))
		exit()
	
	return pitch

def Dur(dur):
	duration = {'length': '4',
	            'triplet': None,
	            'grace': False,
	            'staccato': False,
	            'staccatissimo': False,
	            'tenuto': False,
	            'marcato': False,
	            'accent': False,
	            'slur': False}
	if dur[0] == 'Whole':
		duration['length'] = '1'
	elif dur[0] == 'Half':
		duration['length'] = '2'
	elif dur[0][:-2].isdigit():
		duration['length'] = dur[0][:-2]
	else:
		printErr("%s is not a number" % (dur[0][:-2],))
	
	if 'DblDotted' in dur:
		duration['length'] += '..'
	elif 'Dotted' in dur:
		duration['length'] += '.'
	
	if 'Triplet=First' in dur:
		duration['triplet'] = 'first'
	elif 'Triplet' in dur:
		duration['triplet'] = True
	elif 'Triplet=End' in dur:
		duration['triplet'] = 'end'
	
	if 'Grace' in dur:
		duration['grace'] = True
	if 'Staccato' in dur:
		duration['staccato'] = True
	if 'Tenuto' in dur:
		duration['tenuto'] = True
	if 'Slur' in dur:
		duration['slur'] = True
	if 'Accent' in dur:
		duration['accent'] = True
	if 'Marcato' in dur:
		duration['marcato'] = True
	if 'Staccatissimo' in dur:
		duration['staccatissimo'] = True
	
	return duration

class Page:
    #SongInfo
    Title = ""
    Author = ""
    Lyricist = ""
    Copyright1 = ""
    Copyright2 = ""

    #PgSetup
    BarNumbers = None
    StartingBar = 1

    #Header
    LocalRepeat = 0
    BrokenDouble = 0
    Ceasura = 0

    def __init__(self):
        global CurPage, CurMultiVoice
        CurPage = self
        self.Staff = [AddStaff("|AddStaff")]

        for line in (Tokenise(a[:-1]) for a in f if a[0] == '|'):
            if line[""][0] == "AddStaff":
                if self.Staff[-1].Measure == [None]:
                    self.Staff.pop()

                self.Staff.append(AddStaff(line))
            elif callable(globals().get(line[""][0], None)):
                CurStaff.append(eval(line[""][0])(line))

        CloseMultiVoice()

        for staff in self.Staff:
            if staff.Span["dynamicvar"]:
                staff.Span["dynamicvar"] = ""
                for item in reversed(staff.Measure):
                    if item.__doc__ == "Expression":
                        item.DynamicSpan = "off"
                        break

    def print(self):
        yield "\\version \"2.18.2\"\n\\pointAndClickOff\n"
        if self.LocalRepeat:
            yield "\\defineBarLine \":||\" #\'(\":||\" \"\" \" ||\")\n"
            yield "\\defineBarLine \"||:\" #\'(\"||:\" \"\" \"|| \")\n"
            yield "\\defineBarLine \":|||:\" #'(\":||\" \"||:\" \" ||| \")\n"
        if self.BrokenDouble:
            yield "\\defineBarLine \"!!\" #\'(\"!!\" \"\" \"!!\")\n"
        if self.Ceasura:
            yield "caesura = {\\once\\override BreathingSign.text=\\markup\\musicglyph #\"scripts.caesura.straight\" \\breathe}\n"
        yield "\n\\score{<<\n"
        for item in (a.print() for a in self.Staff if a):
            for a in item: yield a
        yield ">>}\n"

class AddStaff:
    def __init__(self, line):
        global CurStaff

        self.PrevNote = [0, ""] #pos, dur
        self.Time = "4/4"
        self.NumTimeSig = False
        self.Endbar = "|."
        self.Clef = ["treble", 0] #octave down: 7, octave up: -7
        self.Progress = 0
        self.BarNumber = CurPage.StartingBar
        self.Partial = None
        self.Visible = True

        self.Key = [{a: 'n' for a in "abcdefg"},  #key sig
                    {a: 'n' for a in "abcdefg"},  #measure
                    {a: '' for a in "abcdefg"}]   #ties

        self.Span = {"grace": False,
                     "slur": False,
                     "dynamicvar": ""}

        self.Delay = {"dynamic": ("", 0),
                      "dynamicvar": ("", 0),
                      "tempovar": ("", 0), # ["", -1|1]
                      "fermata": 0,        # -1|1
                      "sustain": (0, 0),
                      "text": ""}

        CloseMultiVoice()
        CurStaff = self
        self.Measure = [None]

    def rfind(self, Type):
        for item in reversed(self.Measure):
            if item.__doc__ == Type:
                return item

    def append(self, cls):
        self.Measure.append(cls)
        if cls.__doc__ == "Expression":
            self.Progress += (Fraction(eval("1/"+cls.Note[1].replace(".", "")))
                             * (2 - Fraction(1,2)**cls.Note[1].count("."))
                             * Fraction(2, (3 if cls.Triplet else 2)))
            if cls.Note[1] == self.PrevNote[1]:
                cls.Note[1] = ""
            else:
                self.PrevNote[1] = cls.Note[1]

    def print(self):
        if self.Visible:
            yield "\\new Staff{\n\t\\compressFullBarRests\n\t\\override Hairpin.to-barline = ##f\n\t\\override DynamicTextSpanner.style = #\'none\n\t\\relative b\'{\n\t"
            if self.Partial:
                yield "\\set Timing.measurePosition = #(ly:make-moment %s)\n\t" % (-self.Partial,)
            for item in (a.print() for a in self.Measure if a):
                for a in item: yield a
            yield "\\bar\"" + self.Endbar + "\"}\n}\n"

class MultiVoiceStart:
    def __init__(self):
        global CurMultiVoice
        CurMultiVoice = MultiVoiceEnd()

    def print(self):
        yield "<<{"

class MultiVoiceEnd:
    def __init__(self):
        self.Voice = []
        self.Progress = 0

    def getMain(self):
        for Voice in self.Voice:
            if Voice.Progress == CurStaff.Progress:
                return Voice
            if Voice.Progress < CurStaff.Progress:
                Voice.fill(CurStaff.Progress)
                return Voice
        else:
            self.Voice.append(MultiVoice())
            return self.Voice[-1]

    def getProgress(self):
        return min(a.Progress for a in self.Voice)

    def fill(self, Progress):
        map(partial(MultiVoice.fill, Progress=Progress), self.Voice)

    def print(self):
        for item in (a.print() for a in self.Voice if a):
            yield "}\\\\\\relative b'{"
            for a in item: yield a
        yield "}>>"

class MultiVoice(AddStaff):
    def __init__(self):
        self.PrevNote = [0, ""] #pos, dur
        self.Progress = 0
        self.Visible = True

        self.Measure = [None]

    def fill(self, Progress):
        if self.Progress < Progress:
            line = Tokenise("|Rest|Dur:Whole")
            self.append( Expression("Rest", Dur(line["Dur"]), None, ["s", "1*%s" % (Progress - self.Progress), ""], line) )

    def print(self):
        for item in (a.print() for a in self.Measure if a):
            for a in item: yield a

def barWrap(cls):

    def wrapper(line):
        if CurStaff.Measure[-1].__doc__ == "Bar":
            if CurStaff.Measure[-1].Style == "MasterRepeatClose" and line["Style"][0] == "MasterRepeatOpen":
                CurStaff.Measure[-1].Style = "MasterRepeatCloseOpen"
            elif CurStaff.Measure[-1].Style == "LocalRepeatClose" and line["Style"][0] == "LocalRepeatOpen":
                CurStaff.Measure[-1].Style = "LocalRepeatCloseOpen"
            elif CurStaff.Measure[-1].Style == "SectionClose" and line["Style"][0] == "SectionOpen":
                CurStaff.Measure[-1].Style = "SectionCloseOpen"
            else:
                return cls(line)
            return None
        return cls(line)

    return wrapper

@barWrap
class Bar:
    """Bar"""
    Style = "Single"
    Repeat = None
    Fermata = 0
    Newline = False
    BarNumber = 0

    def __init__(self, line):
        global CurMultiVoice
        self.Style = line.get("Style", ["Single"])[0]
        self.Repeat = line.get("Repeat", [None])[0]
        self.Fermata = CurStaff.Delay["fermata"]
        CurStaff.Delay["fermata"] = 0

        if self.Style == "BrokenDouble":
            CurPage.BrokenDouble = True
        elif "LocalRepeat" in self.Style:
            CurPage.LocalRepeat = True

        if CurStaff.Progress >= Fraction(CurStaff.Time) or CurStaff.Partial == None:
            if CurStaff.Partial == None:
                CurStaff.Partial = 0
                if CurStaff.Progress < Fraction(CurStaff.Time):
                    CurStaff.Partial = CurStaff.Progress
                    CurStaff.BarNumber -= 1
            if CurMultiVoice:
                if CurMultiVoice.getProgress == 0:
                    CurStaff.append(CurMultiVoice)
                    CurMultiVoice = None
                else:
                    CurMultiVoice.fill(CurStaff.Progress)
            CurStaff.Progress = 0
            self.Newline = True
            self.BarNumber = CurStaff.BarNumber
            CurStaff.BarNumber += 1

        CurStaff.Key[1].update(CurStaff.Key[0])

    def print(self):
        if self.Fermata or self.Repeat:
            yield "\\once\\override Score.RehearsalMark.break-visibility = ##(#t #t #f) "
        if self.Fermata and not self.Repeat:
            if self.Fermata == -1:
                yield "\\once\\override Score.RehearsalMark.direction = #DOWN "
                yield "\\mark\\markup\\musicglyph #\"scripts.dfermata\" "
            else:
                yield "\\mark\\markup\\musicglyph #\"scripts.ufermata\" "
        elif self.Fermata and self.Repeat:
            if self.Fermata == -1:
                yield "\\once\\override Score.RehearsalMark.extra-offset = #\'(0 . -7.6) "
                yield "\\once\\override Score.RehearsalMark.baseline-skip = #6.1 "
                yield "\\mark\\markup\\column{\\small\\center-align\"(%s)\" \\musicglyph #\"scripts.dfermata\"}" % (self.Repeat, )
            else:
                yield "\\mark\\markup\\column{\\musicglyph #\"scripts.ufermata\" \\small\\center-align\"(%s)\"}" % (self.Repeat, )

        elif self.Repeat:
            if self.Style == "LocalRepeatCloseOpen":
                yield "\\once\\override Score.RehearsalMark.extra-offset = #\'(-.6 . 0) "
            yield "\\mark\\markup\\small\"(%s)\"" % (self.Repeat, )

        yield table.bar.get(self.Style, "|")

        if self.Newline:
            if not self.BarNumber % 5:
                yield " %% %d" % (self.BarNumber, )
            yield "\n\t"

class Clef:
    """Clef"""
    Clef = "treble"
    Octave = 0 #up: -7, down: 7

    def __init__(self, line):
        CurStaff.PrevNote[0] -= CLEFDIFF[CurStaff.Clef[0]] + CurStaff.Clef[1]
        self.Clef = line.get("Type", ["Treble"])[0].lower()
        CurStaff.Clef = [self.Clef, 0]

        if "OctaveShift" in line:
            self.Octave = {"Octave Down": 7, "Octave Up": -7}.get(line["OctaveShift"][0], 0)
            CurStaff.Clef[1] = self.Octave

        CurStaff.PrevNote[0] += CLEFDIFF[self.Clef] + self.Octave

    def print(self):
        if self.Octave:
            yield "\\clef \"%s%s\" " % (self.Clef, "_8" if self.Octave == 7 else "^8")
        else:
            yield "\\clef %s " % (self.Clef, )

def Dynamic(line):
    if "Style" in line:
        if CurStaff.Delay["dynamic"][0] == "f" and line["Style"][0] == "p":
            CurStaff.Delay["dynamic"] = ("fp", Direction(line.get("Pos", ["0"])[0]))
        else:
            CurStaff.Delay["dynamic"] = (line["Style"][0], Direction(line.get("Pos", ["0"])[0]))
        CurStaff.Span["dynamicvar"] = ""
    return None

def DynamicVariance(line):
    if "Style" in line:
        if line["Style"][0] in table.dynamic:
            CurStaff.Delay["dynamicvar"] = (table.dynamic[line["Style"][0]], Direction(line.get("Pos", ["0"])[0]))
            CurStaff.Span["dynamicvar"] = ""
        else:
            print("Err: DynamicVariance style \"%s\" not recognised" % (line["Style"][0], ), file=sys.stderr)
    else:
        print("Err: DynamicVariance style not found", file=sys.stderr)
    return None


def NoteName(pitch, PrevNote):
    note = ""
    tie = ""
    name = NOTES[CurStaff.Clef[0]][pitch["pitch"] % 7]
    note += name
    if pitch["accidental"] != "":
        CurStaff.Key[1][name] = pitch["accidental"]

    note += ["", "es", "eses", "is", "isis"]["nbv#x".index(CurStaff.Key[2][name] or CurStaff.Key[1][name])]

    #octave shift
    if abs(pitch["pitch"] - PrevNote[0]) > 3:
        note += ("\'" if pitch["pitch"] > PrevNote[0] else ",") * ((abs(pitch["pitch"] - PrevNote[0]) + 3) // 7)
    PrevNote[0] = pitch["pitch"]

    if pitch["tie"]:
        tie = "~"
        CurStaff.Key[2][name] = CurStaff.Key[2][name] or CurStaff.Key[1][name]
    else:
        CurStaff.Key[2][name] = ""

    return note, tie

def ChordName(Pos, CurStaff=None):
    if CurStaff == None:
        CurStaff = globals()["CurStaff"]
    note = "<"
    note += "".join(NoteName(Pitch(Pos[0]), CurStaff.PrevNote)) + " "
    localPrevNote = list(CurStaff.PrevNote)
    for pitch in ("".join(NoteName(Pitch(a), localPrevNote)) for a in Pos[1:]):
        note += pitch + " "
    note = note[:-1] + ">"

    return note

def Chord(line):
    Type = "Chord"
    note = ["", "", ""]
    if "Dur" in line:
        dur = Dur(line["Dur"])
    else:
        print("Err: duration not found in %s" % line[""], file=sys.stderr)
        return None

    if "Pos" not in line:
        print("Err: position not found in %s" % line[""], file=sys.stderr)
        return None

    note[0] = ChordName(line["Pos"])
    note[1] = dur["length"]

# Voice2
    if "Dur2" in line:
        if not CurMultiVoice:
            CurStaff.append(MultiVoiceStart())

        note2 = ["", "", ""]
        dur2 = Dur(line["Dur2"])

        if "Pos2" not in line:
            print("Err: position not found in %s" % line[""], file=sys.stderr)
            return None

        note2[0] = ChordName(line["Pos2"], CurMultiVoice.getMain())
        note2[1] = dur2["length"]

        CurMultiVoice.getMain().append(Expression(Type, dur2, None, note2, line))
    return Expression(Type, dur, None, note, line)

def Note(line):
    Type = "Note"
    note = ["", "", ""]
    if "Dur" in line:
        dur = Dur(line["Dur"])
    else:
        print("Err: duration not found in %s" % line[""], file=sys.stderr)
        return None

    if "Pos" in line:
        pitch = Pitch(line["Pos"][0])
    else:
        print("Err: position not found in %s" % line[""], file=sys.stderr)
        return None

    note[0],note[2] = NoteName(pitch, CurStaff.PrevNote)
    note[1] = dur["length"]

    return Expression(Type, dur, None, note, line)

def Rest(line):
    Type = "Rest"
    note = ["", "", ""]
    if "Dur" in line:
        dur = Dur(line["Dur"])
    else:
        print("Err: duration not found in %s" % line[""], file=sys.stderr)
        return None

    note[0] = "r"
    note[1] = dur["length"]
    if dur["length"] == '1' and CurStaff.Progress == 0:
        Type += "FullMeasure"
        note[0] = "R"
        if Fraction(CurStaff.Time) != 1:
            note[1] += "*%s" % (CurStaff.Time,)


    return Expression(Type, dur, None, note, line)

#RestChord FIXME

class Expression:
    """Expression"""
    Note = ("", "", "")
    Type = ""

    #span
    Grace = 0       #first: 1, last: -1, only: 2
    Triplet = 0
    Slur = 0
    DynamicSpan = ""

    #articulation
    Staccato = False
    Staccatissimo = False
    Tenuto = False
    Accent = False
    Marcato = False

    #dynamics
    Fermata = 0          #down: -1, up: 1
    Dynamic = ("", 0)
    DynamicVar = ("", 0)
    Tempovar = ("", 0)
    Sustain = (0, 0)     #(down: 1 | release: -1, down: -1 | up: 1)
    Text = ""

    def __init__(self, Type, dur, pitch, Note, line):
        self.Type = Type
        self.Note = Note

        if dur["grace"] and not CurStaff.Span["grace"]:
            CurStaff.Span["grace"] = True
            self.Grace = 1
        elif not dur["grace"] and CurStaff.Span["grace"]:
            CurStaff.Span["grace"] = False
            cls = CurStaff.rfind("Expression")
            if cls.Grace == 1:
                cls.Grace = 2
            else:
                cls.Grace = -1
        if not CurStaff.Span["grace"]:
            if dur["slur"] and not CurStaff.Span["slur"]:
                CurStaff.Span["slur"] = True
                self.Slur = 1
            elif not dur["slur"] and CurStaff.Span["slur"]:
                CurStaff.Span["slur"] = False
                self.Slur = -1

        if "Opts" in line:
            if "Crescendo" in line["Opts"] and CurStaff.Span["dynamicvar"] != "cresc":
                CurStaff.Span["dynamicvar"] = "cresc"
                self.DynamicSpan = "cresc"
            elif "Diminuendo" in line["Opts"] and CurStaff.Span["dynamicvar"] != "decresc":
                CurStaff.Span["dynamicvar"] = "decresc"
                self.DynamicSpan = "decresc"
        if CurStaff.Span["dynamicvar"] and "Crescendo" not in line.get("Opts", [""]) and not "Diminuendo" in line.get("Opts", [""]):
            CurStaff.Span["dynamicvar"] = ""
            cls = CurStaff.rfind("Expression")
            if cls.DynamicSpan in ["cresc", "decresc"]:
                self.DynamicSpan = "off"
            else:
                cls.DynamicSpan = "off"

        if dur["triplet"] == "first":
            self.Triplet = 1
        elif dur["triplet"] == "end":
            self.Triplet = -1

        if "Rest" not in Type:
            self.Staccato = dur["staccato"]
            self.Staccatissimo = dur["staccatissimo"]
            self.Tenuto = dur["tenuto"]
            self.Accent = dur["accent"]
            self.Marcato = dur["marcato"]

        if CurStaff.Delay["fermata"]:
            self.Fermata = CurStaff.Delay["fermata"]
            CurStaff.Delay["fermata"] = 0
        if CurStaff.Delay["sustain"][1]:
            self.Sustain = CurStaff.Delay["sustain"]
            CurStaff.Delay["sustain"] = (0, 0)

        if CurStaff.Delay["dynamic"][1]:
            self.Dynamic = CurStaff.Delay["dynamic"]
            CurStaff.Delay["dynamic"] = ("", 0)
        if CurStaff.Delay["dynamicvar"][1]:
            self.DynamicVar = CurStaff.Delay["dynamicvar"]
            CurStaff.Delay["dynamicvar"] = ("", 0)
        if CurStaff.Delay["tempovar"][1]:
            self.Tempovar = CurStaff.Delay["tempovar"]
            CurStaff.Delay["tempovar"] = ("", 0)
        if CurStaff.Delay["text"]:
            self.Text = CurStaff.Delay["text"]
            CurStaff.Delay["text"] = ""

    def print(self):
        if self.Grace == 1:
            yield "\\%s{" % (GRACE, )
        elif self.Grace == 2:
            yield "\\%s " % (GRACE, )
        if self.Triplet == 1:
            yield "\\tuplet 3/2{"

        yield "".join(self.Note)

        if self.Slur == 1:
            yield "("
        elif self.Slur == -1:
            yield ")"

        if self.Staccato:
            yield "-." if not self.Tenuto else "-_"
        if self.Staccatissimo:
            yield "-!"
        if self.Tenuto and not self.Staccato:
            yield "--"
        if self.Accent:
            yield "->"
        if self.Marcato:
            yield "-^"

        if self.DynamicSpan == "cresc":
            yield "\<"
        elif self.DynamicSpan == "decresc":
            yield "\>"
        elif self.DynamicSpan == "off":
            yield "\!"

        if self.Fermata:
            yield "%s\\%s" %("" if self.Fermata == 1 else "_","fermataMarkup" if self.Type == "RestFullMeasure" else "fermata")
        if self.Dynamic[1]:
            yield "%s\\%s" %("^" if self.Dynamic[1] == 1 else "", self.Dynamic[0])
        if self.DynamicVar[1]:
            yield "%s\\%s" %("^" if self.DynamicVar[1] == 1 else "", self.DynamicVar[0])
        if self.Tempovar[1]:
            yield "%s\\markup\\small\\italic\"%s\"" %("^" if self.Tempovar[1] == 1 else "_", table.tempovar[self.Tempovar[0]])
        if self.Sustain[1]:
            yield "%s\\%s" % ("" if self.Sustain[1] == 1 else "", "sustainOn" if self.Sustain[0] == 1 else "sustainOff")
        if self.Text:
            yield self.Text

        if self.Triplet == -1:
            yield "}"
        if self.Grace == -1:
            yield "}"

        yield " "

class Flow:
    Flow = ""
    Direction = -1

    def __init__(self, line):
        self.Flow = line.get("Style", [""])[0]
        self.Direction = Direction(line.get("Pos", ["0"])[0])

    def print(self):
        if self.Flow:
            if self.Direction == -1:
                yield "\\once\\override Score.RehearsalMark.direction = #DOWN "
            yield "\\mark\\markup%s" % (table.flow[self.Flow], )
        else:
            yield ""

def Instrument(line):
    if "Name" in line:
        CurStaff.Delay["text"] = "^" if Direction(line.get("Pos", ["0"])[0]) == 1 else "_"
        CurStaff.Delay["text"] += line["Name"][0]
    return None

class Key:
    Signature = ["C"]

    def __init__(self, line):
        self.Signature = line.get("Signature", ["C"])
        CurStaff.Key[0] = {a: 'n' for a in "abcdefg"}
        if self.Signature[0] != "C":
            CurStaff.Key[0].update([(a[0].lower(), a[1]) for a in self.Signature])
        CurStaff.Key[1].update(CurStaff.Key[0])

    def print(self):
        yield "\set Staff.keySignature = #`("
        if self.Signature[0] != "C":
            yield " %s" % (" ".join([
                    "(%d . %s) " % (
                                    "CDEFGAB".index(a[0]),
                                    [",FLAT", ",SHARP"]["b#".index(a[1])]
                                   ) for a in self.Signature
                    ]), )
        yield ")\n\t"

#Lyrics FIXME

class PerformanceStyle:
    Direction = 1
    Style = ""

    def __init__(self, line):
        self.Direction = Direction(line.get("Pos", ["0"])[0])
        self.Style = line.get("Style", [""])[0]

    def print(self):
        if self.Style:
            if self.Direction == -1:
                yield "\\once\\override Score.RehearsalMark.direction = #DOWN "
            yield "\\mark\\markup\\italic\\bold\\large\"%s\" " % (table.performstyle[self.Style], )
        else:
            yield ""

class RestMultiBar:
    """RestMultiBar"""
    Note = "1"
    Text = ""

    def __init__(self, line):
        if Fraction(CurStaff.Time) != 1:
            self.Note += "*" + CurStaff.Time

        if line.get("NumBars", ["1"])[0] != "1":
            self.Note += "*" + line["NumBars"][0]
        CurStaff.Progress += Fraction(CurStaff.Time) * Fraction(line["NumBars"][0])
        if self.Note == CurStaff.PrevNote[1]:
            self.Note = ""
        else:
            CurStaff.PrevNote[1] = self.Note

        if CurStaff.Delay["text"]:
            self.Text = CurStaff.Delay["text"]
            CurStaff.Delay["text"] = ""

    def print(self):
        if self.Text:
            yield "<>%s " % (self.Text,)
        yield "R%s " % (self.Note,)


def StaffProperties(line):
    #system connections "WithNextStaff"
    if "EndingBar" in line:
        CurStaff.Endbar = table.endbar.get(line["EndingBar"][0], "|.")
    if "Visible" in line and line["Visible"] == "N":
        CurStaff.Visible = False

    return None

def SustainPedal(line):
    CurStaff.Delay["sustain"] = (-1 if line.get("Status", ["Down"])[0] == "Released" else 1, Direction(line.get("Pos", ["0"])[0]))
    return None

class Tempo:
    Base = None
    Tempo = "120"
    Text = ""
    Direction = 1

    def __init__(self, line):
        if "Tempo" in line:
            self.Base = table.tempo[line.get("Base", ["Quarter"])[0]]
            self.Tempo = line["Tempo"][0]
        if "Text" in line:
            self.Text = line["Text"][0]
        self.Direction = Direction(line.get("Pos", [0])[0])

    def print(self):
        if self.Direction == -1:
            yield "\\once\\override Score.MetronomeMark.direction=#-1 "
        yield "\\tempo"
        if self.Text:
            yield self.Text
        if self.Base:
            yield "%s=%s " % (self.Base, self.Tempo)

def TempoVarWrap(cls):

    def wrapper(line):
        if line.get("Style",[""])[0] == "Fermata":
            CurStaff.Delay["fermata"] = Direction(line.get("Pos", ["0"])[0])
        elif line.get("Style", [""])[0] in table.tempovar:
            CurStaff.Delay["tempovar"] = (line["Style"][0], Direction(line.get("Pos", ["0"])[0]))

        else:
            return cls(line)
        return None

    return wrapper

@TempoVarWrap
class TempoVariance:
    """TempoVariance"""
    Style = ""

    def __init__(self, line):
        if line.get("Style",[""])[0] == "Breath Mark":
            self.Style = "\\breathe "
        elif line.get("Style",[""])[0] == "Caesura":
            self.Style = "\\caesura "
            CurPage.Ceasura = True
        else:
            if "Style" in line:
                print("Err: TempoVariance style \"%s\" not recognised" % (line["Style"][0],), file=sys.stderr)
            else:
                print("Err: TempoVariance style not found")

    def print(self):
        yield self.Style

#Text
def Text(line):
    if "Text" in line:
        text = "^" if Direction(line.get("Pos", ["0"])[0]) == 1 else "_"

        if line["Text"][0][1:-1] in table.textcmd:
            text += table.textcmd[line["Text"][0][1:-1]]
        elif line.get("Font", [""])[0] == "StaffCueSymbols" and line["Text"][0][1:-1] in table.textsmall:
            text += table.textsmall[line["Text"][0][1:-1]]
        elif line.get("Font", [""])[0] == "StaffSymbols" and line["Text"][0][1:-1] in table.textlarge:
            text += table.textlarge[line["Text"][0][1:-1]]
        else:
            if line.get("Font", [""])[0] == "StaffItalic":
                text += "\\markup\\italic"
            elif line.get("Font", [""])[0] == "StaffBold":
                text += "\\markup\\bold"
            text += line["Text"][0]

        CurStaff.Delay["text"] = text
    return None

class TimeSig:
    """TimeSig"""
    Signature = ""
    NumTimeSig = 0 #off: -1, on: 1
    MeasurePos = 0

    def __init__(self, line):
        if "Signature" in line:
            if line["Signature"][0] == "Common":
                self.Signature = "4/4"

            elif line["Signature"][0] == "AllaBreve":
                self.Signature = "2/2"
            else:
                self.Signature = line["Signature"][0]

            if line["Signature"][0] in ["Common", "AllaBreve"] and CurStaff.NumTimeSig:
                self.NumTimeSig = -1
                CurStaff.NumTimeSig = False
            elif line["Signature"][0] in ["4/4", "2/2"] and not CurStaff.NumTimeSig:
                self.NumTimeSig = 1
                CurStaff.NumTimeSig = True

            CurStaff.Progress /= Fraction(CurStaff.Time)
            CurStaff.Time = self.Signature
            if CurStaff.Progress and CurStaff.Progress != 1:
                self.MeasurePos = CurStaff.Progress * Fraction(self.Signature)
            CurStaff.Progress *= Fraction(self.Signature)
        else:
            print("Err: TimeSig no Signature found", file=sys.stderr)

    def print(self):
        if self.MeasurePos:
            yield "\\set Timing.measurePosition = #(ly:make-moment %s) " % (self.MeasurePos, )

        if self.NumTimeSig:
            yield "\\%sTimeSignature " % ("default" if self.NumTimeSig == -1 else "numeric",)
        yield "\\time %s " % (self.Signature,)

with open(IF, errors='backslashreplace', newline=None) as f:
    Page()
    for line in CurPage.print():
        print(line, end="", file=OF)
