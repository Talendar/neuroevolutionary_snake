""" This program uses a genetic algorithm to create an AI capable of playing the Snake Game.

@author Gabriel Nogueira (Talendar)
"""

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

import pygame
from menus import MainMenu
import config


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption('SnakeAI by Talendar')
    MainMenu(config.MENU_HEIGHT, config.MENU_WIDTH, 'SnakeAI by Talendar')
    pygame.quit()
    quit()
