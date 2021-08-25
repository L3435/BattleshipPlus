from __future__ import annotations
from errors import AlreadyShot
import battlefield

MAP = {
    None: battlefield.Polje.strel,
    "BigShot": battlefield.Polje.velik_strel,
    "MedShot": battlefield.Polje.strel_plus,
    "Cluster": battlefield.Polje.trojni_strel,
    "Torpedo": battlefield.Polje.torpedo
}

AI_MAP = {
    "BigShot": battlefield.Polje.optimalen_velik_strel,
    "MedShot": battlefield.Polje.optimalen_plus,
    "Torpedo": battlefield.Polje.tezek_AI
}

DIF_MAP = {
    1: battlefield.Polje.lahek_AI,
    2: battlefield.Polje.srednji_AI,
    3: battlefield.Polje.tezek_AI,
    0: battlefield.Polje.tezek_AI,
}


class Igra:
    """Razred, ki nadzoruje potek igre.

    igralec1:  Polje z računalnikovimi ladjami.
    igralec2:  Polje z igralčevimi ladjami.
    tezavnost: Težavnost igre.
    selected:  Trenutno izbran poseben strel.
    poteze:    Število preteklih potez."""

    def __init__(
        self,
        tezavnost: int,
        selected: str = None,
        poteze: int = 0
    ) -> None:
        self.igralec1 = battlefield.Polje()
        self.igralec1.random_setup()
        self.igralec2 = battlefield.Polje()
        self.igralec2.random_setup()
        self.tezavnost = tezavnost
        self.selected = selected
        self.poteze = poteze

    def konec(self) -> int:
        """Preveri, če je igra končana, in vrne njen status:

        0: Igra še poteka.
        1: Zmagal je igralec.
        2: Izid je izenačen.
        3: Zmagal je računalnik."""
        P1 = self.igralec1
        P2 = self.igralec2
        if not P1.Poteka() and not P2.Poteka():
            return 2
        if not P1.Poteka():
            return 1
        if not P2.Poteka():
            return 3
        return 0

    def v_slovar(self) -> dict:
        """Stanje igre pretvori v slovar, ki ga lahko shranimo v datoteko."""
        return {
            "tezavnost": self.tezavnost,
            "selected": self.selected,
            "poteze": self.poteze,
            "P1": self.igralec1.v_slovar(),
            "P2": self.igralec2.v_slovar(),
        }

    @staticmethod
    def iz_slovarja(slovar: dict) -> Igra:
        """Iz slovarja prebere igro in jo vrne."""
        X = Igra(
            int(slovar["tezavnost"]),
            slovar["selected"],
            slovar["poteze"]
        )
        X.igralec1 = battlefield.Polje.iz_slovarja(slovar["P1"])
        X.igralec2 = battlefield.Polje.iz_slovarja(slovar["P2"])
        return X

    def AI_Poteza(self) -> None:
        """Naredi računalnikovo potezo."""
        P1 = self.igralec1
        P2 = self.igralec2
        if self.tezavnost == 0:
            for metoda in AI_MAP:
                if P1.metoda_dostopna(metoda):
                    MAP[metoda](P2, *AI_MAP[metoda](P2))
                    P1.ladja_z_metodo(metoda).stevec = -1
                    return
            if P1.metoda_dostopna("Cluster"):
                self.streljaj_trojno()
                return
        if self.tezavnost in DIF_MAP:
            P2.strel(*DIF_MAP[self.tezavnost](P2))
        else:
            for x, y in P2:
                if P2.polje[x + 5][y + 5] != ' ' and P2.radar[x][y] == ' ':
                    P2.strel(x, y)
                    return

    def streljaj_trojno(self):
        """Naredi računalnikovo potezo za trojni strel."""
        P1 = self.igralec1
        P2 = self.igralec2
        frekvence = P2.optimalna_strategija()
        x1, y1 = P2.optimalen_velik_strel(frekvence)
        x2, y2 = P2.tezek_AI(frekvence)
        if 3 * frekvence[x2][y2] > sum(
                frekvence[x1 + i][y1 + j]
                for i in range(-1, 2)
                for j in range(-1, 2)):
            P2.strel(x2, y2)
        else:
            P2.trojni_strel(x1, y1)
            P1.ladja_z_metodo("Cluster").stevec = -1

    def poteza(self, x: int, y: int) -> None:
        """Ustreli polje (x,y) in naredi računalniško potezo"""
        self.AI_Poteza()
        P1 = self.igralec1
        P2 = self.igralec2
        if P1.radar[x][y] != ' ':
            raise AlreadyShot
        MAP[self.selected](P1, x, y)
        if self.selected and P2.ladja_z_metodo(self.selected) != None:
            P2.ladja_z_metodo(self.selected).stevec = -1
        self.selected = None
        self.poteze += 1
        self.povecaj_stevec()

    def povecaj_stevec(self):
        """Poveča \'stevec\' vsem ladjam v igri."""
        P1 = self.igralec1
        P2 = self.igralec2
        for ship in P1.flota.values():
            ship.stevec = min(ship.stevec + 1, 5)
        for ship in P2.flota.values():
            ship.stevec = min(ship.stevec + 1, 5)
