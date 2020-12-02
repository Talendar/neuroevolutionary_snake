""" Handles the game's logic.

@author Gabriel Nogueira (Talendar)
"""

from random import Random
from enum import Enum
from math import atan2, degrees
import config


class GameLogicHandler:
    """ Handles the game's logic. Designed to be independent of the implementation of the game's graphics. """

    def __init__(self, food_list=None):
        self._snake_pos, self._board = self._new_board()
        self._food_list = food_list.copy() if food_list is not None else []

        self._random = Random()
        self._food_pos = None
        self._new_food()
        self._increasing_snake = False
        self._random = Random()

    class State(Enum):
        """ Possible states for the GameLogicHandler. """
        DEAD, NO_FOOD, FOOD_EATEN = 0, 1, 2

    @property
    def board(self):
        """ Returns a copy of the matrix that represents the game board. """
        return self._board.copy()

    @property
    def snake_pos(self):
        """ Returns a list containing the position of each of the snake's body parts (starting with the head). """
        return self._snake_pos.copy()

    @property
    def food_pos(self):
        """ Returns the current position of the food. """
        return self._food_pos

    def rel_food_dist(self):
        """ Calculates the relative distance between the snake and the food.

        :return: a tuple containing, respectively, the vertical and the horizontal distance between the snake's head and
        the food.
        """
        i0, j0 = self._snake_pos[0]
        i1, j1 = self._food_pos
        return i0 - i1, j0 - j1

    def abs_food_dist(self):
        """ Calculates the absolute total distance between the snake and the food. """
        d = self.rel_food_dist()
        return abs(d[0]) + abs(d[1])

    def angle_to_food(self):
        """ Approximation of the angle between the snake's head and the food (in degrees). """
        x0, y0 = self._snake_pos[0][1] - config.BOARD_SIZE[1]/2, self._snake_pos[0][0] - config.BOARD_SIZE[0]/2
        x1, y1 = self._food_pos[1] - config.BOARD_SIZE[1]/2, self._food_pos[0] - config.BOARD_SIZE[0]/2
        return -degrees(atan2( (y1 - y0), (x1 - x0) ))

    def board_area(self, radius):
        """ Returns an area of the board. """
        ci, cj = self._snake_pos[0]
        area = []

        for i in range(ci - radius, ci + radius + 1):
            area.append([])
            for j in range(cj - radius, cj + radius + 1):
                try:
                    area[-1].append(self._board[i][j])
                except IndexError:
                    area[-1].append(config.VOID)

        # assertion start - todo: delete
        count = 0
        for r in area:
            count += len(r)
        assert count == (2*radius + 1)**2
        # assertion end
        return area

    def _new_food(self):
        if len(self._food_list) == 0:
            pref_free_slots = []
            other_free_slots = []
            for r in range(len(self._board)):
                for c in range(len(self._board[r])):
                    if self._board[r][c] == config.EMPTY:
                        d = abs(self._snake_pos[0][0] - r) + abs(self._snake_pos[0][1] - c)
                        if d >= config.FOOD_SPAWN_MIN_DIST:
                            pref_free_slots.append((r, c))
                        else:
                            other_free_slots.append((r, c))

            slots = pref_free_slots if len(pref_free_slots) > 0 else other_free_slots
            if len(slots) == 0:
                self._food_pos = None
                raise AssertionError("NO FREE SLOT AVAILABLE FOR PLACING THE NEW FOOD!")

            self._food_list.append(self._random.choice(slots))

        i, j = self._food_list.pop(0)
        if self._board[i][j] == config.SNAKE_HEAD or self._board[i][j] == config.SNAKE_BODY or self._board[i][j] == config.WALL:
            self._new_food()
        else:
            self._food_pos = i, j
            self._board[i][j] = config.FOOD

    def new_head_pos(self, action):
        """ Calculates the new position to be taken by the snake. """
        if action == Action.UP:
            return self._snake_pos[0][0] - 1, self._snake_pos[0][1]

        if action == Action.DOWN:
            return self._snake_pos[0][0] + 1, self._snake_pos[0][1]

        if action == Action.LEFT:
            return self._snake_pos[0][0], self._snake_pos[0][1] - 1

        return self._snake_pos[0][0], self._snake_pos[0][1] + 1

    def _move_snake(self, pos):
        """ Moves the snake. """
        self._board[self._snake_pos[0][0]][self._snake_pos[0][1]] = config.SNAKE_BODY
        self._board[pos[0]][pos[1]] = config.SNAKE_HEAD

        new_tail = None
        if self._increasing_snake:
            new_tail = self._snake_pos[-1]
            self._increasing_snake = False
        else:
            self._board[self._snake_pos[-1][0]][self._snake_pos[-1][1]] = config.EMPTY

        for i in range(len(self._snake_pos) - 1, 0, -1):
            self._snake_pos[i] = self._snake_pos[i - 1]

        self._snake_pos[0] = pos
        if new_tail is not None:
            self._snake_pos.append(new_tail)

    def update(self, action):
        i, j = self.new_head_pos(action)
        if self._board[i][j] == config.WALL or self._board[i][j] == config.SNAKE_BODY:
            return self.State.DEAD  # game over

        food = (self._board[i][j] == config.FOOD)
        self._move_snake((i, j))

        if food:
            self._new_food()
            self._increasing_snake = True
            return self.State.FOOD_EATEN

        return self.State.NO_FOOD

    @staticmethod
    def _new_board():
        b = [[config.WALL] * config.BOARD_SIZE[0]]
        for i in range(config.BOARD_SIZE[1] - 2):
            b.append([config.WALL] + [config.EMPTY] * (config.BOARD_SIZE[0] - 2) + [config.WALL])
        b.append([config.WALL] * config.BOARD_SIZE[0])

        i, j = int(config.BOARD_SIZE[1] / 2), int(config.BOARD_SIZE[0] / 2)
        snake_pos = [(i, j)]
        b[i][j] = config.SNAKE_HEAD
        for count in range(1, config.INITIAL_SNAKE_SIZE):
            b[i][j + count] = config.SNAKE_BODY
            snake_pos.append((i, j + count))

        return snake_pos, b


class Action(Enum):
    """ Actions that can be taken by the snake. """
    UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

    @staticmethod
    def opposite(action):
        """ Returns the action related to a movement in the opposite direction. """
        if action == action.UP: return action.DOWN
        if action == action.DOWN: return action.UP
        if action == action.LEFT: return action.RIGHT
        return action.LEFT

