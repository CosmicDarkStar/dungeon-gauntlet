# settings.py — all constants for Dungeon Gauntlet

# ── Display ──────────────────────────────────────────────────────────────────
TILE = 32
FPS  = 60

# ── Map ───────────────────────────────────────────────────────────────────────
MAP_W = 100   # tiles
MAP_H = 80

# ── Palette (retro 8-bit) ─────────────────────────────────────────────────────
BLACK        = (  0,   0,   0)
DARK_BG      = ( 10,   8,  20)

WALL_BASE    = ( 28,  18,  52)
WALL_EDGE    = ( 75,  55, 120)
WALL_SHADOW  = ( 14,   9,  26)

FLOOR_BASE   = ( 16,  12,  30)
FLOOR_DOT    = ( 30,  22,  48)

# entities
COL_PLAYER   = ( 80, 220, 120)   # green
COL_SHOT_P   = (255, 255,  80)   # yellow

COL_GRUNT    = (220,  50,  50)   # red
COL_GHOST    = ( 80, 210, 210)   # cyan
COL_DEMON    = (210, 110,  20)   # orange
COL_SHOT_D   = (255,  80,  80)   # red

COL_GENERATOR = (170,   0, 200)  # purple
COL_GEN_DEAD  = ( 55,  45,  65)
COL_GEN_EDGE  = (255, 160, 255)

# HUD
COL_HUD_BG   = ( 12,   8,  24)
COL_HP_HI    = ( 60, 220,  80)
COL_HP_MID   = (220, 200,  40)
COL_HP_LO    = (220,  50,  50)
COL_SCORE    = (220, 180,  80)
COL_INFO     = (140, 120, 175)

# ── Gameplay ──────────────────────────────────────────────────────────────────
PLAYER_MAX_HP    = 100
PLAYER_SPEED     = 180    # px / s
HP_DRAIN_RATE    = 1.5    # hp / s (starvation)
SHOOT_COOLDOWN   = 0.22   # s between shots
SHOT_SPEED       = 520    # px / s
SHOT_RANGE       = 440    # px
SHOT_DAMAGE      = 1      # damage per bolt

GRUNT_HP    = 3
GHOST_HP    = 2
DEMON_HP    = 6
GRUNT_SPEED = 75     # px / s
GHOST_SPEED = 58
DEMON_SPEED = 105
GRUNT_DMG   = 8      # hp / s on contact
GHOST_DMG   = 5
DEMON_DMG   = 12
DEMON_SHOT_DMG = 10

GENERATOR_HP         = 12
GENERATOR_SPAWN_TIME = 5.0   # s between spawns
MAX_MONSTERS         = 80    # hard cap

# ── Drops ─────────────────────────────────────────────────────────────────────
HEALTH_DROP_CHANCE = 0.30    # probability a killed monster drops health
HEALTH_DROP_MIN    = 10      # HP restored
HEALTH_DROP_MAX    = 20
COIN_DROP_MIN      = 5       # coins dropped by a destroyed generator
COIN_DROP_MAX      = 15
DROP_PICKUP_RADIUS = 22      # px from player centre to collect

COL_HEALTH_DROP = ( 60, 220,  80)   # bright green
COL_COIN_DROP   = (255, 200,  30)   # gold
