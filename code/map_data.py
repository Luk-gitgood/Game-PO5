"""this file is not used anywhere right now, but could be usefull for dynamically changing music in a map or loading more maps"""


MAP_DATA = {
    "boss_room": {
        "path": "1/boss_room",
        "prefix": "finalroom",
        "tileset": "castle_single_tiles",
        "music": "Insolitum_music1.ogg",
        "enemies": [
            {"type": "flying", "pos": (500, 1400)},
            {"type": "flying", "pos": (1000, 1450)},
            {"type": "flying", "pos": (2200, 1100)},
        ],
       
    },
    "level_2": {
        "path": "1/level_2",
        "prefix": "level_2",
        "tileset": "castle_single_tiles",  
        "music": "Insolitum_music1.ogg",   
        "enemies": [
            {"type": "flying", "pos": (500, 800)},
            {"type": "flying", "pos": (1000, 850)},
        ]   
    
    }
}


SPAWN_POINTS = {
    "boss_room": {
        "left":  (200, 1400),
        "right": (2900, 1400), 
    },
    "level_2": {
        "left":  (200, 800),
        "right": (3000, 700), 
    }
}