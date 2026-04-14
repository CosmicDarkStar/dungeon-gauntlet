# map.py — procedural dungeon generation and tile rendering
import pygame
import random
from settings import *

WALL  = 0
FLOOR = 1


class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = pygame.Rect(x, y, w, h)

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)


class TileMap:
    def __init__(self, width=MAP_W, height=MAP_H, seed=None, max_generators=None):
        if seed is not None:
            random.seed(seed)
        self.width  = width
        self.height = height
        self.tiles  = [[WALL] * width for _ in range(height)]
        self.rooms: list[Room] = []
        self.generator_tiles: list[tuple[int, int, str]] = []
        self.exit_tile:       tuple[int, int]        = (0, 0)
        self.player_start:    tuple[int, int]        = (TILE * 5, TILE * 5)
        self._generate()
        if max_generators is not None:
            self.generator_tiles = self.generator_tiles[:max_generators]

    # ── Generation ───────────────────────────────────────────────────────────

    def _generate(self):
        NUM_ROOMS = 20
        ROOM_MIN  = 6
        ROOM_MAX  = 15
        PADDING   = 2

        attempts = 0
        while len(self.rooms) < NUM_ROOMS and attempts < 800:
            attempts += 1
            rw = random.randint(ROOM_MIN, ROOM_MAX)
            rh = random.randint(ROOM_MIN, ROOM_MAX)
            rx = random.randint(1, self.width  - rw - 1)
            ry = random.randint(1, self.height - rh - 1)
            candidate = Room(rx, ry, rw, rh)

            padded = pygame.Rect(rx - PADDING, ry - PADDING,
                                 rw + PADDING * 2, rh + PADDING * 2)
            if any(padded.colliderect(r.rect) for r in self.rooms):
                continue

            self._carve_room(candidate)

            if self.rooms:
                nearest = min(self.rooms,
                              key=lambda r: _dist(r.center, candidate.center))
                self._carve_corridor(nearest.center, candidate.center)

            self.rooms.append(candidate)

        # Player starts at centre of first room
        cx, cy = self.rooms[0].center
        self.player_start = (cx * TILE + TILE // 2 - (TILE - 4) // 2,
                             cy * TILE + TILE // 2 - (TILE - 4) // 2)

        # ── Room generators ───────────────────────────────────────────────────
        # Skip the first two rooms (safe start zone).
        # Each eligible room gets 1–3 generators of a single randomly chosen
        # monster type, placed at non-overlapping positions within the room.
        gen_positions: set[tuple[int, int]] = set()
        mtypes = ['grunt', 'ghost', 'demon']

        for room in self.rooms[2:]:
            count = random.choices(ROOM_GEN_COUNTS, ROOM_GEN_WEIGHTS)[0]
            mtype = random.choices(mtypes, weights=[5, 3, 2])[0]
            placed = 0
            attempts = 0
            while placed < count and attempts < 40:
                attempts += 1
                cx, cy = room.center
                gx = cx + random.randint(-2, 2)
                gy = cy + random.randint(-2, 2)
                gx = max(room.x + 1, min(room.x + room.w - 2, gx))
                gy = max(room.y + 1, min(room.y + room.h - 2, gy))
                if (gx, gy) not in gen_positions:
                    self.generator_tiles.append((gx, gy, mtype))
                    gen_positions.add((gx, gy))
                    placed += 1

        # ── Corridor generators ───────────────────────────────────────────────
        # Identify floor tiles that belong to corridors (not inside any room).
        room_tile_set: set[tuple[int, int]] = set()
        for room in self.rooms:
            for ry in range(room.y, room.y + room.h):
                for rx in range(room.x, room.x + room.w):
                    room_tile_set.add((rx, ry))

        corridor_floors = [
            (tx, ty)
            for ty in range(self.height)
            for tx in range(self.width)
            if self.tiles[ty][tx] == FLOOR and (tx, ty) not in room_tile_set
        ]
        random.shuffle(corridor_floors)
        for tx, ty in corridor_floors:
            if random.random() < CORRIDOR_GEN_CHANCE and (tx, ty) not in gen_positions:
                mtype = random.choices(mtypes, weights=[5, 3, 2])[0]
                self.generator_tiles.append((tx, ty, mtype))
                gen_positions.add((tx, ty))

        # ── Exit portal ───────────────────────────────────────────────────────
        # Farthest room from the player start whose centre is at least 2 tiles
        # (Manhattan) from every generator tile.
        start_centre = self.rooms[0].center
        sorted_rooms = sorted(self.rooms[1:],
                              key=lambda r: _dist(r.center, start_centre),
                              reverse=True)
        gen_coords = [(g[0], g[1]) for g in self.generator_tiles]
        for room in sorted_rooms:
            ec = room.center
            if all(_dist(ec, g) >= 2 for g in gen_coords):
                self.exit_tile = ec
                break
        else:
            self.exit_tile = sorted_rooms[0].center

    def _carve_room(self, room: Room):
        for ty in range(room.y, room.y + room.h):
            for tx in range(room.x, room.x + room.w):
                self._set(tx, ty, FLOOR)

    def _carve_corridor(self, a: tuple, b: tuple):
        ax, ay = a
        bx, by = b
        if random.random() < 0.5:
            self._hcorridor(ay, ax, bx)
            self._vcorridor(bx, ay, by)
        else:
            self._vcorridor(ax, ay, by)
            self._hcorridor(by, ax, bx)

    def _hcorridor(self, y, x1, x2):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for dy in range(-1, 2):   # 3 tiles wide
                self._set(x, y + dy, FLOOR)

    def _vcorridor(self, x, y1, y2):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            for dx in range(-1, 2):   # 3 tiles wide
                self._set(x + dx, y, FLOOR)

    def _set(self, tx, ty, val):
        if 0 <= tx < self.width and 0 <= ty < self.height:
            self.tiles[ty][tx] = val

    # ── Queries ──────────────────────────────────────────────────────────────

    def is_wall(self, tx: int, ty: int) -> bool:
        if tx < 0 or ty < 0 or tx >= self.width or ty >= self.height:
            return True
        return self.tiles[ty][tx] == WALL

    # ── Drawing ──────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera):
        ox, oy = camera.offset
        sw, sh = surface.get_size()
        tx0 = max(0, ox // TILE)
        ty0 = max(0, oy // TILE)
        tx1 = min(self.width,  (ox + sw) // TILE + 2)
        ty1 = min(self.height, (oy + sh) // TILE + 2)

        for ty in range(ty0, ty1):
            for tx in range(tx0, tx1):
                sx = tx * TILE - ox
                sy = ty * TILE - oy

                if self.tiles[ty][tx] == WALL:
                    pygame.draw.rect(surface, WALL_BASE, (sx, sy, TILE, TILE))
                    # Bevelled highlight / shadow edges
                    pygame.draw.line(surface, WALL_EDGE,   (sx,        sy),        (sx+TILE-1, sy))
                    pygame.draw.line(surface, WALL_EDGE,   (sx,        sy),        (sx,        sy+TILE-1))
                    pygame.draw.line(surface, WALL_SHADOW, (sx+TILE-1, sy+1),      (sx+TILE-1, sy+TILE-1))
                    pygame.draw.line(surface, WALL_SHADOW, (sx+1,      sy+TILE-1), (sx+TILE-1, sy+TILE-1))
                else:
                    pygame.draw.rect(surface, FLOOR_BASE, (sx, sy, TILE, TILE))
                    # Subtle corner dots for texture
                    pygame.draw.rect(surface, FLOOR_DOT, (sx + 2,      sy + 2,      2, 2))
                    pygame.draw.rect(surface, FLOOR_DOT, (sx + TILE-4, sy + TILE-4, 2, 2))


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
