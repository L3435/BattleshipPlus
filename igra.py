from __future__ import annotations
import battlefield

MAP = {
	None : battlefield.Polje.Shoot,
	"BigShot" : battlefield.Polje.BigShot,
	"MedShot" : battlefield.Polje.MedShot,
	"Cluster" : battlefield.Polje.Cluster,
	"Torpedo" : battlefield.Polje.Torpedo
}

AI_MAP = {
	"BigShot" : (battlefield.Polje.BigShot, battlefield.Polje.OptimalBigShot),
	"MedShot" : (battlefield.Polje.MedShot, battlefield.Polje.OptimalMedShot),
	"Torpedo" : (battlefield.Polje.Torpedo, battlefield.Polje.OptimalShot)
}

class Igra:
	def __init__(self, n: int, selected: str=None, poteze: int=0) -> None:
		self.igralec1 = battlefield.Polje()
		self.igralec1.RandomSetup()
		self.igralec2 = battlefield.Polje()
		self.igralec2.RandomSetup()
		self.tezavnost = n
		self.selected = selected
		self.poteze = poteze

	def Konec(self) -> int:
		"""Preveri, če je igra končana"""
		P1 = self.igralec1
		P2 = self.igralec2
		if not P1.Poteka() and not P2.Poteka(): return 2
		if not P1.Poteka(): return 1
		if not P2.Poteka(): return 3
		return 0

	def v_slovar(self) -> dict:
		"""Zapiše stanje igre v slovar"""
		return {
			"tezavnost" : self.tezavnost,
			"selected" : self.selected,
			"poteze" : self.poteze,
			"P1" : self.igralec1.v_slovar(),
			"P2" : self.igralec2.v_slovar(),
		}

	@staticmethod
	def iz_slovarja(slovar: dict) -> Igra:
		"""Iz zapisa v slovarju vrne igro"""
		X = Igra(int(slovar["tezavnost"]), slovar["selected"], slovar["poteze"])
		X.igralec1 = battlefield.Polje.iz_slovarja(slovar["P1"])
		X.igralec2 = battlefield.Polje.iz_slovarja(slovar["P2"])
		return X

	def AI_Poteza(self) -> None:
		P1 = self.igralec1
		P2 = self.igralec2
		if self.tezavnost == 0:
			for metoda in AI_MAP:
				if P1.metoda_dostopna(metoda):
					AI_MAP[metoda][0](P2, *AI_MAP[metoda][1](P2))
					P1.ladja_z_metodo(metoda).counter = 0
					return
			if P2.metoda_dostopna("Cluster"):
				verjetnosti = P2.Optimal()
				x1, y1 = P2.OptimalBigShot(verjetnosti)
				x2, y2 = P2.OptimalShot(verjetnosti)
				if 2 * verjetnosti[x2][y2] > sum(
					verjetnosti[x1 + i][y1 + j]
					for i in range(-1, 2)
					for j in range(-1, 2)):
					P2.Shoot(x2, y2)
				else:
					P2.Cluster(x1, y1)
				return
			else: P2.Shoot(*P2.OptimalShot())
			return
		if self.tezavnost == 1: P2.Shoot(*P2.LahekAI())
		elif self.tezavnost == 2: P2.Shoot(*P2.SrednjiAI())
		elif self.tezavnost == 3: P2.Shoot(*P2.OptimalShot())
		else:
			for x, y in P2:
				if P2.polje[x + 5][y + 5] != ' ' and P2.radar[x][y] == ' ':
					P2.Shoot(x, y)
					return

	def Poteza(self, x: int, y: int) -> None:
		"""Ustreli polje (x, y) in naredi računalniško potezo"""
		P1 = self.igralec1
		P2 = self.igralec2
		MAP[self.selected](P1, x, y)
		if self.selected:
			P2.ladja_z_metodo(self.selected).counter = 0
		self.selected = None
		self.poteze += 1
		self.AI_Poteza()

	def Stevec(self):
		P1 = self.igralec1
		P2 = self.igralec2
		for ship in P1.mornarica.values():
			ship.counter = min(ship.counter + 1, 8 - ship.dolzina)
		for ship in P2.mornarica.values():
			ship.counter = min(ship.counter + 1, 8 - ship.dolzina)