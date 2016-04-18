# encoding: utf-8

#MKA:xkurka03

import os, sys, analysis

help = "Aplikace pro minimalizaci konecneho automatu.\n\
	--help\n\
		Vypise tuto napovedu.\n\
	--input=filename\n\
		Vstupni soubor. Pokud neni zadan, pouzije se stdin\n\
	--output=filname\n\
		Vystupni soubor. Pokud neni zadan, pouzije se stdout\n\
	-f, --find-non-finishing\n\
		Hleda neukoncujici stav zadaneho WSPFA.\n\
	-m, --minimize\n\
		Minimalizace WSPFA.\n\
	-i, --case-insensitive\n\
		Ignoruje se rozdil ve velikosti pismen.\n\
"

def exit(e_id='e_unknown'):
	"""Prints error message in stderr and closes the program with corresponding error code. 
	Arguments:
		e_id -- identification of error
	"""

	errors = {
		'e_ok'			: [0],
		'e_arg'  		: [1,  'Spatny format parametru skriptu.'],
		'e_in'  		: [2,  'Chyba pri cteni vstupu skriptu.'],
		'e_out'  		: [3,  'Chyba pri otevreni pro zapis do vystupniho souboru.'],
		'e_format'		: [4,  'Chybny format vstupniho souboru.'],
		'e_ana'			: [60, 'Chybny format konecneho automatu.'],
		'e_sem'			: [61, 'Semanticka chyba definice konecneho automatu.'],
		'e_wsfa'		: [62, 'Konecny automat neni dobre specifikovan.'],
		'e_unknown'		: [255,'Neznama chyba.'],
	}
	if e_id != 'e_ok':
		print(errors[e_id][1], file=sys.stderr)
		sys.exit(errors[e_id][0])
	else:
		sys.exit(0)

class Arguments:
	def __init__(self):
		self.input 	= sys.stdin
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
		except: #cath 'em all :-D
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

	def show(self):
		""" Prints values of variables in object """
		print("Argumenty:")
		print("\tinput:", self.input)
		print("\toutput:", self.output)
		print("\tfind-non-finishing:", self.f)
		print("\tminimize:", self.m)
		print("\tcase-insensitive:", self.i)
		print("\tuknown(optional):", self.unknown)
	#show

	def is_ok(self):
		""" Check if there are all of the rules OK """
		if self.f and self.m:
			return False
		elif (self.f or self.m) and self.mst:
			return False
		elif self.unknown:
			return False

		return True
	#is_ok

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
	#for

	if not args.is_ok():
		exit("e_arg")

	#read input
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
