from errors import *
import random

class Battlefield:
	def __init__(self):
		self.field = [ ['x'] * 20 for _ in range(20)]
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

	def __str__(self):
		return '\n'.join([' '.join(str(self.field[x][y]) for x in range(5,15)) for y in range(5,15)])

	def Reveal(self, x, y):
		self.field[x + 5][y + 5] = '.' if self.field[x + 5][y + 5] in ' .' else 'x'

	def Shoot(self, x, y):
		if self.field[x + 5][y + 5] in '.x': raise AlreadyShot
		self.Reveal(x, y)

	def SetShip(self, ship, x, y, r):
		if any(self.field[x + 5 + r * i][y + 5 + i - r * i] != ' ' for i in range(ship.length)):
			raise CellTaken
		for i in range(ship.length):
			self.field[x + 5 + r * i][y + 5 + i - r * i] = ship

	def RandomSetup(self):
		while True:
			try:
				for ladja in self.mornarica.values():
					self.SetShip(ladja, random.randint(1,9), random.randint(1,9), random.randint(0,1))
				break
			except CellTaken:
				self.__init__()
			

class Ship:
	def __init__(self, n, id, battle):
		self.length = n
		self.id = id
		self.battle = battle
		
	def __str__(self):
		return str(self.id)