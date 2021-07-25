from __future__ import annotations
from errors import *
import random
import time

class Ladja:
	"""Razred, ki vsebuje vse podatke o ladjah"""

	def __init__(self, n: int, id: int) -> None:
		self.dolzina = n
		self.id = id
		self.nezadeta = n
		self.potopljena = False
		
	def __str__(self) -> str:
		"""Izpiše id ladje"""
		return str(self.id)

	def zadeta(self) -> None:
		"""Zmanjša število polj in preveri, če je potopljena"""
		self.nezadeta -= 1
		if not self.nezadeta:
			self.potopljena = True

	def v_slovar(self) -> dict:
		return {
			"l" : self.dolzina,
			"id" : self.id,
			"nezadeta" : self.nezadeta,
			"potopljena" : self.potopljena,
		}

	@staticmethod
	def iz_slovarja(slovar: dict) -> Ladja:
		X = Ladja(int(slovar["l"]), slovar["id"])
		X.nezadeta = int(slovar["nezadeta"])
		X.potopljena = slovar["potopljena"]
		return X

KLASIKA = {
			"A" : Ladja(5, "A"),
			"B" : Ladja(4, "B"),
			"C" : Ladja(3, "C"),
			"D" : Ladja(3, "D"),
			"E" : Ladja(2, "E")
		}

class Polje:
	"""Razred z metodami za pripravo igralnega polja"""

	def __init__(self, mornarica: dict=KLASIKA) -> None:
		self.polje = [ ['x'] * 20 for _ in range(20)]
		for x, y in self:
			self.polje[x + 5][y + 5] = ' '
		self.mornarica = mornarica.copy()
		for id in self.mornarica:
			mornarica[id] = Ladja(mornarica[id].dolzina, mornarica[id].id)
		self.ladje = len(self.mornarica)
		self.radar = [ [' '] * 10 for _ in range(10)]

	def __str__(self) -> str:
		"""Izpiše trenutno stanje polja"""
		return '\n'.join([' '.join(str(self.radar[x][y])
			for x in range(10)) for y in range(10)])

	def __iter__(self):
		self.iterx = 0
		self.itery = -1
		return self

	def __next__(self):
		self.itery += 1
		if self.itery > 9:
			self.itery = 0
			self.iterx += 1
		if self.iterx > 9: raise StopIteration
		return (self.iterx, self.itery)

	def SetShip(self, ship: Ladja, x: int, y: int, r: int) -> None:
		"""Na polje (x, y) postavi ladjo ship z rotacijo r"""
		if any(self.polje[x + 5 + r * i][y + 5 + i - r * i] != ' '
			for i in range(ship.dolzina)):
			raise CellTaken
		for i in range(ship.dolzina):
			self.polje[x + 5 + r * i][y + 5 + i - r * i] = ship.id

	def RemoveShip(self, ship: Ladja, x: int, y: int, r: int) -> None:
		"""S polja odstrani ladjo"""
		for i in range(ship.dolzina):
			self.polje[x + 5 + r * i][y + 5 + i - r * i] = ' '
	
	def ClearField(self) -> None:
		"""Počisti polje"""
		for x, y in self: self.polje[x + 5][y + 5] = ' '

	def RandomSetup(self) -> None:
		"""Na polje naključno postavi ladje"""
		while True:
			try:
				for ladja in self.mornarica.values():
					self.SetShip(ladja,
						random.randint(1, 10),
						random.randint(1, 10),
						random.randint(0, 1))
				break
			except CellTaken:
				self.ClearField()

	def Reveal(self, x: int, y: int) -> None:
		"""Prikaže izid streljanja polja (x, y) na radarju"""
		self.radar[x][y] = '.' if self.polje[x + 5][y + 5] == ' ' else 'x'

	def Shoot(self, x: int, y: int) -> None:
		"""Osnovni strel v polje (x, y)"""
		if self.radar[x][y] in '.xP': raise AlreadyShot
		self.Reveal(x, y)
		if self.radar[x][y] == 'x':
			ladja = self.mornarica[self.polje[x + 5][y + 5]]
			ladja.zadeta()
			if ladja.potopljena:
				self.Sink(ladja)
	
	def Sink(self, ladja: Ladja) -> None:
		"""Označi ladjo kot potopljeno"""
		self.ladje -= 1
		self.mornarica.pop(ladja.id)
		for x, y in self:
			if self.polje[x + 5][y + 5] == ladja.id:
				self.radar[x][y] = 'P'

	def Poteka(self) -> bool:
		"""Če je igra že končana, vrne False, drugače True"""
		return self.ladje > 0

	def v_slovar(self) -> dict:
		return {
			"polje" : [
				[self.polje[x + 5][y + 5] for y in range(10)]
				for x in range(10)
			],
			"radar" : [
				[self.radar[x][y] for y in range(10)] for x in range(10)
			],
			"mornarica" : { id : self.mornarica[id].v_slovar()
							for id in self.mornarica }
		}

	@staticmethod
	def iz_slovarja(slovar: dict) -> Polje:
		X = Polje()
		for x, y in X:
			X.polje[x + 5][y + 5] = slovar["polje"][x][y]
		for x, y in X:
			X.radar[x][y] = slovar["radar"][x][y]
		X.mornarica = {id : Ladja.iz_slovarja(slovar["mornarica"][id])
			for id in slovar["mornarica"] }
		X.ladje = len(X.mornarica)
		return X

	def RandomChoice(self) -> tuple[int, int]:
		"""Metoda, ki naključno strelja polja"""
		prazna = [(x, y) for x, y in self if self.radar[x][y] == ' ']
		return random.choice(prazna)
	
	def SemiRandomChoice(self) -> tuple[int, int]:
		"""Metoda, ki naključno strelja polovico polj
		(polja šahovnice iste barve)"""
		prazna = [[], []]
		for x, y in self:
			if self.radar[x][y] == ' ': prazna[(x + y) % 2].append((x, y))
		try:
			return random.choice(min(prazna, key=lambda list: len(list)))
		except IndexError:
			return self.RandomChoice()

	def RandomHunt(self) -> tuple[int, int]:
		"""Naključno strelja okolico zadetih ladij"""
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		sosednja = []
		for x, y in self:
			if self.radar[x][y] == 'x':
				for i, j in smeri:
					try:
						if self.radar[x + i][y + j] == ' ':
							sosednja.append((x + i, y + j))
					except IndexError:
						continue
		return random.choice(sosednja)

	def Hunt(self, x: int, y: int) -> tuple[int, int]:
		"""Strelja v okolici zadetih ladij,
		   pri čemer upošteva sosednja polja"""
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		for i, j in smeri:
			try:
				if self.radar[x - i][y - j] == 'x':
					if self.radar[x + i][y + j] == ' ':
						return (x + i, y + j)
			except IndexError:
				continue

	def PrestejProsta(self, x: int, y: int) -> list[int]:
		"""Prešteje nezadeta polja v vsaki smeri"""
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		prosta = [0, 0, 0, 0]
		for k in range(4):
			i, j = smeri[k]
			try:
				x1 = x + i
				y1 = y + j
				while self.radar[x1][y1] == ' ':
					if x1 < 0 or y1 < 0:
						raise IndexError
					prosta[k] += 1
					x1 += i
					y1 += j
			except IndexError:
				continue
		return prosta


	def StartHunt(self) -> tuple[int, int]:
		"""Strelja okolico zadete ladje glede na število praznih polj
		   v posamezni smeri"""
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		for x, y in self:
			if self.radar[x][y] == 'x':
				prosta = self.PrestejProsta(x, y)
				if prosta[0] + prosta[2] > prosta[1] + prosta[3]:
					i, j = smeri[0] if prosta[0] > prosta[2] else smeri[2]
				else:
					i, j = smeri[1] if prosta[1] > prosta[3] else smeri[3]
				return (x + i, y + j)

	def LahekAI(self) -> tuple[int, int]:
		if all(self.radar[x][y] in " .P" for x, y in self):
			return self.RandomChoice()
		return self.RandomHunt()

	def SrednjiAI(self) -> tuple[int, int]:
		if all(self.radar[x][y] in " .P" for x, y in self):
			return self.SemiRandomChoice()
		for x, y in self:
			if self.radar[x][y] == 'x':
				if self.Hunt(x, y): return self.Hunt(x, y)
		return self.StartHunt()

	def MoznePostavitve(self) -> dict[Ladja, list[tuple[int, int, int]]]:
		"""Za vsako ladjo preveri, kam jo lahko postavimo"""
		postavitve = {}
		for ship in self.mornarica.values():
			postavitve[ship] = []
			simulacija = Polje()
			for x, y in self:
				if self.radar[x][y] in ".P":
					simulacija.polje[x + 5][y + 5] = '.'
			simulacija.mornarica = self.mornarica
			for x, y in self:
				for r in range(2):
					try:
						simulacija.SetShip(ship, x, y, r)
						postavitve[ship].append((x,y,r))
						simulacija.RemoveShip(ship, x, y, r)
					except CellTaken:
						continue
		return postavitve

	def MonteCarlo(self, t: float=3) -> tuple[int, int]:
		"""Z naključnimi postavitvami oceni najverjetnejšo lokacijo ladij"""
		start = time.time()
		verjetnosti = [ [0] * 10 for _ in range(10)]
		postavitve = self.MoznePostavitve()
		for _ in range(10000):
			if time.time() - start > t:
				break
			simulacija = Polje()
			simulacija.mornarica = self.mornarica
			legal = True
			for ship in self.mornarica.values():
				try:
					simulacija.SetShip(ship, *random.choice(postavitve[ship]))
				except CellTaken:
					legal = False
					continue
			if not legal:
				continue
			if not self.PrestejLadje(simulacija, verjetnosti):
				continue
		list = sorted([(x, y) for x, y in self],
			key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in list:
			if self.radar[p[0]][p[1]] == ' ': return p

	def PrestejLadje(self, simulacija: Polje,
			tabela: list[list[int]]) -> tuple[int, int]:
		"""Preveri, na katerih poljih so ladje in to zapiše v tabelo"""
		if any(simulacija.polje[x + 5][y + 5] == ' ' and
			   self.radar[x][y] == 'x' for x, y in self):
			return False
		for x, y in self:
			if simulacija.polje[x + 5][y + 5] not in ' .':
				tabela[x][y] += 1
		return True

	def RekurzivnoPostavljanje(self, indeks: int, simulacija: Polje,
			tabela: list[list[int]], start: float, t: float) -> None:
		"""Rekurzivna funkcija za optimalno strategijo"""
		if time.time() - start > t: return
		if indeks == len(simulacija.mornarica):
			self.PrestejLadje(simulacija, tabela)
			return
		for x, y in Polje():
			for r in range(2):
				try:
					seznam = list(simulacija.mornarica.values())
					simulacija.SetShip(seznam[indeks], x, y, r)
					self.RekurzivnoPostavljanje(indeks + 1,
						simulacija, tabela, start, t)
					simulacija.RemoveShip(seznam[indeks], x, y, r)
				except CellTaken:
					continue

	def OptimalHunt(self, simulacija: Polje,
			tabela: list[list[int]], start: float, t: float) -> None:
		"""Optimalna strategija, če smo že zadeli kakšno ladjo"""
		for i, j in self:
			x, y = 0, 0
			if self.radar[i][j] == 'x':
				x, y = i, j
				break
			for ship in list(self.mornarica.values()):
				simulacija.mornarica.pop(ship.id)
				for i in range(ship.dolzina):
					for r in range(2):
						try:
							simulacija.SetShip(ship, x - r * i,
								y - i + r * i, r)
							self.RekurzivnoPostavljanje(0,
								simulacija,	tabela, start, t)
							simulacija.RemoveShip(ship, x - r * i,
								y - i + r * i, r)
						except CellTaken:
							continue
				simulacija.mornarica[ship.id] = ship

	def Optimal(self, t: float=1) -> tuple[int, int]:
		"""Metoda, ki vrne polje, na katerem je najbolj verjetno ladja"""
		start = time.time()
		verjetnosti = [ [0] * 10 for _ in range(10)]
		simulacija = Polje()
		for x, y in self:
			if self.radar[x][y] in ".P":
				simulacija.polje[x + 5][y + 5] = '.'
		simulacija.mornarica = self.mornarica.copy()
		if any(self.radar[x][y] == 'x' for x, y in self):
			self.OptimalHunt(simulacija, verjetnosti, start, t)
		else:
			self.RekurzivnoPostavljanje(0, simulacija, verjetnosti, start, t)
		if time.time() - start > t:
			return self.MonteCarlo()
		sez = sorted([(x, y) for x, y in self],
					 key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in sez:
			if self.radar[p[0]][p[1]] == ' ': return p