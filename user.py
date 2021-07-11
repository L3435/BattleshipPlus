import hashlib
import json
import random

class User:
	def __init__(self, name, pwd):
		self.username = name
		self.pwd = pwd

	@staticmethod
	def prijava(uporabnisko_ime, geslo_v_cistopisu):
		uporabnik = User.iz_datoteke(uporabnisko_ime)
		if uporabnik is None:
			raise ValueError("Uporabniško ime ne obstaja!")
		elif uporabnik.preveri_geslo(geslo_v_cistopisu):
			return uporabnik		
		else:
			raise ValueError("Napačno geslo!")

	@staticmethod
	def registracija(uporabnisko_ime, geslo):
		if User.iz_datoteke(uporabnisko_ime) is not None:
			raise ValueError("Uporabniško ime že obstaja")
		else:
			pwd = User._zasifriraj_geslo(geslo)
			uporabnik = User(uporabnisko_ime, pwd)
			uporabnik.v_datoteko()
			return uporabnik

	def _zasifriraj_geslo(geslo_v_cistopisu, sol=None):
		if sol is None:
			sol = str(random.getrandbits(32))
		posoljeno_geslo = sol + geslo_v_cistopisu
		h = hashlib.blake2b()
		h.update(posoljeno_geslo.encode(encoding="utf-8"))
		return f"{sol}${h.hexdigest()}"


	def v_slovar(self):
		return {
			"username": self.username,
			"pwd": self.pwd,
		}

	def v_datoteko(self):
		with open(
			User.UserFile(self.username), "w"
		) as datoteka:
			json.dump(self.v_slovar(), datoteka, ensure_ascii=False, indent=4)

	def preveri_geslo(self, geslo):
		sol, _ = self.pwd.split("$")
		return self.pwd == User._zasifriraj_geslo(geslo, sol)

	@staticmethod
	def UserFile(username):
		return f"{username}.json"

	@staticmethod
	def iz_slovarja(slovar):
		username = slovar["username"]
		pwd = slovar["pwd"]
		return User(username, pwd)

	@staticmethod
	def iz_datoteke(username):
		try:
			with open(User.UserFile(username)) as datoteka:
				slovar = json.load(datoteka)
				return User.iz_slovarja(slovar)
		except FileNotFoundError:
			return None
