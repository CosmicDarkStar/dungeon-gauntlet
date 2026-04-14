# main.py — Dungeon Gauntlet entry point and game loop
# Requires: pip install pygame
import sys
import random
import pygame
from settings import *
from map import TileMap
from camera import Camera
from player import Player
from monster import Monster
from generator import Generator
from projectile import Projectile
from drop import Drop
from hud import HUD


def run():
    pygame.init()
    info   = pygame.display.Info()
    SW, SH = info.current_w, info.current_h
    screen = pygame.display.set_mode((SW, SH), pygame.FULLSCREEN)
    pygame.display.set_caption("DUNGEON GAUNTLET")

    while True:
        difficulty = _start_menu(screen, SW, SH)
        if difficulty is None:
            break
        _play_game(screen, SW, SH, difficulty)

    pygame.quit()
    sys.exit()


# ── Menus ─────────────────────────────────────────────────────────────────────

def _start_menu(screen: pygame.Surface, sw: int, sh: int):
    """Main title screen. Returns a difficulty string or None to quit."""
    font_title = pygame.font.SysFont('monospace', 80, bold=True)
    font_opt   = pygame.font.SysFont('monospace', 36, bold=True)
    font_hint  = pygame.font.SysFont('monospace', 20)

    options  = ['NEW GAME', 'QUIT']
    selected = 0
    clock    = pygame.time.Clock()

    while True:
        screen.fill(DARK_BG)

        t1 = font_title.render('DUNGEON',  True, COL_PLAYER)
        t2 = font_title.render('GAUNTLET', True, COL_DEMON)
        screen.blit(t1, (sw // 2 - t1.get_width() // 2, sh // 3 - 70))
        screen.blit(t2, (sw // 2 - t2.get_width() // 2, sh // 3 + 30))

        for i, label in enumerate(options):
            active = i == selected
            colour = COL_SHOT_P if active else COL_INFO
            prefix = '>  ' if active else '   '
            surf = font_opt.render(prefix + label, True, colour)
            screen.blit(surf, (sw // 2 - surf.get_width() // 2,
                                sh // 2 + 70 + i * 60))

        hint = font_hint.render(
            'W / S  or  \u2191\u2193  to select     ENTER to confirm',
            True, COL_INFO)
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 55))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    selected = (selected - 1) % len(options)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    selected = (selected + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if selected == 1:
                        return None
                    diff = _difficulty_menu(screen, sw, sh)
                    if diff is not None:
                        return diff
                    # ESC on difficulty screen → back to main menu
                elif event.key == pygame.K_ESCAPE:
                    return None


def _difficulty_menu(screen: pygame.Surface, sw: int, sh: int):
    """Difficulty selection. Returns 'easy'/'normal'/'hard' or None (back)."""
    font_title = pygame.font.SysFont('monospace', 42, bold=True)
    font_opt   = pygame.font.SysFont('monospace', 34, bold=True)
    font_desc  = pygame.font.SysFont('monospace', 17)
    font_hint  = pygame.font.SysFont('monospace', 20)

    order = ['easy', 'normal', 'hard']
    meta  = {
        'easy':   ('EASY',
                   'Fewer generators  \u2022  slower spawns  \u2022  weaker monsters',
                   COL_HP_HI),
        'normal': ('NORMAL',
                   'Standard challenge across all settings',
                   COL_SHOT_P),
        'hard':   ('HARD',
                   'More generators  \u2022  faster spawns  \u2022  tougher monsters',
                   COL_HP_LO),
    }
    selected = 1
    clock = pygame.time.Clock()

    while True:
        screen.fill(DARK_BG)

        title = font_title.render('SELECT DIFFICULTY', True, COL_INFO)
        screen.blit(title, (sw // 2 - title.get_width() // 2, sh // 3 - 30))

        for i, key in enumerate(order):
            label, desc, col = meta[key]
            active = i == selected
            prefix = '>  ' if active else '   '
            colour = col if active else (80, 70, 100)
            surf = font_opt.render(prefix + label, True, colour)
            dy = sh // 2 + (i - 1) * 95
            screen.blit(surf, (sw // 2 - surf.get_width() // 2, dy))
            if active:
                ds = font_desc.render(desc, True, (140, 130, 160))
                screen.blit(ds, (sw // 2 - ds.get_width() // 2, dy + 40))

        hint = font_hint.render(
            'W / S to select     ENTER to confirm     ESC to go back',
            True, COL_INFO)
        screen.blit(hint, (sw // 2 - hint.get_width() // 2, sh - 55))

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    selected = (selected - 1) % len(order)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    selected = (selected + 1) % len(order)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return order[selected]
                elif event.key == pygame.K_ESCAPE:
                    return None


# ── Difficulty scaling ────────────────────────────────────────────────────────

def _scale_difficulty(base: str, level: int) -> dict:
    """Return a difficulty-stats dict scaled for the given level number."""
    s = DIFFICULTY_PRESETS[base].copy()
    n = level - 1
    s['hp_mult']    = round(s['hp_mult']    + n * LEVEL_HP_SCALE,    3)
    s['dmg_mult']   = round(s['dmg_mult']   + n * LEVEL_DMG_SCALE,   3)
    s['spawn_mult'] = round(max(0.3, s['spawn_mult'] - n * LEVEL_SPAWN_SCALE), 3)
    s['gen_count']  = min(18, s['gen_count'] + n * LEVEL_GEN_SCALE)

    # Shift generator tier weights toward stronger tiers each level
    w      = list(s['tier_weights'])
    shift  = min(n * LEVEL_TIER_SHIFT, 30)
    w[0]   = max(5, w[0] - shift)
    w[2]  += shift
    s['tier_weights'] = w
    return s


# ── Game session loop ─────────────────────────────────────────────────────────

def _play_game(screen: pygame.Surface, sw: int, sh: int, base_difficulty: str):
    """Outer level loop for one full game session."""
    player = None
    level  = 1

    while True:
        diff = _scale_difficulty(base_difficulty, level)
        result, player = _run_level(screen, sw, sh, player, level, diff)

        if result == 'died':
            _game_over(screen, player, sw, sh)
            return
        if result == 'quit':
            return

        # Level complete — open shop
        if not _shop_screen(screen, sw, sh, player, level):
            return
        level += 1


# ── Level ─────────────────────────────────────────────────────────────────────

def _run_level(screen: pygame.Surface, sw: int, sh: int,
               player, level: int, diff: dict):
    """
    Run one dungeon level.
    Returns ('died' | 'complete' | 'quit', player).
    """
    clock = pygame.time.Clock()

    tilemap = TileMap(max_generators=diff['gen_count'])
    camera  = Camera(sw, sh)

    if player is None:
        player = Player(*tilemap.player_start)
    else:
        player.fx = float(tilemap.player_start[0])
        player.fy = float(tilemap.player_start[1])
        player.hp = float(PLAYER_MAX_HP)

    spawn_time  = GENERATOR_SPAWN_TIME * diff['spawn_mult']
    generators  = [Generator(tx, ty, mtype,
                              tier=random.choices([1, 2, 3],
                                                  weights=diff['tier_weights'])[0],
                              spawn_time=spawn_time,
                              hp_mult=diff['hp_mult'],
                              dmg_mult=diff['dmg_mult'])
                   for tx, ty, mtype in tilemap.generator_tiles]
    monsters:    list[Monster]    = []
    projectiles: list[Projectile] = []
    drops:       list[Drop]       = []
    hud       = HUD(sw, sh)
    exit_rect = pygame.Rect(tilemap.exit_tile[0] * TILE,
                             tilemap.exit_tile[1] * TILE,
                             TILE, TILE)
    exit_t    = 0.0   # pulse timer

    for gen in generators:
        gen._try_spawn(monsters, tilemap)
        gen._try_spawn(monsters, tilemap)

    while True:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit', player
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'quit', player

        keys = pygame.key.get_pressed()

        # ── Update ───────────────────────────────────────────────────────────
        exit_t += dt
        player.handle_input(keys)
        player.update(dt, tilemap, projectiles, monsters)

        for gen in generators:
            gen.update(dt, monsters, tilemap)

        for m in monsters:
            m.update(dt, tilemap, player, projectiles, monsters)

        for p in projectiles:
            p.update(dt, tilemap)

        # ── Collision resolution ─────────────────────────────────────────────
        live = [m for m in monsters if m.alive]

        for p in [x for x in projectiles if x.alive]:
            if p.owner == 'player':
                for m in live:
                    if p.rect.colliderect(m.rect):
                        m.take_damage(p.damage)
                        p.alive = False
                        if not m.alive:
                            player.score += m.score_value
                            if random.random() < HEALTH_DROP_CHANCE:
                                cx, cy = m.rect.center
                                drops.append(Drop(cx, cy, 'health',
                                                  random.randint(HEALTH_DROP_MIN,
                                                                 HEALTH_DROP_MAX)))
                        break
                if p.alive:
                    for gen in generators:
                        if gen.alive and p.rect.colliderect(gen.rect):
                            gen.take_damage(p.damage)
                            p.alive = False
                            if not gen.alive:
                                player.score += GEN_TIER_SCORE[gen.tier]
                                cx, cy = gen.rect.center
                                drops.append(Drop(cx, cy, 'coin',
                                                  random.randint(
                                                      GEN_TIER_COINS_MIN[gen.tier],
                                                      GEN_TIER_COINS_MAX[gen.tier])))
                            break
            elif p.owner == 'monster':
                # Shots can't pass through other monsters (friendly fire,
                # no health drop).  Skip self-hit by ignoring the first
                # Monster.SIZE pixels of travel.
                if p.dist > Monster.SIZE:
                    for m in live:
                        if p.rect.colliderect(m.rect):
                            m.take_damage(p.damage)
                            p.alive = False
                            break   # no health drop for monster-killed monsters
                if p.alive and p.rect.colliderect(player.rect):
                    player.take_damage(p.damage * diff['dmg_mult'])
                    p.alive = False

        # ── Drops: update, pickup, cull ───────────────────────────────────────
        for d in drops:
            d.update(dt)
            if d.check_pickup(player):
                if d.kind == 'health':
                    player.hp = min(PLAYER_MAX_HP, player.hp + d.value)
                else:
                    player.coins += d.value

        # ── Cull dead ────────────────────────────────────────────────────────
        monsters    = [m for m in monsters    if m.alive]
        projectiles = [p for p in projectiles if p.alive]
        drops       = [d for d in drops       if d.alive]

        # ── Camera ───────────────────────────────────────────────────────────
        camera.update(player.rect)

        # ── Draw ─────────────────────────────────────────────────────────────
        screen.fill(DARK_BG)
        tilemap.draw(screen, camera)
        _draw_exit(screen, camera, exit_rect, exit_t)

        for gen in generators:
            gen.draw(screen, camera)
        for d in drops:
            d.draw(screen, camera)
        for m in monsters:
            m.draw(screen, camera)
        for p in projectiles:
            p.draw(screen, camera)
        player.draw(screen, camera)

        gen_alive = sum(1 for g in generators if g.alive)
        hud.draw(screen, player, level, len(monsters), gen_alive, len(generators))

        pygame.display.flip()

        # ── End conditions ────────────────────────────────────────────────────
        if player.hp <= 0:
            return 'died', player

        if player.rect.colliderect(exit_rect):
            _level_complete_flash(screen, sw, sh, level)
            return 'complete', player


# ── Exit portal drawing ───────────────────────────────────────────────────────

def _draw_exit(screen: pygame.Surface, camera, exit_rect: pygame.Rect, t: float):
    import math
    r   = camera.apply(exit_rect)
    pulse = (math.sin(t * 2.8) + 1) / 2          # 0.0 – 1.0

    # Pulsing teal fill
    intensity = 0.45 + 0.55 * pulse
    fill = tuple(int(c * intensity) for c in COL_EXIT)
    pygame.draw.rect(screen, fill, r)

    # Bright border (thicker at peak pulse)
    border_w = 1 + int(pulse * 2)
    pygame.draw.rect(screen, COL_EXIT_EDGE, r, border_w)

    # Downward-pointing chevron (▼) drawn with two lines
    cx, cy = r.centerx, r.centery
    pad = r.w // 5
    tip = cy + r.h // 4
    left  = (cx - pad * 2, cy - r.h // 8)
    right = (cx + pad * 2, cy - r.h // 8)
    mid   = (cx, tip)
    pygame.draw.line(screen, COL_EXIT_EDGE, left,  mid, 2)
    pygame.draw.line(screen, COL_EXIT_EDGE, right, mid, 2)

    # Second smaller chevron above
    offset = r.h // 5
    left2  = (cx - pad,        cy - r.h // 8 - offset)
    right2 = (cx + pad,        cy - r.h // 8 - offset)
    mid2   = (cx, tip - offset)
    pygame.draw.line(screen, COL_EXIT_EDGE, left2, mid2, 1)
    pygame.draw.line(screen, COL_EXIT_EDGE, right2, mid2, 1)


# ── Level complete flash ──────────────────────────────────────────────────────

def _level_complete_flash(screen: pygame.Surface, sw: int, sh: int, level: int):
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont('monospace', 64, bold=True)
    font_sm  = pygame.font.SysFont('monospace', 22)

    t1 = font_big.render(f'LEVEL {level} COMPLETE!', True, COL_SHOT_P)
    t2 = font_sm .render('Heading to the shop...', True, COL_INFO)

    screen.blit(t1, (sw // 2 - t1.get_width() // 2, sh // 2 - 50))
    screen.blit(t2, (sw // 2 - t2.get_width() // 2, sh // 2 + 30))
    pygame.display.flip()
    pygame.time.wait(1800)


# ── Shop screen ───────────────────────────────────────────────────────────────

def _shop_screen(screen: pygame.Surface, sw: int, sh: int,
                 player, level: int) -> bool:
    """
    Between-level upgrade shop.
    Returns True to continue to next level, False to return to main menu.
    """
    UPGRADES = [
        ('DEFENCE',
         'defence_lvl',
         UPGRADE_COST_DEFENCE,
         lambda p: f'{int(p.damage_reduction * 100)}% dmg reduction'),
        ('SHOT RANGE',
         'range_lvl',
         UPGRADE_COST_RANGE,
         lambda p: f'{int(p.effective_shot_range)} px range'),
        ('MAX SHOTS',
         'shots_lvl',
         UPGRADE_COST_MAX_SHOTS,
         lambda p: f'{p.max_active_shots} shots on screen'),
        ('SHOT DAMAGE',
         'damage_lvl',
         UPGRADE_COST_DAMAGE,
         lambda p: f'{int(p.shot_damage)} damage per bolt'),
    ]
    CONTINUE_IDX = len(UPGRADES)
    ITEMS        = len(UPGRADES) + 1

    font_title = pygame.font.SysFont('monospace', 46, bold=True)
    font_sub   = pygame.font.SysFont('monospace', 24, bold=True)
    font_row   = pygame.font.SysFont('monospace', 22, bold=True)
    font_stat  = pygame.font.SysFont('monospace', 17)
    font_hint  = pygame.font.SysFont('monospace', 18)

    selected = 0
    clock    = pygame.time.Clock()
    cx       = sw // 2

    ROW_H = 72
    row_y = 210   # y of first upgrade row

    while True:
        screen.fill(DARK_BG)

        # ── Header ────────────────────────────────────────────────────────────
        t = font_title.render(f'LEVEL {level + 1} APPROACHING', True, COL_SHOT_P)
        screen.blit(t, (cx - t.get_width() // 2, 40))

        sub = font_sub.render(
            f'Score: {player.score}     \u25c6 Coins: {player.coins}',
            True, COL_SCORE)
        screen.blit(sub, (cx - sub.get_width() // 2, 105))

        sep_y = 152
        pygame.draw.line(screen, (55, 42, 80), (sw // 6, sep_y), (sw * 5 // 6, sep_y), 1)
        sh_label = font_sub.render('UPGRADES', True, COL_INFO)
        screen.blit(sh_label, (cx - sh_label.get_width() // 2, sep_y + 12))

        # ── Upgrade rows ──────────────────────────────────────────────────────
        rx = sw // 6
        rw = sw * 2 // 3

        for i, (name, attr, costs, stat_fn) in enumerate(UPGRADES):
            cur_lvl = getattr(player, attr)
            maxed   = cur_lvl >= MAX_UPGRADE_LEVEL
            cost    = costs[cur_lvl] if not maxed else 0
            can_buy = (not maxed) and player.coins >= cost
            active  = i == selected

            ry = row_y + i * ROW_H

            if active:
                pygame.draw.rect(screen, (28, 20, 48),
                                 (rx, ry, rw, ROW_H - 8), border_radius=6)
                pygame.draw.rect(screen, (85, 60, 130),
                                 (rx, ry, rw, ROW_H - 8), 1, border_radius=6)

            # Upgrade name
            prefix   = '>  ' if active else '   '
            name_col = COL_SHOT_P if active else (155, 135, 195)
            screen.blit(font_row.render(prefix + name, True, name_col),
                        (rx + 12, ry + 10))

            # Level arrow  e.g.  Lv 1 ► Lv 2
            if maxed:
                lvl_txt = f'Lv {cur_lvl}  [ MAX ]'
                lvl_col = (80, 200, 90)
            else:
                lvl_txt = f'Lv {cur_lvl}  \u25ba  Lv {cur_lvl + 1}'
                lvl_col = (175, 155, 220) if active else (105, 95, 135)
            screen.blit(font_stat.render(lvl_txt, True, lvl_col),
                        (rx + 270, ry + 8))

            # Current stat value
            stat_col = (110, 225, 115) if active else (80, 150, 85)
            screen.blit(font_stat.render(stat_fn(player), True, stat_col),
                        (rx + 270, ry + 28))

            # Cost (right-aligned)
            if not maxed:
                if can_buy:
                    cost_txt = f'\u25c6 {cost}'
                    cost_col = COL_COIN_DROP
                else:
                    cost_txt = f'\u25c6 {cost}  (need {cost - player.coins} more)'
                    cost_col = (150, 65, 65)
                cs = font_stat.render(cost_txt, True, cost_col)
                screen.blit(cs, (rx + rw - cs.get_width() - 14, ry + 18))

        # ── Continue button ───────────────────────────────────────────────────
        cont_y  = row_y + len(UPGRADES) * ROW_H + 18
        active  = selected == CONTINUE_IDX
        cont_col = COL_SHOT_P if active else COL_INFO
        prefix  = '>  ' if active else '   '
        cont_s  = font_row.render(f'{prefix}CONTINUE  TO  LEVEL {level + 1}',
                                  True, cont_col)
        screen.blit(cont_s, (cx - cont_s.get_width() // 2, cont_y))

        # ── Hint ──────────────────────────────────────────────────────────────
        hint = font_hint.render(
            'W / S to navigate     ENTER to buy / continue     ESC to menu',
            True, (65, 55, 85))
        screen.blit(hint, (cx - hint.get_width() // 2, sh - 38))

        pygame.display.flip()
        clock.tick(30)

        # ── Input ─────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    selected = (selected - 1) % ITEMS
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    selected = (selected + 1) % ITEMS
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if selected == CONTINUE_IDX:
                        return True
                    name, attr, costs, _ = UPGRADES[selected]
                    cur_lvl = getattr(player, attr)
                    if cur_lvl >= MAX_UPGRADE_LEVEL:
                        continue
                    cost = costs[cur_lvl]
                    if player.coins >= cost:
                        player.coins -= cost
                        setattr(player, attr, cur_lvl + 1)
                elif event.key == pygame.K_ESCAPE:
                    return False


# ── Game over ─────────────────────────────────────────────────────────────────

def _game_over(screen: pygame.Surface, player, sw: int, sh: int):
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont('monospace', 72, bold=True)
    font_med = pygame.font.SysFont('monospace', 30, bold=True)
    font_sm  = pygame.font.SysFont('monospace', 20)

    t1 = font_big.render('GAME  OVER', True, (220, 50, 50))
    t2 = font_med.render(f'FINAL SCORE :  {player.score}', True, COL_SCORE)
    t3 = font_sm .render('Press any key to return to menu', True, COL_INFO)

    screen.blit(t1, (sw // 2 - t1.get_width() // 2, sh // 2 - 90))
    screen.blit(t2, (sw // 2 - t2.get_width() // 2, sh // 2 + 10))
    screen.blit(t3, (sw // 2 - t3.get_width() // 2, sh // 2 + 60))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False


if __name__ == '__main__':
    run()
