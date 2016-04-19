# encoding: utf-8
# 2. Projekt do predmetu IPP 2016 v jaztku python
# varianta projektu: MKA – minimalizace konecniho automatu
# autor : xondri04 -> xondri04@stud.fit.vutbr.cz
# datum: 4/10/2016

import os, sys, analysis

napoveda = "Skript sluziaci na minimalizaciu konecneho automatu v pythone.\n\
       --help\n\
              Vypis napovedy skriptu.\n\
       --input=filename\n\
              Zadany vstupny subor relativnou, alebo absolutnou cestou. Pokial  nieje zadany, ako vstup sa pouzije stdin\n\
       --output=filname\n\
              Vystupni subor relativnou, alebo absolutnou cestou. Pokial nieje zadany, ako vystup sa pouzije stdout\n\
       -f, --find-non-finishing\n\
              Hlada sa neukoncujuci stav zadaneho WSPFA.\n\
       -m, --minimize\n\
              Minimalizacia WSPFA.\n\
       -i, --case-insensitive\n\
              Skript ignoruje rozdiel vo velkosti pismen.\n\
"

""" Vypis chybovej hlasky na stderr a exit skriptu s prislusnym chybovym stavom (cislom). 
Argument e_id - iidentifikator chyby
"""
def chybovy_vypis(e_id='e_unknown'):
	
	errors = {
		'e_ok'			: [0],
		'e_arg'  		: [1,  'Chybne zadane parametre skryptu, alebo nespravny format.'],
		'e_in'  		: [2,  'Chyba vstupneho suboru - neexistuje , alebo nejde otvorit pre citanie.'],
		'e_out'  		: [3,  'Chyba vystupneho suboru - neexistuje, alebo nejde otvorit pre zapis.'],
		'e_format'		: [4,  'Chybny format vstupneho suboru.'],
		'e_ana'			: [60, 'Chybne zadany konecny automat, nesplna lexikalne a syntakticke pravidla.'],
		'e_sem'			: [61, 'Semanticka chyba.'],
		'e_wsfa'		: [62, 'Konecny automat neni dobre specifikovan.'],
		'e_unknown'		: [101,'Ostatne chyby.'],
	}
	if e_id != 'e_ok':
		print(errors[e_id][1], file=sys.stderr)
		sys.chybovy_vypis(errors[e_id][0])
	else:
		sys.exit(0)

# trieda argumenty, obsahuje zaznamy o zadanych argumentoch
class Arguments:
	def __init__(self):
		self.vstup = sys.stdin
		self.vystup = sys.stdout
		self.f 			= None # argument -f
		self.m 			= None # argument -m
		self.i 			= None # argument -i
		self.wht		= None # bonus wth
		self.rlo		= None # bonus rlo
		self.mst		= None # bonus mst
		self.mws 		= None # bonus mws
		self.neznama		= None

# Spracovanie parametru imput , zistenie ci sa jedna o subor , alebo stdin
	def nastav_vstup(self, argumenty):
		vstupny_subor = argumenty[argumenty.find("--input=")+len("--input="):]
		try:
# Pokus otvorit subor pre citanie 			
			self.vstup = open(vstupny_subor, 'r')
		except: 
			chybovy_vypis('e_in')

# Spracovanie parametru output , zistenie ci sa jedna o subor , alebo stdout
	def nastav_vystup(self, argumenty):
		vystupny_subor = argumenty[argumenty.find("--output=")+len("--output="):]
		try:
# Pokus otvorit subor pre zapis 			
			self.vystup = open(vystupny_subor, 'w')
		except:
			chybovy_vypis('e_in')
# Spracovanie parametru anamyze-string 
	def nastav_hladany(self,argumenty):
		mst_text = argumenty[argumenty.find("--analyze-string=")+len("--analyze-string="):]
		if mst_text[0] == "\"" or mst_text[-1] == "\"":
			mst_text = mst_text[1:-1]
		self.mst = mst_text

	def show(self):
		""" Prints values of variables in object """
		print("Argumenty:")
		print("\tinput:", self.vstup)
		print("\toutput:", self.vystup)
		print("\tfind-non-finishing:", self.f)
		print("\tminimize:", self.m)
		print("\tcase-insensitive:", self.i)
		print("\tuknown(optional):", self.neznama)

# kontrola, ci boli argumenty zadane spravne , ci sa nevyskytuje nepovolena kombinacia
	def kontrola_argumentov(self):
		if self.f and self.m:
			return False
		elif (self.f or self.m) and self.mst:
			return False
		elif self.neznama:
			return False

		return True

if __name__ == '__main__':
	argumenty = Arguments()

	for p in sys.argv[1:]:
		if p == "--help":
			if len(sys.argv) == 2:
				print(help)
				chybovy_vypis('e_ok')
			else:
				chybovy_vypis('e_arg')

		if p == "-f" or p == "--find-non-finishing":
			argumenty.f = True
		elif p.find("--input=") != -1:
			argumenty.nastav_vstup(p
		elif p.find("--output=") != -1:
			argumenty.nastav_vystup(p)
		elif p == "-m" or p == "--minimize":
			argumenty.m = True
			
		elif p == "-i" or p == "--case-insensitive":
			argumenty.i = True
		elif p == "-r" or p == "--rules-only":
			argumenty.rlo = True	
		elif p.find("--analyze-string=") != -1:
			argumenty.nastav_hladany(p)
		elif p == "-w" or p == "--white-char":
			argumenty.wht = True
		elif p == "--wsfa":
			argumenty.mws = True
		else:
			argumenty.neznama = True

	if not argumenty.kontrola_argumentov():
		chybovy_vypis("e_arg")

#citanie vstupu , nacitanie do pamati
	try:
		citany_text = argumenty.vstup.read()
	except:
		chybovy_vypis('e_in')

# ak bol zadany parameter i , vsetky znaky zmen na male teda A na a , ...
	if argumenty.i:
		citany_text = citany_text.lower()

#vytvorenie instancie Analysis objektu a jej analyza
	ana = analysis.Analysis(citany_text, argumenty.wht, argumenty.i)
	code, machine = 0, ""
#v pripade, ze je pozadovane previest rlo bonus, pouzije sa odlisna funkcia na analyzovanie
	if argumenty.rlo:
		code, machine = ana.analyze_by_rules()
	else:
		code, machine = ana.analyze()
	if code != 0:
		print(machine, file=sys.stderr)
		chybovy_vypis('e_ana')

#odstranenie opakujucich sa
	machine._nahrad_opakujucel_()

#hladanie semantickych chyb
	code, msg = machine.over()
	if code != 0:
		chybovy_vypis('e_sem')

# ak je zadany parameter mws, pokusi sa previest fsm into wsfa
	if argumenty.mws:
		machine._preved_na_wsfa_()

#kontrola , ci sa jedna o wsfa
	if not machine._je_wsfa_():
		chybovy_vypis('e_wsfa')

#kontola , ci je zadany mst a ak ano tak pokus previest na pozadovany retazec
	if argumenty.mst:
		if machine._analyzuj_retazec_(argumenty.mst):
			print("1", sep="", end="\n", file=argumenty.vystup)
		else:
			print("0", sep="", end="\n", file=argumenty.vystup)
		chybovy_vypis('e_ok')

	if argumenty.f:
#najdenie neukoncujucich stavov
		non_finishing = machine._neukoncujuce_stavy_()
		if len(non_finishing) > 0:
			print(non_finishing[0], file=argumenty.vystup, end="")
		chybovy_vypis('e_ok')

	if argumenty.m:
#minimalizacia
		machine._minimalizuj_()
#vypis
		machine._vypis_minimalizovany_(argumenty.vystup)
		chybovy_vypis('e_ok')

# ak nebol nutny ziaden prevod , ani zasah vypise sa le wsfa
	machine._vypis_wsfa_(argumenty.vystup)

# zatvorenie suborov a ukoncenie skriptu
	argumenty.vystup.close()
	argumenty.vstup.close()
	chybovy_vypis('e_ok')
