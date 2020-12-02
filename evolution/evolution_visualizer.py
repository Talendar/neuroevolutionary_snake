""" Handles the visualization of AI players.

@author Gabriel Nogueira (Talendar)
"""

from game_logic_handler import *
from snake_game import SnakeGame
from evolution.snake_ai import SnakeAI
from neural_network.neural_network import NeuralNetwork


class EvolutionVisualizer:
    """ Simulates a game with an AI player of a population. """

    def __init__(self, pop_dir, use_food_list=True):
        self._models_dir = pop_dir + "best_models/"
        self._food_list = []

        if use_food_list:
            with open(pop_dir + "base_food_list.txt", "r") as file:
                items = file.read().split("\n")
                for i in items:
                    s = i.split(" ")
                    self._food_list.append(( int(s[0]), int(s[1]) ))

        with open(pop_dir + "info.txt", "r") as file:
            lines = file.readlines()
            size = tuple([int(i) for i in lines[2].split() if i.isdigit()])
            config.BOARD_SIZE = size
            self.best_gen = int(lines[9].split()[1])

    def start(self, gen):
        snake = SnakeAI(brain=NeuralNetwork.load(self._models_dir + "gen_%d" % gen))
        game = SnakeGame(snake, handler=GameLogicHandler(food_list=self._food_list))
        game.start(gen=gen+1, bonus_points=True)