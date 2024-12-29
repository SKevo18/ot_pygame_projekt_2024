import typing as t

if t.TYPE_CHECKING:
    from triedy.sceny.scena import Scena

import pygame

import nastavenia as n
from triedy.mixer import Mixer
from triedy.kamera import Kamera
from triedy.sprity.entity.fakla import Fakla
from triedy.sprity.entity.svetelna_entita import SvetelnaEntita


class Hrac(SvetelnaEntita):
    """
    Hlavná postava hry.
    """

    def __init__(self, pozicia: t.Tuple[int, int]):
        super().__init__(
            pozicia,
            n.ASSETY_ROOT / "sprite" / "hrac",
            # prevolene je animácia behu, ktorá sa iba pozastaví ak sa hráč nepohybuje:
            animacia_id="bez",
            rychlost=0.5,
        )

        self.hp = 100
        """Zdravie hráča."""
        self.aktualny_zvuk_krokov = None
        """Zvuk krokov, ktorý sa momentálne prehráva (ak prestaneme chodiť, zastavíme aj tento zvuk)"""

    def spracuj_event(self, event: pygame.event.Event, aktualna_scena: "Scena"):
        if event.type == pygame.KEYDOWN:
            # pohyb
            if event.key == pygame.K_LEFT:
                self.velocita.x = -1
                self.je_otoceny = False
            elif event.key == pygame.K_RIGHT:
                self.velocita.x = 1
                self.je_otoceny = True
            elif event.key == pygame.K_UP:
                self.velocita.y = -1
            elif event.key == pygame.K_DOWN:
                self.velocita.y = 1

            # približovanie kamery
            elif event.key == pygame.K_p:
                Kamera.zmen_priblizenie(0.5)
            elif event.key == pygame.K_o:
                Kamera.zmen_priblizenie(-0.5)

            # položenie fakle
            elif event.key == pygame.K_SPACE:
                # nemôžme položiť faklu, ak pokladáme alebo berieme inú
                if self.id_aktualnej_animacie == "poloz":
                    return

                # animácia a zvuk
                Mixer.prehrat_zvuk("poloz")
                self.prehrat_animaciu("poloz")

                # ak je neďaleko fakľa, odobereme ju
                for sprite in aktualna_scena.sprites():
                    if isinstance(sprite, Fakla) and sprite.rect.colliderect(self.rect):
                        aktualna_scena.remove(sprite)
                        break
                # inak položíme novú, zarovnanú podľa mriežky
                else:
                    podla_mriezky = (
                        (self.rect.centerx // aktualna_scena.velkost_spritu)
                        * aktualna_scena.velkost_spritu,
                        (self.rect.centery // aktualna_scena.velkost_spritu)
                        * aktualna_scena.velkost_spritu,
                    )
                    aktualna_scena.add(Fakla(podla_mriezky))

        elif event.type == pygame.KEYUP:
            # pohyb - zastavíme, iba ak sme sa pohybovali tým smerom
            # (aby sa hráč nezastavil ak zmení smer na opačný)
            if event.key == pygame.K_LEFT and self.velocita.x < 0:
                self.velocita.x = 0
            elif event.key == pygame.K_RIGHT and self.velocita.x > 0:
                self.velocita.x = 0
            elif event.key == pygame.K_UP and self.velocita.y < 0:
                self.velocita.y = 0
            elif event.key == pygame.K_DOWN and self.velocita.y > 0:
                self.velocita.y = 0

    def update(self):
        pohybuje_sa = self.velocita.length() > 0

        # hráčovi povolíme pohyb iba ak máme animáciu behu a nestojíme
        # napr. ak máme animáciu "poloz", tak sa hráč nemôže hýbať
        self.moze_ist = self.id_aktualnej_animacie == "bez" and pohybuje_sa

        if self.moze_ist:
            # ak sa pohybujeme, prehráme zvuk
            zvuk = Mixer.prehrat_zvuk("kroky")
            if zvuk:  # ak je `None`, znamená to že sa prehráva iný zvuk (t. j. zvuk krokov sa neprehral)
                self.aktualny_zvuk_krokov = zvuk
        elif self.aktualny_zvuk_krokov:
            # inak, ak nechodíme a prehráva sa zvuk, zastavíme ho:
            self.aktualny_zvuk_krokov.stop()

        # ak sa pohybujeme, animujeme pohyb
        # ak je animácia iná ako beh, prioritne prehrávame tú (napr. niečo položíme alebo útok a podobne)
        self.animuj = pohybuje_sa or self.id_aktualnej_animacie != "bez"

        return super().update()