from errors import *
import random

class Battlefield:
	"""Razred, ki nadzoruje potek igre"""
	def __init__(self):
		self.field = [ ['x'] * 20 for _ in range(20)]
		self.radar = [ [' '] * 10 for _ in range(10)]
		for x in range(5, 15):
			for y in range(5, 15):
				self.field[x][y] = ' '
		self.mornarica = {
			1 : Ship(5, 1, self),
			2 : Ship(4, 2, self),
			3 : Ship(3, 3, self),
			4 : Ship(3, 4, self),
			5 : Ship(2, 5, self),
		}
		self.ladje = sum(ladja.length for ladja in self.mornarica.values())

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
			self.field[x + 5][y + 5].zadeta()

	def SetShip(self, ship, x, y, r):
		"""Na polje (x, y) postavi ladjo ship z rotacijo r"""
		if any(self.field[x + 5 + r * i][y + 5 + i - r * i] != ' ' for i in range(ship.length)):
			raise CellTaken
		for i in range(ship.length):
			self.field[x + 5 + r * i][y + 5 + i - r * i] = ship

	def RandomSetup(self):
		"""Na polje naključno postavi ladje"""
		while True:
			try:
				for ladja in self.mornarica.values():
					self.SetShip(ladja,
								random.randint(1, 10 - ladja.length),
								random.randint(1, 10 - ladja.length),
								random.randint(0,1))
				break
			except CellTaken:
				self.__init__()

	def Poteka(self):
		"""Če je igra že končana, vrne False, drugače True"""
		return self.ladje > 0

	def RandomAI(self):
		"""Funkcija, ki naključno strelja polja"""
		prazna = []
		for x in range(10):
			for y in range(10):
				if self.radar[x][y] == ' ': prazna.append((x, y))
		x, y = random.choice(prazna)
		self.Shoot(x, y)
			

class Ship:
	"""Razred, ki vsebuje vse podatke o ladjah"""
	def __init__(self, n, id, igra):
		self.length = n
		self.id = id
		self.igra = igra
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