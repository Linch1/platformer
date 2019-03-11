# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from random import *
from math import *
import sys
import os.path
from os import listdir
import threading
from threading import Timer
import time


class Window:

    def __init__(self, canvas, master, key_list, total_height=0, total_width=0,
                 start_screen_width=0, start_screen_height=0,
                 entyties_movement=3,
                 **kwargs):

        self.canvas = canvas
        self.master = master

        self.game_screen_width = start_screen_width
        self.game_screen_height = start_screen_height

        self.full_screen_width = self.master.winfo_screenwidth()
        self.full_screen_height = self.master.winfo_screenheight()

        self.biomes_num = randint(4, 4)
        self.biomes = []
        self.biomes_width = 0
        self.biomes_paths = []
        self.biomes_raw_images = []
        self.images_binder = []
        self.biomes_order = []
        self.backgrounds_objects = []
        self.biomes_and_images_dict = dict()
        self.changing_background_images_dict = dict()  # biomes(pastBiome_newBiome):[images list(img1, img2, ...)]
        self.current_biome = None
        self.past_biome = None

        self.game_width = total_width
        self.game_height = total_height

        self.entyties_movement = entyties_movement
        self._key_list = key_list

        self.player = None

        for key, value in kwargs.items():
            if key.startswith("biome_"):  # i take the args of the type biome_(biome_name)="biome" and insert them into a list
                self.biomes.append(value)
            if key.endswith("_path"):  # i take the args of the type (bioma_name)_path="path" and insert them into another list
                self.biomes_paths.append(value)

        for path in self.biomes_paths:
            image = resize_image(self.full_screen_width, self.full_screen_height, path)  # i take all the path of thr biomes and resize them (it returns an image)
            print(image.mode)
            if image.mode != 'RGBA':
                new_image = image.convert('RGBA')
                new_image.save(path, 'PNG')
            image = resize_image(self.full_screen_width, self.full_screen_height, path)
            self.biomes_raw_images.append(image)  # i put all the resized images in a list

        for index in range(len(self.biomes)):
            biome = self.biomes[index]
            biome_image = self.biomes_raw_images[index]
            self.biomes_and_images_dict[biome] = [biome_image, index]  # i create a dictionary where i associate at each (biome_name):[not_usable_biome_image, biome_index]  (the index is for the self.biomes_order list)
            images_to_use = ImageTk.PhotoImage(biome_image)
            self.images_binder.append(images_to_use)  # i create a list with all the biomes images that can be uset in the canvas
        self.backgrounds_path = None

    def get_game_width(self):
        return self.game_width

    def get_game_height(self):
        return self.game_height

    def get_game_screen_width(self):
        return self.game_screen_width

    def get_game_screen_heigth(self):
        return self.game_screen_height

    def get_full_screen_width(self):
        return self.full_screen_width

    def get_full_screen_height(self):
        return self.full_screen_height

    def get_player(self):
        return self.player

    def get_background(self):
        return self.backgrounds_objects

    def get_backgrounds_path(self):
        return self.backgrounds_path

    def key_list(self):
        return self._key_list

    def update_game_screen_width(self):
        self.game_screen_width = self.canvas.winfo_width()

    def update_game_screen_heigth(self):
        self.game_screen_height = self.canvas.winfo_height()

    def update_player(self, player):
        self.player = player  # update the player object

    def update_backgrounds_path(self, path):
        self.backgrounds_path = path

    def update_backgrounds(self, **kwargs):
        for key, value in kwargs.items():  # watch for extra args of the type background_... = (Background class object)
                if key.startswith("background"):
                    self.backgrounds_objects.append(value)  # append all the background object passed as arg in a list

    def devide_biomes(self):

        self.biomes_width = self.game_width/self.biomes_num

        for _ in range(self.biomes_num):
            index = randint(0, len(self.biomes) - 1)
            biome = self.biomes[index]

            while biome in self.biomes_order:
                index = randint(0, len(self.biomes) - 1)
                biome = self.biomes[index]
            self.biomes_order.append(biome)
        shuffle(self.biomes_order)

        print("Biomes in world:", self.biomes_order)

    def create_backgrounds(self):
        all_possible_changes = all_combinations(self.biomes_order)
        a = time.time()
        for combination in all_possible_changes:
            path = self.backgrounds_path + combination
            if not os.path.exists(path):
                os.makedirs(path)
                biome1, biome2 = combination.split("_")
                image_biome1 = self.biomes_and_images_dict[biome1][0]
                image_biome2 = self.biomes_and_images_dict[biome2][0]
                create_change_gradually_image(img_to_change=image_biome1, new_image=image_biome2, path=path)
        b = time.time()
        print("time 1 :", b-a)
        time.sleep(1)
        for combination in all_possible_changes:
            path = self.backgrounds_path + combination

            #raw_images = [path + "/" + counter for counter in listdir(path)]                         ############################  SPRECA MOLTO TEMPO DI AVVIO FARE IL REDIMENSIONAMENTO DELLE IMMAGIINI
            #for image_path in raw_images:                                                            ############################  OGNI VOLTA ( CIRCA 3 SECONDI )
            #    image = resize_image(self.full_screen_width, self.full_screen_height, image_path)    ############################  can do this just the first time that the user starts
            #    image.save(image_path, 'PNG')                                                        ############################  the game (the resize of the images)

            raw_images = [path + "/" + counter for counter in listdir(path)]
            usable_images = []
            for image_path in raw_images:
                usable_image = PhotoImage(file=image_path)
                usable_images.append(usable_image)
            self.changing_background_images_dict[combination] = usable_images
        c = time.time()
        print("time 2 :", c-b)

    def check_biome(self):
        x = self.player.x()  # get the player x pos
        num_current_biome = int(x//self.biomes_width)  # get the index of the current biome
        current_biome = self.biomes_order[num_current_biome]  # get the name of the current biome

        if self.current_biome is None:  # if is the first cycle
            self.past_biome = current_biome  # the current_biome and the past_biome are initialized with the biome where the player is
            self.current_biome = current_biome
            image = self.biomes_and_images_dict[current_biome][0]
            image = ImageTk.PhotoImage(image)  # get the image of the current biome from a list with all the images of the biomes in the world
            for background_object in self.backgrounds_objects:
                background_object.change_image(image)

        if self.current_biome != current_biome:  # if the current biome and the past biome are different ( the player passed from a biome to another )
            self.past_biome = self.current_biome  # the past biome becomes the previous current biome
            self.current_biome = current_biome  # the current biome becomes the new biome where the player is
            current_biome_index = self.biomes_and_images_dict[current_biome][1]  # get the biome index (relative to the images binder list)
            combination = self.past_biome + "_" + self.current_biome
            images_list = self.changing_background_images_dict[combination]
            for background_object in self.backgrounds_objects:
                background_object.change_gradually_image(images_list)

    def scroll_backgrounds(self):
        if self.player.get_facing() == "right":
            for background in self.backgrounds_objects:
                background.scroll_right(self.player)
        elif self.player.get_facing() == "left":
            for background in self.backgrounds_objects:
                background.scroll_left(self.player)


class Background:

    def __init__(self, master=None, canvas=None, game_window=None,
                left_upper_x=0, left_upper_y=0):
        self.master = master
        self.canvas = canvas
        self.game_window = game_window
        self.monitor_width = master.winfo_screenwidth()
        self.monitor_height = master.winfo_screenheight()
        self.left_upper_x = left_upper_x
        self.left_upper_y = left_upper_y

        self.background_image = None
        self.background = None

    def create(self):
        self.background = self.canvas.create_image(self.left_upper_x, self.left_upper_y, tag='background', anchor=NW)

    def scroll_right(self, object):
        object_speed = object.x_speed()
        scroll_speed = object_speed/3
        x1, y1 = self.canvas.coords(self.background)
        for i in range(int(scroll_speed)):
            self.canvas.coords(self.background, x1 + 1, y1)

    def scroll_left(self, object):
        object_speed = object.x_speed()
        scroll_speed = object_speed/3
        x1, y1 = self.canvas.coords(self.background)
        for i in range(int(scroll_speed)):
            self.canvas.coords(self.background, x1 - 1, y1)

    def fill_width(self):
        num_images = self.game_window.get_game_width()//self.image_width
        print(num_images)
        print(self.left_upper_y)
        for i in range(num_images):
            self.canvas.create_image(self.left_upper_x + i * self.image_width, self.left_upper_y, image=self.background_image, tag='background', anchor=NW)

    def id(self):
        return self.background

    def image(self):
        return self.background_image

    def change_image(self, new_image):
        self.canvas.itemconfigure(self.id(), image=new_image)
        self.background_image = new_image

    def change_gradually_image(self, images_list, counter=0):
        if counter > len(images_list) - 1:
            return
        else:
            new_image = images_list[counter]
            self.canvas.itemconfigure(self.id(), image=new_image)
            Timer(0.01, lambda: self.change_gradually_image(images_list, counter=counter + 1)).start()


class Entity:
    def __init__(self,
                 master=None, canvas=None, positions_dict=None, tags=(), width=0, height=0,
                 x_pos=0, y_pos=0, player_image_right=None, player_image_left=None, facing="", x_speed=3, y_speed=3):

        self.master = master
        self.canvas = canvas
        self.tags = tags
        self.x_pos = x_pos
        self.y_pos = y_pos
        self._width = width
        self._height = height
        self.base_center = ((x_pos * 2 + width) // 2, y_pos + height)
        self.facing = facing
        self.player_image_right = player_image_right
        self.player_image_left = player_image_left
        self.positions_dict = positions_dict

        self.player_right_index = 0
        self.player_left_index = 0
        self.player_right_end_index = len(self.player_image_right) - 1
        self.player_left_end_index = len(self.player_image_left) - 1
        if self.facing == "right":
            self.player_img = self.player_image_right[self.player_right_index]
            self.player_right_index += 1
        elif self.facing == "left":
            self.player_img = self.player_image_left[self.player_left_index]
            self.player_left_index += 1

        self.entity = None
        self.bullet = None

        self.entity_hit_box = ""
        self._x_speed = x_speed
        self._y_speed = y_speed
        self.jump = True
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.type = 0

    def create(self):
        self.entity = self.canvas.create_image(self.x_pos, self.y_pos, image=self.player_img, anchor=NW, tag=self.tags)
        coords = self.canvas.coords(self.entity)

        if len(coords) == 2:
            self.x1 = coords[0]
            self.y1 = coords[1]
            self.x2 = self.x1 + self._width
            self.y2 = self.y1 + self._height
            self.type = 2

        elif len(coords) == 4:
            self.x1 = coords[0]
            self.y1 = coords[1]
            self.x2 = coords[2]
            self.y2 = coords[3]
            self.type = 4

    def update_player_image(self):
        if self.facing == "right":
            if self.player_right_index > self.player_right_end_index:
                self.player_right_index = 0
            self.player_img = self.player_image_right[self.player_right_index]
            self.player_right_index += 1
        elif self.facing == "left":
            if self.player_left_index > self.player_left_end_index:
                self.player_left_index = 0
            self.player_img = self.player_image_left[self.player_left_index]
            self.player_left_index += 1
        self.canvas.itemconfigure(self.entity, image=self.player_img)

    def id(self):
        return self.entity

    def width(self):
        return self._width

    def height(self):
        return self._height

    def x_speed(self):
        return self._x_speed

    def get_coords(self):
        x1, y1 = self.canvas.coords(self.entity)
        x1 = round(x1)
        y1 = round(y1)
        x2 = x1 + self._width
        y2 = y1 + self._height

        return x1, y1, x2, y2

    def x(self):
        return self.canvas.coords(self.entity)[0]

    def y(self):
        return self.canvas.coords(self.entity)[1]

    def draw_hit_box(self, first=True):
        x1, y1, x2, y2 = self.get_coords()
        if first:
            self.entity_hit_box = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red")  # HIT BOX HERE
        elif not first:
            self.canvas.coords(self.entity_hit_box, x1, y1, x2, y2)  # HIT BOX HERE
        Timer(5/1000, lambda: self.draw_hit_box(first=False)).start()

    def in_hit_box(self, coord_x, coord_y):
        x1, y1, x2, y2 = self.get_coords()
        if (x2 > coord_x > x1) and (y2 > coord_y > y1):
            return True
        else:
            return False

    def facing_left(self):
        self.facing = "left"

    def facing_right(self):
        self.facing = "right"

    def get_facing(self):
        return self.facing

    def is_facing_right(self):
        return self.facing == "right"

    def is_facing_left(self):
        return self.facing == "left"

    def move_right(self):
        # right
        self.x1 += self._x_speed
        self.x2 += self._x_speed
        self.apply_movement(self.x1, self.y1, self.x2, self.y2)
        self.gravity_active()

    def move_down(self):
        # down
        self.y1 += self._y_speed
        self.y2 += self._y_speed
        self.apply_movement(self.x1, self.y1, self.x2, self.y2)
        self.gravity_active()

    def move_left(self):
        # left

        self.x1 -= self._x_speed
        self.x2 -= self._x_speed
        self.apply_movement(self.x1, self.y1, self.x2, self.y2)
        self.gravity_active()

    def move_up(self, time=0.0, gravity=20, jump=10, jump_speed=0.04):
        # up

        centro_base = ((self.x1 + self.x2) // 2, self.y2)
        chiave_dizionario = list(self.positions_dict.keys())[round(centro_base[0])]
        incremento_y = ((1 / 2 * gravity * (time ** 2)) - jump * time)

        if round(self.y2) <= self.positions_dict[chiave_dizionario][1][1][0] or \
                incremento_y <= 0:

            if round(self.y2 + incremento_y) > self.positions_dict[chiave_dizionario][1][1][0]:
                self.jump_on()
                self.gravity_active()
                return

            self.y1 = incremento_y + self.y1
            self.y2 = self.y1 + self._height

            self.apply_movement(self.x1, self.y1, self.x2, self.y2)
            Timer(5/1000, lambda: self.move_up(time=time + jump_speed, gravity=gravity, jump=jump, jump_speed=jump_speed)).start()
        else:
            self.jump_on()
            self.gravity_active()

    def apply_movement(self, x1, y1, x2, y2):
        if self.type == 4:
            self.canvas.coords(self.id(), x1, y1, x2, y2)
        elif self.type == 2:
            self.canvas.coords(self.id(), x1, y1)

    def gravity_active(self):

        if self.get_jump_status():
            centro_base = ((self.x1 + self.x2) // 2, self.y2)
            chiave_dizionario = list(self.positions_dict.keys())[round(centro_base[0])]

            if self.positions_dict[chiave_dizionario][1][1][0] > round(centro_base[1]):
                self.y1 = self.y1 + self._y_speed
                self.y2 = self.y2 + self._y_speed
                self.apply_movement(self.x1, self.y1 + 1, self.x2, self.y2 + 1)
                Timer(2/1000, lambda: self.gravity_active()).start()

            elif self.positions_dict[chiave_dizionario][1][1][0] < round(centro_base[1]):

                self.y2 = self.positions_dict[chiave_dizionario][1][1][0]
                self.y1 = self.y2 - self._height
                self.apply_movement(self.x1, self.y1, self.x2, self.y2)
                Timer(2/1000, lambda: self.gravity_active()).start()

    def jump_off(self):
        self.jump = False

    def jump_on(self):
        self.jump = True

    def get_jump_status(self):
        return self.jump


def gun_bullet():
    if shot.get_shot_status():
        Shot(shooter=player, canvas=canvas, master=master, game_window=game_window,
             bullet_image_right=PROIETTILE_GIALLO_RIGHT_IMAGE, bullet_image_left=PROIETTILE_GIALLO_LEFT_IMAGE,
             bullet_width=PROIETTILE_GIALLO_WIDTH, bullet_height=PROIETTILE_GIALLO_HEIGTH,
             surplus_for_destroy_bullet=50, bullet_movement=15, bullet_update_speed=30).start()
        shot.reload()


class Shot:

    def __init__(self, master, canvas, shooter, game_window, bullet_image_left=[], bullet_image_right=[], bullet_width=10,
                 bullet_height=10, surplus_for_destroy_bullet=50, bullet_movement=15, bullet_update_speed=30):
        self.shooter = shooter
        self.id = shooter.id()
        self.shooter_width = shooter.width()
        self.shooter_height = shooter.height()
        self.bullet_width = bullet_width
        self.bullet_height = bullet_height

        self.bullet_image_right = bullet_image_right
        self.bullet_image_left = bullet_image_left
        self.bullet_right_index = 0
        self.bullet_left_index = 0
        self.bullet_right_end_index = len(self.bullet_image_right) - 1
        self.bullet_left_end_index = len(self.bullet_image_left) - 1
        self.facing = shooter.get_facing()
        if self.facing == "right":
            self.bullet_img = self.bullet_image_right[self.bullet_right_index]
            self.bullet_right_index += 1
        elif self.facing == "left":
            self.bullet_img = self.bullet_image_left[self.bullet_left_index]
            self.bullet_left_index += 1

        self.canvas = canvas
        self.master = master
        self.game_window = game_window
        self.bullet = None
        self.coords = self.canvas.coords(self.id)
        self.surplus_for_destroy_bullet = surplus_for_destroy_bullet
        self.bullet_movement = bullet_movement
        self.bullet_update_speed = bullet_update_speed  # ms

    def update_bullet_image(self):
        if self.facing == "right":
            if self.bullet_right_index > self.bullet_right_end_index:
                self.bullet_right_index = 0
            self.bullet_img = self.bullet_image_right[self.bullet_right_index]
            self.bullet_right_index += 1
        elif self.facing == "left":
            if self.bullet_left_index > self.bullet_left_end_index:
                self.bullet_left_index = 0
            self.bullet_img = self.bullet_image_left[self.bullet_left_index]
            self.bullet_left_index += 1
        self.canvas.itemconfigure(self.bullet, image=self.bullet_img)

    def shot(self):

        if len(self.coords) == 4:
            x1, y1, x2, y2 = coords
        else:
            x1, y1 = self.coords
            x1 = round(x1)
            y1 = round(y1)
            x2 = x1 + self.shooter_width
            y2 = y1 + self.shooter_height
        if self.facing == "right":
            x_media, y_media = x2 - self.bullet_width, ((y1 + y2) / 2)
            y_media = round(y_media)
            bullet_x1 = x_media
            bullet_y1 = y_media
            self.bullet = self.canvas.create_image(bullet_x1, bullet_y1, image=self.bullet_img, anchor=NW, tag="bullet")
            self.move_bullet()
        elif self.facing == "left":
            x_media, y_media = x1, ((y1 + y2) / 2)
            y_media = round(y_media)
            bullet_x1 = x_media
            bullet_y1 = y_media
            self.bullet = self.canvas.create_image(bullet_x1, bullet_y1, image=self.bullet_img, anchor=NW, tag="bullet")
            self.move_bullet()
        else:
            return

    def move_bullet(self):

        try:
            x1, y1 = self.canvas.coords(self.bullet)

            region_start_x = self.canvas.canvasx(0)
            region_end_x = region_start_x + self.game_window.get_game_screen_width()
            region_start_y = self.canvas.canvasy(0)
            region_end_y = region_start_y + self.game_window.get_game_screen_heigth()

            if self.facing == "right":
                if x1 + self.bullet_width >= region_end_x + self.surplus_for_destroy_bullet:
                    self.canvas.delete(self.bullet)
                    return
                x1 += self.bullet_movement
            elif self.facing == "left":
                if x1 <= region_start_x - self.surplus_for_destroy_bullet:
                    self.canvas.delete(self.bullet)
                    return
                x1 -= self.bullet_movement

            self.canvas.coords(self.bullet, x1, y1)
            self.check_who_destroy(x1, y1)
            self.update_bullet_image()
        except Exception:
            return
        else:
            Timer(self.bullet_update_speed/1000, lambda: self.move_bullet()).start()

    def check_who_destroy(self, x1, y1):

        encolsest_elements = self.canvas.find_overlapping(x1, y1, x1 + self.bullet_width, y1 + self.bullet_height)
        encolsest_elements = list(encolsest_elements)
        if self.bullet in encolsest_elements:
            encolsest_elements.remove(self.bullet)
        for elem in encolsest_elements:
            if len(self.canvas.gettags(elem)) > 0:
                if "terrain" in self.canvas.gettags(elem):
                    self.canvas.delete(self.bullet)
                    continue
                elif "rain" in self.canvas.gettags(elem):
                    continue
                elif "rain particells" in self.canvas.gettags(elem):
                    continue
                elif self.canvas.gettags(self.id)[0] in self.canvas.gettags(elem):
                    continue
                elif "background" in self.canvas.gettags(elem):
                    continue

                self.canvas.delete(elem)

class ShotStatus:
    def __init__(self, master, reload_time):
        self.loaded = True
        self.reload_time = reload_time
        self.master = master

    def shot_off(self):
        self.loaded = False

    def shot_on(self):
        self.loaded = True

    def reload(self, first=True):
        self.shot_off()
        if not first:
            self.shot_on()
        else:
            Timer(self.reload_time/1000, lambda: self.reload(False)).start()

    def get_shot_status(self):
        return self.loaded


class Rain:  #  NOT EDITED
    def __init__(self, master):
        self.canvas = canvas
        self.master = master
        self.lenght = randint(10, 20)
        self.rain_speed = randint(5, 30)
        self.particel_speed = randint(5, 50)

    def blob(self):
        x1 = randint(character.get_coords()[0] - game_window.get_game_screen_width()//2, character.get_coords()[0] + game_window.get_game_screen_width()//2)
        y1 = randint(RAIN_START_Y_1, RAIN_START_Y_2)
        colors = ["red", "yellow", "blue", "green", "purple"]
        index = randint(0, len(colors) - 1)
        line = self.canvas.create_line(x1, y1, x1, y1 + self.lenght, fill=colors[index], width=2, tag="rain")
        self.move(line, self.canvas.coords(line))

    def move(self, line, coords):
        try:

            line_x1 = round(coords[0])
            line_y1 = round(coords[1])
            line_x2 = round(coords[2])
            line_y2 = round(coords[3])
            character_x = character.get_coords()[0]
            character_y = character.get_coords()[1]
            chiave_dizionario = list(positions_list.keys())[line_x2]

            if line_y2 >= positions_list[chiave_dizionario][1][1][0] > line_y1 \
                    or character.in_hit_box(line_x2, line_y2) or line_y2 >= game_window.get_game_screen_heigth() - 10:
                for _ in range(1):
                    self.create_particells(coords)
                self.canvas.delete(line)
                self.blob()
            elif line_x2 < character_x - game_window.get_game_screen_width()//2 or line_x2 > character_x + game_window.get_game_screen_width()//2:
                self.canvas.delete(line)
                self.blob()

            elif coords[3] < character_y + game_window.get_game_screen_heigth()//2:
                self.canvas.coords(line, coords[0], coords[1] + RAIN_PARTICELLS_MOVEMENT_Y, coords[2],
                                   coords[3] + RAIN_PARTICELLS_MOVEMENT_Y)
                coords = self.canvas.coords(line)
                Timer(self.rain_speed/1000, lambda: self.move(line, coords)).start()

        except Exception:
            pass


    def create_particells(self, coords):
        x1, y1, x2, y2 = coords
        x1 = x2 + 5
        y1 = y2 + 5
        colors = ["red", "yellow", "blue", "green", "purple"]
        index = randint(0, len(colors) - 1)
        particel = canvas.create_rectangle(x1, y1, x1 - 5, y1 - 5, fill=colors[index], tag="rain particell")
        coords = canvas.coords(particel)
        self.move_particells(particel, coords)

    def move_particells(self, particel, coords, counter=0):
        if counter < 100:
            x1, y1, x2, y2 = coords
            canvas.coords(particel, x1, y1, x1 - 5, y1 - 5)
            coords = canvas.coords(particel)
            counter += 1
            Timer(self.particel_speed/1000, lambda: self.move_particells(particel, coords, counter)).start()
        else:
            canvas.delete(particel)


def rain():
    for _ in range(RAIN_NUM):
        Rain(master).blob()


class Circle:

    def __init__(self, event, canvas, master):
        self.x, self.y = mouse_coords(event.x, event.y - 1, canvas)
        self.master = master
        self.speed = randint(5, 30)
        self.canvas = canvas
        self.counter = 0
        self.width = randint(50, 100)
        print("MOUSE POS:", self.x, self.y)

    def make_oval(self):
        x1, y1 = (self.x - 1), (self.y - 1)
        x2, y2 = (self.x + 1), (self.y + 1)
        colors = ["red", "yellow", "blue", "green", "purple"]
        index = randint(0, len(colors) - 1)
        oval = self.canvas.create_oval(x1, y1, x2, y2, outline=colors[index], width=2)
        self.move_oval(oval, self.canvas.coords(oval), self.counter)

    def move_oval(self, oval, coords, counter):

        if counter < self.width:
            counter += 1
            Timer(self.speed/1000, lambda: self.move_oval(oval, coords, counter)).start()
            expansion = 1
            self.canvas.coords(oval, coords[0] - expansion, coords[1] - expansion, coords[2] + expansion,
                               coords[3] + expansion)
            coords = self.canvas.coords(oval)
        else:
            self.canvas.delete(oval)

class Terrain:

    def __init__(self, canvas, game_window, positions_dict):
        self.stop_move = False
        self.canvas = canvas
        self.game_window = game_window
        self.positions_dict = positions_dict

    def make_terrain(self, previous_x=0, previouse_y=0, terrain_dislevel=3, terrain_width=3,
                     line_min_lenght=15, line_max_lenght=30):
        terrain_level = randint(-terrain_dislevel, terrain_dislevel)
        terrain_lenght = randint(previous_x + line_min_lenght, previous_x + line_max_lenght)
        x1 = previous_x
        y1 = previouse_y
        x2 = terrain_lenght
        y2 = previouse_y + terrain_level
        if y2 > self.game_window.get_game_height():
            y2 = previouse_y
        line = self.canvas.create_line(x1, y1, x2, y2, fill="white", width=terrain_width, tag="terrain")

        y = (((x2 - x1) / (x2 - x1)) * (y2 - y1)) + y1
        y = round(y)
        y = [y]
        for x in range(x1, x2):
            self.positions_dict[(x, 500)] = [line, [x, y]]
        if not (x2 >= self.game_window.get_game_width()):
            self.make_terrain(x2, y2)


lista = []
move_left = 0
move_right = 0
previous_skeletone_move_side_frame = ""
first_move = True

class Keyboard_listner:

    def __init__(self, game_window, master, canvas, player):
        self.game_window = game_window
        self.master = master
        self.player = player
        self.canvas = canvas
        self.ARROW_UP = 38
        self.ARROW_LEFT = 37
        self.ARROW_RIGHT = 39
        self.ARROW_DOWN = 40
        self.SPACE = 32
        self.ASTERISCO = 106
        self.KEY_V = 86
        self.ESC = 27

    def key_listner(self, event):
        key_list = self.game_window.key_list()
        event = event.keycode
        if event not in key_list:
            key_list.append(event)

    def key_organizator(self):
        key_list = self.game_window.key_list()
        if len(key_list) > -1:

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

            if set(key_list) in combo:
                pass
            else:
                for key in key_list:
                    if {key} in combo:
                        key_list.clear()
                        key_list.append(key)

            if set(key_list) in combo:

                if self.player.get_jump_status():
                    if self.ARROW_UP in key_list:
                        self.player.jump_off()
                        self.player.move_up()
                        key_list.remove(self.ARROW_UP)
                        if self.SPACE in key_list:
                            shot_function()

                if self.ARROW_LEFT in key_list:

                    self.player.facing_left()  # no lag
                    self.player.update_player_image()  # no lag
                    self.player.move_left()
                    scroll_screen_left(to_who=self.player, canvas=self.canvas, game_window=self.game_window)  # lag

                    if self.SPACE in key_list:
                        shot_function()

                elif self.ARROW_RIGHT in key_list:

                    self.player.facing_right()  # no lag
                    self.player.update_player_image()  # no lag
                    self.player.move_right()
                    scroll_screen_right(to_who=self.player, canvas=self.canvas, game_window=self.game_window)  # lag

                    if self.SPACE in key_list:
                        shot_function()

                elif self.ARROW_DOWN in key_list and len(key_list) == 1:
                    self.player.move_down()
                    if self.SPACE in key_list:
                        shot_function()

                elif self.ARROW_UP in key_list and self.KEY_V in key_list:
                    self.master.quit()

                elif self.SPACE in key_list and len(key_list) == 1:
                    shot_function()

                elif self.ESC in key_list and len(key_list) == 1:
                    pass

            self.master.after(5, lambda: self.key_organizator())


    def clear_key(self, event):
        key_list = self.game_window.key_list()
        event = event.keycode
        if event in key_list:
            key_list.remove(event)


def make_circle(event, canvas, master):
    Circle(event, canvas=canvas, master=master).make_oval()


def clear():
    canvas.delete("all")
    canvas.destroy()


def scroll_screen_left(to_who, canvas, game_window):

    x = to_who.x()
    if x < 0 + (game_window.get_game_screen_width()//2):
        pass
    elif x > game_window.get_game_width() - (game_window.get_game_screen_width()//2):
        pass
    else:
        for i in range(to_who.x_speed()):
            canvas.xview_scroll(-1, UNITS)


def scroll_screen_right(to_who, canvas, game_window):

    x = to_who.x()
    if x > game_window.get_game_width() - (game_window.get_game_screen_width()//2):
        pass
    elif x < 0 + (game_window.get_game_screen_width()//2):
        pass
    else:
        for i in range(to_who.x_speed()):
            canvas.xview_scroll(1, UNITS)


def scroll_start(event, canvas):
    canvas.scan_mark(event.x, event.y)


def scroll_move(event, canvas):

    x = event.x
    y = event.y
    canvas.scan_dragto(x, y, gain=1)


def mouse_coords(mouse_x, mouse_y, canvas):

    mouse_x = canvas.canvasx(mouse_x)
    mouse_y = canvas.canvasy(mouse_y)
    return mouse_x, mouse_y


def resize_window(event, canvas, master, game_window, center_element):

    canvas.config(width=master.winfo_width() - 4, height=master.winfo_height() - 4)
    x = center_element.x()
    y = center_element.y()

    game_window.update_game_screen_width()
    game_window.update_game_screen_heigth()

    canvas.xview_moveto((x - (game_window.get_game_screen_width()/2))/game_window.get_game_width())
    canvas.yview_moveto((y - (game_window.get_game_screen_heigth()/2))/game_window.get_game_height())


def screen_center(canvas, monitor_width, monitor_height):
    x1 = canvas.canvasx(0)
    x2 = canvas.canvasx(monitor_width)
    y1 = canvas.canvasy(0)
    y2 = canvas.canvasy(monitor_height)

    center_x = (x1 + x2)/2
    center_y = (y1 + y2)/2

    return center_x, center_y


def resize_image(width, height, path_image):
    image = Image.open(path_image)
    img_copy = image.copy()
    image = img_copy.resize((width, height))
    return image


def create_image(image_path, width, height):
    raw_image = resize_image(path_image=image_path, width=width, height=height)
    image = ImageTk.PhotoImage(raw_image)
    return image


def create_change_gradually_image(img_to_change, new_image, path, alpha=0.0, counter=0):

    if alpha > 1:
        return
    else:  # if is not the first or the last cycle
        new_img = Image.blend(img_to_change, new_image, alpha)  # it modify a bit the image ( depends to the alpha value )
        image_path = path + "/" + str(counter) + ".png"
        new_img.save(image_path, 'PNG')
        Timer(0.05, create_change_gradually_image, [img_to_change, new_image, path, alpha + 0.5, counter + 1]).start()  # call again the cycle with alpha increased by 2


def all_combinations(lista, new_lista=[]):
    modify_this = lista[:]
    if len(lista) >= 2:
        first_elem = modify_this[0]
        second_elem = modify_this[1]
        new_lista.append(first_elem + "_" + second_elem)
        new_lista.append(second_elem + "_" + first_elem)
        modify_this.remove(first_elem)
        new_lista = all_combinations(modify_this, new_lista)
        return new_lista
    else:
        return new_lista

