# monster.py — Grunt, Ghost, Demon enemy types
import pygame
import math
import random
from settings import *
from projectile import Projectile


def _wall_check(tilemap, rect: pygame.Rect) -> bool:
    for cx, cy in [(rect.left,    rect.top),
                   (rect.right-1, rect.top),
                   (rect.left,    rect.bottom-1),
                   (rect.right-1, rect.bottom-1)]:
        if tilemap.is_wall(cx // TILE, cy // TILE):
            return True
    return False


_TYPES = {
    'grunt': dict(hp=GRUNT_HP, speed=GRUNT_SPEED, color=COL_GRUNT,
                  dmg=GRUNT_DMG, score=10, walls=False),
    'ghost': dict(hp=GHOST_HP, speed=GHOST_SPEED, color=COL_GHOST,
                  dmg=GHOST_DMG, score=15, walls=True),
    'demon': dict(hp=DEMON_HP, speed=DEMON_SPEED, color=COL_DEMON,
                  dmg=DEMON_DMG, score=30, walls=False),
}


class Monster:
    SIZE = TILE - 8   # 24 px

    def __init__(self, x: float, y: float, mtype: str = 'grunt',
                 hp_mult: float = 1.0, dmg_mult: float = 1.0):
        cfg = _TYPES[mtype]
        self.mtype         = mtype
        self.fx            = float(x)
        self.fy            = float(y)
        self.hp            = float(cfg['hp']) * hp_mult
        self.max_hp        = self.hp
        self.speed         = cfg['speed']
        self.color         = cfg['color']
        self.dmg           = cfg['dmg'] * dmg_mult
        self.score_value   = cfg['score']
        self.through_walls = cfg['walls']
        self.alive         = True
        self.flash         = 0.0
        self._shoot_cd     = random.uniform(1.5, 4.0)
        self._wander_t     = random.uniform(0, math.pi * 2)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.fx), int(self.fy), self.SIZE, self.SIZE)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, tilemap, player, projectiles: list,
               monsters: list):
        self._move(dt, tilemap, player, monsters)

        if self.mtype == 'demon':
            self._shoot_cd -= dt
            if self._shoot_cd <= 0:
                self._fire(player, projectiles)
                self._shoot_cd = random.uniform(2.2, 4.5)

        self.flash = max(0.0, self.flash - dt)

        # Continuous contact damage
        if self.rect.colliderect(player.rect):
            player.take_damage(self.dmg * dt)

    # ── Private ───────────────────────────────────────────────────────────────

    def _move(self, dt: float, tilemap, player, monsters: list):
        px, py = player.rect.center
        mx = self.fx + self.SIZE / 2
        my = self.fy + self.SIZE / 2
        dx, dy = px - mx, py - my
        dist   = math.hypot(dx, dy)
        if dist < 1:
            return
        nx, ny = dx / dist, dy / dist

        # Demons strafe slightly while chasing
        if self.mtype == 'demon':
            self._wander_t += dt * 1.8
            perp = math.sin(self._wander_t) * 0.35
            wnx  = nx - ny * perp
            wny  = ny + nx * perp
            ln   = math.hypot(wnx, wny)
            if ln > 0.001:
                nx, ny = wnx / ln, wny / ln

        step = self.speed * dt

        def _free(fx, fy):
            r = pygame.Rect(int(fx), int(fy), self.SIZE, self.SIZE)
            if not self.through_walls and _wall_check(tilemap, r):
                return False
            return not self._overlaps_monster(r, monsters)

        new_fx = self.fx + nx * step
        new_fy = self.fy + ny * step

        # Priority chain — first free candidate wins:
        #   1. full diagonal  (ideal path)
        #   2. X-only slide   (wall on Y side)
        #   3. Y-only slide   (wall on X side)
        #   4. perp-left      (-ny,  nx) — steer around the corner
        #   5. perp-right     ( ny, -nx) — other side of the corner
        for cfx, cfy in (
            (new_fx,              new_fy             ),
            (new_fx,              self.fy            ),
            (self.fx,             new_fy             ),
            (self.fx - ny * step, self.fy + nx * step),
            (self.fx + ny * step, self.fy - nx * step),
        ):
            if _free(cfx, cfy):
                self.fx = cfx
                self.fy = cfy
                return

    def _overlaps_monster(self, rect: pygame.Rect, monsters: list) -> bool:
        for m in monsters:
            if m is self or not m.alive:
                continue
            if rect.colliderect(m.rect):
                return True
        return False

    def _fire(self, player, projectiles: list):
        cx, cy = self.rect.center
        px, py = player.rect.center
        dx, dy = px - cx, py - cy
        dist   = math.hypot(dx, dy)
        if dist < 1:
            return
        projectiles.append(
            Projectile(cx, cy, dx / dist, dy / dist,
                       COL_SHOT_D, SHOT_SPEED * 0.55, SHOT_RANGE * 0.75, 'monster'))

    # ── Public ────────────────────────────────────────────────────────────────

    def take_damage(self, amount: float):
        self.hp -= amount
        self.flash = 0.15
        if self.hp <= 0:
            self.alive = False

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        r     = camera.apply(self.rect)
        color = (240, 240, 240) if self.flash > 0 else self.color

        if self.mtype == 'grunt':
            pygame.draw.rect(surface, color, r, border_radius=2)
            # Horns
            for hx in (r.left + 6, r.right - 6):
                pygame.draw.polygon(surface, color, [
                    (hx - 3, r.top), (hx + 3, r.top), (hx, r.top - 7)
                ])
            # Eyes
            pygame.draw.circle(surface, (20, 0, 0), (r.centerx - 4, r.centery - 2), 3)
            pygame.draw.circle(surface, (20, 0, 0), (r.centerx + 4, r.centery - 2), 3)

        elif self.mtype == 'ghost':
            alpha = 255 if self.flash > 0 else 185
            s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (*color, alpha), s.get_rect())
            # Squiggly hem — three downward bumps
            bw = r.w // 3
            for i in range(3):
                bx = bw // 2 + i * bw
                pygame.draw.circle(s, (*color, alpha), (bx, r.h - 1), bw // 2 + 1)
            surface.blit(s, r.topleft)
            # Eyes on top
            pygame.draw.circle(surface, (0, 50, 50), (r.centerx - 4, r.centery - 3), 3)
            pygame.draw.circle(surface, (0, 50, 50), (r.centerx + 4, r.centery - 3), 3)

        elif self.mtype == 'demon':
            pygame.draw.rect(surface, color, r, border_radius=3)
            # Wings
            pygame.draw.polygon(surface, color, [
                (r.left,      r.centery),
                (r.left - 10, r.top),
                (r.left,      r.top + 7),
            ])
            pygame.draw.polygon(surface, color, [
                (r.right,      r.centery),
                (r.right + 10, r.top),
                (r.right,      r.top + 7),
            ])
            # Glowing red eyes
            pygame.draw.circle(surface, (255, 50, 0), (r.centerx - 4, r.centery - 2), 3)
            pygame.draw.circle(surface, (255, 50, 0), (r.centerx + 4, r.centery - 2), 3)
