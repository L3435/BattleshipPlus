import battlefield

class Enoigralski:
	def __init__(self):
		self.igralec = battlefield.Igra()
		self.igralec.RandomSetup()
		self.AI = battlefield.AI()
		self.AI.RandomSetup()

	def Poteza(self, x, y, time):
		self.igralec.Shoot(x, y)
		if not self.AI.faza:
			self.AI.Shoot(*self.AI.MonteCarlo(time))
		else:
			self.AI.Shoot(*self.AI.Optimal(time))

	def v_slovar(self):
		return {
			"P1" : self.igralec.v_slovar(),
			"P2" : self.AI.v_slovar(),
		}

	@staticmethod
	def iz_slovarja(slovar):
		X = Enoigralski()
		X.igralec = battlefield.Igra.iz_slovarja(slovar["P1"])
		X.AI = battlefield.AI.iz_slovarja(slovar["P2"])
		return X