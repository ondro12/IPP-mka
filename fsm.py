#projekt : mka
#autor : Matus Ondris

import pprint

# nastavenie premenych triedy
class FinalStateMachine:
	def __init__(self, c_insensitive):
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

#metoda sluziaca na overenie zakladnych pravidiel konecneho automatu
	def over(self):
#kontrola, ci sa nachadzaju nejake znaky vo vstupnej abecede
		if len(self.abeceda) == 0:
			return 1, 'Vstupna abeceda nemoze byt prazdna.'

#kontrola , ci sa vsetky stavy nachazdajuce sa v stavoch pravidiel tiez nachadzaju v stavoch automatu
		for rule in self.pravidla:
			if rule["first_state"] not in self.stavy:
				return 1, 'Pociatocny stav sa nenachadza v mnozine stavov.'
			if rule["second_state"] not in self.stavy:
				return 1, 'Koncovy stav sa nenachadza v mnozine stavov.'
			if rule["alpha_char"] != None and \
				rule["alpha_char"] not in self.abeceda:
				return 1, 'Symbol abecedy sa nenachadza v zadanej mnozine abecedy.'

#kontrola, ci sa pociatocny stav nachadza v mnozine stavov
		if self.pociatocny_stav not in self.stavy:
			return 1, 'Pociatocny stav sa nenachadza v mnozine stavov.'

#kontrola, ci sa koncove stavy nachadzaju v mnozine stavov
		for final in self.ukoncujuce_stavy:
			if final not in self.stavy:
				return 1, 'Koncovy stav sa nenachadza v mnozine stavov.'

		return 0, ''
#prejdenie vsetkych dostupnych stavov ktore mozeme dosiahnut z pociatocneho stavu v argumente a ich navrat v poli
	def _prejdene_stavy_(self, pociatocny_stav):
		to_visit = []
		to_visit.append(pociatocny_stav)
		visited = []

# pouziva BFS algoritmus na prejdenie vsetkych dostupnych stavov v grafe
		while len(to_visit) != 0:
			actual = to_visit.pop()
			visited.append(actual)
			for rule in self.pravidla:
				if rule["first_state"] == actual:
					if rule["second_state"] not in visited:
						to_visit.append(rule["second_state"])

		return visited
#ziskanie vsetkych nedosiahnutelnych stavov KA
	def _nedosiahnutelne_stavy_(self):
		visited = self._prejdene_stavy_(self.pociatocny_stav)

#ziskanie vsethych stavov, ktore je mozne ziskat z pociatocneho stavu
		unreachable = []
		for state in self.stavy:
#pokial najde stav do ktoreho sa nemoze dostat vlozi ho do zoznamu nedosiahnutelnych stavov
			if state not in visited and state not in self.ukoncujuce_stavy:
				unreachable.append(state)

		return unreachable

# ziskanie a vratenie vsetkych neukoncujucich stavov KA
	def _neukoncujuce_stavy_(self):
		non_finishing = []

		for state in self.stavy:
			present = False
#pre kazdy stav ziska vsetky stavy, ku ktorym sa moze dostat
			visited = self._prejdene_stavy_(state)
			for final_state in self.ukoncujuce_stavy:
#pokial tu niesu ziadne ukoncujuce stavy vo vsetkych prejdenych stavoch je to neukoncujuci 
				if final_state in visited:
					present = True
			if not present:
				non_finishing.append(state)

		return non_finishing

#kontrola, ci zadany KA je kompletny
	def _kompletny_over_(self):
		for state in self.stavy:
			for char in self.abeceda:
#kontrola vsetkych kombinacii stavov a abecedy , ci su pre en pravidla
				found_rule = False
				for rule in self.pravidla:
					if rule["first_state"] == state and rule["alpha_char"] == char:
						found_rule = True
				if found_rule == False:
					return False
		return True

# zistenie , ci sa jedna o podmnozinu nejakeho ineho stavu
	def _je_podmnozina_(self, original_set, sub_set):
		for state in sub_set:
			if state not in original_set:
				return False
		return True

# zistenie ci je KA well-specified
	def _je_wsfa_(self):
		unreachable = self._nedosiahnutelne_stavy_()
		non_finishing = self._neukoncujuce_stavy_()
# well-specified konecny automat nema ziadne nedosiahnutelne stavy a nanajvys jeden neukoncujuci stav
# a taktiez kazda kombinacia stavu a abecedy musi mat vlastne pravidlo
		if len(unreachable) == 0 and len(non_finishing) <= 1 and self._kompletny_over_()\
			and len(self.ukoncujuce_stavy) > 0 and self._je_podmnozina_(self.stavy, self.ukoncujuce_stavy):
			if len(non_finishing) == 1:
				return True
			else:
				return True
		return False

#nahradi vsetky duplikaty zanadne v poli 
	def _nahrad_opak_vpol_(self, array):
		rslt = []
		for item in array:
			if item not in rslt:
				rslt.append(item)
		return rslt

#nahradi vsetky duplicity v premennych tried vztahujucim sa ku KA
	def _nahrad_opakujucel_(self):
		self.stavy = self._nahrad_opak_vpol_(self.stavy)
		self.abeceda = self._nahrad_opak_vpol_(self.abeceda)
		self.ukoncujuce_stavy = self._nahrad_opak_vpol_(self.ukoncujuce_stavy)
		self.pravidla = self._nahrad_opak_vpol_(self.pravidla)

#pridanie pravidiel
	def _pridaj_pravidlol_(self, first_state, alpha_char, second_state):
		self.pravidla.append({
			'first_state' : first_state,
			'alpha_char'  : alpha_char,
			'second_state': second_state
			})
#prevedenie dka na  well-specified KA """
	def _preved_na_wsfa_(self):
		if self._je_wsfa_():
			return
		unreachable = self._nedosiahnutelne_stavy_()
		non_finishing = self._neukoncujuce_stavy_()
		qfalse = "qFALSE" if not self.c_insensitive else "qfalse"

#odstrani vsetky pravilda pre nedosiahnutelne stavy identifikatorov na lavej strane pravidla
		new_rules = []
		for rule in self.pravidla:
			if rule["first_state"] not in unreachable:
				new_rules.append(rule)

#odstrani vsetky pravidla pre neukoncujuce stavy identifikatorov na pravej strane pravidla 
		rslt = []
		for rule in new_rules:
			if rule["second_state"] not in non_finishing:
				rslt.append(rule)
		self.pravidla = rslt

		rslt = []
#odstrani vsetky nedosiahnutelne a neukoncujuce stavy
		for state in self.stavy:
			if state not in unreachable and state not in non_finishing:
				rslt.append(state)
		self.stavy = rslt

#vytvorenie chybajuceich pravidiel , aby bol automat kompletny
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
				
#ziskanie neukoncujucich stavov KA
	def _ziskaj_neukoncujuce_stavy_(self):
		rslt = []
		for state in self.stavy:
			if state not in self.ukoncujuce_stavy:
				rslt.append(state)
		return rslt

#ziskanie konecnyc stavov zalozene na pravidlach ktore pouzivaju prvy stav a znak abecedy 
	def _ziskaj_ukoncujuce_stavy_(self, s_set, char):
		dest_states = []
		for state in s_set:
			for rule in self.pravidla:
				if rule["first_state"] == state and rule["alpha_char"] == char:
					dest_states.append(rule["second_state"])
		return dest_states
#ziskanie konecneho stavu zalozene na pravidlach ktore pouzivaju prvy stav a znak abecedy 
	def _ziskaj_ukoncujuci_stav_(self, state, char):
		for rule in self.pravidla:
			if rule["first_state"] == state and rule["alpha_char"] == char:
				return rule["second_state"]
				
#kontrola ci su vsetky stavy z rovnakej mnoziny
	def _su_v_rovnakej_mnozine_(self, state_sets, stavy):
		for s_set in state_sets:
			present = True
			for state in stavy:
				if state not in s_set:
					present = False

			if present == True:
				return True
		return False

#ziskanie indexu podmnoziny zalozeneho na stave
	def _ziskaj_id_stavu_(self, original_sets, state):
		for i in range(len(original_sets)):
			if state in original_sets[i]:
				return i
		return None
		
#rozdelenie podmnozin stavov zalozene na indexe koncovych stavov
	def _rozdel_podla_stavu_(self, original_sets, con_set, char):
		identified = []
#vytvorenie struktury s povodnymi stavmi a konecnymi stavmi a ulozenie id
		for state in con_set:
			identified.append({
				"pociatocny_stav" : state,
				"final_state" : self._ziskaj_ukoncujuci_stav_(state, char),
				"id"		: self._ziskaj_id_stavu_(original_sets, self._ziskaj_ukoncujuci_stav_(state, char))
				})
#odstranenie z original_sets prave spracovavany 
		rslt = []
		for s_set in original_sets:
			if s_set != con_set:
				rslt.append(s_set)

		for i in range(len(original_sets)):
			tmp = []
			for iden in identified:
				if iden["id"] == i:
					tmp.append(iden["pociatocny_stav"])
			if len(tmp) > 0:
				rslt.append(tmp)

		return rslt

#ziska koncovy stav pravidla zalozene na prvom stave a znaku
	def _ziskaj_pravy_stav_(self, left_state, char):
#skusi vsetky stavy na lavejs trane
		for lst in left_state:
#skontroluje pravidla
			for rule in self.pravidla:
#najdenie pravidla, ktore koresponduje s left_state a alpha_char
				if rule["first_state"] == lst and rule["alpha_char"] == char:
					return rule["second_state"]
		return None

#metoda sluziaca na minimalizaciu
	def _minimalizuj_(self):
		dividing = True
#vytvorenie a naplnenie mnoziny stavov
		state_sets = []
		state_sets.append(self.ukoncujuce_stavy)
		non_final_states = self._ziskaj_neukoncujuce_stavy_()
		if len(non_final_states) > 0:
			state_sets.append(non_final_states)

		while dividing == True:
			dividing = False
			for char in self.abeceda:
				for s_set in state_sets:
					ukoncujuce_stavy = self._ziskaj_ukoncujuce_stavy_(s_set,char)
					if not self._su_v_rovnakej_mnozine_(state_sets, ukoncujuce_stavy):
						dividing = True
						state_sets = self._rozdel_podla_stavu_(state_sets, s_set, char)
						break

		for s_set in state_sets:
			s_set.sort()
			self.minimalne_stavy.append('_'.join(s_set))

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

		for s_set in state_sets:
			for final_state in self.ukoncujuce_stavy:
				if final_state in s_set:
					s_set.sort()
					self.minimalne_konecne_stavy.append('_'.join(s_set))
					break

		for s_set in state_sets:
			if self.pociatocny_stav in s_set:
				s_set.sort()
				self.minimalny_pociatocny_stav = '_'.join(s_set)
				break
			
#vypisanie minimalizovaneho KA na vystup
	def _vypis_minimalizovany_(self, o):
		print("(", file=o)

#minimalizovany set stavov
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

#vypis pravidiel
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

#vypis pociatocneho znaku
		print(self.minimalny_pociatocny_stav,",",sep="",file=o)

		print("{", file=o, end="")
		self.minimalne_konecne_stavy.sort()
		count = 1
		for state in self.minimalne_konecne_stavy:
			print(state, end="", file=o)
			if count < len(self.minimalne_konecne_stavy):
				print(", ", end="", file=o)
		print("}", file=o)

		print(")", file=o, end="")

#vypisanie originalneho KA na vystup
	def _vypis_wsfa_(self, o):
		print("(", file=o)

		print("{", file=o, end="")
		self.stavy.sort()
		for i in range(len(self.stavy)):
			print(self.stavy[i], file=o, end="")
			if i != (len(self.stavy)-1):
				print(", ", file=o, end="")
		print("},", file=o)

		print("{", file=o, end="")
		self.abeceda.sort()
		for i in range(len(self.abeceda)):
			print('\'', self.abeceda[i], '\'', file=o, end="", sep="")
			if i != (len(self.abeceda)-1):
				print(", ", file=o, end="")
		print("},", file=o)

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

		print(self.pociatocny_stav,",",sep="",file=o)

		print("{", file=o, end="")
		self.ukoncujuce_stavy.sort()
		count = 1
		for state in self.ukoncujuce_stavy:
			print(state, end="", file=o)
			if count < len(self.ukoncujuce_stavy):
				print(", ", end="", file=o)
		print("}", file=o)

		print(")", file=o, end="")

	def _analyzuj_retazec_(self, text):
		actual_state = self.pociatocny_stav
		for char in text:
			actual_state = self._ziskaj_pravy_stav_(actual_state, char)
			if actual_state == None:
				return False

		if actual_state in self.ukoncujuce_stavy:
			return True
		return False

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
