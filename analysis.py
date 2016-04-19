#projekt : mka
#autor : Matus Ondris

import fsm, re, sys

class lex:
	class left_par: #(
		pass
	class right_par: #)
		pass
	class left_curly: #{
		pass
	class right_curly: #}
		pass
	class comma: #,
		pass
	class dot: #.
		pass
	class arrow: #->
		pass
	class string: #'abc' or abc
		pass
	class eof:
		pass

# deklaracia triedy + premennych
class Analysis:
	def __init__(self, source, ws, c_insensitive):
		self.text = source
		self.ws = ws
		self.was_ws = False

		self.got_ws = False
		self.txt = ""
		self.token = lex.eof


		self.fsm = fsm.FinalStateMachine(c_insensitive)

		self.cursor = 0

		self.re_identifier = re.compile(r"^[^\d\W]\w*\Z")

		self.reserved_chars = [
			'(',
			')',
			'{',
			'}',
			'-',
			'>',
			',',
			'.',
		]
		
## metody sluziace na lexikalnu analyzu ##

#rozdeli vstupny retazec a vrati dalsi token 
	def __get_token(self):
		if self.got_ws == True:
			self.got_ws = False
			return self.txt, self.token

#kontrola , ci kurzor je mimo retazec
		if self.cursor >= len(self.text):
			self.txt = ""
			self.token = lex.eof
			return '', lex.eof

#odstranenie bielych znakov
		while self.text[self.cursor].isspace():
			self.was_ws = True
			self.cursor += 1
			if self.cursor >= len(self.text):
				self.txt = ""
				self.token = lex.eof
				return '', lex.eof

#ziska aktualny znak a nastavy kurzor na dalsi znak
		char = self.text[self.cursor]
		self.cursor += 1

		if char in self.reserved_chars:
			if char == '-' and self.text[self.cursor] == '>':
				self.cursor += 1 
				self.char = "->"
				self.token = lex.arrow
				return '->', lex.arrow
			elif char == '(':
				self.char = "("
				self.token = lex.left_par
				return char, lex.left_par
			elif char == ')':
				self.char = ")"
				self.token = lex.right_par
				return char, lex.right_par
			elif char == '{':
				self.char = "{"
				self.token = lex.left_curly
				return char, lex.left_curly
			elif char == '}':
				self.char = "}"
				self.token = lex.right_curly
				return char, lex.right_curly
			elif char == ',':
				self.char = ","
				self.token = lex.comma
				return char, lex.comma
			elif char == '.':
				self.char = "."
				self.token = lex.dot
				return char, lex.dot


#odstranenie komentarob a ziskanie dalsieho tokenu
		elif char == '#':
			self.was_ws = True
			while char != '\n':
				self.cursor += 1
				if self.cursor >= len(self.text):
					self.txt = ""
					self.token = lex.eof
					return '', lex.eof
				char = self.text[self.cursor]
			return self.__get_token()

#analyzovanie retazca v apostrofoch
		elif char == '\'':
			rslt = ""
			end = False

			while not end:
				rslt += char
				if self.cursor >= len(self.text):
					self.txt = ""
					self.token = lex.eof
					return '', lex.eof
				char = self.text[self.cursor]
				self.cursor += 1

				if char == '\'':
					if self.text[self.cursor] != '\'':
						rslt += char
						end = True
					else:
						rslt += char
						self.cursor += 1
			self.txt = rslt[1:-1]
			self.token = lex.string
			return rslt[1:-1], lex.string

#analyzovanie identifikatora alebo retazca mimo apostrofov
		else:
			rslt = ""
			while not char.isspace() and char not in self.reserved_chars and char != '\'':
				rslt += char
				if self.cursor >= len(self.text):
					self.txt = ""
					self.token = lex.eof
					return '', lex.eof
				char = self.text[self.cursor]
				self.cursor += 1
			self.cursor -= 1 
			self.txt = rslt
			self.token = lex.string
			return rslt, lex.string

#kontrola ci retazec v textovom argumente je C identifikator , alebo nie
	def __is_identifier(self, text):
		return True if re.match(self.re_identifier, text) != None else False

## metody sluziace na semanticku analyzu ##

#rozdely vsetky stavy z tokenov a ulozi ich do triednych premennych
	def __a_states(self):
		txt, token = self.__get_token()
		#check for left curly bracket
		if token != lex.left_curly:
			return 1, 'Definicia stavu sa musi nachadzat v zatvorkach.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
#ziskanie identifikatoru
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'U definicie stavu je nutny retazec v tvare C identifikatoru.'

#vlozenie do fsm.stavy
			self.fsm.stavy.append(txt)

#hladanie ciarky , alebo }
			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'U definicie stavu musia byt jednotlive polozky oddelene ciarkou.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'U definicie stavu musia byt jednotlive polozky oddelene bielym znakom .'
				if token != lex.right_curly and token != lex.comma:
					self.got_ws = True
			if token != lex.right_curly:
				txt, token = self.__get_token()

		if token != lex.right_curly:
			return 1, 'Definicia stavu musi byt uzatvorena v zlozenych zatvorkach.'

		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Za definiciou stavu sa musi nachadzat ciarka.'
		else:
			if token != lex.comma and self.was_ws != True:
				return 1, 'Za definiciou stavu sa musi nachadzat biely znak .'
			if token != lex.comma:
				self.got_ws = True

		return 0, ''

#rozdelenie znakov abecedy na tokeny a ulozenie ich v premennych tried
	def __a_alphabet(self):
		txt, token = self.__get_token()
		#check for left curly bracket
		if token != lex.left_curly:
			return 1, 'Abeceda musi byt uzatvorena v zlozenych zatvorkach.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			if token != lex.string:
				return 1, 'Ocakavam znak abecedy.'

			self.fsm.abeceda.append(txt)

			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'V abecede musia byt jednotlive polozky oddelene ciarkou alebo koncit pravou zlozenou zatvorkou.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'V abecede musia byt jednotlive polozky oddelene beilym znakem alebo koncit pravou zlozenou zavorkou.'
				if token != lex.comma and token != lex.right_curly:
					self.got_ws = True
		
			if token != lex.right_curly:
				txt, token = self.__get_token()

		if token != lex.right_curly:
			return 1, 'Abeceda musi byt uzatvorena v zlozenych zatvorkach.'

		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Za abecedou sa musi nachadzat ciarka.'
		else:
			if self.was_ws != True and token != lex.comma:
				return 1, 'Za abecedou sa musi nachadzat biely znak.'
			if token != lex.comma:
				self.got_ws = True


		return 0, ''

#rozreli pravidla ziskane z tokenov a ulozi ich v triednych premenych
	def __a_rules(self):
		txt, token = self.__get_token()
		if token != lex.left_curly:
			return 1, 'Pravidla musia byt ohranicene zlozenymi zatvorkami.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			was_arrow = False
			first_state = ""
			alpha_char = ""
			second_state = ""

			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'Na zaciatku stavu ocakavam identifikator stavu.'
			first_state = txt

			txt, token = self.__get_token()
			if token == lex.string:
				alpha_char = txt if txt != "''" else ''
			elif token == lex.arrow:
				was_arrow = True
				alpha_char = ""
			else:
				return 1, 'Po pociatocnom stave ocakavam bud "->" alebo znak abecedy.'

			if not was_arrow:
				txt, token = self.__get_token()
				if token != lex.arrow:
					return 1, 'Po pociatocnom stave a pripadnom znaku abecedy ocakavam "->".'

			txt, token = self.__get_token()
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'Po "->" ocakavam identifikator cieloveho stavu.'
			second_state = txt

			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'Na konci stavu cakam ciarku alebo pravu zlozenu zatvorku.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'Na konci stavu cakam ciarku alebo pravu zlozenu zatvorku.'
				if token != lex.comma and token != lex.right_curly:
					self.got_ws = True

			if token != lex.right_curly:
				txt, token = self.__get_token()

			self.fsm.pravidla.append({
				"first_state": 	first_state,
				"alpha_char": 	alpha_char,
				"second_state":	second_state
			})

		if token != lex.right_curly:
			return 1, 'Definicia pravidiel musi byt ukoncena pravou zlozenou zatvorkou.'

		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Za definiciou pravidiel sa musi nachadzat ciarka.'
		else:
			if self.was_ws != True and token != lex.comma:
				return 1, 'Za definiciou pravidiel sa musi nachadzat biely znak.'
			if token != lex.comma:
				self.got_ws = True

		return 0, ''

#rozdeli pociatocny stav a ulozi ho v premennych triedy
	def __a_start_state(self):
#ocakava identifikator pociatocneho stavu
		txt, token = self.__get_token()
		if token != lex.string or not self.__is_identifier(txt):
			return 1, 'Ocakavam identifikator pociatocneho stavu.'
		self.fsm.pociatocny_stav = txt

		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Po identifikacii pociatocneho stavu ocakavam ciarku.'
		else:
			if token != lex.comma and self.was_ws != True:
				return 1, 'Po identifikacii pociatocneho stavu ocakavam biely znak.'
			if token != lex.comma:
				self.got_ws = True
		return 0, ''

#rozdely koncove stavy z tokenu a ulozi ich v premennej triedy
	def __a_final_states(self):
		txt, token = self.__get_token()
		if token != lex.left_curly:
			return 1, 'Definicia konecnych stavou musi byt uzatvorena v zlozenych zatvorkach.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'V definicii konecnych stavov sa musi nachadzat retazec v tvare C identifikatoru.'

			self.fsm.ukoncujuce_stavy.append(txt)

			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'V definicii konecnych stavov musia byt jednotlive polozky oddelene ciarkou.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'V definicii konecnych stavov musia byt jednotlive polozky oddelene bielym znakem .'
				if token != lex.right_curly and token != lex.comma:
					self.got_ws = True

			if token != lex.right_curly:
				txt, token = self.__get_token()

		if token != lex.right_curly:
			return 1, 'Definicia konecnych stavov musi byt uzatvorena v zlozenych zatvorkach.'

		return 0, ''

#rozdeli cely KA a zavola metody pre rozdelenie jednotlivych komponentov
	def __a_whole(self):
		char, token = self.__get_token()

		if token != lex.left_par:
			return 1, "Cely KA musi byt uzatvoreny lavou gulatou zatvorkou."

		err, msg = self.__a_states()
		if err != 0:
			return err, msg

		err, msg = self.__a_alphabet()
		if err != 0:
			return err, msg

		err, msg = self.__a_rules()
		if err != 0:
			return err, msg

		err, msg = self.__a_start_state()
		if err != 0:
			return err, msg

		err, msg = self.__a_final_states()
		if err != 0:
			return err, msg

		char, token = self.__get_token()
		if token != lex.right_par:
			return 1, "Cely KA musi byt ohraniceny v gulatych zatvorkach."

		char, token = self.__get_token()
		if token != lex.eof:
			return 1, "Po pravej zavorke mozu nasledovat jedine komentare alebo biele znaky."

		return 0, ''

#rozdelenie pravidiel z RLO bonusu a ulozenie v priednych premennych
	def __rules(self):
		txt, token = self.__get_token()
		got_start_state = False

# pokial nenarazi an eof
		while token != lex.eof:
			if token != lex.string or not self.__is_identifier(txt):
				return 1, "Identifikator vychodzieho stavu musi byt v C formatu."

			if not got_start_state:
				self.fsm.pociatocny_stav = txt
				got_start_state = True

			first_state = txt
			self.fsm.stavy.append(txt)

			txt, token = self.__get_token()
			if token != lex.string:
				return 1, "Za vychodzim pravidlom ocakavam znak abecedy."

			self.fsm.abeceda.append(txt)
			char = txt

			txt, token = self.__get_token()
			if token != lex.arrow:
				return 1, "Za znakom abecedy ocakavam dvojznak"

			txt, token = self.__get_token()
			if token != lex.string and not self.__is_identifier(txt):
				return 1, "Identifikator cieloveho stavu musi byt v C formate."

			self.fsm.stavy.append(txt)
			second_state = txt

			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.dot and token != lex.eof:
					return 1, "Za pravidlom ocakavam ciarku alebo bodku."
			else:
				if token != lex.comma and token != lex.dot and token != lex.eof and self.was_ws != True:
					return 1, "Za pravidlom ocekavam ciarku, bodku alebo biely znak."

			if token == lex.dot:
				self.fsm.ukoncujuce_stavy.append(second_state)

			self.fsm.pravidla.append({
				'first_state' : first_state,
				'alpha_char'  : char,
				'second_state': second_state
			})

			txt, token = self.__get_token()

		self.fsm._nahrad_opakujucel_()
		return 0, ""

#obalenie verejnej funkcie pre analyzu pravidiel RLO bonusovej lokacie
	def analyze_by_rules(self):
		err, msg = self.__rules()
		if err != 0:
			return err, msg
		else:
			return err, self.fsm

#obalenie verejnej funkcie pre analyzu KA
	def analyze(self):
		err, msg = self.__a_whole()
		if err != 0:
			return err, msg
		else:
			return 0, self.fsm

if __name__ == '__main__':
	fsm_test = """# velmi jednoducha minimalizace
(
{p, q, r},
{0, 1},
{
p 0 -> q,
p 1 -> p,
q 0 -> r,
q 1 -> q,
r 0 -> q,
r 1 -> p
},
p,
{q}
)"""
	ana = Analysis(fsm_test)
	code, fsm_or_msg = ana.analyze()
	if code == 0:
		fsm_or_msg._nahrad_opakujucel_()
		code, msg = fsm_or_msg.over()
		if code != 0:
			print(msg)
			sys.exit(0)
		#fsm_or_msg._preved_na_wsfa_()
		fsm_or_msg._minimalizuj_()
		fsm_or_msg.show()
	else:
		print(fsm_or_msg)
