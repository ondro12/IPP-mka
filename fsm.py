# encoding: utf-8

#MKA:xkurka03

import pprint

class FinalStateMachine:
	def __init__(self, c_insensitive):
		""" Sets init values of class variables """
		self.stavy = []
		self.abeceda = []
		self.pravidla = []
		self.pociatocny_stav = ""
		self.ukoncujuce_stavy = []
		self.c_insensitive = c_insensitive

		self.minimalne_stavy = []
		self.minimalne_pravidla = []
		self.minimalny_pociatocny_stav = ""
		self.minimalne_konecne_stavy = []

	def over(self):
		""" Validates basic pravidla of FSM """
		#check if there are characters in abeceda
		if len(self.abeceda) == 0:
			return 1, 'Vstupni abeceda nesmi byt prazdna.'

		#check if all stavy in pravidla are also in stavy
		for rule in self.pravidla:
			if rule["first_state"] not in self.stavy:
				return 1, 'Pocatecni stav stavy neni v seznamu stavu.'
			if rule["second_state"] not in self.stavy:
				return 1, 'Koncovy stav stavy neni v seznamu stavu.'
			if rule["alpha_char"] != None and \
				rule["alpha_char"] not in self.abeceda:
				return 1, 'Symbol abecedy stavy neni v abecede.'

		#check if start state is in stavy
		if self.pociatocny_stav not in self.stavy:
			return 1, 'Pocatecni stav neni v seznamu stavu.'

		#check if final stavy are in stavy
		for final in self.ukoncujuce_stavy:
			if final not in self.stavy:
				return 1, 'Koncovy stav neni v seznamu stavu.'

		return 0, ''
	#over

	def _prejdene_stavy_(self, pociatocny_stav):
		""" Returns array of all reachable stavy we can get to 
		from pociatocny_stav in argument. """
		to_visit = []
		to_visit.append(pociatocny_stav)
		visited = []

		# use BFS algorithm to visit all possible stavy in graph
		while len(to_visit) != 0:
			actual = to_visit.pop()
			visited.append(actual)
			for rule in self.pravidla:
				if rule["first_state"] == actual:
					if rule["second_state"] not in visited:
						to_visit.append(rule["second_state"])

		return visited
	#_prejdene_stavy_

	def _nedosiahnutelne_stavy_(self):
		""" Returns all unreachable stavy of FSM """
		visited = self._prejdene_stavy_(self.pociatocny_stav)

		#get all stavy i can go to from start state
		unreachable = []
		for state in self.stavy:
			#and if there is some state i cant go to, its the unreachable one
			if state not in visited and state not in self.ukoncujuce_stavy:
				unreachable.append(state)

		return unreachable
	#unreachable_states

	def _neukoncujuce_stavy_(self):
		""" Return all non finishing stavy of FSM"""
		non_finishing = []

		for state in self.stavy:
			present = False
			#for every state get all stavy i can go to
			visited = self._prejdene_stavy_(state)
			for final_state in self.ukoncujuce_stavy:
				#and if there are no final stavy in visited, its non-finishing
				if final_state in visited:
					present = True
			if not present:
				non_finishing.append(state)

		return non_finishing
	#__non_finishing_states

	def _kompletny_over_(self):
		""" Checks if FSM is complete """
		for state in self.stavy:
			for char in self.abeceda:
				#check all combinations of state and abeceda char if there is rule for them
				found_rule = False
				for rule in self.pravidla:
					if rule["first_state"] == state and rule["alpha_char"] == char:
						found_rule = True
				if found_rule == False:
					return False
		return True
	#_kompletny_over_

	def _je_podmnozina_(self, original_set, sub_set):
		""" Returns true if one set is subset of another """
		for state in sub_set:
			if state not in original_set:
				return False
		return True

	def _je_wsfa_(self):
		""" Returns true if FSM is well-specified """
		unreachable = self._nedosiahnutelne_stavy_()
		non_finishing = self._neukoncujuce_stavy_()
		# well specified final automat has no unreachable stavy and maximum one non-finishing
		# state. Also it is complete automat (every combination of state and abeceda char)
		# has its own rule.
		if len(unreachable) == 0 and len(non_finishing) <= 1 and self._kompletny_over_()\
			and len(self.ukoncujuce_stavy) > 0 and self._je_podmnozina_(self.stavy, self.ukoncujuce_stavy):
			if len(non_finishing) == 1:
				#if non_finishing[0] == 'qFALSE' or non_finishing[0] == 'qfalse':
				return True
			else:
				return True
		return False
	#is_wfa

	def _nahrad_opak_vpol_(self, array):
		""" Removes all duplicates in given array """
		rslt = []
		for item in array:
			if item not in rslt:
				rslt.append(item)
		return rslt
	#_nahrad_opak_vpol_


	def _nahrad_opakujucel_(self):
		""" Removes all duplicates in class variables related to FSM """
		self.stavy = self._nahrad_opak_vpol_(self.stavy)
		self.abeceda = self._nahrad_opak_vpol_(self.abeceda)
		self.ukoncujuce_stavy = self._nahrad_opak_vpol_(self.ukoncujuce_stavy)
		self.pravidla = self._nahrad_opak_vpol_(self.pravidla)
	#_nahrad_opakujucel_

	def _pridaj_pravidlol_(self, first_state, alpha_char, second_state):
		""" Adds rule to the class set of pravidla """
		self.pravidla.append({
			'first_state' : first_state,
			'alpha_char'	: alpha_char,
			'second_state': second_state
			})
	#_pridaj_pravidlol_

	def _preved_na_wsfa_(self):
		""" Converts deterministic FSM to well-specified FSM """
		if self._je_wsfa_():
			return
		unreachable = self._nedosiahnutelne_stavy_()
		non_finishing = self._neukoncujuce_stavy_()
		qfalse = "qFALSE" if not self.c_insensitive else "qfalse"

		#remove all pravidla of unreachable stavy with state identifier on left side of rule
		new_rules = []
		for rule in self.pravidla:
			if rule["first_state"] not in unreachable:
				new_rules.append(rule)

		#remove all pravidla of non-finishing stavy with state identifier on right side of rule
		rslt = []
		for rule in new_rules:
			if rule["second_state"] not in non_finishing:
				rslt.append(rule)
		self.pravidla = rslt

		rslt = []
		#remove all unreachable and non-finishing stavy from fsm stavy
		for state in self.stavy:
			if state not in unreachable and state not in non_finishing:
				rslt.append(state)
		self.stavy = rslt

		#create missing pravidla to make it complete automat
		used_qfalse = False
		for state in self.stavy:
			for char in self.abeceda:
				is_there = False
				for rule in self.pravidla:
					if rule["first_state"] == state and rule["alpha_char"] == char:
						is_there = True
				if is_there == False:
					used_qfalse = True
					self._pridaj_pravidlol_(state, char, qfalse)

		#if we used qFALSE, we must add it to the stavy and create additional pravidla
		if used_qfalse:
			self.stavy.append(qfalse)
			for char in self.abeceda:
				self._pridaj_pravidlol_(qfalse, char, qfalse)
	#_preved_na_wsfa_

	def _ziskaj_neukoncujuce_stavy_(self):
		""" Returns all stavy that are not final stavy of FSM """
		rslt = []
		for state in self.stavy:
			if state not in self.ukoncujuce_stavy:
				rslt.append(state)
		return rslt
	#_ziskaj_neukoncujuce_stavy_

	def _ziskaj_ukoncujuce_stavy_(self, s_set, char):
		""" Returns destination stavy of set based on pravidla with using 
		first state and abeceda character """
		dest_states = []
		for state in s_set:
			for rule in self.pravidla:
				if rule["first_state"] == state and rule["alpha_char"] == char:
					dest_states.append(rule["second_state"])
		return dest_states
	#_ziskaj_ukoncujuce_stavy_

	def _ziskaj_ukoncujuci_stav_(self, state, char):
		""" Returns destination state based on pravidla with using first state
		and abeceda character """
		for rule in self.pravidla:
			if rule["first_state"] == state and rule["alpha_char"] == char:
				return rule["second_state"]
	#_ziskaj_ukoncujuce_stavy_

	def _su_v_rovnakej_mnozine_(self, state_sets, stavy):
		""" Returns true if all stavy in set are from same subset """
		for s_set in state_sets:
			present = True
			for state in stavy:
				if state not in s_set:
					present = False

			if present == True:
				return True
		return False
	#are_in_same_set

	def _ziskaj_id_stavu_(self, original_sets, state):
		""" Returns index of subset based on state """
		for i in range(len(original_sets)):
			if state in original_sets[i]:
				return i
		return None
	#__get_set_by_state

	def _rozdel_podla_stavu_(self, original_sets, con_set, char):
		""" Divides subset of stavy based on their index of destination stavy """
		identified = []
		#create structure with original state, final state (by using pravidla)
		#and set id of set
		for state in con_set:
			identified.append({
				"pociatocny_stav" : state,
				"final_state" : self._ziskaj_ukoncujuci_stav_(state, char),
				"id"		: self._ziskaj_id_stavu_(original_sets, self._ziskaj_ukoncujuci_stav_(state, char))
				})
		#remove from original_sets the one that we are working on (dividing)
		rslt = []
		for s_set in original_sets:
			if s_set != con_set:
				rslt.append(s_set)

		#create subsets based on original set we are dividing
		for i in range(len(original_sets)):
			tmp = []
			for iden in identified:
				if iden["id"] == i:
					tmp.append(iden["pociatocny_stav"])
			#and add them to the original set
			if len(tmp) > 0:
				rslt.append(tmp)

		return rslt
	#_rozdel_podla_stavu_

	def _ziskaj_pravy_stav_(self, left_state, char):
		""" Returns destination state of rule based on first state and character """
		#try all stavy on left side
		for lst in left_state:
			#check pravidla
			for rule in self.pravidla:
				#and find the one that corresponds with left_state and alpha_char
				if rule["first_state"] == lst and rule["alpha_char"] == char:
					return rule["second_state"]
		return None

	def _minimalizuj_(self):
		""" Controlling function for minimizing algorithm """
		dividing = True
		#create and fill starting set of stavy (final and non-final set of stavy)
		state_sets = []
		state_sets.append(self.ukoncujuce_stavy)
		non_final_states = self._ziskaj_neukoncujuce_stavy_()
		if len(non_final_states) > 0:
			state_sets.append(non_final_states)

		# divide until we can divide
		while dividing == True:
			dividing = False
			for char in self.abeceda:
				for s_set in state_sets:
					#go through all subsets in original_set and check destination stavy
					ukoncujuce_stavy = self._ziskaj_ukoncujuce_stavy_(s_set,char)
					#if they are not in one subset
					if not self._su_v_rovnakej_mnozine_(state_sets, ukoncujuce_stavy):
						dividing = True
						#divide it and start all over
						state_sets = self._rozdel_podla_stavu_(state_sets, s_set, char)
						break

		#create set of all minimized stavy with right naming
		for s_set in state_sets:
			s_set.sort()
			self.minimalne_stavy.append('_'.join(s_set))

		#and all the pravidla
		for s_set in state_sets:
			for char in self.abeceda:
				right_state = self._ziskaj_pravy_stav_(s_set, char)
				r_s_set = []
				for state in state_sets:
					if right_state in state:
						r_s_set = state

				s_set.sort()
				self.minimalne_pravidla.append({
					'first_state' : '_'.join(s_set),
					'alpha_char'	: char,
					'second_state': '_'.join(r_s_set)
					})

		#final stavy
		for s_set in state_sets:
			for final_state in self.ukoncujuce_stavy:
				if final_state in s_set:
					s_set.sort()
					self.minimalne_konecne_stavy.append('_'.join(s_set))
					break

		#and start state ofcourse
		for s_set in state_sets:
			if self.pociatocny_stav in s_set:
				s_set.sort()
				self.minimalny_pociatocny_stav = '_'.join(s_set)
				break
	#_minimalizuj_

	def _vypis_minimalizovany_(self, o):
		""" Prints minimized FSM to the output """
		#opening parenthesis
		print("(", file=o)

		#minimized set of stavy
		print("{", file=o, end="")
		self.minimalne_stavy.sort()
		for i in range(len(self.minimalne_stavy)):
			print(self.minimalne_stavy[i], file=o, end="")
			if i != (len(self.minimalne_stavy)-1):
				print(", ", file=o, end="")
		print("},", file=o)

		print("{", file=o, end="")
		self.abeceda.sort()
		for i in range(len(self.abeceda)):
			print('\'', self.abeceda[i], '\'', file=o, end="", sep="")
			if i != (len(self.abeceda)-1):
				print(", ", file=o, end="")
		print("},", file=o)

		#print pravidla
		print("{", file=o)
		self.minimalne_stavy.sort()
		self.abeceda.sort()
		count = 1
		for f_state in self.minimalne_stavy:
			for char in self.abeceda:
				for s_state in self.minimalne_stavy:
					for rule in self.minimalne_pravidla:
						if f_state == rule["first_state"] and \
						char == rule["alpha_char"] and \
						s_state == rule["second_state"]:
							print(f_state, " ", "'", char, "'"," -> ", s_state, file=o, sep="", end="")
							if count < len(self.minimalne_pravidla):
								print(",", file=o, end="")
							print("", file=o)
							count += 1
		print("},", file=o)

		#print start state
		print(self.minimalny_pociatocny_stav,",",sep="",file=o)

		print("{", file=o, end="")
		self.minimalne_konecne_stavy.sort()
		count = 1
		for state in self.minimalne_konecne_stavy:
			print(state, end="", file=o)
			if count < len(self.minimalne_konecne_stavy):
				print(", ", end="", file=o)
		print("}", file=o)

		#closing parenthesis
		print(")", file=o, end="")
	#_vypis_minimalizovany_

	def _vypis_wsfa_(self, o):
		""" Writes original FSM to the output """
		#opening parenthesis
		print("(", file=o)

		#minimized set of stavy
		print("{", file=o, end="")
		self.stavy.sort()
		for i in range(len(self.stavy)):
			print(self.stavy[i], file=o, end="")
			if i != (len(self.stavy)-1):
				print(", ", file=o, end="")
		print("},", file=o)

		#print abeceda
		print("{", file=o, end="")
		self.abeceda.sort()
		for i in range(len(self.abeceda)):
			print('\'', self.abeceda[i], '\'', file=o, end="", sep="")
			if i != (len(self.abeceda)-1):
				print(", ", file=o, end="")
		print("},", file=o)

		#print pravidla
		print("{", file=o)
		self.stavy.sort()
		self.abeceda.sort()
		count = 1
		for f_state in self.stavy:
			for char in self.abeceda:
				for s_state in self.stavy:
					for rule in self.pravidla:
						if f_state == rule["first_state"] and \
						char == rule["alpha_char"] and \
						s_state == rule["second_state"]:
							print(f_state, " ", "'", char, "'"," -> ", s_state, file=o, sep="", end="")
							if count < len(self.pravidla):
								print(",", file=o, end="")
							print("", file=o)
							count += 1
		print("},", file=o)

		#print start state
		print(self.pociatocny_stav,",",sep="",file=o)

		print("{", file=o, end="")
		self.ukoncujuce_stavy.sort()
		count = 1
		for state in self.ukoncujuce_stavy:
			print(state, end="", file=o)
			if count < len(self.ukoncujuce_stavy):
				print(", ", end="", file=o)
		print("}", file=o)

		#closing parenthesis
		print(")", file=o, end="")
	#_vypis_wsfa_

	def _analyzuj_retazec_(self, text):
		actual_state = self.pociatocny_stav
		for char in text:
			actual_state = self._ziskaj_pravy_stav_(actual_state, char)
			if actual_state == None:
				return False

		if actual_state in self.ukoncujuce_stavy:
			return True
		return False
	#_analyzuj_retazec_

	def show(self):
		""" Shows FSM variables. For debugging purposes """
		pp = pprint.PrettyPrinter(indent=2)
		print("FinalStateMachine:")
		print("Definice stavu:")
		pp.pprint(self.stavy)
		print("Abeceda:")
		pp.pprint(self.abeceda)
		print("Pravidla:")
		pp.pprint(self.pravidla)
		print("Pocatecni stav:")
		pp.pprint(self.pociatocny_stav)
		print("Konecne stavy:")
		pp.pprint(self.ukoncujuce_stavy)
		print("Nedostupne stavy:")
		pp.pprint(self._nedosiahnutelne_stavy_())
		print("Neukoncujici stavy:")
		pp.pprint(self._neukoncujuce_stavy_())
		print("Je to DSKA?:")
		if self._je_wsfa_():
			print("Ano.")
		else:
			print("Ne.")
		print("--------------------------------")
		print("Minimalizovany FSM:")
		print("Definice stavu:")
		pp.pprint(self.minimalne_stavy)
		print("Abeceda:")
		pp.pprint(self.abeceda)
		print("Pravidla:")
		pp.pprint(self.minimalne_pravidla)
		print("Pocatecni stav:")
		pp.pprint(self.minimalny_pociatocny_stav)
		print("Konecne stavy:")
		pp.pprint(self.minimalne_konecne_stavy)
		print("Nedostupne stavy:")
		pp.pprint(self._nedosiahnutelne_stavy_())
		print("Neukoncujici stavy:")
		pp.pprint(self._neukoncujuce_stavy_())

	#show
