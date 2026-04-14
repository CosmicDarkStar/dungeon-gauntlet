# generator.py — monster spawner buildings
import pygame
import random
from settings import *
from monster import Monster


class Generator:
    W = TILE
    H = TILE

    def __init__(self, tx: int, ty: int,
                 mtype: str = 'grunt',
                 tier: int = 1,
                 spawn_time: float = GENERATOR_SPAWN_TIME,
                 hp_mult: float = 1.0, dmg_mult: float = 1.0):
        self.rect        = pygame.Rect(tx * TILE, ty * TILE, self.W, self.H)
        self.tier        = tier                      # base (immutable) tier
        self.max_hp      = float(GEN_TIER_HP[tier])
        self.hp          = self.max_hp
        self.alive       = True
        self.mtype       = mtype
        self._col, self._edge = GEN_TYPE_COLORS[mtype]
        self._spawn_time = spawn_time
        self._timer      = random.uniform(0.5, spawn_time)
        self._pulse      = 0.0
        self._pulse_dir  = 1
        self._hp_mult    = hp_mult
        self._dmg_mult   = dmg_mult

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def current_tier(self) -> int:
        """Effective tier based on remaining HP — downgrades as damage accumulates."""
        pct = self.hp / self.max_hp
        if pct > 0.66:
            return self.tier
        elif pct > 0.33:
            return max(1, self.tier - 1)
        else:
            return max(1, self.tier - 2)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, monsters: list, tilemap):
        if not self.alive:
            return

        self._timer -= dt
        if self._timer <= 0:
            self._timer = self._spawn_time
            self._try_spawn(monsters, tilemap)

        # Pulse speed increases with current tier (stronger = more energetic)
        pulse_spd = 1.8 + (self.current_tier - 1) * 0.9
        self._pulse += dt * self._pulse_dir * pulse_spd
        if self._pulse >= 1.0:
            self._pulse = 1.0;  self._pulse_dir = -1
        elif self._pulse <= 0.0:
            self._pulse = 0.0;  self._pulse_dir  = 1

    def _try_spawn(self, monsters: list, tilemap):
        if len(monsters) >= MAX_MONSTERS:
            return

        gx = self.rect.centerx // TILE
        gy = self.rect.centery  // TILE

        occupied = set()
        for m in monsters:
            if m.alive:
                occupied.add((int(m.fx + Monster.SIZE / 2) // TILE,
                              int(m.fy + Monster.SIZE / 2) // TILE))

        ct = self.current_tier
        tier_hp  = GEN_TIER_HP_MULT[ct]
        tier_dmg = GEN_TIER_DMG_MULT[ct]

        for radius in range(1, 4):
            ring = [
                (gx + ox, gy + oy)
                for ox in range(-radius, radius + 1)
                for oy in range(-radius, radius + 1)
                if abs(ox) == radius or abs(oy) == radius
            ]
            random.shuffle(ring)
            for tx, ty in ring:
                if tilemap.is_wall(tx, ty):
                    continue
                if (tx, ty) in occupied:
                    continue
                monsters.append(Monster(tx * TILE, ty * TILE, self.mtype,
                                        hp_mult=self._hp_mult * tier_hp,
                                        dmg_mult=self._dmg_mult * tier_dmg))
                return

    # ── Public ────────────────────────────────────────────────────────────────

    def take_damage(self, amount: float):
        self.hp -= amount
        if self.hp <= 0:
            self.hp    = 0
            self.alive = False

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        r  = camera.apply(self.rect)
        ct = self.current_tier
        t  = self._pulse

        if not self.alive:
            pygame.draw.rect(surface, COL_GEN_DEAD, r, border_radius=4)
            pygame.draw.rect(surface, (40, 30, 50), r, 2, border_radius=4)
            pygame.draw.line(surface, (70, 55, 80), r.topleft,  r.bottomright, 2)
            pygame.draw.line(surface, (70, 55, 80), r.topright, r.bottomleft,  2)
            return

        # Outer glow for tier 2+ (expands beyond the tile)
        if ct >= 2:
            expand  = (ct - 1) * 4
            glow_r  = r.inflate(expand * 2, expand * 2)
            glow_a  = int(60 * t)
            glow_s  = pygame.Surface((glow_r.w, glow_r.h), pygame.SRCALPHA)
            ec      = self._edge
            pygame.draw.rect(glow_s, (*ec, glow_a),
                             glow_s.get_rect(), border_radius=8)
            surface.blit(glow_s, glow_r.topleft)

        # Main tile fill (brightness pulses with tier speed)
        brightness = 0.45 + 0.55 * t
        col = tuple(int(c * brightness) for c in self._col)
        pygame.draw.rect(surface, col, r, border_radius=4)

        # Border — thicker for higher tiers
        pygame.draw.rect(surface, self._edge, r, ct, border_radius=4)

        # ── HP bar ────────────────────────────────────────────────────────────
        bar_w = self.W - 4
        bx, by = r.x + 2, r.y - 8
        pct = self.hp / self.max_hp
        pygame.draw.rect(surface, (40, 10, 10), (bx, by, bar_w, 4))
        pygame.draw.rect(surface, self._edge,   (bx, by, int(bar_w * pct), 4))

        # Tier-pip indicators above HP bar (filled dots = current tier)
        for i in range(self.tier):
            filled = i < ct          # dims pips that have been lost
            pip_col = self._edge if filled else (50, 40, 60)
            pygame.draw.circle(surface, pip_col,
                               (bx + 4 + i * 8, by - 6), 3)

        # ── Rune crosshair ────────────────────────────────────────────────────
        cx, cy = r.center
        pygame.draw.circle(surface, (20, 10, 10), (cx, cy), 8)
        pygame.draw.circle(surface, self._edge,   (cx, cy), 5, 1)
        pygame.draw.line(surface, self._edge, (cx - 9, cy), (cx + 9, cy), 1)
        pygame.draw.line(surface, self._edge, (cx, cy - 9), (cx, cy + 9), 1)

        if ct >= 2:
            # Outer ring
            pygame.draw.circle(surface, self._edge, (cx, cy), 11, 1)

        if ct >= 3:
            # Corner diamond marks
            for ddx, ddy in [(-12, -12), (12, -12), (-12, 12), (12, 12)]:
                pts = [
                    (cx + ddx,     cy + ddy - 3),
                    (cx + ddx + 3, cy + ddy    ),
                    (cx + ddx,     cy + ddy + 3),
                    (cx + ddx - 3, cy + ddy    ),
                ]
                pygame.draw.polygon(surface, self._edge, pts)
