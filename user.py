from __future__ import annotations
import hashlib
import json
import random
import igra
import statistika


class User:
    """Razred s podatki o uporabniku.

    uporabnisko_ime: Uporabniško ime.
    geslo:           Zašifrirano geslo.
    igre:            Seznam aktivnih iger."""

    def __init__(self, uporabnisko_ime: str, geslo: str) -> None:
        self.uporabnisko_ime = uporabnisko_ime
        self.geslo = geslo
        self.igre = []

    @staticmethod
    def prijava(uporabnisko_ime: str, geslo_v_cistopisu: str) -> User:
        """Preveri, če je prijava uspešna."""
        uporabnik = User.iz_datoteke(uporabnisko_ime)
        if uporabnik is None:
            raise ValueError("Uporabniško ime ne obstaja!")
        elif uporabnik.preveri_geslo(geslo_v_cistopisu):
            return uporabnik
        else:
            raise ValueError("Napačno geslo!")

    @staticmethod
    def registracija(uporabnisko_ime: str, geslo: str) -> User:
        """Preveri, če je registracija uspešna."""
        stats = statistika.get_stats()
        if User.uporabnikova_statistika(uporabnisko_ime) in stats:
            raise ValueError("Uporabniško ime že obstaja!")
        else:
            pwd = User._zasifriraj_geslo(geslo)
            uporabnik = User(uporabnisko_ime, pwd)
            uporabnik.v_datoteko()
            stats = statistika.get_stats()
            stats[User.uporabnikova_statistika(uporabnisko_ime)] = {
                str(i) : [0, 0, 0] for i in range(4)
            }
            statistika.save_stats(stats)
            return uporabnik

    def _zasifriraj_geslo(geslo_v_cistopisu: str, sol=None) -> str:
        """Zašifrira geslo."""
        if sol is None:
            sol = str(random.getrandbits(32))
        posoljeno_geslo = sol + geslo_v_cistopisu
        h = hashlib.blake2b()
        h.update(posoljeno_geslo.encode(encoding="utf-8"))
        return f"{sol}${h.hexdigest()}"

    def v_slovar(self) -> dict:
        """Uporabnika shrani v slovar."""
        return {
            "username": self.uporabnisko_ime,
            "pwd": self.geslo,
            "igre": [igra.v_slovar() for igra in self.igre]
        }

    def v_datoteko(self) -> None:
        """Uporabnika shrani v datoteko."""
        with open(
                User.uporabnikova_datoteka(self.uporabnisko_ime), "w"
        ) as datoteka:
            json.dump(self.v_slovar(), datoteka, ensure_ascii=False, indent=4)

    def preveri_geslo(self, geslo: str) -> bool:
        """Preveri, če je geslo pravilno."""
        sol, _ = self.geslo.split("$")
        return self.geslo == User._zasifriraj_geslo(geslo, sol)

    @staticmethod
    def uporabnikova_datoteka(username: str) -> str:
        return f"users/user_{username}.json"
        # Windows ne dovoli uporabe določenih imen za datoteke,
        # kar obidemo s predpono "user_"

    @staticmethod
    def uporabnikova_statistika(username: str) -> str:
        """Vrne niz, ki določa statistiko uporabnika v slovarju."""
        return f"stats_{username}"

    @staticmethod
    def iz_slovarja(slovar: dict) -> User:
        """Iz slovarja prebere uporabnika in ga vrne."""
        username = slovar["username"]
        pwd = slovar["pwd"]
        user = User(username, pwd)
        user.igre = [igra.Igra.iz_slovarja(game) for game in slovar["igre"]]
        return user

    @staticmethod
    def iz_datoteke(username: str) -> User:
        """Iz datoteke prebere uporabnika in ga vrne."""
        try:
            with open(User.uporabnikova_datoteka(username)) as datoteka:
                slovar = json.load(datoteka)
                return User.iz_slovarja(slovar)
        except FileNotFoundError:
            return None

    def nova_igra(self, tezavnost: int) -> int:
        """Ustvari novo igro."""
        self.igre.append(igra.Igra(tezavnost))
        return len(self.igre) - 1

    def konec_igre(self, id: int) -> None:
        """Zaključi igro in shrani njen izid."""
        igra = self.igre[id]
        stats = statistika.get_stats()
        if igra.tezavnost in [0, 1, 2, 3]:
            stats[User.uporabnikova_statistika(self.uporabnisko_ime)]\
				[str(igra.tezavnost)][igra.konec() - 1] += 1
            dif = "1" if igra.tezavnost else "0"
            if igra.konec() == 1:
                stats["min_moves"][dif].append(
                    (self.uporabnisko_ime, igra.poteze)
                )
                stats["min_moves"][dif].sort(key=lambda p: p[1])
                stats["min_moves"][dif] = stats["min_moves"][dif][:10]
        statistika.save_stats(stats)
        self.igre = self.igre[:id] + self.igre[id + 1:]
        self.v_datoteko()
