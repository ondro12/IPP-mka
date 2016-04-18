# encoding: utf-8

#MKA:xondri04

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

class Analysis:
	def __init__(self, source, ws, c_insensitive):
		""" Sets all the variables to init values """
		#main source text
		self.text = source

		#whitespace instead of commas (bonus)
		self.ws = ws

		#"global" variable to contain information if get_token loaded some whitespaces
		self.was_ws = False

        	# just to now if we had ws or comma
		self.got_ws = False
		self.txt = ""
		self.token = lex.eof

		#object from fsm module for containing final state machine
		self.fsm = fsm.FinalStateMachine(c_insensitive)

		#cursor for get_token method
		self.cursor = 0

		#regex for C identifier
		self.re_identifier = re.compile(r"^[^\d\W]\w*\Z")

		#reserved characters
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
	########## methods for lex analysis ##########
	def __get_token(self):
		""" Parses and returns next token from input string """
		if self.got_ws == True:
			self.got_ws = False
			return self.txt, self.token

		#check if cursor is outside string
		if self.cursor >= len(self.text):
			self.txt = ""
			self.token = lex.eof
			return '', lex.eof

		#remove whitespaces from the begging of the rest of a source text
		while self.text[self.cursor].isspace():
			self.was_ws = True
			self.cursor += 1
			if self.cursor >= len(self.text):
				self.txt = ""
				self.token = lex.eof
				return '', lex.eof

		#get acutal character and set cursor to the next char
		char = self.text[self.cursor]
		self.cursor += 1

		#main "switch"
		if char in self.reserved_chars:
			if char == '-' and self.text[self.cursor] == '>':
				self.cursor += 1 #because we used another char for this
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
		#if

		#delete comment and get next token
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

		#analyzing string in apostrophes
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
		#elif

		#analyzing identifier or string outside apostrophes
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
			self.cursor -= 1 #magic, dont touch
			self.txt = rslt
			self.token = lex.string
			return rslt, lex.string
	#get_token

	def __is_identifier(self, text):
		""" Checks if string in text argument is C identifier or not """
		return True if re.match(self.re_identifier, text) != None else False

########## methods for syntactic analysis ##########
	def __a_states(self):
		""" Parses all states from tokens and stores them in class variable """
		txt, token = self.__get_token()
		#check for left curly bracket
		if token != lex.left_curly:
			return 1, 'Definice stavu musi byt uzavrena ve slozenych zavorkach.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			#look for identifier
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'V definici stavu musi byt retezec ve tvaru C identifikatoru.'

			#insert it into fsm.states
			self.fsm.states.append(txt)

			#look for comma or right curly bracket
			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'V definici stavu musi byt jednotlive polozky oddeleny carkou.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'V definici stavu musi byt jednotlive polozky oddeleny bilym znakem (znaky).'
				if token != lex.right_curly and token != lex.comma:
					self.got_ws = True
			# we already got end of state definition - right curly bracket
			if token != lex.right_curly:
				txt, token = self.__get_token()

		#check for right curly bracket
		if token != lex.right_curly:
			return 1, 'Definice stavu musi byt uzavrena ve slozenych zavorkach.'

		#and finally for comma after state definition
		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Za definici stavu musi byt carka.'
		else:
			if token != lex.comma and self.was_ws != True:
				return 1, 'Za definici stavu musi byt bily znak (znaky).'
			if token != lex.comma:
				self.got_ws = True

		#if all went well, we got here
		return 0, ''
	#__a_states

	def __a_alphabet(self):
		""" Parses alphabet characters from token and stores them in class variables """
		txt, token = self.__get_token()
		#check for left curly bracket
		if token != lex.left_curly:
			return 1, 'Abeceda musi byt uzavrena ve slozenych zavorkach.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			#look for alphabet character
			if token != lex.string:
				return 1, 'Ocekavam znak abecedy.'

			#insert it into fsm.alphabet
			self.fsm.alphabet.append(txt)

			#look for comma or right curly bracket
			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'V abecede musi byt jednotlive polozky oddeleny carkou nebo koncit pravou slozenou zavorkou.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'V abecede musi byt jednotlive polozky oddeleny bilym znakem (znaky) nebo koncit pravou slozenou zavorkou.'
				if token != lex.comma and token != lex.right_curly:
					self.got_ws = True
		
			# we already got end of alphabet - right curly bracket
			if token != lex.right_curly:
				txt, token = self.__get_token()

		#check for right curly bracket
		if token != lex.right_curly:
			return 1, 'Abeceda musi byt uzavrena ve slozenych zavorkach.'

		#and finally for comma after state definition
		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Za abecedou musi byt carka.'
		else:
			if self.was_ws != True and token != lex.comma:
				return 1, 'Za abecedou musi byt bily znak.'
			if token != lex.comma:
				self.got_ws = True

		#if all went well, we got here
		return 0, ''
	#__a_alphabet

	def __a_rules(self):
		""" Parses rules from tokens and stores them in class variable """
		txt, token = self.__get_token()
		if token != lex.left_curly:
			return 1, 'Pravidla musi byt ohranicena slozenymi zavorkami.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			was_arrow = False
			first_state = ""
			alpha_char = ""
			second_state = ""

			#look for first state
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'Na zacatku pravidla ocekavam identifikator stavu.'
			first_state = txt

			#if there is alphabet, save it. If not, set arrow flag to true
			txt, token = self.__get_token()
			if token == lex.string:
				alpha_char = txt if txt != "''" else ''
			elif token == lex.arrow:
				was_arrow = True
				alpha_char = ""
			else:
				return 1, 'Po pocatecnim stavu ocekavam bud "->" nebo znak abecedy.'

			#if there wasnt already arrow, check it
			if not was_arrow:
				txt, token = self.__get_token()
				if token != lex.arrow:
					return 1, 'Po pocatecnim stavu a pripadnem znaku abecedy cekam "->".'

			#after arrow must be second state identifier
			txt, token = self.__get_token()
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'Po "->" ocekavam identifikator ciloveho stavu.'
			second_state = txt

			#rule must end with comma or right curly bracket
			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'Na konci pravidla cekam carku nebo pravou slozenou zavorku.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'Na konci pravidla cekam carku nebo pravou slozenou zavorku.'
				if token != lex.comma and token != lex.right_curly:
					self.got_ws = True

			#we already got right curly bracket
			if token != lex.right_curly:
				txt, token = self.__get_token()

			#add rule to the FinalStateMachine
			self.fsm.rules.append({
				"first_state": 	first_state,
				"alpha_char": 	alpha_char,
				"second_state":	second_state
			})
		#while

		if token != lex.right_curly:
			return 1, 'Definice pravidel musi koncit pravou slozenou zavorkou.'

		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Za definici pravidel musi byt carka.'
		else:
			if self.was_ws != True and token != lex.comma:
				return 1, 'Za definici pravidel musi byt bily znak(znaky).'
			if token != lex.comma:
				self.got_ws = True

		return 0, ''
	#__a_rules

	def __a_start_state(self):
		""" Parses start state and stores it in class variable """
		#expecting identifier of start state
		txt, token = self.__get_token()
		if token != lex.string or not self.__is_identifier(txt):
			return 1, 'Ocekavam identifikator pocatecniho stavu.'
		self.fsm.start_state = txt

		self.was_ws = False
		txt, token = self.__get_token()
		if not self.ws:
			if token != lex.comma:
				return 1, 'Po identifikaci pocatecniho stavu ocekavam carku.'
		else:
			if token != lex.comma and self.was_ws != True:
				return 1, 'Po identifikaci pocatecniho stavu ocekavam bily znak(znaky).'
			if token != lex.comma:
				self.got_ws = True
		return 0, ''
	#__a_start_state

	def __a_final_states(self):
		""" Parses final states from token and stores it in class variable """
		txt, token = self.__get_token()
		#check for left curly bracket
		if token != lex.left_curly:
			return 1, 'Definice konecnych stavu musi byt uzavrena ve slozenych zavorkach.'

		txt, token = self.__get_token()
		while token != lex.right_curly and token != lex.eof:
			#look for identifier
			if token != lex.string or not self.__is_identifier(txt):
				return 1, 'V definici konecnych stavu musi byt retezec ve tvaru C identifikatoru.'

			#insert it into fsm.final_states
			self.fsm.final_states.append(txt)

			#look for comma or right curly bracket
			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.right_curly:
					return 1, 'V definici konecnych stavu musi byt jednotlive polozky oddeleny carkou.'
			else:
				if token != lex.right_curly and token != lex.comma and self.was_ws != True:
					return 1, 'V definici konecnych stavu musi byt jednotlive polozky oddeleny bilym znakem (znaky).'
				if token != lex.right_curly and token != lex.comma:
					self.got_ws = True

			# we already got end of final state definition - right curly bracket
			if token != lex.right_curly:
				txt, token = self.__get_token()

		#check for right curly bracket
		if token != lex.right_curly:
			return 1, 'Definice konecnych stavu musi byt uzavrena ve slozenych zavorkach.'

		#if all went well, we got here
		return 0, ''
	#__a_final_states

	def __a_whole(self):
		""" Parses whole FSM and calls methods for parsing components """
		char, token = self.__get_token()

		#check if is there left parenthesis around whole object
		if token != lex.left_par:
			return 1, "Cely FSM musi byt uzavren kulatou zavorkou."

		#parse all states (first curly brackets)
		err, msg = self.__a_states()
		if err != 0:
			return err, msg

		#parse alphabet
		err, msg = self.__a_alphabet()
		if err != 0:
			return err, msg

		#parse rules
		err, msg = self.__a_rules()
		if err != 0:
			return err, msg

		#parse start state
		err, msg = self.__a_start_state()
		if err != 0:
			return err, msg

		#parse final states
		err, msg = self.__a_final_states()
		if err != 0:
			return err, msg

		#check if is there right parenthesis around whole object
		char, token = self.__get_token()
		if token != lex.right_par:
			return 1, "Cely FSM musi byt ohranicen v kulatych zavorkach."

		#check if is there something more then we want
		char, token = self.__get_token()
		if token != lex.eof:
			return 1, "Po prave zavorce mohou nasledovat pouze komentare nebo bile znaky."

		# all went well and FSM is saved in instance of FinalStateMachine obejct
		return 0, ''
	#__a_whole

	def __rules(self):
		""" Parse rules from RLO bonus extension and stores it in class variables"""
		txt, token = self.__get_token()
		got_start_state = False

		# repeat until eof
		while token != lex.eof:
			#first we except state identifier
			if token != lex.string or not self.__is_identifier(txt):
				return 1, "Identifikator vychoziho stavu musi byt v C formatu."

			# mark it like a start state if we have no one like it so far
			if not got_start_state:
				self.fsm.start_state = txt
				got_start_state = True

			# and add it to the array if states. We will remove duplicates later
			first_state = txt
			self.fsm.states.append(txt)

			# now we except alphabet character
			txt, token = self.__get_token()
			if token != lex.string:
				return 1, "Za vychozim pravidlem ocekavam znak abecedy."

			self.fsm.alphabet.append(txt)
			char = txt

			# check for arrow
			txt, token = self.__get_token()
			if token != lex.arrow:
				return 1, "Za znakem abecedy ocekavam dvojznak \"sipku\""

			# and check second state identifier
			txt, token = self.__get_token()
			if token != lex.string and not self.__is_identifier(txt):
				return 1, "Identifikator ciloveho stavu musi byt v C formatu."

			self.fsm.states.append(txt)
			second_state = txt

			# check for dot, comma or in case wht is on for white spaces too
			self.was_ws = False
			txt, token = self.__get_token()
			if not self.ws:
				if token != lex.comma and token != lex.dot and token != lex.eof:
					return 1, "Za pravidlem ocekavam bud carku nebo tecku."
			else:
				if token != lex.comma and token != lex.dot and token != lex.eof and self.was_ws != True:
					return 1, "Za pravidlem ocekavam carku, tecku nebo bily znak."

			# if last separator was dot, add final state to the array
			if token == lex.dot:
				self.fsm.final_states.append(second_state)

			self.fsm.rules.append({
				'first_state' : first_state,
				'alpha_char'	: char,
				'second_state': second_state
			})

			txt, token = self.__get_token()
		#while

		# and finally remove duplicates
		self.fsm.remove_duplicates()
		return 0, ""
	#__rules

	def analyze_by_rules(self):
		""" Wrapping public function for analyzing rules from RLO bonus extension"""
		err, msg = self.__rules()
		if err != 0:
			return err, msg
		else:
			return err, self.fsm
	#analyze_by_rules


	def analyze(self):
		""" Wrapping public function for analyzing FSM """
		err, msg = self.__a_whole()
		if err != 0:
			return err, msg
		else:
			return 0, self.fsm
	#analyze

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
		fsm_or_msg.remove_duplicates()
		code, msg = fsm_or_msg.validate()
		if code != 0:
			print(msg)
			sys.exit(0)
		#fsm_or_msg.to_wsfa()
		fsm_or_msg.minimize()
		fsm_or_msg.show()
	else:
		print(fsm_or_msg)
