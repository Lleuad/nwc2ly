# -*- coding: utf-8
#from __future__ import unicode_literals
bar = {
"Single": "|",
"Double": "\\bar\"||\"",
"BrokenSingle": "\\bar\"!\"",
"BrokenDouble": "\\bar\"!!\"",
"SectionOpen": "\\bar\".|\"",
"SectionClose": "\\bar\"|.\"",
"SectionCloseOpen": "\\bar\"|.|\"",
"LocalRepeatOpen": "\\bar\"||:\"",
"LocalRepeatClose": "\\bar\":||\"",
"LocalRepeatCloseOpen": "\\bar\":|||:\"",
"MasterRepeatOpen": "\\bar\".|:\"",
"MasterRepeatClose": "\\bar\":|.\"",
"MasterRepeatCloseOpen": "\\bar\":|.|:\"",
"Transparent": "\\bar\"\"",
}

endbar = {
"Section Close": "|.",
"Master Repeat Close": ":|.",
"Single": "|",
"Double": "||",
"Open (hidden)": ""}

tempovar = {
"Accelerando": "accel.",
"Allargando": "allarg.",
"Rallentando": "rall.",
"Ritardando": "ritard.",
"Ritenuto": "rit.",
"Rubato": "rubato",
"Stringendo": "string."}

performstyle = {
"Ad Libitum": "ad lib.",
"Animato": "animato",
"Cantabile": "cantabile",
"Con brio": "con brio",
"Dolce": "dolce",
"Espressivo": "espress.",
"Grazioso": "grazioso",
"Legato": "legato",
"Maestoso": "maestoso",
"Marcato": "marc.",
"Meno mosso": "meno mosso",
"Poco a poco": "poco a poco",
"Pi\\xf9 mosso": "più mosso",
"Semplice": "semplice",
"Simile": "simile",
"Solo": "solo",
"Sostenuto": "sostenuto",
"Sotto Voce": "sotto voce",
"Staccato": "staccato",
"Subito": "subito",
"Tenuto": "tenuto",
"Tutti": "tutti",
"Volta Subito": "volta subito"}

flow = {
"Coda": "{\\musicglyph #\"scripts.coda\"}",
"Segno": "{\\musicglyph #\"scripts.segno\"}",
"Fine": "\"fine\"",
"ToCoda": "\\musicglyph #\"scripts.coda\" ",
"DaCapo": "\"D.C.\"",
"DCalCoda": "{\"D.C. al \"\\raise #1.0 \\musicglyph #\"scripts.coda\"}",
"DCalFine": "\"D.C. al fine\"",
"DalSegno": "\"D.S.\"",
"DSalCoda": "{\"D.S. al\"\\raise #1.0 \\musicglyph #\"scripts.coda\"}",
"DSalFine": "\"D.S. al fine\""}
