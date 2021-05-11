from errors import *

class Battlefield:
	def __init__(self):
		self.field = [ [' '] * 20 for _ in range(20)]
		self.mornarica = {}

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


class Ship:
	def __init__(self, n, id, battle):
		self.length = n
		self.id = id
		self.battle = battle
		
	def __str__(self):
		return str(self.id)