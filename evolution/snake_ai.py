""" Implements the AI player and the genetic algorithm.

@author Gabriel Nogueira (Talendar)
"""

from game_logic_handler import *
from player import Player
from neural_network.neural_network import NeuralNetwork
import config

from pathlib import Path
from datetime import datetime
import numpy as np
import random
import multiprocessing


class SnakeAI(Player):
    """ Implementation of the AI player, controlled by a neural network. """

    def __init__(self, brain, life_saving=config.LIFE_SAVING):
        self.brain = brain
        self._life_saving = life_saving
        self._life_saving_cooldown = 0
        self.score = 0
        self.last_action = Action.LEFT

    def act(self, handler, user_events=None):
        features = mount_features(handler)
        h = self.brain.predict(features)

        h = sorted(zip(h, range(len(h))), key=lambda pair: pair[0], reverse=True)
        index = h[0][1]

        self._life_saving_cooldown -= 1
        if self._life_saving and self._life_saving_cooldown <= 0:
            for p in h:
                index = p[1]
                i, j = handler.new_head_pos(list(Action)[index])
                if handler.board[i][j] == config.EMPTY or handler.board[i][j] == config.FOOD:
                    break
                self._life_saving_cooldown = config.LIFE_SAVING_COOLDOWN

            if self._life_saving_cooldown == config.LIFE_SAVING_COOLDOWN:
                self.score += config.LIFE_SAVING_PENALTY

        new_action = list(Action)[index]
        if new_action != Action.opposite(self.last_action):
            self.last_action = new_action

        return self.last_action

    def save_brain(self, out_pathname):
        """ Saves the snake's neural network to disk. """
        self.brain.save(out_pathname)


class SnakePopulation:
    """ Represents a population of AI players.

    Implements the genetic algorithm used to optimize the population's individuals.
    """

    def __init__(self, size=None, in_dir=None, pre_trained_brain=None):
        if size is None and in_dir is None:
            raise AssertionError("Missing size argument or in_dir argument!")
        elif size is not None and in_dir is not None:
            raise AssertionError("Invalid size argument! When in_dir isn't None, the size is retrieved from a file.")

        self._snakes = []
        self._pop_fitness_history = []
        self._best_fitness_history = []
        self._mass_extinction_counter = 0

        # LOADING MODELS
        if in_dir is not None:
            raise NotImplemented()  # todo: load population from directory

        # CREATING NEW MODELS
        else:
            self._out_dir = config.BASE_OUT_DIR + "pop_" + f"{datetime.now():%y_%m_%d_%H_%M_%S}" + "/"
            Path(self._out_dir + "best_models/").mkdir(parents=True)
            self._size = size
            self._new_population()

            if pre_trained_brain is not None:
                self._snakes[0].brain = pre_trained_brain

    @property
    def size(self):
        """ Returns the size of the population. """
        return self._size

    def _new_population(self):
        """ Creates a new population. """
        self._snakes = []
        for i in range(self._size):
            self._snakes.append(SnakeAI(create_brain()))

    @staticmethod
    def _play_process(snake):
        """ Simulates the playing of the game with the given AI. """
        for _ in range(config.PLAYS_PER_GEN):
            game_handler = GameLogicHandler(food_list=config.FOOD_POS_LIST if config.USE_FOOD_LIST else None)
            turn = last_food_turn = 0

            last_state = None
            last_food_dist = game_handler.abs_food_dist()

            while last_state != GameLogicHandler.State.DEAD and \
                    turn < config.MAX_TURNS and (turn - last_food_turn) < config.MAX_NO_FOOD_TURNS:

                move = snake.act(game_handler)
                last_state = game_handler.update(move)
                new_food_dist = game_handler.abs_food_dist()

                if last_state == GameLogicHandler.State.FOOD_EATEN:
                    snake.score += config.FOOD_SCORE
                    last_food_turn = turn
                else:
                    snake.score += config.FARTHER_FROM_FOOD_SCORE if new_food_dist >= last_food_dist else config.CLOSER_TO_FOOD_SCORE

                last_food_dist = new_food_dist
                turn += 1

        snake.score /= config.PLAYS_PER_GEN  # getting the average score
        return snake

    def _play(self):
        """ Make each AI player play the game until it loses or the turn limit is exceeded. """
        # resetting snakes
        for snake in self._snakes:
            snake.score = 0
            snake.last_action = Action.LEFT

        # playing
        proc_pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        results = proc_pool.map(self._play_process, self._snakes)

        # waiting for all processes to finish
        proc_pool.close()
        proc_pool.join()
        self._snakes = results

        # sorting
        self._snakes.sort(key=lambda s: s.score, reverse=True)

    def evolve(self, num_generations):
        self._mass_extinction_counter = 0
        best_score = best_score_ever = 0
        best_score_gen = best_score_ever_gen = 0

        for gen in range(num_generations):
            print(
                "\n\n< GENERATION %d/%d\n" % (gen+1, num_generations) +
                "    Playing... ", end=""
            )

            self._play()
            print("done! Best score: %d" % self._snakes[0].score)
            self._snakes[0].save_brain(self._out_dir + "best_models/gen_%d" % gen)

            total_score = 0
            for s in self._snakes:
                total_score += s.score

            self._pop_fitness_history.append(total_score)
            self._best_fitness_history.append(self._snakes[0].score)

            if self._snakes[0].score > best_score:
                best_score = self._snakes[0].score
                best_score_gen = gen
                self._mass_extinction_counter = 0

                if self._snakes[0].score > best_score_ever:
                    best_score_ever = self._snakes[0].score
                    best_score_ever_gen = gen
            else:
                self._mass_extinction_counter += 1

            print(
                "    Total population score: %d\n" % total_score +
                "    Mean population score: %.2f\n" % (total_score / len(self._snakes)) +
                "    Individuals scores: " + str([s.score for s in self._snakes]) + "\n" +
                "    Mutation rate: %.2f%%" % (100*self._mutation_rate()) + "\n" +
                "    Best score ever: %d (gen %d)\n" % (best_score_ever, best_score_ever_gen) +
                "    Cycle's best score: %d (gen %d)\n" % (best_score, best_score_gen) +
                "    Mass extinction counter: %d/%d" % (self._mass_extinction_counter, config.MASS_EXTINCTION_THRESHOLD)
            )

            # mass extinction
            if self._mass_extinction_counter >= config.MASS_EXTINCTION_THRESHOLD:
                print("    MASS EXTINCTION IN PROGRESS... ", end="")
                self._mass_extinction()
                self._mass_extinction_counter = 0
                best_score = 0

            # reproduction
            else:
                print("    Reproducing best individuals... ", end="")
                self._reward_based_reproduction()
                print("done!")

                kill_count = int(len(self._snakes) * config.RANDOM_KILL_PC)
                print("    Predating %d individuals..." % kill_count, end="")

                for i in range(kill_count):
                    self._random_death()

            print("done!\n/>")

        # writing info
        with open(self._out_dir + "info.txt", "w") as info:
            info.write(
                "SIZE %d\n" % self._size +
                "GENERATIONS %d\n" % num_generations +
                "BOARD_SIZE %d %d\n" % config.BOARD_SIZE +
                "SIGHT_RADIUS %d\n" % config.SIGHT_RADIUS +
                "MAX_TURNS %d\n" % config.MAX_TURNS +
                "MUTATION_RATE %.2f %.2f\n" % (config.MIN_MUTATION_RATE, config.MAX_MUTATION_RATE) +
                "BRAIN_FORMAT: " + str(config.BRAIN_FORMAT) + "\n" +
                "RANDOM_KILL_PC %.2f\n" % config.RANDOM_KILL_PC +
                "BEST_SCORE_EVER %d\n" % best_score_ever +
                "BEST_SCORE_EVER_GEN %d" % best_score_ever_gen
            )

        # saving food list
        with open(self._out_dir + "base_food_list.txt", "w") as file:
            to_write = ""
            for f in config.FOOD_POS_LIST:
                to_write += "%d %d\n" % f
            file.write(to_write[:-1])

        print("\nEvolution finished. Population's info, history and final results saved to: \"%s\"" % self._out_dir)

    def _mutation_rate(self):
        """ Calculates the mutation rate.

        The mutation rate is higher when the population hasn't been improving its fitness much in the past few
        generations and lower when the population has been improving.
        """
        rate = (1/config.MASS_EXTINCTION_THRESHOLD) * (1 + self._mass_extinction_counter) * config.MAX_MUTATION_RATE
        return max(rate, config.MIN_MUTATION_RATE)

    def _reward_based_reproduction(self):
        """ Reproduction method: reward-based selection. """
        assert len(self._snakes) >= 10

        p = [0.3, 0.25, 0.2, 0.15, 0.1] + [0] * (len(self._snakes) - 5)
        new_snakes = [self._snakes[0]]  # always keeps the best snake

        for _ in range(len(self._snakes) - 1):
            chosen = self._snakes[np.random.choice(len(self._snakes), p=p)]
            new_snakes.append(
                SnakeAI(
                    create_brain(mutate_weights(chosen.brain.get_weights(), self._mutation_rate()))
                )
            )

        self._snakes = new_snakes

    def _elitist_reproduction(self):
        """ Reproduction method: elitism. """
        best = self._snakes[0]
        new_snakes = [best]  # always keeps the best snake

        mut_rate = self._mutation_rate()
        for s in self._snakes[1:]:
            new_weights = mate_weights(best.brain.get_weights(), s.brain.get_weights(), mut_rate)
            new_snakes.append(SnakeAI(create_brain(new_weights)))

        self._snakes = new_snakes

    def _random_death(self):
        """ Randomly kills one of the population's individuals, replacing it with a randomly generated one.

        The best individual won't be considered for removal. It must be located at the index 0 of "self._snakes".
        """
        i = np.random.randint(1, len(self._snakes))
        del self._snakes[i]
        self._snakes.append(SnakeAI(create_brain()))

    def _mass_extinction(self):
        """ Kills all the individuals of the current population (except for the best one) and generates new ones. """
        self._snakes = [self._snakes[0]]
        for i in range(self._size):
            self._snakes.append(SnakeAI(create_brain()))


def create_brain(weights=None):
    new_brain = NeuralNetwork(
        layers_size=[config.NUM_FEATURES] + config.BRAIN_FORMAT + [4],
        layers_activation="relu",
        weights_multiplier=config.WEIGHTS_MULT_FACTOR
    )
    new_brain.layers[-1].activation = "sigmoid"

    if weights is not None:
        new_brain.set_weights(weights)

    return new_brain


def mutate_weights(weights, rate, method="replace"):
    """ Returns a mutated copy of the given set of weights.

    :param weights: the weights of a neural network.
    :param rate: the mutation rate.
    :param method:
    :return: a mutated copy of the set of weights.
    """
    # NUDGE
    if method == "nudge":
        mul = [np.random.uniform(low=(1-rate), high=(1+rate), size=w.shape) for w in weights]
        return [a * b for a, b in zip(weights, mul)]

    # REPLACE
    elif method == "replace":
        for w in weights:
            for i in range(len(w)):
                for j in range(len(w[i])):
                    if random.random() < rate:
                        w[i][j] = np.random.uniform(low=-1, high=1) * config.WEIGHTS_MULT_FACTOR
        return weights

    raise ValueError("Mutation method \"%s\" doesn't exist!" % method)


def mate_weights(weights1, weights2, mutation_rate):
    """ Sums each weight of one set with the corresponding weight of the other set. The result is divided by 2 and the
    mutation rate is applied.

    :param weights1: the first set of weights.
    :param weights2: the second set of weights.
    :param mutation_rate: the mutation rate.
    :return: the resultant set of weights.
    """
    n = [(w1 + w2)/2 for w1, w2 in zip(weights1, weights2)]
    return mutate_weights(n, mutation_rate)


def mount_features(game_handler):
    food_dist = game_handler.rel_food_dist()
    features = np.concatenate([
            np.array([
                    game_handler.angle_to_food(),
                    food_dist[0],
                    food_dist[1],
                ]
            ),
            np.hstack(game_handler.board_area(config.SIGHT_RADIUS))
        ]
    )

    return features
