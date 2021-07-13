import battlefield

class Enoigralski:
	def __init__(self, n=1):
		self.igralec = battlefield.Igra()
		self.igralec.RandomSetup()
		self.AI = battlefield.AI()
		self.AI.RandomSetup()
		self.tezavnost = n

	def Poteza(self, x, y):
		self.igralec.Shoot(x, y)
		if self.tezavnost == 1: self.AI.Shoot(*self.AI.BadHunt())
		if self.tezavnost == 2: self.AI.Shoot(*self.AI.Hunt())
		if self.tezavnost == 3: self.AI.Shoot(*self.AI.Optimal())

	def Konec(self):
		if not self.igralec.Poteka(): return 1
		if not self.AI.Poteka(): return 2
		return 0

	def v_slovar(self):
		return {
			"tezavnost" : self.tezavnost,
			"P1" : self.igralec.v_slovar(),
			"P2" : self.AI.v_slovar(),
		}

	@staticmethod
	def iz_slovarja(slovar):
		X = Enoigralski(int(slovar["tezavnost"]))
		X.igralec = battlefield.Igra.iz_slovarja(slovar["P1"])
		X.AI = battlefield.AI.iz_slovarja(slovar["P2"])
		return X