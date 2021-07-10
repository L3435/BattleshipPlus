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
	while game.Poteka():
		game.Shoot(*game.Hunt())
	return bottle.template("igra.html", igra=game)

@bottle.get("/img/<picture>")
def slike(picture):
	return bottle.static_file(picture, "img")

bottle.run(reloader=True, debug=True)