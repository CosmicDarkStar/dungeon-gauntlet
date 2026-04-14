# camera.py — scroll camera that follows the player
import pygame
from settings import TILE, MAP_W, MAP_H


class Camera:
    def __init__(self, screen_w: int, screen_h: int,
                 map_w: int = MAP_W, map_h: int = MAP_H):
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.map_px_w  = map_w * TILE
        self.map_px_h  = map_h * TILE
        self.offset    = [0, 0]

    def update(self, target: pygame.Rect):
        x = target.centerx - self.screen_w // 2
        y = target.centery - self.screen_h // 2
        self.offset[0] = max(0, min(x, self.map_px_w - self.screen_w))
        self.offset[1] = max(0, min(y, self.map_px_h - self.screen_h))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(rect.x - self.offset[0],
                           rect.y - self.offset[1],
                           rect.w, rect.h)

    def apply_point(self, x: float, y: float) -> tuple[int, int]:
        return (int(x) - self.offset[0], int(y) - self.offset[1])
