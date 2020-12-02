""" Handles the drawing on the game screen.

@author Gabriel Nogueira (Talendar)
"""

from game_logic_handler import *
import pygame
import config


class GameScreen:
    """ Handles the drawing on the game screen. """

    def __init__(self, size=config.SCREEN_SIZE):
        self._size = size
        self._display = pygame.display.set_mode(size)
        self._FONT = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        self._arrows_imgs = [(
                pygame.transform.scale(pygame.image.load("./imgs/arrow_%s_inactive.png" % s), (52, 52)),
                pygame.transform.scale(pygame.image.load("./imgs/arrow_%s_active.png" % s), (52, 52)),
            ) for s in ["up", "down", "left", "right"]]

    def draw(self, board, score, turn, fps, gen, alive, action, start_msg=False):
        """ Draws the game on the screen. """
        self._display.fill(config.BACKGROUND_COLOR)
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] != config.EMPTY:
                    x = j * config.CELL_SIZE + config.RIGHT_PADDING
                    y = i * config.CELL_SIZE + config.TOP_PADDING

                    if alive or board[i][j] == config.WALL or board[i][j] == config.FOOD:
                        color = config.COLOR_MAP[board[i][j]]
                    else:
                        color = config.DEAD_SNAKE_BODY_COLOR if board[i][j] == config.SNAKE_BODY else config.DEAD_SNAKE_HEAD_COLOR

                    pygame.draw.rect(self._display, color, [x, y, config.CELL_SIZE, config.CELL_SIZE])

        # upper bar
        pygame.draw.rect(self._display, (50, 50, 50), [config.RIGHT_PADDING, 10, config.SCREEN_SIZE[0] - 2*config.RIGHT_PADDING, 115])

        txt_surface = self._FONT.render("TURNO: %d" % turn, False, (255, 247, 0))
        self._display.blit(txt_surface, (190, 40))

        txt_surface = self._FONT.render("GERACAO: " + str(gen), False, (255, 247, 0))
        self._display.blit(txt_surface, (190, 85))

        txt_surface = self._FONT.render("FPS: %d" % fps, False, (255, 247, 0))
        self._display.blit(txt_surface, (550, 40))

        txt_surface = self._FONT.render("SCORE: %d" % score, False, (255, 247, 0))
        self._display.blit(txt_surface, (550, 85))

        # right action bar
        self._display.blit(self._arrows_imgs[0][1 if action == Action.UP else 0], (930, 13))
        self._display.blit(self._arrows_imgs[1][1 if action == Action.DOWN else 0], (930, 69))
        self._display.blit(self._arrows_imgs[2][1 if action == Action.LEFT else 0], (876, 69))
        self._display.blit(self._arrows_imgs[3][1 if action == Action.RIGHT else 0], (984, 69))

        # "press space" msg
        if start_msg:
            txt_surface = self._FONT.render("Press SPACE to start.", False, (255, 255, 255))
            self._display.blit(txt_surface, (530, 450))

        pygame.display.update()