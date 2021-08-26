from __future__ import annotations
from ast import Index
from types import MethodType
from errors import *
import random
import time

MEDIUM = [(0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)]
BIG = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]

OPIS_STRELOV = {
	"BigShot" : """
		Z letalonosilke vzleti letalo, ki na polje spusti bombo.
		Ta odkrije vseh 9 celic v okolici izbrane celice.
	""",
	"MedShot" : """
		Na bojni ladji izstreli glavna baterija.
		Na polju odkrije 5 celic v obliki + s središčem v izbrani celici.
	""",
    "Torpedo" : """
        Podmornica izstreli torpedo iz naključne smeri.
        Ta odkriva polja v liniji, dokler ne zadene ladje.
    """,
    "Cluster" : """
        Križarka sproži 3 naboje hkrati.
        Ti zadenejo 3 naključno izbrana polja v okolici izbrane celice.
    """
}

class Ladja:
    """Razred, ki vsebuje vse podatke o ladjah.

    dolzina:    Število polj, ki jih ladja zaseda.
    id:         Identifikacijska črka ladje.
    nezadeta:   Število polj ladje, ki še niso bila zadeta.
    potopljena: Če je ladja potopljena, se ta atribut nastavi na True.
    metoda:     Poseben strel ladje (dostopen v načinu Plus).
    stevec:     Število potez od zadnje uporabe posebnega strela."""

    def __init__(self, dolzina: int, id: str, metoda: str) -> None:
        self.dolzina = dolzina
        self.id = id
        self.nezadeta = dolzina
        self.potopljena = False
        self.metoda = metoda
        self.stevec = 5 - self.dolzina

    def __str__(self) -> str:
        """Izpiše id ladje."""
        return self.id

    def zadeta(self) -> None:
        """Zmanjša število nezadetih polj in preveri, če je potopljena."""
        self.nezadeta -= 1
        if not self.nezadeta:
            self.potopljena = True

    def special(self) -> bool:
        """Preveri, če je poseben strel dostopen."""
        return self.dolzina == self.nezadeta and self.stevec == 5

    def v_slovar(self) -> dict:
        """Ladjo pretvori v slovar, ki ga lahko shranimo v datoteko."""
        return {
            "l": self.dolzina,
            "id": self.id,
            "nezadeta": self.nezadeta,
            "potopljena": self.potopljena,
            "metoda": self.metoda,
            "counter": self.stevec
        }

    @staticmethod
    def iz_slovarja(slovar: dict) -> Ladja:
        """Iz slovarja prebere in vrne ladjo."""
        X = Ladja(int(slovar["l"]), slovar["id"], slovar["metoda"])
        X.nezadeta = int(slovar["nezadeta"])
        X.potopljena = slovar["potopljena"]
        X.stevec = int(slovar["counter"])
        return X


class Polje:
    """Razred z metodami za pripravo igralnega polja.

    polje: Tabela z lokacijami ladij.
    flota: Slovar ladij, ki še niso bile potopljene.
    ladje: Število nepotopljenih ladij.
    radar: Polje, ki ga vidi nasprotni igralec."""

    def __init__(self, flota: dict = None) -> None:
        self.polje = [['x'] * 20 for _ in range(20)]
        for x, y in self:
            self.polje[x + 5][y + 5] = ' '
        if flota:
            self.flota = flota
        else:
            self.flota = {
                "A": Ladja(5, "A", "BigShot"),
                "B": Ladja(4, "B", "MedShot"),
                "C": Ladja(3, "C", "Torpedo"),
                "D": Ladja(3, "D", "Cluster"),
                "E": Ladja(2, "E", None)
            }
        self.ladje = len(self.flota)
        self.radar = [[' '] * 10 for _ in range(10)]

    def __str__(self) -> str:
        """Izpiše trenutno stanje polja."""
        return '\n'.join([' '.join(str(self.radar[x][y])
                          for x in range(10)) for y in range(10)])

    def __iter__(self):
        """Iterator po koordinatah radarja."""
        return iter((x, y) for x in range(10) for y in range(10))

    def postavi_ladjo(self, ladja: Ladja, x: int, y: int, r: int) -> None:
        """Na polje postavi ladjo.

        x, y:  Koordinati izhodišča ladje.
        ladja: Ladja, ki jo postavljamo na polje.
        r:     Orientacija ladje (0 za vertikalno, 1 za horizontalno)."""
        if any(self.polje[x + 5 + r * i][y + 5 + i - r * i] != ' '
                for i in range(ladja.dolzina)):
            raise CellTaken
        for i in range(ladja.dolzina):
            self.polje[x + 5 + r * i][y + 5 + i - r * i] = ladja.id

    def odstrani_ladjo(self, ladja: Ladja, x: int, y: int, r: int) -> None:
        """S polja odstrani ladjo.

        x, y:  Koordinati izhodišča ladje.
        ladja: Ladja, ki jo odstranjujemo s polja.
        r:     Orientacija ladje (0 za vertikalno, 1 za horizontalno)."""
        for i in range(ladja.dolzina):
            self.polje[x + 5 + r * i][y + 5 + i - r * i] = ' '

    def clear_field(self) -> None:
        """Počisti vse ladje s polja."""
        for x, y in self:
            self.polje[x + 5][y + 5] = ' '

    def random_setup(self) -> None:
        """Na polje naključno postavi ladje."""
        while True:
            try:
                for ladja in self.flota.values():
                    self.postavi_ladjo(
                        ladja,
                        random.randint(1, 10),
                        random.randint(1, 10),
                        random.randint(0, 1))
                break
            except CellTaken:
                self.clear_field()

    def ladja_z_metodo(self, metoda: str) -> Ladja:
        """Poišče ladjo s posebno metodo streljanja."""
        for ladja in self.flota.values():
            if ladja.metoda == metoda:
                return ladja

    def metoda_dostopna(self, metoda: str) -> bool:
        """Preveri, ali lahko streljamo z izbrano metodo."""
        ladja = self.ladja_z_metodo(metoda)
        if ladja == None:
            return False
        return ladja.special()

    def odkrij(self, x: int, y: int) -> None:
        """Prikaže izid streljanja celice (x,y) na radarju."""
        if self.radar[x][y] != ' ':
            return
        self.radar[x][y] = '.' if self.polje[x + 5][y + 5] == ' ' else 'x'

    def strel(self, x: int, y: int) -> None:
        """Strelja in odkrije celico (x,y)."""
        if self.radar[x][y] in '.xP':
            raise AlreadyShot
        self.odkrij(x, y)
        if self.radar[x][y] == 'x':
            ladja = self.flota[self.polje[x + 5][y + 5]]
            ladja.zadeta()
            if ladja.potopljena:
                self.potopi(ladja)

    def multistrel(
        self,
        x: int,
        y: int,
        tarca: list[tuple[int, int]]
    ) -> None:
        """Strelja vse celice, določena z izhodiščem (x,y) in tarčo."""
        for i, j in tarca:
            try:
                if x + i < 0 or y + j < 0 or x + i > 9 or y + j > 9:
                    raise IndexError
                self.strel(x + i, y + j)
            except AlreadyShot:
                continue
            except IndexError:
                continue

    def strel_plus(self, x: int, y: int) -> None:
        """Zadene 5 celic v okolici (x,y) v obliki +."""
        self.multistrel(x, y, MEDIUM)

    def velik_strel(self, x: int, y: int) -> None:
        """Zadene 9 celic v okolici (x,y)."""
        self.multistrel(x, y, BIG)

    def trojni_strel(self, x: int, y: int) -> None:
        """Zadene tri naključne celice v okolici (x,y)."""
        target = BIG.copy()
        random.shuffle(target)
        self.multistrel(x, y, target[:3])

    def torpedo(self, x: int, y: int) -> None:
        """Po polju pošlje torpedo proti (x,y) iz naključne smeri."""
        smer = int(random.random() * 4)
        smeri = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        start = [(0, y), (9, y), (x, 0), (x, 9)]
        x, y = start[smer]
        i, j = smeri[smer]
        for _ in range(10):
            if self.polje[x + 5][y + 5] == ' ' or self.radar[x][y] in 'xP':
                self.odkrij(x, y)
                x, y = x + i, y + j
            else:
                self.strel(x, y)
                return

    def potopi(self, ladja: Ladja) -> None:
        """Označi ladjo kot potopljeno."""
        self.ladje -= 1
        self.flota.pop(ladja.id)
        for x, y in self:
            if self.polje[x + 5][y + 5] == ladja.id:
                self.radar[x][y] = 'P'

    def Poteka(self) -> bool:
        """Vrne True, če igra še ni končana."""
        return self.ladje > 0

    def v_slovar(self) -> dict:
        """Stanje polja pretvori v slovar, ki ga lahko shranimo v datoteko."""
        return {
            "polje": [
                [self.polje[x + 5][y + 5] for y in range(10)]
                for x in range(10)
            ],
            "radar": [
                [self.radar[x][y] for y in range(10)] for x in range(10)
            ],
            "flota": {id: self.flota[id].v_slovar()
                      for id in self.flota}
        }

    @staticmethod
    def iz_slovarja(slovar: dict) -> Polje:
        """Iz slovarja prebere polje in ga vrne."""
        X = Polje()
        for x, y in X:
            X.polje[x + 5][y + 5] = slovar["polje"][x][y]
            X.radar[x][y] = slovar["radar"][x][y]
        X.flota = {id: Ladja.iz_slovarja(slovar["flota"][id])
                   for id in slovar["flota"]}
        X.ladje = len(X.flota)
        return X

    def nakljucen_strel(self) -> tuple[int, int]:
        """Metoda, ki naključno strelja polja."""
        prazna = [(x, y) for x, y in self if self.radar[x][y] == ' ']
        return random.choice(prazna)

    def skoraj_nakljucen_strel(self) -> tuple[int, int]:
        """Metoda, ki naključno strelja polovico polj
        (polja šahovnice iste barve)."""
        prazna = [[], []]
        for x, y in self:
            if self.radar[x][y] == ' ':
                prazna[(x + y) % 2].append((x, y))
        try:
            return random.choice(min(prazna, key=lambda list: len(list)))
        except IndexError:
            return self.nakljucen_strel()

    def nakljucno_potapljanje(self) -> tuple[int, int]:
        """Naključno strelja okolico zadetih ladij."""
        smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        sosednja = []
        for x, y in self:
            if self.radar[x][y] == 'x':
                for i, j in smeri:
                    try:
                        if self.radar[x + i][y + j] == ' ':
                            sosednja.append((x + i, y + j))
                    except IndexError:
                        continue
        return random.choice(sosednja)

    def potapljanje(self, x: int, y: int) -> tuple[int, int]:
        """Strelja v okolici zadetih ladij,
           pri čemer upošteva sosednja polja."""
        smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for i, j in smeri:
            try:
                if self.radar[x - i][y - j] == 'x':
                    if self.radar[x + i][y + j] == ' ':
                        return (x + i, y + j)
            except IndexError:
                continue

    def prestej_prosta(self, x: int, y: int) -> list[int]:
        """Prešteje nezadeta polja v vsaki smeri."""
        smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        prosta = [0, 0, 0, 0]
        for k in range(4):
            i, j = smeri[k]
            try:
                x1 = x + i
                y1 = y + j
                while self.radar[x1][y1] == ' ':
                    if x1 < 0 or y1 < 0:
                        raise IndexError
                    prosta[k] += 1
                    x1 += i
                    y1 += j
            except IndexError:
                continue
        return prosta

    def zacni_potop(self) -> tuple[int, int]:
        """Strelja okolico zadete ladje glede na število praznih polj
           v posamezni smeri."""
        smeri = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for x, y in self:
            if self.radar[x][y] == 'x':
                prosta = self.prestej_prosta(x, y)
                if prosta[0] + prosta[2] > prosta[1] + prosta[3]:
                    i, j = smeri[0] if prosta[0] > prosta[2] else smeri[2]
                else:
                    i, j = smeri[1] if prosta[1] > prosta[3] else smeri[3]
                return (x + i, y + j)

    def lahek_AI(self) -> tuple[int, int]:
        """Vrne celico glede na lahko težavnost."""
        if all(self.radar[x][y] in " .P" for x, y in self):
            return self.nakljucen_strel()
        return self.nakljucno_potapljanje()

    def srednji_AI(self) -> tuple[int, int]:
        """Vrne celico glede na srednjo težavnost."""
        if all(self.radar[x][y] in " .P" for x, y in self):
            return self.skoraj_nakljucen_strel()
        for x, y in self:
            if self.radar[x][y] == 'x':
                if self.potapljanje(x, y):
                    return self.potapljanje(x, y)
        return self.zacni_potop()

    def mozne_postavitve(self) -> dict[Ladja, list[tuple[int, int, int]]]:
        """Za vsako ladjo preveri, kam jo lahko postavimo."""
        postavitve = {}
        simulacija = Polje()
        for x, y in self:
            if self.radar[x][y] in ".P":
                simulacija.polje[x + 5][y + 5] = '.'
        simulacija.flota = self.flota
        for ladja in self.flota.values():
            postavitve[ladja] = []
            for x, y in self:
                for r in range(2):
                    try:
                        simulacija.postavi_ladjo(ladja, x, y, r)
                        if any(self.radar[x + r * i][y + i - r * i] != 'x'
                               for i in range(ladja.dolzina)):
                            postavitve[ladja].append((x, y, r))
                        simulacija.odstrani_ladjo(ladja, x, y, r)
                    except CellTaken:
                        continue
        return postavitve

    def najdi_ladje(self, simulacija: Polje, tabela: list[list[int]]) -> bool:
        """Preveri, na katerih poljih so ladje in jih doda v tabelo."""
        if any(simulacija.polje[x + 5][y + 5] == ' ' and
               self.radar[x][y] == 'x' for x, y in self):
            return False
        for x, y in self:
            if simulacija.polje[x + 5][y + 5] not in ' .':
                tabela[x][y] += 1
        return True

    def rekurzivno_postavljanje(
        self,
        indeks: int,
        simulacija: Polje,
        tabela: list[list[int]],
        start: float, t: float
    ) -> None:
        """Rekurzivna funkcija za optimalno strategijo.
        indeks:     Indeks ladje, ki jo postavimo v tej iteraciji.
        simulacija: Polje, na katerega postavljamo ladje.
        tabela:     Tabela, v kateri shranjujemo frekvence ladij.
        start:      Čas začetka.
        t:          Časovna omejitev v sekundah."""
        if time.time() - start > t:
            return
        if indeks == len(simulacija.flota):
            self.najdi_ladje(simulacija, tabela)
            return
        seznam = list(simulacija.flota.values())
        for x, y in Polje():
            for r in range(2):
                try:
                    simulacija.postavi_ladjo(seznam[indeks], x, y, r)
                    self.rekurzivno_postavljanje(
                        indeks + 1,
                        simulacija,
                        tabela,
                        start,
                        t
                    )
                    simulacija.odstrani_ladjo(seznam[indeks], x, y, r)
                except CellTaken:
                    continue

    def optimalno_potapljanje(
        self,
        simulacija: Polje,
        tabela: list[list[int]],
        start: float,
        t: float
    ) -> None:
        """Optimalna strategija, če smo že zadeli kakšno ladjo.
        simulacija: Polje, na katerega postavljamo ladje.
        tabela:     Tabela, v kateri shranjujemo frekvence ladij.
        start:      Čas začetka.
        t:          Časovna omejitev v sekundah."""
        for i, j in self:
            x, y = 0, 0
            if self.radar[i][j] == 'x':
                x, y = i, j
                break
        for ladja in list(self.flota.values()):
            simulacija.flota.pop(ladja.id)
            for i in range(ladja.dolzina):
                for r in range(2):
                    try:
                        x0 = x - r * i
                        y0 = y - i + r * i
                        simulacija.postavi_ladjo(ladja, x0, y0, r)
                        self.rekurzivno_postavljanje(
                            0,
                            simulacija,
                            tabela,
                            start,
                            t
                        )
                        simulacija.odstrani_ladjo(ladja, x0, y0, r)
                    except CellTaken:
                        continue
            simulacija.flota[ladja.id] = ladja

    def optimalna_strategija(self, t: float = 1) -> list[list[int]]:
        """Metoda, ki vrne frekvence polj po vseh možnih postavitvah.
        t: Časovna omejitev v sekundah."""
        start = time.time()
        frekvence = [[0] * 10 for _ in range(10)]
        simulacija = Polje()
        for x, y in self:
            if self.radar[x][y] in ".P":
                simulacija.polje[x + 5][y + 5] = '.'
        simulacija.flota = self.flota.copy()
        if any(self.radar[x][y] == 'x' for x, y in self):
            self.optimalno_potapljanje(simulacija, frekvence, start, t)
        else:
            self.rekurzivno_postavljanje(0, simulacija, frekvence, start, t)
        if time.time() - start > t:
            frekvence = self.semi_optimalna_strategija()
        for x, y in self:
            if self.radar[x][y] != ' ':
                frekvence[x][y] = 0
        return frekvence

    def semi_optimalna_strategija(self):
        postavitve = self.mozne_postavitve()
        frekvence = [[0] * 10 for _ in range(10)]
        for ladja in self.flota.values():
            for x, y, r in postavitve[ladja]:
                counter = 200 ** [self.radar[x + r * i][y + i - r * i]
                           for i in range(ladja.dolzina)].count('x')
                for i in range(ladja.dolzina):
                    frekvence[x + r * i][y + i - r * i] += counter
        return frekvence

    def tezek_AI(self, frekvence: list[list[int]] = None) -> tuple[int, int]:
        """Vrne celico z največjim matematičnim upanjem.

        frekvence: V primeru predhodno izračunanih frekvenc polj jih
        podamo kot parameter."""
        if frekvence == None:
            frekvence = self.optimalna_strategija(1)
        if all(frekvence[x][y] == 0 for x, y in self):
            return self.srednji_AI()
        sez = [(x, y) for x, y in self]
        random.shuffle(sez)
        sez.sort(key=lambda p: -frekvence[p[0]][p[1]])
        for p in sez:
            if self.radar[p[0]][p[1]] == ' ':
                return p

    def optimalen_plus(
        self,
        frekvence: list[list[int]] = None
    ) -> tuple[int, int]:
        """Vrne celico z največjim matematičnim upanjem za strel plus.

        frekvence: V primeru predhodno izračunanih frekvenc polj jih
        podamo kot parameter."""
        if frekvence == None:
            frekvence = self.optimalna_strategija()
        medshot_frekvence = [
            [
                sum(
                    frekvence[x + i][y + j] for i, j in MEDIUM if
                    x + i in range(10) and y + j in range(10)
                )
                for y in range(10)
            ]
            for x in range(10)
        ]
        for x, y in self:
            if self.radar[x][y] != ' ':
                medshot_frekvence[x][y] = 0
        sez = [(x, y) for x, y in self]
        random.shuffle(sez)
        sez.sort(key=lambda p: -medshot_frekvence[p[0]][p[1]])
        for p in sez:
            if self.radar[p[0]][p[1]] == ' ':
                return p

    def optimalen_velik_strel(
        self,
        frekvence: list[list[int]] = None
    ) -> tuple[int, int]:
        """Vrne celico z največjim matematičnim upanjem za velik strel.

        frekvence: V primeru predhodno izračunanih frekvenc polj jih
        podamo kot parameter."""
        if frekvence == None:
            frekvence = self.optimalna_strategija()
        bigshot_frekvence = [
            [
                sum(
                    frekvence[x + i][y + j] for i, j in BIG
                    if x + i in range(10) and y + j in range(10))
                for y in range(10)
            ]
            for x in range(10)
        ]
        for x, y in self:
            if self.radar[x][y] != ' ':
                bigshot_frekvence[x][y] = 0
        sez = [(x, y) for x, y in self]
        random.shuffle(sez)
        sez.sort(key=lambda p: -bigshot_frekvence[p[0]][p[1]])
        for p in sez:
            if self.radar[p[0]][p[1]] == ' ':
                return p
