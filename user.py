import hashlib
import json
import random
import igra

class User:
	def __init__(self, name, pwd):
		self.username = name
		self.pwd = pwd
		self.igre = dict({})

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
			"igre": {id : self.igre[id].v_slovar() for id in self.igre}
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
		return f"user_{username}.json"
		# Windows ne dovoli uporabe določenih imen za datoteke, kar obidemo s predpono "user_"

	@staticmethod
	def iz_slovarja(slovar):
		username = slovar["username"]
		pwd = slovar["pwd"]
		uporabnik = User(username, pwd)
		uporabnik.igre = {int(id) : igra.Enoigralski.iz_slovarja(slovar["igre"][id]) for id in slovar["igre"]}
		return uporabnik

	@staticmethod
	def iz_datoteke(username):
		try:
			with open(User.UserFile(username)) as datoteka:
				slovar = json.load(datoteka)
				return User.iz_slovarja(slovar)
		except FileNotFoundError:
			return None

	def prost_id_igre(self):
		return len(self.igre)

	def nova_igra(self):
		id = self.prost_id_igre()
		self.igre[id] = igra.Enoigralski()
		return id

A = User.iz_datoteke("a")