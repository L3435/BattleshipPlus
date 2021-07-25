from __future__ import annotations
import battlefield

class Igra:
	def __init__(self, n: int=1) -> None:
		self.igralec1 = battlefield.Polje()
		self.igralec1.RandomSetup()
		self.igralec2 = battlefield.Polje()
		self.igralec2.RandomSetup()
		self.tezavnost = n

	def Konec(self) -> int:
		"""Preveri, če je igra končana"""
		if not self.igralec1.Poteka(): return 1
		if not self.igralec2.Poteka(): return 2
		return 0

	def v_slovar(self) -> dict:
		"""Zapiše stanje igre v slovar"""
		return {
			"tezavnost" : self.tezavnost,
			"P1" : self.igralec1.v_slovar(),
			"P2" : self.igralec2.v_slovar(),
		}

	@staticmethod
	def iz_slovarja(slovar: dict) -> Igra:
		"""Iz zapisa v slovarju vrne igro"""
		X = Enoigralski(int(slovar["tezavnost"]))
		X.igralec1 = battlefield.Polje.iz_slovarja(slovar["P1"])
		X.igralec2 = battlefield.Polje.iz_slovarja(slovar["P2"])
		return X

class Enoigralski(Igra):
	def Poteza(self, x: int, y: int) -> None:
		"""Ustreli polje (x, y) in naredi računalniško potezo"""
		self.igralec1.Shoot(x, y)
		P2 = self.igralec2
		if self.tezavnost == 1: P2.Shoot(*P2.LahekAI())
		elif self.tezavnost == 2: P2.Shoot(*P2.SrednjiAI())
		elif self.tezavnost == 3: P2.Shoot(*P2.Optimal())
		else:
			for x, y in P2:
				if P2.polje[x + 5][y + 5] != ' ' and P2.radar[x][y] == ' ':
					P2.Shoot(x, y)
					return