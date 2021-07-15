from errors import *
import random
import time

class Ship:
	"""Razred, ki vsebuje vse podatke o ladjah"""

	def __init__(self, n, id):
		self.length = n
		self.id = id
		self.nezadeta = n
		self.potopljena = False
		
	def __str__(self):
		"""Izpiše id ladje"""
		return str(self.id)

	def zadeta(self):
		"""Zmanjša število polj in preveri, če je potopljena"""
		self.nezadeta -= 1
		if not self.nezadeta:
			self.potopljena = True

	def v_slovar(self):
		return {
			"l" : self.length,
			"id" : self.id,
			"nezadeta" : self.nezadeta,
			"potopljena" : self.potopljena,
		}

	@staticmethod
	def iz_slovarja(slovar):
		X = Ship(int(slovar["l"]), slovar["id"])
		X.nezadeta = int(slovar["nezadeta"])
		X.potopljena = slovar["potopljena"]
		return X

KLASIKA = {
			"A" : Ship(5, "A"),
			"B" : Ship(4, "B"),
			"C" : Ship(3, "C"),
			"D" : Ship(3, "D"),
			"E" : Ship(2, "E")
		}

class Polje:
	"""Razred z metodami za pripravo igralnega polja"""

	def __init__(self, mornarica=KLASIKA):
		self.field = [ ['x'] * 20 for _ in range(20)]
		for x, y in self:
			self.field[x + 5][y + 5] = ' '
		self.mornarica = mornarica.copy()
		for id in self.mornarica:
			mornarica[id] = Ship(mornarica[id].length, mornarica[id].id)
		self.ladje = sum(ladja.length for ladja in self.mornarica.values())

	def __str__(self):
		"""Izpiše trenutno stanje polja"""
		return '\n'.join([' '.join(str(self.field[x][y])
						for x in range(5, 15)) for y in range(5, 15)])

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

	def SetShip(self, ship, x, y, r):
		"""Na polje (x, y) postavi ladjo ship z rotacijo r"""
		if any(self.field[x + 5 + r * i][y + 5 + i - r * i] != ' '
				for i in range(ship.length)):
			raise CellTaken
		for i in range(ship.length):
			self.field[x + 5 + r * i][y + 5 + i - r * i] = ship.id

	def RemoveShip(self, ship, x, y, r):
		"""S polja odstrani ladjo"""
		for i in range(ship.length):
			self.field[x + 5 + r * i][y + 5 + i - r * i] = ' '

	def RandomSetup(self):
		"""Na polje naključno postavi ladje"""
		while True:
			try:
				for ladja in self.mornarica.values():
					self.SetShip(ladja,
								random.randint(1, 10),
								random.randint(1, 10),
								random.randint(0,1))
				break
			except CellTaken:
				self.__init__(self.mornarica)


class Igra(Polje):
	"""Razred, ki nadzoruje potek igre"""

	def __init__(self, mornarica=KLASIKA):
		super().__init__(mornarica)
		self.radar = [ [' '] * 10 for _ in range(10)]

	def __str__(self):
		"""Izpiše trenutno stanje igre"""
		return '\n'.join([' '.join(str(self.radar[x][y])
						for x in range(10)) for y in range(10)])

	def Reveal(self, x, y):
		"""Prikaže izid streljanja polja (x, y) na radarju"""
		self.radar[x][y] = '.' if self.field[x + 5][y + 5] == ' ' else 'x'

	def Shoot(self, x, y):
		"""Osnovni strel v polje (x, y)"""
		if x < 0 or y < 0 or x > 9 or y > 9: raise OutOfRange
		if self.radar[x][y] in '.xP': raise AlreadyShot
		self.Reveal(x, y)
		if self.radar[x][y] == 'x':
			self.ladje -= 1
			ladja = self.mornarica[self.field[x + 5][y + 5]]
			ladja.zadeta()
			if ladja.potopljena:
				self.mornarica.pop(ladja.id)
				for x, y in self:
					if self.field[x + 5][y + 5] == ladja.id:
						self.radar[x][y] = 'P'

	def Poteka(self):
		"""Če je igra že končana, vrne False, drugače True"""
		return self.ladje > 0

	def v_slovar(self):
		return {
			"polje" : [
				[self.field[x + 5][y + 5] for y in range(10)]
				for x in range(10)
			],
			"radar" : [
				[self.radar[x][y] for y in range(10)] for x in range(10)
			],
			"mornarica" : { id : self.mornarica[id].v_slovar()
							for id in self.mornarica }
		}

	@staticmethod
	def iz_slovarja(slovar):
		X = AI()
		for x, y in X:
			X.field[x + 5][y + 5] = slovar["polje"][x][y]
		for x, y in X:
			X.radar[x][y] = slovar["radar"][x][y]
		X.mornarica = {id : Ship.iz_slovarja(slovar["mornarica"][id])
						for id in slovar["mornarica"] }
		c = 0
		for x, y in X:
			if X.radar[x][y] == 'x': c += 1
		X.ladje = sum(ladja.length for ladja in X.mornarica.values()) - c
		return X
		

class AI(Igra):

	def __init__(self, mornarica=KLASIKA):
		super().__init__(mornarica)
		self.faza = False

	def RandomChoice(self):
		"""Metoda, ki naključno strelja polja"""
		prazna = []
		for x, y in self:
			if self.radar[x][y] == ' ': prazna.append((x, y))
		return random.choice(prazna)
	
	def SemiRandomChoice(self):
		"""Metoda, ki naključno strelja polovico polj
		(polja šahovnice iste barve)"""
		prazna = [[], []]
		for x, y in self:
				if self.radar[x][y] == ' ': prazna[(x + y) % 2].append((x, y))
		try:
			return random.choice(min(prazna, key=lambda list: len(list)))
		except IndexError:
			return self.RandomChoice()

	def LahekAI(self, method=RandomChoice):
		if all(self.radar[x][y] in " .P" for x, y in self):
			return method(self)
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		options = []
		for x, y in self:
			if self.radar[x][y] == 'x':
				for i, j in smeri:
					try:
						if self.radar[x + i][y + j] == ' ':
							options.append((x + i, y + j))
					except IndexError:
						continue
		try:
			return random.choice(options)
		except IndexError:
			return self.RandomChoice()

	def SrednjiAI(self, method=SemiRandomChoice): # AI 2
		if all(self.radar[x][y] in " .P" for x, y in self):
			return method(self)
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		for x, y in self:
			if self.radar[x][y] == 'x':
				for i, j in smeri:
					try:
						if self.radar[x - i][y - j] == 'x' and self.radar[x + i][y + j] == ' ':
							return (x + i, y + j)
					except IndexError:
						continue
		for x, y in self:
			if self.radar[x][y] == 'x':
				prosta = [0, 0, 0, 0]
				for k in range(4):
					i, j = smeri[k]
					try:
						while self.radar[x + i * (1 + prosta[k])][y + j * (1 + prosta[k])] == ' ':
							prosta[k] += 1
					except IndexError:
						continue
				if prosta[0] + prosta[2] > prosta[1] + prosta[3]:
					i, j = smeri[0] if prosta[0] > prosta[2] else smeri[2]
				else:
					i, j = smeri[1] if prosta[1] > prosta[3] else smeri[3]
				return (x + i, y + j)

	def MonteCarlo(self, t=3):
		start = time.time()
		if any(self.radar[x][y] == 'x' for x, y in self):
			return self.SrednjiAI(self.SemiRandomChoice)
		verjetnosti = [ [0] * 10 for _ in range(10)]
		postavitve = {}
		for ship in self.mornarica.values():
			postavitve[ship] = []
			simulacija = Polje()
			for x, y in self:
				if self.radar[x][y] == '.' or self.radar[x][y] == 'P':
					simulacija.field[x + 5][y + 5] = '.'
			simulacija.mornarica = self.mornarica
			for x, y in self:
				for r in range(2):
					try:
						simulacija.SetShip(ship, x, y, r)
						postavitve[ship].append((x,y,r))
						simulacija.RemoveShip(ship, x, y, r)
					except CellTaken:
						continue
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
			if any(simulacija.field[x + 5][y + 5] != ' ' and self.radar[x][y] == '.' for x, y in self):
				continue
			for x, y in self:
				if simulacija.field[x + 5][y + 5] != ' ':
					verjetnosti[x][y] += 1
		
		list = sorted([(x, y) for x, y in self], key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in list:
			if self.radar[p[0]][p[1]] == ' ': return p

	def RekurzivnoPostavljanje(self, indeks, simulacija, tabela, start, t):
		if time.time() - start > t:
			return
		if indeks == len(simulacija.mornarica):
			if any(simulacija.field[x + 5][y + 5] == ' ' and self.radar[x][y] == 'x' for x, y in self):
				return
			for x, y in self:
				if simulacija.field[x + 5][y + 5] != ' ' and simulacija.field[x + 5][y + 5] != '.':
					tabela[x][y] += 1
			return
		for x, y in self:
			for r in range(2):
				try:
					simulacija.SetShip(list(simulacija.mornarica.values())[indeks], x, y, r)
					self.RekurzivnoPostavljanje(indeks + 1, simulacija, tabela, start, t)
					simulacija.RemoveShip(list(simulacija.mornarica.values())[indeks], x, y, r)
				except CellTaken:
					continue

	def Optimal(self, t=1): # AI 3
		"""Optimalna, a počasna strategija"""
		start = time.time()
		verjetnosti = [ [0] * 10 for _ in range(10)]
		simulacija = Polje()
		for x, y in self:
			if self.radar[x][y] == '.' or self.radar[x][y] == 'P':
				simulacija.field[x + 5][y + 5] = '.'
		simulacija.mornarica = self.mornarica.copy()
		if any(self.radar[x][y] == 'x' for x, y in self):
			for i, j in self:
				if self.radar[i][j] == 'x':
					x, y = i, j
					break
			for ship in list(self.mornarica.values()):
				simulacija.mornarica.pop(ship.id)
				for i in range(ship.length):
					for r in range(2):
						try:
							simulacija.SetShip(ship, x - r * i, y - i + r * i, r)
							self.RekurzivnoPostavljanje(0, simulacija, verjetnosti, start, t)
							simulacija.RemoveShip(ship, x - r * i, y - i + r * i, r)
						except CellTaken:
							continue
				simulacija.mornarica[ship.id] = ship
		else:
			self.RekurzivnoPostavljanje(0, simulacija, verjetnosti, start, t)
		if time.time() - start > t:
			return self.MonteCarlo(3)
		sez = sorted([(x, y) for x, y in self], key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in sez:
			if self.radar[p[0]][p[1]] == ' ': return p