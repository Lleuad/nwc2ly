import sys
IF = "SONG1.nwctxt"
OF = sys.stdout
ERR = sys.stderr

PREVNOTE = [0, ""] #pos, dur
TIME = '4/4'
CLEF = "Treble"
CLEFDIFF = {"Treble": 0, "Bass": 12, "Tenor": 8, "Alto": 6}
KEY = [
       {a: '' for a in "abcdefg"},  #key sig
       {a: '' for a in "abcdefg"},  #measure
       {a: '' for a in "abcdefg"}]  #ties

NOTES = {"Treble": ['b', 'c', 'd', 'e', 'f', 'g', 'a'],
         "Bass":   ['d', 'e', 'f', 'g', 'a', 'b', 'c'],
         "Tenor":  ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
         "Alto":   ['c', 'd', 'e', 'f', 'g', 'a', 'b']}

def Tokenise(s):
	return {a[0]:a[1].split(',') for a in (a.split(':') for a in (':' + s[1:]).split('|')) }

def Pitch(pos):
	pitch = {'accidental': 'n', 'pitch': '', 'head': 'o', 'tie': False}
	if not pos[0].isdigit():
		pitch['accidental'] = pos.pop(0)
	if not pos[-1].isdigit() and pos[-1] == '^':
		pitch['tie'] = True
		pos.pop()
	if not pos[-1].isdigit():
		pitch['head'] = pos.pop()
	if pos.isdigit():
		pitch['pitch'] = pos
	else:
		print("%s is not a number" % (str(pos), ), file=ERR)
		exit()
	
	return pitch

def Dur(dur):
	duration = {'length': '4', 'triplet': None, 'grace': False, 'staccato': False, 'tenuto': False, 'accent': False, 'slur': False}
	if dur[0] == 'Whole':
		duration['length'] = '1'
	elif dur[0] == 'Half':
		duration['length'] = '2'
	elif dur[0][:-2].isdigit()::
		duration['length'] = dur[0][:-2]
	else:
		print("%s is not a number", (str(dur[0][:-2]),))
	
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

def Note(line):
	pitch = Pitch(line['Pos'][0])
	dur = Dur(line['dur'])
	

with open(IF, errors='backslashreplace', newline=None) as f:
	for line in (Tokenise(a[:-1]) for a in f if a[0] == '|' ):
		if line[''] == "Note":
			Note(line)
	

