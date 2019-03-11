# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from random import *
from math import *
import sys
from game_ import *
import threading
from threading import Timer
from msvcrt import getch


def make_image(path):
    img = PhotoImage(file=path)
    single_images.append(img)
    return img


def shot_function():
    if player_gun.get_shot_status():
        Shot(shooter=player, canvas=canvas, master=master, game_window=game_window,
             bullet_image_right=[PROIETTILE_GIALLO_RIGHT_IMAGE], bullet_image_left=[PROIETTILE_GIALLO_LEFT_IMAGE],
             bullet_width=PROIETTILE_GIALLO_WIDTH, bullet_height=PROIETTILE_GIALLO_HEIGTH,
             surplus_for_destroy_bullet=50, bullet_movement=15, bullet_update_speed=30).shot()
        player_gun.reload()


class KeyboardListner:

    def __init__(self, game_window, master, canvas, player):
        self.game_window = game_window
        self.master = master
        self.player = player
        self.canvas = canvas
        self.ARROW_UP = "Up"
        self.ARROW_LEFT = "Left"
        self.ARROW_RIGHT = "Right"
        self.ARROW_DOWN = "Down"
        self.SPACE = "space"
        self.ASTERISCO = "asterisk"
        self.KEY_V = "v"
        self.ESC = "Escape"
        self.key_list = None

    def key_listner(self, event):
        key = event.keysym
        if key not in self.key_list:
            self.key_list.append(key)

    def key_organizator(self):

        self.key_list = self.game_window.key_list()
        if len(self.key_list) > -1:

            combo = [
                {self.ARROW_UP},
                {self.ARROW_LEFT},
                {self.ARROW_RIGHT},
                {self.ARROW_LEFT, self.ARROW_RIGHT},
                {self.ARROW_DOWN},
                {self.ARROW_UP, self.ARROW_RIGHT},
                {self.ARROW_UP, self.ARROW_LEFT},
                {self.ARROW_UP, self.KEY_V},
                {self.SPACE},
                {self.ARROW_UP, self.SPACE},
                {self.ARROW_LEFT, self.SPACE},
                {self.ARROW_RIGHT, self.SPACE},
                {self.ARROW_DOWN, self.SPACE},
                {self.ARROW_LEFT, self.SPACE, self.ARROW_UP},
                {self.ARROW_RIGHT, self.SPACE, self.ARROW_UP},
                {self.ESC},
            ]

            if set(self.key_list) in combo:
                pass
            else:
                for key in key_list:
                    if {key} in combo:
                        key_list.clear()
                        key_list.append(key)

            if set(self.key_list) in combo:

                if self.player.get_jump_status():
                    if self.ARROW_UP in self.key_list:
                        self.player.jump_off()
                        self.player.move_up(gravity=20, jump=13, jump_speed=0.03)
                        self.key_list.remove(self.ARROW_UP)
                        if self.SPACE in self.key_list:
                            shot_function()

                if self.ARROW_LEFT in self.key_list:

                    self.player.facing_left()  # no lag
                    self.player.update_player_image()  # no lag
                    self.player.move_left()
                    game_window.scroll_backgrounds()
                    game_window.check_biome()
                    scroll_screen_left(to_who=self.player, canvas=self.canvas, game_window=self.game_window)  # lag
                    if self.SPACE in self.key_list:
                        shot_function()

                elif self.ARROW_RIGHT in self.key_list:

                    self.player.facing_right()  # no lag
                    self.player.update_player_image()  # no lag
                    self.player.move_right()
                    game_window.scroll_backgrounds()
                    game_window.check_biome()
                    scroll_screen_right(to_who=self.player, canvas=self.canvas, game_window=self.game_window)  # lag
                    if self.SPACE in self.key_list:
                        shot_function()

                elif self.ARROW_DOWN in self.key_list and len(self.key_list) == 1:
                    self.player.move_down()
                    if self.SPACE in self.key_list:
                        shot_function()

                elif self.ARROW_UP in self.key_list and self.KEY_V in self.key_list:
                    self.master.quit()

                elif self.SPACE in self.key_list and len(self.key_list) == 1:
                    shot_function()

                elif self.ESC in self.key_list and len(self.key_list) == 1:
                    pass
            self.master.after(40, lambda: self.key_organizator())

    def clear_key(self, event):
        event = event.keysym
        if event in self.key_list:
            self.key_list.remove(event)

positions_dict = dict()
key_list = []
single_images = []

master = Tk()
monitor_width = master.winfo_screenwidth()
monitor_height = master.winfo_screenheight()
start_screen_width = 700
start_screen_height = 700
canvas = Canvas(master, width=start_screen_width, height=start_screen_height, bg="black")

BACKGROUND_1_LAYER_PATH = "assets/background/Hills Layer 01.png"
BACKGROUND_4_LAYER_PATH = "assets/background/notte.png"
BACKGROUND_5_LAYER_PATH = "assets/background/alberi.png"


BACKGROUND_2_LAYER_PATH = "assets/background/montagne.png"
BACKGROUND_3_LAYER_PATH = "assets/background/città.png"

cespugli = "assets/background/cespugli.png"

game_window = Window(master=master, canvas=canvas, key_list=key_list, total_height=monitor_height * 2,
                     total_width=monitor_width * 4,
                     start_screen_width=700, start_screen_height=700,
                     biome_desert="desert",
                     desert_biome_path=BACKGROUND_1_LAYER_PATH,
                     biome_night="night",
                     night_biome_path=BACKGROUND_4_LAYER_PATH,
                     biome_mountain="mountain",
                     mountain_biome_path=BACKGROUND_2_LAYER_PATH,
                     biome_alberi="città",
                     alberi_biome_path=BACKGROUND_3_LAYER_PATH)

game_window.devide_biomes()
game_window.update_backgrounds_path("assets/background/")
game_window.create_backgrounds()

x = (monitor_width / 2) - (game_window.get_game_screen_width() // 2)
y = (monitor_height / 2) - (game_window.get_game_screen_width() // 2)
master.geometry('%dx%d+%d+%d' % (game_window.get_game_screen_width() + 4, game_window.get_game_screen_heigth() + 4, x, y))
master.title("My game")

canvas.configure(scrollregion=(0, 0, game_window.get_game_width(), game_window.get_game_height()), yscrollincrement='1', xscrollincrement='1')
canvas.grid(row=0)

CHARACTER_X_MOVEMENT = 5
GAME_X_MOVEMENT = CHARACTER_X_MOVEMENT
CHARACTER_Y_MOVEMENT = 1
GAME_Y_MOVEMENT = CHARACTER_Y_MOVEMENT

TERRAIN_TOTAL_LENGHT = game_window.get_game_width()
TERRAIN_MOVEMENT_SPEED = 5
TERRAIN_SLICE_MIN_LENGHT = 30
TERRAIN_SLICE_MAX_LENGHT = 40
START_X_TERRAIN = 0
START_Y_TERRAIN = game_window.get_game_height()//2
TERRAIN_DISLIVELLO = GAME_X_MOVEMENT
TERRAIN_WIDTH = TERRAIN_DISLIVELLO

MOVE_RIGHT_GIF_LENGHT = 13
MOVE_RIGHT_GIF_PATH = "assets/character/Skeleton Walk.gif"
MOVE_LEFT_GIF_LENGHT = 13
MOVE_LEFT_GIF_PATH = "assets/character/Skeleton Walk Left.gif"

PROIETTILE_BLU_RIGHT_PATH = "assets/bullets/proiettili_blu_right.png"
PROIETTILE_BLU_RIGHT_IMAGE = make_image(PROIETTILE_BLU_RIGHT_PATH)
PROIETTILE_BLU_LEFT_PATH = "assets/bullets/proiettili_blu_left.png"
PROIETTILE_BLU_LEFT_IMAGE = make_image(PROIETTILE_BLU_LEFT_PATH)
PROIETTILE_BLU_WIDTH = 20
PROIETTILE_BLU_HEIGTH = 12

PROIETTILE_GIALLO_RIGHT_PATH = "assets/bullets/proiettili_giallo_right.png"
PROIETTILE_GIALLO_RIGHT_IMAGE = make_image(PROIETTILE_GIALLO_RIGHT_PATH)
PROIETTILE_GIALLO_LEFT_PATH = "assets/bullets/proiettili_giallo_left.png"
PROIETTILE_GIALLO_LEFT_IMAGE = make_image(PROIETTILE_GIALLO_LEFT_PATH)
PROIETTILE_GIALLO_WIDTH = 20
PROIETTILE_GIALLO_HEIGTH = 12


# BACKGROUNDS  ----------------------------
layer1_x = game_window.get_game_width()/2 - monitor_width/2
layer1_y = game_window.get_game_height()/2 - monitor_height/2 - 50

layer1_background = Background(master=master, canvas=canvas,
                               game_window=game_window,
                               left_upper_x=layer1_x, left_upper_y=layer1_y)
layer1_background.create()

layer2_background = Background(master=master, canvas=canvas,
                               game_window=game_window,
                               left_upper_x=layer1_x - game_window.get_full_screen_width(), left_upper_y=layer1_y)
layer2_background.create()

layer3_background = Background(master=master, canvas=canvas,
                               game_window=game_window,
                               left_upper_x=layer1_x + game_window.get_full_screen_width(), left_upper_y=layer1_y)
layer3_background.create()

layer4_background = Background(master=master, canvas=canvas,
                               game_window=game_window,
                               left_upper_x=layer1_x, left_upper_y=layer1_y)
layer4_background.create()

a = create_image(cespugli, game_window.get_full_screen_width(), game_window.get_full_screen_height())
img = a
layer4_background.change_image(a)

game_window.update_backgrounds(background_1=layer1_background,
                               background_2=layer2_background,
                               background_3=layer3_background,)

# TERRAIN MAKER  ----------------------------
terrain = Terrain(canvas=canvas, game_window=game_window, positions_dict=positions_dict)
terrain.make_terrain(previous_x=START_X_TERRAIN, previouse_y=START_Y_TERRAIN, terrain_dislevel=TERRAIN_DISLIVELLO,
                     terrain_width=TERRAIN_WIDTH, line_min_lenght=15, line_max_lenght=30)

# ENTITY GRAPHICS  ----------------------------
skeleton_move_right_frames = [PhotoImage(file=MOVE_RIGHT_GIF_PATH, format='gif -index %i' % i) for i in
                              range(MOVE_RIGHT_GIF_LENGHT)]  # character move right
skeleton_move_left_frames = [PhotoImage(file=MOVE_LEFT_GIF_PATH, format='gif -index %i' % i) for i in
                             range(MOVE_LEFT_GIF_LENGHT)]  # character move left

# ENTITY CREATION  ----------------------------

A = Entity(master=master, canvas=canvas, positions_dict=positions_dict,
           tags=("enemy", "paolo"), width=20, height=16,
           player_image_right=[PROIETTILE_GIALLO_RIGHT_IMAGE], player_image_left=[PROIETTILE_BLU_LEFT_IMAGE], facing="left",
           x_pos=game_window.get_game_width()//2 + 50, y_pos=game_window.get_game_height()//2 - 50,
           x_speed=CHARACTER_X_MOVEMENT, y_speed=CHARACTER_Y_MOVEMENT)  # character
A.create()

player = Entity(master=master, canvas=canvas, positions_dict=positions_dict,
                tags="character", width=22, height=34,
                player_image_right=skeleton_move_right_frames, player_image_left=skeleton_move_left_frames, facing="left",
                x_pos=game_window.get_game_width()//2, y_pos=game_window.get_game_height()//2,
                x_speed=CHARACTER_X_MOVEMENT, y_speed=CHARACTER_Y_MOVEMENT)  # character
player.create()
player.gravity_active()
player_gun = ShotStatus(master, reload_time=250)
game_window.update_player(player)

game_window.check_biome()  # change the background image to the current biome image

# keyboard listner  -----------------------
input_listner = KeyboardListner(game_window=game_window, master=master, canvas=canvas, player=player)
input_listner.key_organizator()

# BINDING EVENTS  ------------------------------
canvas.bind("<Button-3>", lambda event, canvas=canvas, master=master: make_circle(event, canvas, master))
canvas.bind("<ButtonPress-1>", lambda event, canvas=canvas: scroll_start(event, canvas))
canvas.bind("<B1-Motion>", lambda event, canvas=canvas: scroll_move(event, canvas))
master.bind("<KeyRelease>", input_listner.clear_key)
master.bind("<KeyPress>", input_listner.key_listner)
master.bind("<Configure>", lambda event, canvas=canvas, game_window=game_window, center_element=player, master=master: resize_window(event, canvas, master, game_window, center_element))

master.mainloop()

