# drop.py — collectible health and coin drops
import math
import pygame
from settings import *


class Drop:
    RADIUS = 7

    def __init__(self, x: float, y: float, kind: str, value: int):
        self.x     = x
        self.y     = y
        self.kind  = kind    # 'health' | 'coin'
        self.value = value
        self.alive = True
        self._t    = 0.0     # used for bobbing animation

    def update(self, dt: float):
        self._t += dt

    def check_pickup(self, player) -> bool:
        """Return True (and mark dead) if the player is close enough to collect."""
        px, py = player.rect.center
        if math.hypot(px - self.x, py - self.y) <= DROP_PICKUP_RADIUS:
            self.alive = False
            return True
        return False

    def draw(self, surface: pygame.Surface, camera):
        bob     = int(math.sin(self._t * 3.5) * 2)
        cx, cy  = camera.apply_point(self.x, self.y)
        cy     += bob

        if self.kind == 'health':
            # Green circle with white cross
            pygame.draw.circle(surface, COL_HEALTH_DROP, (cx, cy), self.RADIUS)
            pygame.draw.line(surface, (240, 255, 240),
                             (cx, cy - 4), (cx, cy + 4), 2)
            pygame.draw.line(surface, (240, 255, 240),
                             (cx - 4, cy), (cx + 4, cy), 2)
        else:
            # Gold coin with darker inner ring
            pygame.draw.circle(surface, COL_COIN_DROP,   (cx, cy), self.RADIUS)
            pygame.draw.circle(surface, (200, 155, 10),  (cx, cy), self.RADIUS - 3)
            pygame.draw.circle(surface, COL_COIN_DROP,   (cx, cy), self.RADIUS, 1)
