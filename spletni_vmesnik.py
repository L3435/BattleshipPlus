import bottle
import battlefield

uporabnik = None

@bottle.get("/")
def zacetna_stran():
	return bottle.template("home.tpl")

@bottle.get("/pravila")
def pravila_igre():
	return bottle.template("pravila.tpl")
	
@bottle.get("/igra")
def igra():
	game = battlefield.AI()
	game.RandomSetup()
	while game.Poteka():
		game.Shoot(*game.Hunt())
	return bottle.template("igra.tpl", igra=game)

@bottle.get("/img/<picture>")
def slike(picture):
	return bottle.static_file(picture, "img")

bottle.run(reloader=True, debug=True)