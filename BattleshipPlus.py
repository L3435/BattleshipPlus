import bottle
import user
import statistika

USERNAME_COOKIE = "username"
SECRET = "2 + 2 is 4 - 1 is 3 quickmaths"

MAP = {
    "Klasičen, težavnost 1": 1,
    "Klasičen, težavnost 2": 2,
    "Klasičen, težavnost 3": 3,
    "Plus": 0
}

OPIS_STRELOV = {
    "Letalonosilka": """
		Z letalonosilke vzleti letalo, ki na polje spusti bombo.
		Ta odkrije vseh 9 celic v okolici izbrane celice.
	""",
    "Bojna ladja": """
		Na bojni ladji izstreli glavna baterija.
		Na polju odkrije 5 celic v obliki + s središčem v izbrani celici.
	""",
    "Podmornica": """
        Podmornica izstreli torpedo iz naključne smeri.
        Ta odkriva polja v liniji, dokler ne zadene ladje.
    """,
    "Križarka": """
        Križarka sproži 3 naboje hkrati.
        Ti zadenejo 3 naključno izbrana polja v okolici izbrane celice.
    """
}


def trenutni_uporabnik() -> user.User:
    uporabnisko_ime = bottle.request.get_cookie(
        USERNAME_COOKIE,
        secret=SECRET
    )
    if uporabnisko_ime:
        return user.User.iz_datoteke(uporabnisko_ime)


@bottle.get("/")
def zacetna_stran():
    return bottle.template("home.html", user=trenutni_uporabnik())


@bottle.get("/pravila")
def pravila_igre():
    return bottle.template("pravila.html", user=trenutni_uporabnik())


@bottle.get("/pravila_plus")
def pravila_plus():
    return bottle.template("pravila_plus.html", user=trenutni_uporabnik())


@bottle.get("/prijava")
def prijava():
    return bottle.template("prijava.html", user=trenutni_uporabnik())


@bottle.post("/prijava")
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode("username")
    geslo = bottle.request.forms.getunicode("geslo")
    if not uporabnisko_ime:
        return bottle.template(
            "prijava.html",
            napaka="Vnesi uporabniško ime!",
            uname=uporabnisko_ime,
            user=trenutni_uporabnik()
        )
    if not geslo:
        return bottle.template(
            "prijava.html",
            napaka="Vnesi geslo!",
            uname=uporabnisko_ime,
            user=trenutni_uporabnik()
        )
    try:
        user.User.prijava(uporabnisko_ime, geslo)
        bottle.response.set_cookie(
            USERNAME_COOKIE, uporabnisko_ime, path="/", secret=SECRET
        )
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template(
            "prijava.html",
            napaka=e.args[0],
            uname=uporabnisko_ime,
            user=trenutni_uporabnik()
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
        return bottle.template(
            "registracija.html",
            napaka="Vnesi uporabniško ime!",
            uname=username,
            user=trenutni_uporabnik()
        )
    if not geslo1:
        return bottle.template(
            "registracija.html",
            napaka="Vnesi geslo!",
            uname=username,
            user=trenutni_uporabnik()
        )
    if geslo1 != geslo2:
        return bottle.template(
            "registracija.html",
            napaka="Gesli se ne ujemata!",
            uname=username,
            user=trenutni_uporabnik()
        )
    try:
        user.User.registracija(username, geslo1)
        bottle.response.set_cookie(
            USERNAME_COOKIE,
            username, path="/",
            secret=SECRET
        )
        bottle.redirect("/")
    except ValueError as e:
        return bottle.template(
            "registracija.html",
            napaka=e.args[0],
            uname=username,
            user=trenutni_uporabnik()
        )


@bottle.get("/odjava")
def odjava():
    bottle.response.delete_cookie(USERNAME_COOKIE, path="/")
    bottle.redirect("/")


@bottle.get("/profil")
def profil():
    if trenutni_uporabnik() == None:
        bottle.redirect("/")
    return bottle.template(
        "profil.html",
        user=trenutni_uporabnik(),
        statistika=statistika.get_stats()
    )


@bottle.get("/igra/<id:int>")
def trenutna(id: int):
    user = trenutni_uporabnik()
    igra = user.igre[id]
    if bottle.request.query.x:
        x = int(bottle.request.query.x)
        y = int(bottle.request.query.y)
        igra.poteza(x, y)
        if igra.konec():
            user.konec_igre(id)
            if igra.tezavnost == -1:
                user.v_datoteko()
                bottle.redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        user.v_datoteko()
    return bottle.template(
        "igra.html",
        id=id,
        igra=igra,
        user=trenutni_uporabnik(),
        opis=OPIS_STRELOV
    )


@bottle.get("/igra/<id:int>/<metoda>")
def sprememba_metode(id, metoda):
    user = trenutni_uporabnik()
    igra = user.igre[id]
    if igra.tezavnost == 0 and igra.igralec2.metoda_dostopna(metoda):
        if igra.selected == metoda:
            igra.selected = None
        else:
            igra.selected = metoda
        user.v_datoteko()
    else:
        igra.selected = None
        user.v_datoteko()
    bottle.redirect(f"/igra/{id}")


@bottle.get("/nastavitve")
def nastavitve():
    user = trenutni_uporabnik()
    if user == None:
        bottle.redirect("/prijava")
    if len(user.igre) >= 5:
        bottle.redirect("/profil")
    return bottle.template("nastavitve.html", user=user)


@bottle.post("/nastavitve")
def nastavitve_post():
    string = bottle.request.forms.getunicode('tezavnost')
    if string in MAP:
        n = MAP[string]
    else:
        n = -1
    user = trenutni_uporabnik()
    id = user.nova_igra(n)
    user.v_datoteko()
    bottle.redirect(f"/igra/{id}")


@bottle.get("/lestvice")
def lestvice():
    return bottle.template(
        "lestvice.html",
        user=trenutni_uporabnik(),
        statistika=statistika.get_stats()
    )


@bottle.get("/lestvice_plus")
def lestvice_plus():
    return bottle.template(
        "lestvice_plus.html",
        user=trenutni_uporabnik(),
        statistika=statistika.get_stats()
    )


@bottle.get("/about")
def about_page():
    return bottle.template("about.html", user=trenutni_uporabnik())


@bottle.get("/img/<picture>")
def slike(picture):
    return bottle.static_file(picture, "img")


@bottle.get("/css/<stylesheet>")
def style(stylesheet):
    return bottle.static_file(stylesheet, "css")


if __name__ == '__main__':
    bottle.run(host="0.0.0.0", port="3435")
