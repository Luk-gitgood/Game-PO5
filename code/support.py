from csv import reader
import pygame
from settings import *
from os import walk

def import_csv_layout(path):
    """
    Importeert een CSV-bestand (meestal geëxporteerd vanuit Tiled) en zet dit om naar een Python list.

    Deze lijst fungeert als een matrix (grid) waarin elk getal een specifiek tile-type 
    of sprite-ID vertegenwoordigt op een specifieke locatie in het level.

    Args:
        path (str/Path): Het pad naar het .csv-bestand.

    Returns:
        list: een geneste lijst (matrix) van strings die het level-ontwerp bevatten.
    """
    terrain_map = []
    with open(path, mode='r') as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map


def import_folder(path):
    """
    Laadt automatisch alle afbeeldingen uit een specifieke map in als Pygame Surfaces.

    Dit is ideaal voor animaties waarbij de frames als losse bestanden zijn opgeslagen. 
    De functie sorteert de bestanden op naam, zodat animaties in de juiste volgorde worden geladen.

    Args:
        path (str/Path): Het pad naar de map met afbeeldingen.

    Returns:
        list: Een lijst met pygame.Surface objecten (inclusief convert_alpha voor performance).
    """
    surface_list = []

    # walk(path) kijkt in de map en geeft de mapnaam, submappen en bestandsnamen terug
    for _, _, img_files in walk(path):
        # Sorteren is cruciaal voor animatievolgorde (bijv. frame_01, frame_02)
        for image in sorted(img_files):

            # only load real png files, so that accidentally adding wrong files to png folders doesn mess up the folder importing
            if not image.endswith(".png") or image.startswith("._"):
                continue

            full_path = str(path) + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list