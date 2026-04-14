# main.py — Dungeon Gauntlet entry point and game loop
# Requires: pip install pygame
import sys
import pygame
from settings import *
from map import TileMap
from camera import Camera
from player import Player
from monster import Monster
from generator import Generator
from projectile import Projectile
from hud import HUD


def run():
    pygame.init()
    info   = pygame.display.Info()
    SW, SH = info.current_w, info.current_h
    screen = pygame.display.set_mode((SW, SH), pygame.FULLSCREEN)
    pygame.display.set_caption("DUNGEON GAUNTLET")
    clock  = pygame.time.Clock()

    tilemap     = TileMap()
    camera      = Camera(SW, SH)
    player      = Player(*tilemap.player_start)
    generators  = [Generator(tx, ty) for tx, ty in tilemap.generator_tiles]
    monsters:    list[Monster]    = []
    projectiles: list[Projectile] = []
    hud         = HUD(SW, SH)
    level       = 1

    # Pre-seed a few monsters so the dungeon feels alive immediately
    for gen in generators:
        gen._try_spawn(monsters, tilemap)
        gen._try_spawn(monsters, tilemap)

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)   # cap at 50 ms

        # ── Events ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()

        # ── Update ───────────────────────────────────────────────────────────
        player.handle_input(keys)
        player.update(dt, tilemap, projectiles)

        for gen in generators:
            gen.update(dt, monsters, tilemap)

        for m in monsters:
            m.update(dt, tilemap, player, projectiles)

        for p in projectiles:
            p.update(dt, tilemap)

        # ── Collision resolution ─────────────────────────────────────────────
        live = [m for m in monsters if m.alive]

        for p in [x for x in projectiles if x.alive]:
            if p.owner == 'player':
                # vs monsters
                for m in live:
                    if p.rect.colliderect(m.rect):
                        m.take_damage(SHOT_DAMAGE)
                        p.alive = False
                        if not m.alive:
                            player.score += m.score_value
                        break
                # vs generators (only if still alive after monster check)
                if p.alive:
                    for gen in generators:
                        if gen.alive and p.rect.colliderect(gen.rect):
                            gen.take_damage(SHOT_DAMAGE)
                            p.alive = False
                            if not gen.alive:
                                player.score += 100
                            break
            elif p.owner == 'monster':
                if p.rect.colliderect(player.rect):
                    player.take_damage(DEMON_SHOT_DMG)
                    p.alive = False

        # ── Cull dead ────────────────────────────────────────────────────────
        monsters    = [m for m in monsters    if m.alive]
        projectiles = [p for p in projectiles if p.alive]

        # ── Camera ───────────────────────────────────────────────────────────
        camera.update(player.rect)

        # ── Draw ─────────────────────────────────────────────────────────────
        screen.fill(DARK_BG)
        tilemap.draw(screen, camera)

        for gen in generators:
            gen.draw(screen, camera)
        for m in monsters:
            m.draw(screen, camera)
        for p in projectiles:
            p.draw(screen, camera)
        player.draw(screen, camera)

        gen_alive = sum(1 for g in generators if g.alive)
        hud.draw(screen, player, level, len(monsters), gen_alive, len(generators))

        pygame.display.flip()

        # ── Game over check ───────────────────────────────────────────────────
        if player.hp <= 0:
            _game_over(screen, player, SW, SH)
            running = False

    pygame.quit()
    sys.exit()


def _game_over(screen: pygame.Surface, player, sw: int, sh: int):
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    screen.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont('monospace', 72, bold=True)
    font_med = pygame.font.SysFont('monospace', 30, bold=True)
    font_sm  = pygame.font.SysFont('monospace', 20)

    t1 = font_big.render('GAME  OVER', True, (220, 50, 50))
    t2 = font_med.render(f'FINAL SCORE :  {player.score}', True, COL_SCORE)
    t3 = font_sm .render('Press any key to exit', True, COL_INFO)

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
