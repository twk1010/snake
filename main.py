import os
import pygame
from settings import load_settings
from menu import StartMenu
from game import Game

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 10

if __name__ == "__main__":
    pygame.init()
    settings = load_settings(os.path.join(os.getcwd(), "settings.yaml"))
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    menu = StartMenu(screen, settings, (WINDOW_WIDTH, WINDOW_HEIGHT))
    chosen_fps = menu.run()
    if chosen_fps is None:
        pygame.quit()
    else:
        settings["fps"] = chosen_fps
        game = Game(screen, settings, (WINDOW_WIDTH, WINDOW_HEIGHT), CELL_SIZE)
        game.run()