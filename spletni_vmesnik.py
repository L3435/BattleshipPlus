import bottle
import battlefield

uporabnik = None

@bottle.get("/")
def zacetna_stran():
	return bottle.template("home.html")

@bottle.get("/pravila")
def pravila_igre():
	return bottle.template("pravila.html")
	
@bottle.get("/igra")
def igra():
	game = battlefield.AI()
	game.RandomSetup()
	for  i in range(100):
		if not game.Poteka():
			break
		if i < 20 or len(game.mornarica) > 3:
			game.Shoot(*game.MonteCarlo())
		else:
			game.Shoot(*game.Optimal())
		print("Strel")
	return bottle.template("igra.html", igra=game)

@bottle.get("/img/<picture>")
def slike(picture):
	return bottle.static_file(picture, "img")

bottle.run(reloader=True, debug=True)