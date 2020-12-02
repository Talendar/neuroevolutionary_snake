""" Implements the game's menus.

@author Gabriel Nogueira (Talendar)
"""

import pygame
import pygame_menu

import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory

import config
from snake_game import SnakeGame
from player import HumanPlayer
from evolution.snake_ai import SnakePopulation
from evolution.evolution_visualizer import EvolutionVisualizer
import neural_network.neural_network as nn


class MainMenu:
    def __init__(self, height, width, title, theme=pygame_menu.themes.THEME_BLUE):
        self._width = width
        self._height = height
        self._theme = theme

        self._screen = pygame.display.set_mode((width, height))
        self._menu = pygame_menu.Menu(height, width, title, theme=theme)

        self._menu.add_button('Play', self._play_game)
        self._menu.add_button('Evolve', self._evolve)
        self._menu.add_button('Visualize', self._visualize)
        self._menu.add_button('Settings', self._settings)

        self._menu.add_vertical_margin(40)
        self._menu.add_button('Quit', pygame_menu.events.EXIT)
        self._menu.mainloop(self._screen)

    def _play_game(self):
        SnakeGame(HumanPlayer()).start()
        pygame.display.set_mode((self._width, self._height))

    def _evolve(self):
        EvolutionMenu(self._height, self._width, theme=self._theme)
        pygame.display.set_mode((self._width, self._height))

    def _visualize(self):
        VisualizationMenu(self._height, self._width, theme=self._theme)
        pygame.display.set_mode((self._width, self._height))

    def _settings(self):
        SettingsMenu(self._height, self._width, theme=self._theme)
        pygame.display.set_mode((self._width, self._height))


class EvolutionMenu:
    def __init__(self, height, width, title="Evolution Config", theme=pygame_menu.themes.THEME_BLUE):
        self._width, self._height = width, height
        self._screen = pygame.display.set_mode((width, height))
        self._menu = pygame_menu.Menu(height, width, title, theme=theme)

        self._ev_button = self._menu.add_button("Evolve!", self._evolve)
        self._menu.add_vertical_margin(40)

        self._base_model_path = ""
        self._fs_button = self._menu.add_button("Base model: none", None)
        self._fs_button.update_callback(self._select_file)

        self._pop_size = 20
        self._menu.add_text_input('Pop. size: ', default=self._pop_size, input_type=pygame_menu.locals.INPUT_INT, onchange=self._update_pop_size)

        self._gens = 25
        self._menu.add_text_input('Generations: ', default=self._gens, input_type=pygame_menu.locals.INPUT_INT, onchange=self._update_gen_count)

        self._menu.add_vertical_margin(40)
        self._menu.add_button("Back", self._menu.disable)
        self._menu.add_vertical_margin(40)
        self._menu.add_label("(check config.py for more settings)", font_size=20)
        self._menu.mainloop(self._screen)

    def _select_file(self):
        root = tk.Tk()
        self._base_model_path = askopenfilename(initialdir="./evolution/pre_trained_models")
        root.destroy()
        if len(self._base_model_path) > 0:
            self._fs_button.set_title("Base model: [...]" + self._base_model_path[-12:])

    def _update_gen_count(self, count):
        self._gens = count

    def _update_pop_size(self, count):
        self._pop_size = count

    def _evolve(self):
        pop = SnakePopulation(size=self._pop_size,
                              pre_trained_brain=(
                                    None if self._fs_button.get_title() == "Base model: none"
                                    else nn.NeuralNetwork.load(self._base_model_path)))

        self._screen = pygame.display.set_mode((380, 90))
        self._screen.fill((0, 0, 0))
        self._screen.blit(pygame.font.SysFont("monospace", 24, bold=True).render("Evolving...", False, (255, 247, 0)), (10, 20))
        self._screen.blit(pygame.font.SysFont("monospace", 16).render("(check real time logging on stdout)", False, (255, 247, 0)), (8, 55))
        pygame.display.update()
        pop.evolve(self._gens)
        pygame.display.set_mode((self._width, self._height))


class VisualizationMenu:
    def __init__(self, height, width, title="Visualize", theme=pygame_menu.themes.THEME_BLUE):
        self._width, self._height = width, height
        self._screen = pygame.display.set_mode((width, height))
        self._menu = pygame_menu.Menu(height, width, title, theme=theme)

        self._vis_button = self._menu.add_button("Visualize!", self._visualize)
        self._menu.add_vertical_margin(40)

        self._pop = None
        self._pop_dir = ""
        self._fs_button = self._menu.add_button("Pop. directory:  -", None)
        self._fs_button.update_callback(self._select_dir)

        self._gen = 20
        self._gen_txt_widget = self._menu.add_text_input('Generation: ', default=self._gen, onchange=self._update_gen,
                                                         input_type=pygame_menu.locals.INPUT_INT)

        self._menu.add_vertical_margin(40)
        self._menu.add_button("Back", self._menu.disable)
        self._menu.mainloop(self._screen)

    def _select_dir(self):
        root = tk.Tk()
        self._pop_dir = askdirectory(initialdir="./evolution/populations")
        root.destroy()
        if self._pop_dir is not None and len(self._pop_dir) > 0:
            self._pop_dir += "/"
            self._pop = EvolutionVisualizer(self._pop_dir, False)
            self._fs_button.set_title("Pop. directory: [...]" + self._pop_dir[-15:])
            self._gen_txt_widget.set_value(self._pop.best_gen)
            self._update_gen(self._pop.best_gen)

    def _update_gen(self, gen):
        self._gen = gen

    def _visualize(self):
        self._pop.start(self._gen)
        pygame.display.set_mode((self._width, self._height))


class SettingsMenu:
    def __init__(self, height, width, title="Settings", theme=pygame_menu.themes.THEME_BLUE):
        self._width, self._height = width, height
        self._screen = pygame.display.set_mode((width, height))
        self._menu = pygame_menu.Menu(height, width, title, theme=theme)

        def update_fps(f): config.FPS = f
        self._menu.add_text_input('FPS: ', default=config.FPS, input_type=pygame_menu.locals.INPUT_INT, onchange=update_fps)

        self._menu.add_vertical_margin(40)
        def update_head(c): config.COLOR_MAP[config.SNAKE_HEAD] = c
        self._menu.add_color_input('Head color: ', color_type='rgb', default=config.COLOR_MAP[config.SNAKE_HEAD],
                                   onchange=update_head, font_size=20)

        def update_body(c): config.COLOR_MAP[config.SNAKE_BODY] = c
        self._menu.add_color_input('Body color: ', color_type='rgb', default=config.COLOR_MAP[config.SNAKE_BODY],
                                   onchange=update_body, font_size=20)

        self._menu.add_vertical_margin(40)
        def update_dead_head(c): config.DEAD_SNAKE_HEAD_COLOR = c
        self._menu.add_color_input('Dead head color: ', color_type='rgb', default=config.DEAD_SNAKE_HEAD_COLOR,
                                   onchange=update_dead_head, font_size=20)

        def update_dead_body(c): config.DEAD_SNAKE_BODY_COLOR = c
        self._menu.add_color_input('Dead head color: ', color_type='rgb', default=config.DEAD_SNAKE_BODY_COLOR,
                                   onchange=update_dead_body, font_size=20)

        self._menu.add_vertical_margin(40)
        self._menu.add_button("Back", self._menu.disable)
        self._menu.add_vertical_margin(40)
        self._menu.add_label("(check config.py for more settings)", font_size=20)
        self._menu.mainloop(self._screen)
