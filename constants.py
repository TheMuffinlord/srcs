from equipment import Engine, Weapon_Minigun, Weapon_Laser

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

SELECTION_RADIUS = 50
SELECTION_DECAY_TIMER = 5

DAMAGE_ALERT_LIFESPAN = 1
DAMAGE_ALERT_WIDTH = 80
DAMAGE_ALERT_HEIGHT = 40

HIT_COOLDOWN = 0.25

PLAYER_RADIUS = 25
PLAYER_HEALTH = 1500

PLAYER_DETECTION_RANGE = 500 

ENEMY_RADIUS = 10
ENEMY_MAX_HEALTH = 10
ENEMY_MOVE_SPEED = 300
ENEMY_TURN_SPEED = 200
ENEMY_DETECTION_RANGE = 300
ENEMY_DAMAGE_VALUE = 25

SPAWN_COOLDOWN = 0.5
SPAWNER_MULTIPLIER = 500



DEFAULT_PLAYERLIST = [
    {
        "number": 1,
        "name": "john character",
        "equipment" : {
            "engine": Engine(1),
            "weapons": [
                Weapon_Minigun(1),
                Weapon_Laser(1),
            ]
        }
    },
    {
        "number": 2,
        "name": "jane character",
        "equipment": {
            "engine": Engine(2),
            "weapons": [
                Weapon_Minigun(2),
            ]
        }
    },
    {
        "number": 3,
        "name": "steve thirdguy",
        "equipment": {
            "engine": Engine(1),
            "weapons": [
                Weapon_Laser(1),
            ]
        }
    }
]