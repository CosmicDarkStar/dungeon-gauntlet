# player.py — player entity: movement, shooting, health
import pygame
import math
from settings import *
from projectile import Projectile

_DIAG = 1.0 / math.sqrt(2)


def _wall_check(tilemap, rect: pygame.Rect) -> bool:
    for cx, cy in [(rect.left,   rect.top),
                   (rect.right-1, rect.top),
                   (rect.left,   rect.bottom-1),
                   (rect.right-1, rect.bottom-1)]:
        if tilemap.is_wall(cx // TILE, cy // TILE):
            return True
    return False


class Player:
    W = TILE - 4   # 28 px
    H = TILE - 4

    def __init__(self, x: float, y: float):
        self.fx   = float(x)    # float world position
        self.fy   = float(y)
        self.hp    = float(PLAYER_MAX_HP)
        self.score = 0
        self.coins = 0
        # ── Upgrade levels (0 = base, max = MAX_UPGRADE_LEVEL) ────────────────
        self.defence_lvl  = 0   # reduces damage taken
        self.range_lvl    = 0   # increases shot range
        self.shots_lvl    = 0   # increases max simultaneous shots
        self.damage_lvl   = 0   # increases shot damage
        # ── Movement / shooting state ─────────────────────────────────────────
        self._dx   = 0.0
        self._dy   = 0.0
        self.facing = (1, 0)    # last non-zero move direction (raw ints)
        self._shoot_cd    = 0.0
        self._inv         = 0.0  # invincibility seconds after a hit
        self._drain_accum = 0.0
        self.flash        = 0.0  # white-flash timer when hit

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.fx), int(self.fy), self.W, self.H)

    # ── Upgrade-derived stats ─────────────────────────────────────────────────

    @property
    def damage_reduction(self) -> float:
        """Fraction of incoming damage blocked (0.0 – 0.40)."""
        return self.defence_lvl * ATTR_DEFENCE_REDUX

    @property
    def effective_shot_range(self) -> float:
        return SHOT_RANGE + self.range_lvl * ATTR_RANGE_BONUS

    @property
    def max_active_shots(self) -> int:
        return ATTR_MAX_SHOTS_BASE + self.shots_lvl

    @property
    def shot_damage(self) -> float:
        return ATTR_DAMAGE_BASE + self.damage_lvl * ATTR_DAMAGE_BONUS

    # ── Input ─────────────────────────────────────────────────────────────────

    def handle_input(self, keys):
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN])  - int(keys[pygame.K_w] or keys[pygame.K_UP])

        if dx != 0 and dy != 0:
            self._dx = dx * _DIAG
            self._dy = dy * _DIAG
        else:
            self._dx = float(dx)
            self._dy = float(dy)

        if dx != 0 or dy != 0:
            self.facing = (dx, dy)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, tilemap, projectiles: list, monsters: list = None):
        self._move(tilemap, dt, monsters or [])

        # Shooting
        self._shoot_cd = max(0.0, self._shoot_cd - dt)
        if pygame.key.get_pressed()[pygame.K_SPACE] and self._shoot_cd == 0.0:
            self._fire(projectiles)
            self._shoot_cd = SHOOT_COOLDOWN

        # Passive HP drain
        self._drain_accum += dt
        if self._drain_accum >= 1.0:
            self._drain_accum -= 1.0
            self.hp = max(0.0, self.hp - HP_DRAIN_RATE)

        self._inv  = max(0.0, self._inv  - dt)
        self.flash = max(0.0, self.flash - dt)

    # ── Private ───────────────────────────────────────────────────────────────

    def _move(self, tilemap, dt: float, monsters: list):
        spd = PLAYER_SPEED * dt

        new_fx = self.fx + self._dx * spd
        test   = pygame.Rect(int(new_fx), int(self.fy), self.W, self.H)
        if not _wall_check(tilemap, test) and not self._overlaps_monster(test, monsters):
            self.fx = new_fx

        new_fy = self.fy + self._dy * spd
        test   = pygame.Rect(int(self.fx), int(new_fy), self.W, self.H)
        if not _wall_check(tilemap, test) and not self._overlaps_monster(test, monsters):
            self.fy = new_fy

    def _overlaps_monster(self, rect: pygame.Rect, monsters: list) -> bool:
        for m in monsters:
            if m.alive and rect.colliderect(m.rect):
                return True
        return False

    def _fire(self, projectiles: list):
        active = sum(1 for p in projectiles if p.owner == 'player')
        if active >= self.max_active_shots:
            return
        fx, fy = self.facing
        length = math.hypot(fx, fy)
        if length == 0:
            fx, fy = 1.0, 0.0
        else:
            fx /= length
            fy /= length
        projectiles.append(
            Projectile(self.rect.centerx, self.rect.centery,
                       fx, fy, COL_SHOT_P, SHOT_SPEED,
                       self.effective_shot_range, 'player',
                       damage=self.shot_damage))

    # ── Public ────────────────────────────────────────────────────────────────

    def take_damage(self, amount: float):
        if self._inv > 0:
            return
        reduced    = amount * (1.0 - self.damage_reduction)
        self.hp    = max(0.0, self.hp - reduced)
        self._inv  = 0.5
        self.flash = 0.3

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        r     = camera.apply(self.rect)
        color = (240, 240, 240) if (self.flash > 0 and int(self.flash * 14) % 2 == 0) else COL_PLAYER

        pygame.draw.rect(surface, color, r, border_radius=5)

        # Eyes pointing toward facing direction
        fx, fy = self.facing
        # Map to cardinal for eye placement
        ex = 1 if fx > 0 else (-1 if fx < 0 else 0)
        ey = 1 if fy > 0 else (-1 if fy < 0 else 0)
        oe = 5
        e1 = (r.centerx + ex * oe + ey * 4, r.centery + ey * oe - ex * 4)
        e2 = (r.centerx + ex * oe - ey * 4, r.centery + ey * oe + ex * 4)
        pygame.draw.circle(surface, (10, 10, 10), e1, 2)
        pygame.draw.circle(surface, (10, 10, 10), e2, 2)
