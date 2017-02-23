import sys
IF = sys.argv[1] if sys.argv.__len__() > 1 else "SONG1.nwctxt"
OF = sys.stdout
ERR = sys.stderr
HEADER = """\
\\version \"2.18.2\"
\\pointAndClickOff
\\defineBarLine \":||\" #\'(\":||\" \"\" \" ||\")
\\defineBarLine \"||:\" #\'(\"||:\" \"\" \"|| \")
\\defineBarLine \"!!\" #\'(\"!!\" \"\" \"!!\")

\\score{
<< \\new Staff{
	\\relative b\'{
	"""

FOOTER = """\
}
}>>
}
"""

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
          "Note":            lambda : Expression(line,'note'),
          "Rest":            lambda : Expression(line,'rest'),
          "Bar":             lambda : Bar(line),
          "Key":             lambda : Key(line),
          "TimeSig":         lambda : Time(line),
          "Clef":            lambda : Clef(line),
          "StaffProperties": lambda : StaffProperties(line),
          "AddStaff":        lambda : AddStaff(line),
          "Text":            lambda : Text(line)}

#Tempo
#TempoVariance
#Dynamic
#DynamicVariance
#Chord
#Text

FONT = {"StaffItalic":   "\\abs-fontsize #10 \\bold\\italic",
        "StaffBold":     "\\abs-fontsize #8 \\bold",
		"StaffLyric":    "\\abs-fontsize #7 ",
		"PageTitleText": "\\abs-fontsize #24 \\bold",
		"PageText":      "\\abs-fontsize #12 ",
		"PageSmallText": "\\abs-fontsize #8 ",
		"User1":         "\\abs-fontsize #8 ",
		"User2":         "\\abs-fontsize #8 ",
		"User3":         "\\abs-fontsize #8 ",
		"User4":         "\\abs-fontsize #8 ",
		"User5":         "\\abs-fontsize #8 ",
		"User6":         "\\abs-fontsize #8 "}

def Reset():
	global PREVNOTE, TIME, NUMTIMESIG, ENDBAR, CLEF, KEY, SPAN, DELAY
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
			 "dynamicvar": ''}

def Tokenise(s):
	return {a[0]:a[1].split(',') for a in (a.split(':') for a in (':' + s[1:]).split('|')) }

def printOut(s):
	print(s, end='', file=OF)

def printErr(s):
	print("\r\tError: %s" % (s,), file=ERR)

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
	if expr in ['note']:
		pitch = Pitch(line['Pos'][0])
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
	
	#triplet off
	if dur['triplet'] == 'end':
		note += '}'
	
	#grace off
	if not dur['grace'] and SPAN['grace']:
		SPAN['grace'] = False
		note = '}' + note
	
	printOut("%s " % (note,))

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
	
	return note

def Bar(line):
	printOut("%s\n\t" % (
        {"Single": "|",
         "Double": "\\bar\"||\"",
         "BrokenSingle": "\\bar\"!\"",
         "BrokenDouble": "\\bar\"!!\"",
         "SectionOpen": "\\bar\".|\"",
         "SectionClose": "\\bar\"|.\"",
         "LocalRepeatOpen": "\\bar\"||:\"",
         "LocalRepeatClose": "\\mark\\markup\\small\"(%s)\"\\bar\":||\"" % (line.get("Repeat",["2"])[0],),
         "MasterRepeatOpen": "\\bar\".|:\"",
         "MasterRepeatClose": "\\bar\":|.\""
        }.get(line.get("Style",["Single"])[0],"|"),
	))
	KEY[1].update(KEY[0])
	
def Key(line):
	printOut("\set Staff.keySignature = #`( %s)\n\t" % (" ".join(["(%d . %s) " % ("CDEFGAB".index(a[0]), [",FLAT", ",SHARP"]["b#".index(a[1])]) for a in line["Signature"]]) if line["Signature"][0] != "C" else '', ))
	KEY[0] = {a: 'n' for a in "abcdefg"}
	if line["Signature"][0] != "C":
		KEY[0].update([(a[0].lower(), a[1]) for a in line["Signature"]])
	KEY[1].update(KEY[0])

def Time(line):
	global TIME, NUMTIMESIG
	TIME = {"Common": '4/4', "AllaBreve": '2/2'}.get(line["Signature"][0], line["Signature"][0])
	
	if line['Signature'][0] in ["Common", "AllaBreve"] and NUMTIMESIG:
		printOut("\\defaultTimeSignature ")
		NUMTIMESIG = False
	elif line['Signature'][0] in ['4/4', '2/2'] and not NUMTIMESIG:
		printOut("\\numericTimeSignature ")
		NUMTIMESIG = True
	
	printOut("\\time %s\n\t" % (TIME,))

def Clef(line):
	PREVNOTE[0] -= CLEFDIFF[CLEF[0]] + {"_8": 7, "^8": -7, "":0}[CLEF[1]]
	CLEF[0] = line["Type"][0]
	
	if "OctaveShift" in line:
		CLEF[1] = {"Octave Down": "_8", "Octave Up": "^8"}.get(line["OctaveShift"][0],"")
		printOut("\\clef \"%s%s\" " % (CLEF[0].lower(), CLEF[1]))
	else:
		CLEF[1] = ""
		printOut("\clef %s " % (line["Type"][0].lower(), ))
	PREVNOTE[0] += CLEFDIFF[CLEF[0]] + {"_8": 7, "^8": -7, "":0}[CLEF[1]]

def StaffProperties(line):
	global ENDBAR
	if "EndingBar" in line:
		ENDBAR = {"Section Close": "|.",
                  "Master Repeat Close": ":|.",
                  "Single": "|",
                  "Double": "||",
                  "Open (hidden)": ""}.get(line["EndingBar"][0],"|.")

def AddStaff(line):
	global STAFFADDED
	if STAFFADDED:
		printOut("\\bar \"%s\"}\n}\\new Staff{\n\t\\relative b\'{\n\t" % (ENDBAR,))
	
	STAFFADDED = True
	Reset()

def Text(line):
	printOut("<>%c\\markup%s%s" % ('_' if line["Pos"][0][0] == '-' else '^', FONT[line["Font"][0]], line["Text"][0]))

Reset()
with open(IF, errors='backslashreplace', newline=None) as f:
	printOut(HEADER)
	for line in (Tokenise(a[:-1]) for a in f if a[0] == '|' ):
		#faking switch case
		SWITCH.get(line[''][0], lambda : printErr(line[''][0]))()
	
	printOut("\\bar \"%s\"" % (ENDBAR,))
	printOut(FOOTER)

