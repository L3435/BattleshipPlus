from __future__ import annotations
import battlefield

MAP = {
	None : battlefield.Polje.Shoot,
	"BigShot" : battlefield.Polje.BigShot,
	"MedShot" : battlefield.Polje.MedShot,
	"Cluster" : battlefield.Polje.Cluster,
	"Torpedo" : battlefield.Polje.Torpedo,
	"Radar" : battlefield.Polje.Radar
}

class Igra:
	def __init__(self, n: int=1, plus: bool=True, selected: str=None) -> None:
		self.igralec1 = battlefield.Polje()
		self.igralec1.RandomSetup()
		self.igralec2 = battlefield.Polje()
		self.igralec2.RandomSetup()
		self.tezavnost = n
		self.plus = plus
		self.selected = selected

	def Konec(self) -> int:
		"""Preveri, če je igra končana"""
		if not self.igralec1.Poteka(): return 1
		if not self.igralec2.Poteka(): return 2
		return 0

	def v_slovar(self) -> dict:
		"""Zapiše stanje igre v slovar"""
		return {
			"tezavnost" : self.tezavnost,
			"plus" : self.plus,
			"selected" : self.selected,
			"P1" : self.igralec1.v_slovar(),
			"P2" : self.igralec2.v_slovar(),
		}

	@staticmethod
	def iz_slovarja(slovar: dict) -> Igra:
		"""Iz zapisa v slovarju vrne igro"""
		X = Igra(int(slovar["tezavnost"]), slovar["plus"], slovar["selected"])
		X.igralec1 = battlefield.Polje.iz_slovarja(slovar["P1"])
		X.igralec2 = battlefield.Polje.iz_slovarja(slovar["P2"])
		return X

	def Poteza(self, x: int, y: int) -> None:
		"""Ustreli polje (x, y) in naredi računalniško potezo"""
		for ship in self.igralec1.mornarica.values():
			ship.counter = min(ship.counter + 1, 8 - ship.dolzina)
		for ship in self.igralec2.mornarica.values():
			ship.counter = min(ship.counter + 1, 8 - ship.dolzina)
		MAP[self.selected](self.igralec1, x, y)
		if self.selected:
			self.igralec2.ladja_z_metodo(self.selected).counter = 0
		self.selected = None
		P2 = self.igralec2
		if self.tezavnost == 1: P2.Shoot(*P2.LahekAI())
		elif self.tezavnost == 2: P2.Shoot(*P2.SrednjiAI())
		elif self.tezavnost == 3: P2.Shoot(*P2.Optimal())
		else:
			for x, y in P2:
				if P2.polje[x + 5][y + 5] != ' ' and P2.radar[x][y] == ' ':
					P2.Shoot(x, y)
					return