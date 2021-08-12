import json

def get_stats() -> dict:
	"""Iz datoteke prebere statistiko iger."""
	try:
		with open("statistika.json") as datoteka:
			slovar = json.load(datoteka)
			return slovar
	except FileNotFoundError:
		return None

def save_stats(slovar: dict) -> None:
	"""Shrani statistiko iger v datoteko."""
	with open("statistika.json", "w") as datoteka:
		json.dump(slovar, datoteka, ensure_ascii=False, indent=4)