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

# ── Player upgrades ───────────────────────────────────────────────────────────
MAX_UPGRADE_LEVEL   = 5
ATTR_DEFENCE_REDUX  = 0.08   # damage reduction fraction per defence level
ATTR_RANGE_BONUS    = 100    # extra px of shot range per level
ATTR_MAX_SHOTS_BASE = 3      # shots allowed on screen at upgrade level 0
ATTR_DAMAGE_BASE    = 1      # shot damage at upgrade level 0
ATTR_DAMAGE_BONUS   = 1      # extra damage per upgrade level

# Cost in coins to buy each upgrade level (index 0 = buying level 1, etc.)
UPGRADE_COST_DEFENCE   = [20, 35,  55,  80, 110]
UPGRADE_COST_RANGE     = [15, 25,  40,  60,  85]
UPGRADE_COST_MAX_SHOTS = [25, 40,  60,  85, 120]
UPGRADE_COST_DAMAGE    = [20, 35,  55,  80, 110]

# ── Difficulty ────────────────────────────────────────────────────────────────
DIFFICULTY_PRESETS = {
    'easy':   dict(label='EASY',   hp_mult=0.6, dmg_mult=0.6, spawn_mult=1.5, gen_count=6),
    'normal': dict(label='NORMAL', hp_mult=1.0, dmg_mult=1.0, spawn_mult=1.0, gen_count=9),
    'hard':   dict(label='HARD',   hp_mult=1.5, dmg_mult=1.5, spawn_mult=0.7, gen_count=12),
}
LEVEL_HP_SCALE    = 0.15   # monster HP multiplier added per level
LEVEL_DMG_SCALE   = 0.10   # monster damage multiplier added per level
LEVEL_SPAWN_SCALE = 0.05   # spawn_mult reduced per level (faster spawns)
LEVEL_GEN_SCALE   = 1      # extra generators added per level
