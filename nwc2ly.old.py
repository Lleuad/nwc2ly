#!/bin/python
# -*- coding: utf-8
from __future__ import print_function, unicode_literals
import sys
if sys.version_info < (3,0):
	if sys.version_info < (2,6,0,'alpha',2):
		raise SystemExit("This script requires Python version 2.6.0 alpha 2 or later")
	from layer import *

import table, re

if sys.argv.__len__() > 1:
	IF = sys.argv[1]
	OF = sys.stdout
else:
	import os
	if sys.version_info < (3,0):
		import Tkinter as tkinter
		import tkFileDialog as filedialog
	else:
		import tkinter
		from tkinter import filedialog
		tkinter.Tk().withdraw()
	
	IF = filedialog.askopenfilename()
	OF = open(os.path.splitext(IF)[0] + ".ly", "w")

ERR = sys.stderr
HEADER = """\
\\version \"2.18.2\"
\\pointAndClickOff
\\defineBarLine \":||\" #\'(\":||\" \"\" \" ||\")
\\defineBarLine \"||:\" #\'(\"||:\" \"\" \"|| \")
\\defineBarLine \" :|||:\" #'(\":||\" \"||:\" \" ||| \")
\\defineBarLine \"!!\" #\'(\"!!\" \"\" \"!!\")
caesura = {\\once\\override BreathingSign.text=\\markup\\musicglyph #"scripts.caesura.straight" \\breathe}

\\score{<<
\\new Staff{
	\\compressFullBarRests
	\\relative b\'{
	"""

FOOTER = """\
}
}
>>}
"""

FONT = {"StaffItalic":   "\\italic\\bold\\large",
        "StaffBold":     "\\bold\\normalsize",
        "StaffLyric":    "\\normalsize",
        "PageTitleText": "\\abs-fontsize #24 \\bold",
        "PageText":      "\\abs-fontsize #12 ",
        "PageSmallText": "\\abs-fontsize #8 ",
        "User1":         "\\abs-fontsize #8 ",
        "User2":         "\\abs-fontsize #8 ",
        "User3":         "\\abs-fontsize #8 ",
        "User4":         "\\abs-fontsize #8 ",
        "User5":         "\\abs-fontsize #8 ",
        "User6":         "\\abs-fontsize #8 "}

STAFFADDED = False
CLEFDIFF = {"Treble": 0, "Bass": 12, "Tenor": 8, "Alto": 6, "Percussion": 6}

NOTES = {"Treble":     ['b', 'c', 'd', 'e', 'f', 'g', 'a'],
         "Bass":       ['d', 'e', 'f', 'g', 'a', 'b', 'c'],
         "Tenor":      ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
         "Alto":       ['c', 'd', 'e', 'f', 'g', 'a', 'b'],
         "Percussion": ['c', 'd', 'e', 'f', 'g', 'a', 'b']}

SWITCH = {"Editor":          lambda : '',
          "SongInfo":        lambda : '',
          "PgSetup":         lambda : '',
          "Font":            lambda : '',
          "PgMargins":       lambda : '',
          "StaffInstrument": lambda : '',
          "MPC":             lambda : '',
          "User":            lambda : '',
          "Note":            lambda : Expression(line,'note'), #note heads
          "Rest":            lambda : Expression(line,'rest'),
          "Chord":           lambda : Expression(line,'chord'),
          "Bar":             lambda : Bar(line),
          "Key":             lambda : Key(line),
          "TimeSig":         lambda : Time(line),
          "Clef":            lambda : Clef(line),
          "StaffProperties": lambda : StaffProperties(line),
          "AddStaff":        lambda : AddStaff(line),
          "Text":            lambda : Text(line),
          "Dynamic":         lambda : Dynamic(line),
          "DynamicVariance": lambda : DynamicVar(line),
          "Tempo":           lambda : Tempo(line),
          "TempoVariance":   lambda : TempoVar(line),
          "RestMultiBar":    lambda : MultiBarRest(line),
          "SustainPedal":    lambda : Sustain(line),
          "PerformanceStyle":lambda : PerformStyle(line),
          "Flow":            lambda : Flow(line)}

#Chord (multi voice)
#RestChord
#Lyrics
#Ending
#Instrument (as text only?)

###USER SETTINGS
# strict beaming
# block rest articulation
# voice2 is dur2 (default) or stem down
###

def Reset(all = 1, measure = 0):
	global PREVNOTE, TIME, NUMTIMESIG, ENDBAR, CLEF, KEY, SPAN, DELAY, MEASURE
	if all:
		PREVNOTE = [0, ""] #pos, dur
		TIME = '4/4'
		NUMTIMESIG = False
		ENDBAR = "|."
		CLEF = ["Treble", ""]
		
		KEY = [{a: 'n' for a in "abcdefg"},  #key sig
		       {a: 'n' for a in "abcdefg"},  #measure
		       {a: '' for a in "abcdefg"}]   #ties
		
		SPAN = {"grace": False,
		        "slur": False,
		        "dynamicvar": False}
		
		DELAY = {"dynamic": '',
		         "dynamicvar": '',
		         "tempovar": '',
		         "fermata": '',
		         "sustain": '',
		         "line": {},
		         "out": ''}
	
	if all or measure:
		MEASURE = {"first": True,
		           "threshold": 0.5,
		           "dur": 0,
		           "dur2": 0,
		           "last": 0,
		           "voice2": "",
		           "prevnote": [0, ""]}

def Tokenise(s): return {a[0]:a[1].split(',') for a in (a.split(':') for a in (':' + str(s)[1:]).split('|')) }

def printOut(s): print(s, end='', file=OF)

def printErr(s): print("\r\tError: %s" % (s,), file=ERR)

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

def Expression(line, expr):
	printOut(DELAY["out"])
	
	if expr == 'note':
		pitch = Pitch(line['Pos'][0])
	elif expr == 'chord':
		pitch = [Pitch(a) for a in line['Pos']]
		if "Pos2" in line:
			pitch2 = [Pitch(a) for a in line["Pos2"]]
			dur2 = Dur(line['Dur2'])
		else:
			pitch2 = {}
			dur2 = {}
	
	dur = Dur(line['Dur'])
	note = ""
	
	#grace on
	if dur['grace'] and not SPAN['grace']:
		SPAN['grace'] = True
		note += '\\grace{'
	
	#triplet on
	if dur['triplet'] == 'first':
		note += '\\tuplet 3/2{'
	
	#note or rest
	if expr == 'note':
		note += Note(pitch, dur)
	elif expr == 'rest':
		note += Rest(dur)
	elif expr == 'chord':
		note += Chord(pitch, dur, pitch2, dur2)
	
	#slur
	if dur['slur'] and not SPAN['slur']:
		note += '('
		SPAN['slur'] = True
	elif not dur['slur'] and SPAN['slur']:
		note += ')'
		SPAN['slur'] = False
	
	#articulation
	if dur['staccato']:
		note += '-.' if not dur['tenuto'] else '-_'
	if dur['staccatissimo']:
		note += '-!'
	if dur['tenuto'] and not dur['staccato']:
		note += '--'
	if dur['accent']:
		note += '->'
	if dur['marcato']:
		note += '-^'
	
	#dynamics
	if DELAY["fermata"]:
		note += DELAY["fermata"]
		DELAY["fermata"] = ''
	if DELAY["dynamic"]:
		note += DELAY["dynamic"]
		DELAY["dynamic"] = ''
	if DELAY["dynamicvar"]:
		note += DELAY["dynamicvar"]
		DELAY["dynamicvar"] = ''
	if DELAY["tempovar"]:
		note += DELAY["tempovar"]
		DELAY["tempovar"] = ''
	
	#sustain pedal
	if DELAY["sustain"]:
		note += DELAY["sustain"]
		DELAY["sustain"] = ''
	
	#triplet off
	if dur['triplet'] == 'end':
		note += '}'
	
	#grace off
	if not dur['grace'] and SPAN['grace']:
		SPAN['grace'] = False
		note = '}' + note
	
	#multivoiced
	if MEASURE["dur2"] and MEASURE["dur"] - MEASURE["dur2"] >= MEASURE["threshold"] and not dur["triplet"]:
		note += "}\\\\{" + MEASURE["voice2"] + "s1*%d/%d}}>>" % (MEASURE["dur"] - MEASURE["dur2"]).as_integer_ratio()
		Reset(all = 0, measure = 1)
		PREVNOTE[1] = ""
	
	DELAY["out"] = "%s " % (note,)
	DELAY["line"] = line

def Note(pitch, dur):
	name = NOTES[CLEF[0]][pitch['pitch'] % 7]
	
	#note name
	note = name
	if pitch['accidental'] != '':
		KEY[1][name] = pitch['accidental']
	
	note += ['', 'es', 'eses', 'is', 'isis']['nbv#x'.index( KEY[2][name] or KEY[1][name] )]
	
	#octave shift
	if abs(pitch['pitch'] - PREVNOTE[0]) > 3:
		note += ('\'' if pitch['pitch'] > PREVNOTE[0] else ',') * ((abs(pitch['pitch'] - PREVNOTE[0]) + 3) // 7)
	PREVNOTE[0] = pitch['pitch']
	
	if dur['length'] != PREVNOTE[1]:
		note += dur['length']
		PREVNOTE[1] = dur['length']
	
	#tie
	if pitch['tie']:
		note += '~'
		KEY[2][name] = KEY[2][name] or KEY[1][name]
	else:
		KEY[2][name] = ''
	
	if MEASURE["dur2"]:
		MEASURE["dur"] += 0 if dur["triplet"] else (2-2**-dur["length"].count('.'))/( int(dur["length"].rstrip('.')) * (3 if dur["triplet"] else 1) )
	
	return note

def Chord(pitchlist, dur, pitch2list, dur2):
	note = ""
	if dur2:
		if not MEASURE["dur2"]:
			MEASURE["prevnote"][0] = PREVNOTE[0]
			MEASURE["prevnote"][1] = ""
			tmp = (PREVNOTE[0] + 13 - CLEFDIFF[CLEF[0]] + {"_8": -7, "^8": 7, "":0}[CLEF[1]])
			MEASURE["voice2"] = "\\relative " + NOTES[CLEF[0]][(tmp+1) % 7] + ('\'' if tmp > 0 else ',') * (abs(tmp) // 7) + "{"
			note = "<<{"
		
		if MEASURE["dur2"] > MEASURE["dur"]:
			MEASURE["voice2"] = MEASURE["voice2"][:-1] + "*%d/%d " % (1-(MEASURE["dur2"] - MEASURE["dur"])/MEASURE["last"]).as_integer_ratio()
		elif MEASURE["dur2"] < MEASURE["dur"]:
			MEASURE["voice2"] += "s1*%d/%d " % (MEASURE["dur"] - MEASURE["dur2"]).as_integer_ratio()
		MEASURE["dur2"] = MEASURE["dur"]
		
		MEASURE["voice2"] += _Chord(pitch2list, dur2, MEASURE["prevnote"]) + " "
		MEASURE["last"] = 0 if dur2["triplet"] else (2-2**-dur2["length"].count('.'))/( int(dur2["length"].rstrip('.')) * (3 if dur2["triplet"] else 1) )
		MEASURE["dur2"] += MEASURE["last"]
	
	if MEASURE["dur2"]:
		MEASURE["dur"] += 0 if dur["triplet"] else (2-2**-dur["length"].count('.'))/( int(dur["length"].rstrip('.')) * (3 if dur["triplet"] else 1) )
	
	return note + _Chord(pitchlist, dur, PREVNOTE)

def _Chord(pitchlist, dur, localprevnote):
	note = "<"
	
	for pitch in pitchlist:
		name = NOTES[CLEF[0]][pitch['pitch'] % 7]
		
		#note name
		note += name
		if pitch['accidental'] != '':
			KEY[1][name] = pitch['accidental']
		
		note += ['', 'es', 'eses', 'is', 'isis']['nbv#x'.index( KEY[2][name] or KEY[1][name] )]
		
		#octave shift
		if abs(pitch['pitch'] - localprevnote[0]) > 3:
			note += ('\'' if pitch['pitch'] > localprevnote[0] else ',') * ((abs(pitch['pitch'] - localprevnote[0]) + 3) // 7)
		localprevnote[0] = pitch['pitch']
		
		#tie
		if pitch['tie']:
			note += '~'
			KEY[2][name] = KEY[2][name] or KEY[1][name]
		else:
			KEY[2][name] = ''
		
		note += ' '
	
	localprevnote[0] = pitchlist[0]['pitch']
	note = note[:-1] + ">"
	
	if dur['length'] != localprevnote[1]:
		note += dur['length']
		localprevnote[1] = dur['length']
	
	return note

def Rest(dur):
	#note name
	note = 'R' if dur['length'] == '1' else 'r'
	
	if dur['length'] != PREVNOTE[1]:
		note += dur['length']
		PREVNOTE[1] = dur['length']
		
		if dur['length'] == '1' and eval(TIME) != 1.:
			note += "*%s" % (TIME,)
			PREVNOTE[1] += "*%s" % (TIME,)
	
	if MEASURE["dur2"]:
		MEASURE["dur"] += 0 if dur["triplet"] else (2-2**-dur["length"].count('.'))/( int(dur["length"].rstrip('.')) * (3 if dur["triplet"] else 1) )
	
	return note

def Bar(line):
	if DELAY["line"] and DELAY["line"][''][0] == "Bar":
		regex = re.compile(r"\\bar\".*?\"")
		if DELAY["line"]["Style"][0] == "LocalRepeatClose" and line["Style"][0] == "LocalRepeatOpen":
			DELAY["out"] = "\\once\\override Score.RehearsalMark.break-visibility = ##(#t #t #f)" + regex.sub("\\\\bar\" :|||:\"", DELAY["out"])
		elif DELAY["line"]["Style"][0] == "SectionClose" and line["Style"][0] == "SectionOpen":
			DELAY["out"] = "\\bar\"|.|\"\n\t"
		elif DELAY["line"]["Style"][0] == "MasterRepeatClose" and line["Style"][0] == "MasterRepeatOpen":
			DELAY["out"] = "\\bar\":|.|:\"\n\t"
		
		DELAY["line"] = line
		return
	
	printOut(DELAY["out"])
	DELAY["out"] = ''
	
	if DELAY["fermata"]:
		if DELAY["fermata"][0] == '_':
			DELAY["out"] += "\\once\\override Score.RehearsalMark.direction = #-1 \\mark\\markup\\musicglyph #\"scripts.dfermata\" "
		else:
			DELAY["out"] += "\\mark\\markup\\musicglyph #\"scripts.ufermata\" "
		DELAY["fermata"] = ''
	
	if line.get("Style",["Single"])[0] == "LocalRepeatClose":
		DELAY["out"] += "\\mark\\markup\\small\"(%s)\"\\bar\":||\"\n\t" % (line.get("Repeat",["2"])[0],)
	else:
		DELAY["out"] += "%s\n\t" % (table.bar.get(line.get("Style",["Single"])[0],"|"),)
	KEY[1].update(KEY[0])
	DELAY["line"] = line
	
def Key(line):
	printOut(DELAY["out"])
	
	DELAY["out"] = "\set Staff.keySignature = #`( %s)\n\t" % (" ".join(["(%d . %s) " % ("CDEFGAB".index(a[0]), [",FLAT", ",SHARP"]["b#".index(a[1])]) for a in line["Signature"]]) if line["Signature"][0] != "C" else '', )
	KEY[0] = {a: 'n' for a in "abcdefg"}
	if line["Signature"][0] != "C":
		KEY[0].update([(a[0].lower(), a[1]) for a in line["Signature"]])
	KEY[1].update(KEY[0])
	DELAY["line"] = line

def Time(line):
	global TIME, NUMTIMESIG
	TIME = {"Common": '4/4', "AllaBreve": '2/2'}.get(line["Signature"][0], line["Signature"][0])
	printOut(DELAY["out"])
	DELAY["out"] = ''
	
	if line['Signature'][0] in ["Common", "AllaBreve"] and NUMTIMESIG:
		DELAY["out"] = "\\defaultTimeSignature "
		NUMTIMESIG = False
	elif line['Signature'][0] in ['4/4', '2/2'] and not NUMTIMESIG:
		DELAY["out"] = "\\numericTimeSignature "
		NUMTIMESIG = True
	
	DELAY["out"] += "\\time %s\n\t" % (TIME,)
	DELAY["line"] = line

def Clef(line):
	printOut(DELAY["out"])
	
	PREVNOTE[0] -= CLEFDIFF[CLEF[0]] + {"_8": 7, "^8": -7, "":0}[CLEF[1]]
	CLEF[0] = line["Type"][0]
	
	if "OctaveShift" in line:
		CLEF[1] = {"Octave Down": "_8", "Octave Up": "^8"}.get(line["OctaveShift"][0],"")
		DELAY["out"] = "\\clef \"%s%s\" " % (CLEF[0].lower(), CLEF[1])
	else:
		CLEF[1] = ""
		DELAY["out"] = "\clef %s " % (line["Type"][0].lower(), )
	PREVNOTE[0] += CLEFDIFF[CLEF[0]] + {"_8": 7, "^8": -7, "":0}[CLEF[1]]
	DELAY["line"] = line

def StaffProperties(line):
	global ENDBAR
	if "EndingBar" in line:
		ENDBAR = table.endbar.get(line["EndingBar"][0],"|.")

def AddStaff(line):
	global STAFFADDED
	printOut(DELAY["out"])
	voice2 = ""
	if MEASURE["dur2"]:
		if MEASURE["dur"] > MEASURE["dur2"]:
			MEASURE["voice2"] += "s1*%d/%d" % (MEASURE["dur"] - MEASURE["dur2"]).as_integer_ratio()
		voice2 = "}\\\\{" + MEASURE["voice2"] + "}}>>"
	Reset()
	
	if STAFFADDED:
		DELAY["out"] = voice2 + "\\bar \"%s\"}\n}\\new Staff{\n\t\\compressFullBarRests\n\t\\relative b\'{\n\t" % (ENDBAR,)
	
	STAFFADDED = True
	DELAY["line"] = line

def Text(line):
	printOut(DELAY["out"])
	
	DELAY["out"] = "<>%c\\markup%s%s" % ('_' if line["Pos"][0][0] == '-' else '^', FONT[line["Font"][0]], line["Text"][0])
	DELAY["line"] = line

def Dynamic(line):
	if DELAY["dynamic"] == '\\f' and line["Style"][0] == 'p':
		DELAY["dynamic"] = '\\fp'
	else:
		DELAY["dynamic"] = "\\%s" % (line["Style"][0],)

def DynamicVar(line):
	if line["Style"][0] == "Crescendo":
		DELAY["dynamicvar"] = "\\cresc"
	elif line["Style"][0] == "Decrescendo":
		DELAY["dynamicvar"] = "\\decresc"
	elif line["Style"][0] == "Diminuendo":
		DELAY["dynamicvar"] = "\\dim"
	elif line["Style"][0] == "Rinforzando":
		DELAY["dynamic"] = "\\rfz"
	elif line["Style"][0] == "Sforzando":
		DELAY["dynamic"] = "\\sfz"

def Tempo(line):
	printOut(DELAY["out"])
	
	DELAY["out"] = "\\tempo"
	if "Text" in line:
		DELAY["out"] += (line["Text"][0])
	DELAY["out"] += "%s=%s " % ({"Eighth":"8", "Eighth Dotted":"8.", "Quarter":"4", "Quarter Dotted":"4.", "Half":"2", "Half Dotted":"2."}[line.get("Base",["Quarter"])[0]], line["Tempo"][0])
	DELAY["line"] = line

def TempoVar(line):
	printOut(DELAY["out"])
	DELAY["out"] = ''
	
	if line["Style"][0] == "Breath Mark":
		DELAY["out"] = "\\breathe "
	elif line["Style"][0] == "Caesura":
		DELAY["out"] = "\\caesura "
	elif line["Style"][0] == "Fermata":
		DELAY["fermata"] = "%s\\fermata" % ('_' if line["Pos"][0][0] == '-' else '', )
	elif line["Style"][0] in table.tempovar:
		DELAY["tempovar"] += "%c\\markup\\italic\"%s\"" % ('_' if line["Pos"][0][0] == '-' else '^', table.tempovar[line["Style"][0]])
	
	DELAY["line"] = line

def MultiBarRest(line):
	printOut(DELAY["out"])
	
	dur = "1*%s*%s" % (TIME, line["NumBars"][0]) if eval(TIME) != 1. else "1*%s" % (line["NumBars"][0],)
	
	if dur != PREVNOTE[1]:
		DELAY["out"] = "R%s " % (dur,)
		PREVNOTE[1] = dur
	
	DELAY["line"] = line

def Sustain(line):
	DELAY["sustain"] = "\\sustainOff" if line.get("Status", ["Down"])[0] == "Released" else "\\sustainOn"

def PerformStyle(line):
	printOut(DELAY["out"])
	DELAY["out"] = ''
	
	if line["Style"][0] in table.performstyle:
		DELAY["out"] = "\\mark\\markup\\italic\\bold\\large\"%s\" " % (table.performstyle[line["Style"][0]],)
	
	DELAY["line"] = line

def Flow(line):
	printOut(DELAY["out"])
	DELAY["out"] = ''
	
	if line["Style"][0] in table.flow:
		DELAY["out"] = "\\mark\\markup%s" % (table.flow[line["Style"][0]],)
	
	DELAY["line"] = line

Reset()
with open(IF, errors='backslashreplace', newline=None) as f:
	printOut(HEADER)
	for line in (Tokenise(a[:-1]) for a in f if a[0] == '|' ):
		#faking switch case
		SWITCH.get(line[''][0], lambda : printErr(line[''][0]))()
	
	printOut(DELAY["out"])
	
	if MEASURE["dur2"]:
		if MEASURE["dur"] > MEASURE["dur2"]:
			MEASURE["voice2"] += "s1*%d/%d" % (MEASURE["dur"] - MEASURE["dur2"]).as_integer_ratio()
		MEASURE["voice2"] = "}\\\\{" + MEASURE["voice2"] + "}}>>"
	printOut("%s\\bar \"%s\"" % (MEASURE["voice2"],ENDBAR))
	printOut(FOOTER)

