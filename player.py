""" Defines an interface for an object representing a player and implements the HumanPlayer class.

@author Gabriel Nogueira (Talendar)
"""

from abc import ABC, abstractmethod
from game_logic_handler import Action
import pygame


class Player(ABC):
    """ Abstract class that represents a player (human or not) of the game. """

    @abstractmethod
    def act(self, handler, user_events):
        """ Returns the action taken by the player. """
        pass


class HumanPlayer(Player):
    """ Defines a human player. """

    def __init__(self):
        """ """
        self._current_action = Action.LEFT
        self.score = 0

    def act(self, handler=None, user_events=None):
        """ Returns the action taken by the human player. """
        events = user_events if user_events is not None else pygame.event.get()
        new_action = self._current_action
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self._current_action != Action.RIGHT:
                    new_action = Action.LEFT
                elif event.key == pygame.K_RIGHT and self._current_action != Action.LEFT:
                    new_action = Action.RIGHT
                elif event.key == pygame.K_UP and self._current_action != Action.DOWN:
                    new_action = Action.UP
                elif event.key == pygame.K_DOWN and self._current_action != Action.UP:
                    new_action = Action.DOWN

        self._current_action = new_action
        return new_action
