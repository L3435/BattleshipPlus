import bottle
import battlefield
import user

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
		return bottle.template("prijava.html", napaka="Vnesi uporabniško ime!", uname=username)
	if not geslo:
		return bottle.template("prijava.html", napaka="Vnesi geslo!", uname=username)
	try:
		user.User.prijava(username, geslo)
		bottle.response.set_cookie(
			USERNAME_COOKIE, username, path="/", secret=SECRET
		)
		bottle.redirect("/")
	except ValueError as e:
		return bottle.template(
			"prijava.html", napaka=e.args[0], uname=username
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
		return bottle.template("registracija.html", napaka="Vnesi uporabniško ime!", uname=username)
	if not geslo1:
		return bottle.template("registracija.html", napaka="Vnesi geslo!", uname=username)
	if geslo1 != geslo2:
		return bottle.template("registracija.html", napaka="Gesli se ne ujemata!", uname=username)
	try:
		user.User.registracija(username, geslo1)
		bottle.response.set_cookie(
			USERNAME_COOKIE, username, path="/", secret=SECRET
		)
		bottle.redirect("/")
	except ValueError as e:
		return bottle.template(
			"registracija.html", napaka=e.args[0]
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
	
@bottle.get("/igra")
def igra():
	game = battlefield.AI()
	game.RandomSetup()
	for  i in range(100):
		if not game.Poteka():
			break
		if not game.faza:
			game.Shoot(*game.MonteCarlo(5))
		else:
			game.Shoot(*game.Optimal(5))
		print("Strel")
	return bottle.template("igra.html", igra=game, user=trenutni_uporabnik())

@bottle.get("/img/<picture>")
def slike(picture):
	return bottle.static_file(picture, "img")

bottle.run(host="0.0.0.0", reloader=True, debug=True)