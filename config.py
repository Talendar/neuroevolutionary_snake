""" Configuration file.

@author Gabriel Nogueira (Talendar)
"""


############### MENUS ####################
MENU_WIDTH, MENU_HEIGHT = 600, 800       #
##########################################


############# GAME LOGIC #################
FPS = 40                                 #
BOARD_SIZE = 60, 42                      # if you change the board size, make sure to change the screen size accordingly
INITIAL_SNAKE_SIZE = 3                   #
FOOD_SPAWN_MIN_DIST = 25                 #
FOOD_SCORE = 100                         #
                                         #
# BOARD ENTITIES                         #
FOOD = 2                                 #
EMPTY = 1                                #
SNAKE_HEAD = 0                           #
SNAKE_BODY = -1                          #
WALL = -2                                #
VOID = -3                                #
##########################################


############## GAME SCREEN ###############
SCREEN_SIZE = 1230, 991                  #
CELL_SIZE = 20                           #
                                         #
TOP_PADDING = 136                        #
RIGHT_PADDING = 15                       #
PRINT_ACTION = True                      #
                                         #
# colors                                 #
BACKGROUND_COLOR = (0, 0, 0)             #
COLOR_MAP = {                            #
    WALL: (255, 255, 255),               #
    SNAKE_HEAD: (0, 255, 0),             #
    SNAKE_BODY: (0, 180, 0),             #
    FOOD: (255, 0, 0),                   #
}                                        #
                                         #
DEAD_SNAKE_HEAD_COLOR = (47, 90, 83)     #
DEAD_SNAKE_BODY_COLOR = (94, 170, 157)   #
##########################################


############### EVOLUTION ##################
MAX_TURNS = 100000                         # maximum number of turns the AI can play during each generation of training
PLAYS_PER_GEN = 5                          # should be different than 1 only when USE_FOOD_LIST is set to False
USE_FOOD_LIST = False                      #
                                           #
LIFE_SAVING = True                         # if true, the AI will, when possible, avoid taking an action that will make it lose the game
LIFE_SAVING_PENALTY = -5                   # penalty on the score when the life saving feature is used by the AI
LIFE_SAVING_COOLDOWN = 0                   # cooldown for the life saving feature
MAX_NO_FOOD_TURNS = 200                    # max number of turns the AI can survive without eating
                                           #
MIN_MUTATION_RATE = 0.01                   # minimum mutation rate for the genetic algorithm
MAX_MUTATION_RATE = 0.5                    # maximum mutation rate for the genetic algorithm
                                           #
WEIGHTS_MULT_FACTOR = 1                    # factor that multiplies the weights of a newly created neural network
BRAIN_FORMAT = [32]                        # number of hidden layers and neurons in each hidden layer
                                           #
RANDOM_KILL_PC = 0.1                       # predatism percentage
MASS_EXTINCTION_THRESHOLD = 40             # max number of turns allowed without improvements in the score
                                           #
CLOSER_TO_FOOD_SCORE = 1                   # score gained when the snake moves towards the food
FARTHER_FROM_FOOD_SCORE = -1               # score lost when the snake moves away from the food
                                           #
SIGHT_RADIUS = 3                           # number of tiles/cells around the snake's head the AI will take into account
NUM_CELLS = (2*SIGHT_RADIUS + 1)**2        #
NUM_FEATURES = NUM_CELLS + 3               #
                                           #
BASE_OUT_DIR = "./evolution/populations/"  #
############################################

FOOD_POS_LIST = [    # optional
    (10, 1),
    (30, 9),
    (9, 35),
    (2, 6),
    (28, 26),
    (6, 35),
    (28, 2),
    (11, 35),
    (31, 11),
    (8, 9),
    (17, 34),
    (4, 21),
    (29, 15),
    (5, 36),
    (23, 29),
    (11, 45),
    (32, 19),
    (16, 8),
    (12, 45),
    (26, 18),
    (3, 29),
    (25, 8),
    (8, 29),
    (26, 1),
    (19, 45),
    (24, 12),
    (25, 36),
    (17, 5),
    (4, 20),
    (29, 1),
    (33, 48),
    (1, 1),
    (3, 48),
    (15, 24),
    (32, 2),
    (33, 46),
    (6, 6),
    (15, 48),
    (20, 1),
    (32, 45),
    (1, 4),
    (17, 45),
    (24, 1),
    (20, 37),
    (29, 10),
    (14, 36),
    (31, 4),
    (28, 36),
    (20, 13),
    (1, 25),
    (18, 5),
    (25, 41),
    (1, 35),
    (2, 7),
    (26, 30),
    (3, 27),
    (24, 4),
    (20, 26),
    (1, 15),
    (33, 5),
    (3, 27),
    (33, 18),
    (12, 46),
    (28, 9),
    (17, 33),
    (4, 16),
    (24, 46),
    (1, 30),
    (28, 33),
    (33, 10),
]