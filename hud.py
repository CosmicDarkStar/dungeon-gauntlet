# hud.py — on-screen HUD: health bar, score, enemy count
import pygame
from settings import *


class HUD:
    HEIGHT = 66

    def __init__(self, screen_w: int, screen_h: int):
        self.sw = screen_w
        self.sh = screen_h
        self.font_lg = pygame.font.SysFont('monospace', 22, bold=True)
        self.font_sm = pygame.font.SysFont('monospace', 14, bold=True)
        self._bg: pygame.Surface | None = None

    def draw(self, surface: pygame.Surface, player,
             level: int, monster_count: int,
             gen_alive: int, gen_total: int):

        # Lazy-init semi-transparent background strip
        if self._bg is None:
            self._bg = pygame.Surface((self.sw, self.HEIGHT), pygame.SRCALPHA)
            self._bg.fill((*COL_HUD_BG, 215))
        surface.blit(self._bg, (0, 0))

        # ── Health bar ────────────────────────────────────────────────────────
        bx, by, bw, bh = 16, 14, 230, 22
        pct = max(0.0, player.hp / PLAYER_MAX_HP)
        col = COL_HP_HI if pct > 0.5 else (COL_HP_MID if pct > 0.25 else COL_HP_LO)

        pygame.draw.rect(surface, (40, 15, 15), (bx, by, bw, bh), border_radius=4)
        if pct > 0:
            pygame.draw.rect(surface, col,
                             (bx, by, int(bw * pct), bh), border_radius=4)
        pygame.draw.rect(surface, (100, 70, 70), (bx, by, bw, bh), 2, border_radius=4)

        lbl = self.font_sm.render(f'HP  {int(player.hp):>3} / {PLAYER_MAX_HP}',
                                  True, (220, 200, 200))
        surface.blit(lbl, (bx + 6, by + 4))

        # ── Coin counter (below HP bar) ───────────────────────────────────────
        coin_lbl = self.font_sm.render(f'\u25c6  {player.coins} coins', True, COL_COIN_DROP)
        surface.blit(coin_lbl, (bx + 6, by + bh + 6))

        # ── Score (centre) ────────────────────────────────────────────────────
        sc = self.font_lg.render(f'SCORE  {player.score:>6}', True, COL_SCORE)
        surface.blit(sc, (self.sw // 2 - sc.get_width() // 2, 13))

        # ── Right info ────────────────────────────────────────────────────────
        info = f'LVL {level}   ENEMIES {monster_count:>3}   GENS {gen_alive}/{gen_total}'
        ri = self.font_sm.render(info, True, COL_INFO)
        surface.blit(ri, (self.sw - ri.get_width() - 16, 17))

        # ── Controls reminder (bottom-left, faint) ────────────────────────────
        hint = self.font_sm.render('WASD move   SPACE shoot   ESC quit', True, (60, 50, 80))
        surface.blit(hint, (16, self.sh - 22))
