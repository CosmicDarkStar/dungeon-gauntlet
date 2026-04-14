# projectile.py — player and monster projectiles
import pygame
from settings import TILE


class Projectile:
    SIZE = 5

    def __init__(self, x: float, y: float,
                 dx: float, dy: float,
                 color: tuple, speed: float,
                 max_range: float, owner: str,
                 damage: float = 1.0):
        self.x         = x
        self.y         = y
        self.dx        = dx
        self.dy        = dy
        self.color     = color
        self.speed     = speed
        self.max_range = max_range
        self.owner     = owner   # 'player' | 'monster'
        self.damage    = damage
        self.dist      = 0.0
        self.alive     = True

    def update(self, dt: float, tilemap):
        step    = self.speed * dt
        self.x += self.dx * step
        self.y += self.dy * step
        self.dist += step

        if self.dist >= self.max_range:
            self.alive = False
            return
        if tilemap.is_wall(int(self.x) // TILE, int(self.y) // TILE):
            self.alive = False

    @property
    def rect(self) -> pygame.Rect:
        s = self.SIZE
        return pygame.Rect(int(self.x) - s, int(self.y) - s, s * 2, s * 2)

    def draw(self, surface: pygame.Surface, camera):
        sx, sy = camera.apply_point(self.x, self.y)
        pygame.draw.circle(surface, self.color, (sx, sy), self.SIZE)
        # bright core
        pygame.draw.circle(surface, (255, 255, 255), (sx, sy), max(1, self.SIZE // 2))
