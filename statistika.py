import json

def get_stats():
	try:
		with open("statistika.json") as datoteka:
			slovar = json.load(datoteka)
			return slovar
	except FileNotFoundError:
		return None