import json

def get_stats() -> dict:
	try:
		with open("statistika.json") as datoteka:
			slovar = json.load(datoteka)
			return slovar
	except FileNotFoundError:
		return None

def save_stats(slovar: dict) -> None:
	with open("statistika.json", "w") as datoteka:
		json.dump(slovar, datoteka, ensure_ascii=False, indent=4)