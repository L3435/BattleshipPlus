from errors import AlreadyShot
import bottle
import battlefield
import user
import igra
import statistika

USERNAME_COOKIE = "username"
SECRET = "2 + 2 is 4 - 1 is 3 quickmaths"

def trenutni_uporabnik():
    username = bottle.request.get_cookie(
        USERNAME_COOKIE, secret=SECRET
    )
    if username:
        return user.User.iz_datoteke(username)

@bottle.get("/")
def zacetna_stran():
	return bottle.template("home.html", user=trenutni_uporabnik())

@bottle.get("/pravila")
def pravila_igre():
	return bottle.template("pravila.html", user=trenutni_uporabnik())

@bottle.get("/prijava")
def prijava():
	return bottle.template("prijava.html", user=trenutni_uporabnik())

@bottle.post("/prijava")
def prijava_post():
	username = bottle.request.forms.getunicode("username")
	geslo = bottle.request.forms.getunicode("geslo")
	if not username:
		return bottle.template("prijava.html", napaka="Vnesi uporabniško ime!", uname=username, user=trenutni_uporabnik())
	if not geslo:
		return bottle.template("prijava.html", napaka="Vnesi geslo!", uname=username, user=trenutni_uporabnik())
	try:
		user.User.prijava(username, geslo)
		bottle.response.set_cookie(
			USERNAME_COOKIE, username, path="/", secret=SECRET
		)
		bottle.redirect("/")
	except ValueError as e:
		return bottle.template(
			"prijava.html", napaka=e.args[0], uname=username, user=trenutni_uporabnik()
		)

@bottle.get("/registracija")
def registracija():
	return bottle.template("registracija.html", user=trenutni_uporabnik())

@bottle.post("/registracija")
def registracija_post():
	username = bottle.request.forms.getunicode("username")
	geslo1 = bottle.request.forms.getunicode("geslo1")
	geslo2 = bottle.request.forms.getunicode("geslo2")
	if not username:
		return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!", uname=username, user=trenutni_uporabnik())
	if not geslo1:
		return bottle.template("registracija.html", napaka="Vnesi geslo!", uname=username, user=trenutni_uporabnik())
	if geslo1 != geslo2:
		return bottle.template("registracija.html", napaka="Gesli se ne ujemata!", uname=username, user=trenutni_uporabnik())
	try:
		user.User.registracija(username, geslo1)
		bottle.response.set_cookie(
			USERNAME_COOKIE, username, path="/", secret=SECRET
		)
		bottle.redirect("/")
	except ValueError as e:
		return bottle.template(
			"registracija.html", napaka=e.args[0], uname=username, user=trenutni_uporabnik()
		)

@bottle.get("/odjava")
def odjava():
    bottle.response.delete_cookie(USERNAME_COOKIE, path="/")
    bottle.redirect("/")

@bottle.get("/profil")
def profil():
	if trenutni_uporabnik() == None:
		bottle.redirect("/")
	return bottle.template("profil.html", user=trenutni_uporabnik())
	
@bottle.get("/igra/<id:int>")
def trenutna(id):
	user = trenutni_uporabnik()
	igra = user.igre[id]
	if bottle.request.query.x:
		x = int(bottle.request.query.x)
		y = int(bottle.request.query.y)
		try:
			igra.Poteza(x, y)
			igra.Stevec()
		except AlreadyShot: pass
		if igra.Konec(): user.konec_igre(id)
		user.v_datoteko()
	return bottle.template("igra.html", id=id, igra=igra, user=trenutni_uporabnik())

@bottle.get("/igra/<id:int>/<metoda>")
def sprememba_metode(id, metoda):
	user = trenutni_uporabnik()
	igra = user.igre[id]
	if igra.tezavnost == 4 and igra.igralec2.metoda_dostopna(metoda):
		igra.selected = metoda
		user.v_datoteko()
	else:
		igra.selected = None
		user.v_datoteko()
	bottle.redirect(f"/igra/{id}")

@bottle.get("/nastavitve")
def nastavitve():
	if trenutni_uporabnik() == None: bottle.redirect("/prijava")
	return bottle.template("nastavitve.html", user=trenutni_uporabnik())

@bottle.post("/nastavitve")
def nastavitve_post():
	n = int(bottle.request.forms.getunicode('tezavnost'))
	user = trenutni_uporabnik()
	id = user.nova_igra(n)
	user.v_datoteko()
	bottle.redirect(f"/igra/{id}")
	
@bottle.get("/lestvice")
def lestvice():
	return bottle.template("lestvice.html", user=trenutni_uporabnik(), statistika = statistika.get_stats())

@bottle.get("/img/<picture>")
def slike(picture):
	return bottle.static_file(picture, "img")

bottle.run(host="0.0.0.0", reloader=True, debug=True)