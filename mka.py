# encoding: utf-8
# 2. Projekt do predmetu IPP 2016 v jaztku python
# varianta projektu: MKA – minimalizace konecniho automatu
# autor : xondri04 -> xondri04@stud.fit.vutbr.cz
# datum: 4/10/2016

import os, sys, analysis

help = "Skript sluziaci na minimalizaciu konecneho automatu v pythone.\n\
       --help\n\
              Vypis napovedy skriptu.\n\
       --input=filename\n\
              Zadany vstupny subor. Pokial  nieje zadany, ako vstup sa pouzije stdin\n\
       --output=filname\n\
              Vystupni subor. Pokial nieje zadany, ako vystup sa pouzije stdout\n\
       -f, --find-non-finishing\n\
              Hlada sa neukoncujuci stav zadaneho WSPFA.\n\
       -m, --minimize\n\
              Minimalizacia WSPFA.\n\
       -i, --case-insensitive\n\
              Skript ignoruje rozdiel vo velkosti pismen.\n\
"


""" Vypis chybovej hlasky na stderr a ukoncenie skriptu s prislusnym chybovym stavom (cislom). 
Argument e_id - iidentifikator chyby
"""

def exit(e_id='e_unknown'):
	
	errors = {
		'e_ok'			: [0],
		'e_arg'  		: [1,  'Chybne zadane parametre skryptu, alebo nespravny format.'],
		'e_in'  		: [2,  'Chyba vstupneho suboru - neexistuje , alebo nejde otvorit pre citanie.'],
		'e_out'  		: [3,  'Chyba vystupneho suboru - neexistuje, alebo nejde otvorit pre zapis.'],
		'e_format'		: [4,  'Chybny format vstupneho suboru.'],
		'e_ana'			: [60, 'Chybne zadany konecny automat, nesplna lexikalne a syntakticke pravidla.'],
		'e_sem'			: [61, 'Semanticka chyba.'],
		'e_wsfa'		: [62, 'Konecny automat neni dobre specifikovan.'], // nema byt
		'e_unknown'		: [100,'Ostatne chyby.'],
	}
	if e_id != 'e_ok':
		print(errors[e_id][1], file=sys.stderr)
		sys.exit(errors[e_id][0])
	else:
		sys.exit(0)

class Arguments:
	def __init__(self):
		self.input = sys.stdin
		self.output = sys.stdout
		self.f 			= None # find non-finishing
		self.m 			= None # minimze
		self.i 			= None # case-insensitive
		self.wht		= None # white-char bonus
		self.rlo		= None # rules-only bonus
		self.mst		= None # analyze string bonus
		self.mws 	= None # well-specified final automat bonus
		self.unknown= None

	def set_input(self, arg):
		filename = arg[arg.find("--input=")+len("--input="):]
		try:
			self.input = open(filename, 'r')
		except: 
			exit('e_in')

	def set_output(self, arg):
		filename = arg[arg.find("--output=")+len("--output="):]
		try:
			self.output = open(filename, 'w')
		except:
			exit('e_in')

	def set_mst(self,arg):
		mst_text = arg[arg.find("--analyze-string=")+len("--analyze-string="):]
		if mst_text[0] == "\"" or mst_text[-1] == "\"":
			mst_text = mst_text[1:-1]
		self.mst = mst_text

	""" Vypis hodnot ulozenych v objekte """
	def show(self):
		print("Argumenty:")
		print("\tinput:", self.input)
		print("\toutput:", self.output)
		print("\tfind-non-finishing:", self.f)
		print("\tminimize:", self.m)
		print("\tcase-insensitive:", self.i)
		print("\tuknown(optional):", self.unknown)

	""" Kontrola, ci su pravidla OK """
	def is_ok(self):
		if self.f and self.m:
			return False
		elif (self.f or self.m) and self.mst:
			return False
		elif self.unknown:
			return False

		return True

if __name__ == '__main__':
	args = Arguments()

	for p in sys.argv[1:]:
		if p == "--help":
			if len(sys.argv) == 2:
				print(help)
				exit('e_ok')
			else:
				exit('e_arg')

		if p == "-f" or p == "--find-non-finishing":
			args.f = True
		elif p == "-m" or p == "--minimize":
			args.m = True
		elif p == "-i" or p == "--case-insensitive":
			args.i = True
		elif p.find("--input=") != -1:
			args.set_input(p)
		elif p.find("--output=") != -1:
			args.set_output(p)
		elif p == "-w" or p == "--white-char":
			args.wht = True
		elif p == "-r" or p == "--rules-only":
			args.rlo = True
		elif p.find("--analyze-string=") != -1:
			args.set_mst(p)
		elif p == "--wsfa":
			args.mws = True
		else:
			args.unknown = True

	if not args.is_ok():
		exit("e_arg")

	#otvorenie vstupneho suboru pre citanie
	try:
		source_txt = args.input.read()
	except:
		exit('e_in')

	if args.i:
		source_txt = source_txt.lower()

	#create instance of Analysis object and analyze it
	ana = analysis.Analysis(source_txt, args.wht, args.i)
	code, machine = 0, ""
	#in case of rlo bonus use different analyze function
	if args.rlo:
		code, machine = ana.analyze_by_rules()
	else:
		code, machine = ana.analyze()
	if code != 0:
		print(machine, file=sys.stderr)
		exit('e_ana')

	#reamove duplicates
	machine.remove_duplicates()

	#validate (look for semantic errors)
	code, msg = machine.validate()
	if code != 0:
		exit('e_sem')

	# if mws is enabled, try convert fsm into wsfa
	if args.mws:
		machine.to_wsfa()

	#check if it is wsfa
	if not machine.is_wsfa():
		exit('e_wsfa')

	#chech if there is mst and if so try string
	if args.mst:
		if machine.analyze_string(args.mst):
			print("1", sep="", end="\n", file=args.output)
		else:
			print("0", sep="", end="\n", file=args.output)
		exit('e_ok')

	if args.f:
		#find non-finishing
		non_finishing = machine.non_finishing_states()
		if len(non_finishing) > 0:
			print(non_finishing[0], file=args.output, end="")
		exit('e_ok')

	if args.m:
		#minimize
		machine.minimize()
		#write it
		machine.write_minimized(args.output)
		exit('e_ok')

	# if we did nothing so far, print only wsfa
	machine.write_wsfa(args.output)

	# cleaning up and exiting
	args.output.close()
	args.input.close()
	exit('e_ok')
