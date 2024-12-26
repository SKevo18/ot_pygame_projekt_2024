import typing as t
from pathlib import Path

import pygame

from triedy.sprite.sprite import Sprite


class OsvetlenySprite(Sprite):
    """
    Predstavuje sprite, ktorý je osvetlený určitou úrovňou svetla (percento).

    Predvolene je úroveň svetla 1.0 (100 %). Znižovanie hodnoty postupne stmavuje obrázok.
    """

    def __init__(
        self,
        pozicia: t.Tuple[int, int],
        velkost = (16, 16),
        cesta_k_obrazku: t.Optional[t.Union[Path, str]] = None,
    ):
        super().__init__(pozicia, velkost, cesta_k_obrazku)
        self.uroven_svetla = 0.0
        self.originalny_obrazok: pygame.Surface = (
            self.image.copy()
        )  # pred aplikovaním svetla

    def _vykresli_svetlo(self):
        alpha = round(255 * (1 - self.uroven_svetla))

        self.image = self.originalny_obrazok.copy()
        self.image.fill((0, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_SUB)

    def update(self):
        self._vykresli_svetlo()
        self.uroven_svetla += 0.01
        if self.uroven_svetla >= 1.0:
            self.uroven_svetla = 0.0