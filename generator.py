# generator.py — monster spawner buildings
import pygame
import random
from settings import *
from monster import Monster


class Generator:
    W = TILE
    H = TILE

    def __init__(self, tx: int, ty: int,
                 spawn_time: float = GENERATOR_SPAWN_TIME,
                 hp_mult: float = 1.0, dmg_mult: float = 1.0):
        self.rect        = pygame.Rect(tx * TILE, ty * TILE, self.W, self.H)
        self.hp          = float(GENERATOR_HP)
        self.max_hp      = float(GENERATOR_HP)
        self.alive       = True
        self._spawn_time = spawn_time
        self._timer      = random.uniform(0.5, spawn_time)
        self._pulse      = 0.0
        self._pulse_dir  = 1
        self._hp_mult    = hp_mult
        self._dmg_mult   = dmg_mult

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, monsters: list, tilemap):
        if not self.alive:
            return

        self._timer -= dt
        if self._timer <= 0:
            self._timer = self._spawn_time
            self._try_spawn(monsters, tilemap)

        self._pulse += dt * self._pulse_dir * 2.2
        if self._pulse >= 1.0:
            self._pulse = 1.0;  self._pulse_dir = -1
        elif self._pulse <= 0.0:
            self._pulse = 0.0;  self._pulse_dir  = 1

    def _try_spawn(self, monsters: list, tilemap):
        if len(monsters) >= MAX_MONSTERS:
            return
        tx = self.rect.centerx // TILE
        ty = self.rect.centery  // TILE
        for _ in range(30):
            ox = random.randint(-3, 3)
            oy = random.randint(-3, 3)
            nx, ny = tx + ox, ty + oy
            if not tilemap.is_wall(nx, ny):
                mtype = random.choices(
                    ['grunt', 'ghost', 'demon'],
                    weights=[6, 3, 1]
                )[0]
                monsters.append(Monster(nx * TILE, ny * TILE, mtype,
                                        hp_mult=self._hp_mult,
                                        dmg_mult=self._dmg_mult))
                return

    # ── Public ────────────────────────────────────────────────────────────────

    def take_damage(self, amount: float):
        self.hp -= amount
        if self.hp <= 0:
            self.hp    = 0
            self.alive = False

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        r = camera.apply(self.rect)

        if not self.alive:
            pygame.draw.rect(surface, COL_GEN_DEAD, r, border_radius=4)
            pygame.draw.rect(surface, (40, 30, 50), r, 2, border_radius=4)
            pygame.draw.line(surface, (70, 55, 80), r.topleft,  r.bottomright, 2)
            pygame.draw.line(surface, (70, 55, 80), r.topright, r.bottomleft,  2)
            return

        t   = self._pulse
        col = tuple(int(c * (0.55 + 0.45 * t)) for c in COL_GENERATOR)
        pygame.draw.rect(surface, col, r, border_radius=4)
        pygame.draw.rect(surface, COL_GEN_EDGE, r, 2, border_radius=4)

        # HP bar above the tile
        bar_w = self.W - 4
        bx, by = r.x + 2, r.y - 7
        pct = self.hp / self.max_hp
        pygame.draw.rect(surface, (60, 0, 60), (bx, by, bar_w, 4))
        pygame.draw.rect(surface, COL_GEN_EDGE, (bx, by, int(bar_w * pct), 4))

        # Rune crosshair
        cx, cy = r.center
        pygame.draw.circle(surface, (30,  0, 50), (cx, cy), 8)
        pygame.draw.circle(surface, COL_GEN_EDGE,  (cx, cy), 5, 1)
        pygame.draw.line(surface, COL_GEN_EDGE, (cx - 9, cy), (cx + 9, cy), 1)
        pygame.draw.line(surface, COL_GEN_EDGE, (cx, cy - 9), (cx, cy + 9), 1)
