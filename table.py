bar = {
"Single": "|",
"Double": "\\bar\"||\"",
"BrokenSingle": "\\bar\"!\"",
"BrokenDouble": "\\bar\"!!\"",
"SectionOpen": "\\bar\".|\"",
"SectionClose": "\\bar\"|.\"",
"LocalRepeatOpen": "\\bar\"||:\"",
"LocalRepeatClose": "\\mark\\markup\\small\"(%s)\"\\bar\":||\"" % (line.get("Repeat",["2"])[0],),
"MasterRepeatOpen": "\\bar\".|:\"",
"MasterRepeatClose": "\\bar\":|.\""}

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

performstyle ={
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
"Pi mosso": "più mosso",
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
