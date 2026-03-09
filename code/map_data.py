"""this file is not used anywhere right now, 
but could be usefull for dynamically changing music in a map or loading more maps"""


MAP_DATA = {
    "boss_room": {
        "path": "1/boss_room",
        "prefix": "finalroom",
        "tileset": "castle_single_tiles",
        "music": "Insolitum_music1.ogg",
        
       
    },
    "level_2": {
        "path": "1/level_2",
        "prefix": "level_2",
        "tileset": "inferno_single_tiles",  
        "music": "Insolitum_music1.ogg",   
       
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

