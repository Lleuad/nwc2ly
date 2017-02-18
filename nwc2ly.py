import sys
IF = "SONG1.nwctxt"
OF = sys.stdout
ERR = sys.stderr

PREVNOTE = [0, ""] #pos, dur
TIME = '4/4'
CLEF = "Treble"
CLEFDIFF = {"Treble": 0, "Bass": 12, "Tenor": 8, "Alto": 6}
KEY = [
       {a: 'n' for a in "abcdefg"},  #key sig
       {a: 'n' for a in "abcdefg"},  #measure
       {a: '' for a in "abcdefg"}]  #ties

NOTES = {"Treble": ['b', 'c', 'd', 'e', 'f', 'g', 'a'],
         "Bass":   ['d', 'e', 'f', 'g', 'a', 'b', 'c'],
         "Tenor":  ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
         "Alto":   ['c', 'd', 'e', 'f', 'g', 'a', 'b']}

SWITCH = {
		"Note": lambda : Expression(line,'note'),
		"Rest": lambda : Expression(line,'rest'),
		"Bar":  lambda : Bar(line),
		}

def Tokenise(s):
	return {a[0]:a[1].split(',') for a in (a.split(':') for a in (':' + s[1:]).split('|')) }

def printOut(s):
	print(s, end='', file=OF)

def printErr(s):
	print("\tError: %s" % (s,), file=ERR)

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
	duration = {'length': '4', 'triplet': None, 'grace': False, 'staccato': False, 'tenuto': False, 'accent': False, 'slur': False}
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
	
	return duration

def Expression(line, expr):
	if expr in ['note']:
		pitch = Pitch(line['Pos'][0])
	dur = Dur(line['Dur'])
	note = ""
	
	if dur['triplet'] == 'first':
		note += '\\tuplet 3/2{'
	
	if expr == 'note':
		note += Note(pitch, dur)
	elif expr == 'rest':
		note += Rest(dur)
	
	if dur['triplet'] == 'end':
		note += '}'
	
	printOut("%s " % (note,))

def Note(pitch, dur):
	name = NOTES[CLEF][pitch['pitch'] % 7]
	
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
	printOut("|\n\t")
	KEY[1].update(KEY[0])
#	KEY[1].update(list(KEY[0].items()) + [a for a in KEY[2].items() if a[1]])

with open(IF, errors='backslashreplace', newline=None) as f:
	printOut('\\version \"2.18.2\"\n\n\\relative b\'{\n\t')
	for line in (Tokenise(a[:-1]) for a in f if a[0] == '|' ):
		#faking switch case
		SWITCH.get(line[''][0], lambda : printErr(line[''][0]))()
	
	printOut('\n}\n')

