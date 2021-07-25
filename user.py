from __future__ import annotations
import hashlib
import json
import random
import igra

class User:
	def __init__(self, name: str, pwd: str) -> None:
		self.username = name
		self.pwd = pwd
		self.igre = dict({})
		self.stats = {1 : [0, 0], 2 : [0, 0], 3 : [0, 0]}

	@staticmethod
	def prijava(uporabnisko_ime: str, geslo_v_cistopisu: str) -> User:
		"""Preveri, če je prijava uspešna"""
		uporabnik = User.iz_datoteke(uporabnisko_ime)
		if uporabnik is None:
			raise ValueError("Uporabniško ime ne obstaja!")
		elif uporabnik.preveri_geslo(geslo_v_cistopisu):
			return uporabnik
		else:
			raise ValueError("Napačno geslo!")

	@staticmethod
	def registracija(uporabnisko_ime: str, geslo: str) -> User:
		"""Preveri, če je registracija uspešna"""
		if User.iz_datoteke(uporabnisko_ime) is not None:
			raise ValueError("Uporabniško ime že obstaja")
		else:
			pwd = User._zasifriraj_geslo(geslo)
			uporabnik = User(uporabnisko_ime, pwd)
			uporabnik.v_datoteko()
			return uporabnik

	def _zasifriraj_geslo(geslo_v_cistopisu: str, sol=None) -> str:
		"""Zašifrira geslo"""
		if sol is None:
			sol = str(random.getrandbits(32))
		posoljeno_geslo = sol + geslo_v_cistopisu
		h = hashlib.blake2b()
		h.update(posoljeno_geslo.encode(encoding="utf-8"))
		return f"{sol}${h.hexdigest()}"


	def v_slovar(self) -> dict:
		"""Uporabnika shrani v slovar"""
		return {
			"username": self.username,
			"pwd": self.pwd,
			"igre": {id : self.igre[id].v_slovar() for id in self.igre},
			"stats": self.stats
		}

	def v_datoteko(self) -> None:
		"""Uporabnika shrani v datoteko"""
		with open(
			User.UserFile(self.username), "w"
		) as datoteka:
			json.dump(self.v_slovar(), datoteka, ensure_ascii=False, indent=4)

	def preveri_geslo(self, geslo: str) -> bool:
		"""Preveri, če je geslo pravilno"""
		sol, _ = self.pwd.split("$")
		return self.pwd == User._zasifriraj_geslo(geslo, sol)

	@staticmethod
	def UserFile(username: str) -> str:
		return f"users/user_{username}.json"
		# Windows ne dovoli uporabe določenih imen za datoteke,
		# kar obidemo s predpono "user_"

	@staticmethod
	def iz_slovarja(slovar: dict) -> User:
		"""Iz slovarja prebere uporabnika"""
		username = slovar["username"]
		pwd = slovar["pwd"]
		user = User(username, pwd)
		user.igre = {int(id) : igra.Enoigralski.iz_slovarja(slovar["igre"][id])
			for id in slovar["igre"]}
		user.stats = {int(n) : slovar["stats"][n] for n in slovar["stats"]}
		return user

	@staticmethod
	def iz_datoteke(username: str) -> User:
		"""Iz datoteke prebere uporabnika"""
		try:
			with open(User.UserFile(username)) as datoteka:
				slovar = json.load(datoteka)
				return User.iz_slovarja(slovar)
		except FileNotFoundError:
			return None

	def prost_id_igre(self) -> int:
		"""Vrne id za novo igro"""
		return len(self.igre)

	def nova_igra(self, tezavnost: int) -> int:
		"""Ustvari novo igro"""
		id = self.prost_id_igre()
		self.igre[id] = igra.Enoigralski(tezavnost)
		return id

	def konec_igre(self, id: int) -> None:
		"""Zaključi igro in shrani njen izid"""
		igra = self.igre[id]
		if igra.tezavnost in [1, 2, 3]:
			self.stats[igra.tezavnost][igra.Konec() - 1] += 1
		for i in range(id, len(self.igre) - 1):
			self.igre[i] = self.igre[i + 1]
		self.igre.pop(len(self.igre) - 1)
		self.v_datoteko()