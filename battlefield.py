from errors import *
import random
import time

class Polje:
	"""Razred z metodami za pripravo igralnega polja"""
	def __init__(self):
		self.field = [ ['x'] * 20 for _ in range(20)]
		for x in range(5, 15):
			for y in range(5, 15):
				self.field[x][y] = ' '
		self.mornarica = {
			"A" : Ship(5, "A"),
			"B" : Ship(4, "B"),
			"C" : Ship(3, "C"),
			"D" : Ship(3, "D"),
			"E" : Ship(2, "E"),
		}
		self.ladje = sum(ladja.length for ladja in self.mornarica.values())

	def __str__(self):
		"""Izpiše trenutno stanje polja"""
		return '\n'.join([' '.join(str(self.field[x][y]) for x in range(5, 15)) for y in range(5, 15)])

	def SetShip(self, ship, x, y, r):
		"""Na polje (x, y) postavi ladjo ship z rotacijo r"""
		if any(self.field[x + 5 + r * i][y + 5 + i - r * i] != ' ' for i in range(ship.length)):
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
				self.__init__()
	
	def OdstraniPotopljene(self):
		for x in range(10):
			for y in range(10):
				pass


class Igra(Polje):
	"""Razred, ki nadzoruje potek igre"""

	def __init__(self):
		super().__init__()
		self.radar = [ [' '] * 10 for _ in range(10)]

	def __str__(self):
		"""Izpiše trenutno stanje igre"""
		return '\n'.join([' '.join(str(self.radar[x][y]) for x in range(10)) for y in range(10)])

	def Reveal(self, x, y):
		"""Prikaže izid streljanja polja (x, y) na radarju"""
		self.radar[x][y] = '.' if self.field[x + 5][y + 5] == ' ' else 'x'

	def Shoot(self, x, y):
		"""Osnovni strel v polje (x, y)"""
		if x < 0 or y < 0 or x > 9 or y > 9: raise OutOfRange
		if self.radar[x][y] in '.x': raise AlreadyShot
		self.Reveal(x, y)
		if self.radar[x][y] == 'x':
			self.ladje -= 1
			ladja = self.mornarica[self.field[x + 5][y + 5]]
			ladja.zadeta()
			if ladja.potopljena:
				for x in range(10):
					for y in range(10):
						if self.field[x + 5][y + 5] == ladja.id:
							self.radar[x][y] = 'P'

	def Poteka(self):
		"""Če je igra že končana, vrne False, drugače True"""
		return self.ladje > 0

	def v_slovar(self):
		return {
			"polje" : [
				[self.field[x + 5][y + 5] for y in range(10)] for x in range(10)
			],
			"radar" : [
				[self.radar[x][y] for y in range(10)] for x in range(10)
			],
			"mornarica" : { id : self.mornarica[id].v_slovar() for id in self.mornarica }
		}

	@staticmethod
	def iz_slovarja(slovar):
		X = AI()
		for x in range(10):
			for y in range(10):
				X.field[x + 5][y + 5] = slovar["polje"][x][y]
		for x in range(10):
			for y in range(10):
				X.radar[x][y] = slovar["radar"][x][y]
		X.mornarica = {id : Ship.iz_slovarja(slovar["mornarica"][id]) for id in slovar["mornarica"] }
		return X
		

class AI(Igra):

	def __init__(self):
		super().__init__()
		self.faza = False

	def RandomAI(self):
		"""Metoda, ki naključno strelja polja"""
		prazna = []
		for x in range(10):
			for y in range(10):
				if self.radar[x][y] == ' ': prazna.append((x, y))
		return random.choice(prazna)
	
	def SemiRandomAI(self):
		"""Metoda, ki naključno strelja polovico polj (polja šahovnice iste barve)"""
		prazna = [[], []]
		for x in range(10):
			for y in range(10):
				if self.radar[x][y] == ' ': prazna[(x + y) % 2].append((x, y))
		return random.choice(max(prazna))

	def Hunt(self):
		if all(self.radar[x][y] in " ." for x in range(10) for y in range(10)):
			return self.SemiRandomAI()
		smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
		for x in range(10):
			for y in range(10):
				if self.radar[x][y] == 'x':
					for i, j in smeri:
						try:
							if self.radar[x - i][y - j] == 'x' and self.radar[x + i][y + j] == ' ':
								return (x + i, y + j)
						except IndexError:
							continue
		for x in range(10):
			for y in range(10):
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
		return self.SemiRandomAI()

	def MonteCarlo(self, t):
		start = time.time()
		if any(self.radar[x][y] == 'x' for x in range(10) for y in range(10)):
			return self.Hunt()
		verjetnosti = [ [0] * 10 for _ in range(10)]
		n = 0
		while n < 1000:
			if time.time() - start > t:
				break
			simulacija = Polje()
			simulacija.mornarica = self.mornarica
			simulacija.RandomSetup()
			if any(simulacija.field[x + 5][y + 5] != ' ' and self.radar[x][y] == '.' for x in range(10) for y in range(10)):
				continue
			for x in range(10):
				for y in range(10):
					if simulacija.field[x + 5][y + 5] != ' ':
						verjetnosti[x][y] += 1
			n += 1
		if n < 250:
			self.faza = True
			return self.SemiOptimal()
		list = sorted([(x, y) for x in range(10) for y in range(10)], key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in list:
			if self.radar[p[0]][p[1]] == ' ': return p

	def RekurzivnoPostavljanje(self, indeks, simulacija, tabela, start, t):
		if time.time() - start > t: return
		if indeks == len(simulacija.mornarica):
			if any(simulacija.field[x + 5][y + 5] == ' ' and self.radar[x][y] == 'x' for x in range(10) for y in range(10)):
				return
			for x in range(10):
				for y in range(10):
					if simulacija.field[x + 5][y + 5] != ' ' and simulacija.field[x + 5][y + 5] != '.':
						tabela[x][y] += 1
			return
		for x in range(10):
			for y in range(10):
				for r in range(2):
					try:
						simulacija.SetShip(list(simulacija.mornarica.values())[indeks], x, y, r)
						self.RekurzivnoPostavljanje(indeks + 1, simulacija, tabela, start, t)
						simulacija.RemoveShip(list(simulacija.mornarica.values())[indeks], x, y, r)
					except CellTaken:
						continue

	def SemiOptimal(self):
		"""Izračuna verjetnosti v primeru, ko imamo eno ladjo"""
		if any(self.radar[x][y] == 'x' for x in range(10) for y in range(10)):
			return self.Hunt()
		verjetnosti = [ [0] * 10 for _ in range(10)]
		simulacija = Polje()
		for x in range(10):
			for y in range(10):
				if self.radar[x][y] == '.':
					simulacija.field[x + 5][y + 5] = '.'
		simulacija.mornarica = self.mornarica.copy()
		for ship in list(self.mornarica.values()):
			for x in range(10):
				for y in range(10):
					for r in range(2):
						try:
							simulacija.SetShip(ship, x, y, r)
							for i in range(ship.length):
								verjetnosti[x + r * i][y + i - r * i] += 1
							simulacija.RemoveShip(ship, x, y, r)
						except CellTaken:
							continue
		sez = sorted([(x, y) for x in range(10) for y in range(10)], key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in sez:
			if self.radar[p[0]][p[1]] == ' ': return p

	def Optimal(self, t):
		start = time.time()
		"""Optimalna, a počasna strategija"""
		verjetnosti = [ [0] * 10 for _ in range(10)]
		simulacija = Polje()
		for x in range(10):
			for y in range(10):
				if self.radar[x][y] == '.':
					simulacija.field[x + 5][y + 5] = '.'
		simulacija.mornarica = self.mornarica.copy()
		if any(self.radar[x][y] == 'x' for x in range(10) for y in range(10)):
			for i in range(10):
				for j in range(10):
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
			return self.SemiOptimal()
		sez = sorted([(x, y) for x in range(10) for y in range(10)], key=lambda p: -verjetnosti[p[0]][p[1]])
		for p in sez:
			if self.radar[p[0]][p[1]] == ' ': return p

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