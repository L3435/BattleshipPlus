import bottle
import battlefield

uporabnik = None

@bottle.get("/")
def zacetna_stran():
	return bottle.template("home.tpl")

@bottle.get("/pravila/")
def pravila_igre():
	return bottle.template("pravila.tpl")

@bottle.get("/img/<picture>")
def slike(picture):
	return bottle.static_file(picture, "img")

bottle.run(reloader=True, debug=True)