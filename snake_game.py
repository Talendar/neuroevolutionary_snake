""" Handles the main game loop.

@author Gabriel Nogueira (Talendar)
"""

from game_logic_handler import *
from game_screen import GameScreen
from pygame.time import Clock
import pygame
import config


class SnakeGame:
    """ Implements the main game loop. """

    def __init__(self, player, handler=None):
        self._player = player
        self._logic_handler = GameLogicHandler() if handler is None else handler
        self._screen = GameScreen()
        self._screen.draw(self._logic_handler.board, 0, 1, config.FPS, " -", True, Action.LEFT)

    def start(self, gen=" -", bonus_points=False):
        alive = True
        clock = Clock()
        turn = 1

        self._screen.draw(self._logic_handler.board, self._player.score, turn, config.FPS, gen, alive, Action.LEFT, start_msg=True)
        ask_start = True
        while ask_start:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    ask_start = False
                    break
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

        last_food_dist = self._logic_handler.abs_food_dist()
        while alive:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            move = self._player.act(handler=self._logic_handler, user_events=events)
            state = self._logic_handler.update(move)
            alive = (state != GameLogicHandler.State.DEAD)

            if state == GameLogicHandler.State.FOOD_EATEN:
                self._player.score += config.FOOD_SCORE

            # bonus points
            if bonus_points:
                new_food_dist = self._logic_handler.abs_food_dist()
                self._player.score += config.FARTHER_FROM_FOOD_SCORE if new_food_dist >= last_food_dist else config.CLOSER_TO_FOOD_SCORE
                last_food_dist = new_food_dist

            # draw
            self._screen.draw(self._logic_handler.board, self._player.score, turn, config.FPS, gen, alive, move)
            clock.tick(config.FPS)
            turn += 1

            if not alive:
                print(move)
                for b in self._logic_handler.board:
                    print(b)
