import pygame, sys
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()
fps = 60

screen_width, screen_height = 1024, 572
window = (screen_width, screen_height)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Door to Security')

header = pygame.font.Font('Assets/Retro Computer.ttf', 40)
header1 = pygame.font.Font('Assets/Pixellari.ttf', 30)
header2 = pygame.font.Font('Assets/Pixellari.ttf', 20)
text = pygame.font.SysFont('OCRB', 25)

tile_size = 32
game_over = 0
main_menu = True
controls = True
question = True
complete = True
level = 1
score = 0


bg = (33, 31, 48)
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0, 0, 255)


bg_img = pygame.transform.scale(pygame.image.load('Assets/bg_img.png'), (1024, 576))
controls_img = pygame.transform.scale(pygame.image.load('Assets/controls.png'), (1024, 572))
enter_img = pygame.image.load('Assets/enter_btn.png')
restart_img = pygame.image.load('Assets/restart_btn.png')
start_img = pygame.transform.scale(pygame.image.load('Assets/start_btn.png'), (200, 90))
exit_img = pygame.transform.scale(pygame.image.load('Assets/exit_btn.png'), (171, 90))
exit2_img = pygame.transform.scale(pygame.image.load('Assets/exit_btn.png'), (151, 70))
coin_img = pygame.transform.scale(pygame.image.load('Assets/coin.png'), (22, 22))
next_img = pygame.transform.scale(pygame.image.load('Assets/next.png'), (42, 44))
info1 = pygame.image.load('Assets/info1.png')
info2 = pygame.image.load('Assets/info2.png')
info3 = pygame.image.load('Assets/info3.png')
info4 = pygame.image.load('Assets/info4.png')
info5 = pygame.image.load('Assets/info5.png')
end = pygame.image.load('Assets/end.png')


pygame.mixer.music.load('Assets/music.mp3')
pygame.mixer.music.play(-1, 0.0, 2000)
pygame.mixer.music.set_volume(0.07)
coin_fx = pygame.mixer.Sound('Assets/coin.mp3')
coin_fx.set_volume(0.1)
jump_fx = pygame.mixer.Sound('Assets/jump.wav')
jump_fx.set_volume(0.1)
death_fx = pygame.mixer.Sound('Assets/death.wav')
death_fx.set_volume(0.1)
complete_fx = pygame.mixer.Sound('Assets/complete.wav')
complete_fx.set_volume(0.1)
click_fx = pygame.mixer.Sound('Assets/click.wav')
click_fx.set_volume(0.1)
victory_fx = pygame.mixer.Sound('Assets/victory.wav')
victory_fx.set_volume(0.1)
correct_fx = pygame.mixer.Sound('Assets/correct.mp3')
correct_fx.set_volume(0.1)
wrong_fx = pygame.mixer.Sound('Assets/wrong.wav')
wrong_fx.set_volume(0.1)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_level(level):
    player.reset(64, screen_height - 128)
    platform_group.empty()
    spike_group.empty()
    lava_group.empty()
    coin_group.empty()
    exit_group.empty()

    # load in level data and create world
    if path.exists(f'Assets/level{level}_data'):
        pickle_in = open(f'Assets/level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()


        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action


class Button_choice():
    def __init__(self, text, width, height, pos):
        self.rect = pygame.Rect(pos, (width, height))
        self.color = WHITE
        self.text_surf = header2.render(text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            self.color = '#88A7C2'
            if self.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    action = True
                    self.clicked = True

            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

        else:
            self.color = WHITE

        pygame.draw.rect(screen, self.color, self.rect, border_radius=12)
        screen.blit(self.text_surf, self.text_rect)

        return action


class Spritesheet:
    def __init__(self, image):
        self.sheet = image

    def get_image(self, row, column, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((row * width), (column * height), width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(colour)

        return image


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cd = 3
        col_thresh = 20     # collision threshold

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -12
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            if self.counter > walk_cd:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            self.in_air = True
            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            if pygame.sprite.spritecollide(self, spike_group, False):
                game_over = -1
                death_fx.play()

            # check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                death_fx.play()

            # check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                complete_fx.play()
                game_over = 2


            for platform in platform_group:
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', header, BLUE, (tile_size * 11) + 8, tile_size * 8)
            if self.rect.y > 100:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'Assets/run{num}.png')
            img_right = pygame.transform.scale(img_right, (46, 56))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('Assets/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        dirt_img = pygame.image.load('Assets/dirt.png')
        grass_img = pygame.image.load('Assets/grass.png')
        stick_img = pygame.image.load('Assets/stick.png')

        dirt1_img = pygame.image.load('Assets/dirt1.png')
        grass1_img = pygame.image.load('Assets/grass1.png')

        dirt2_img = pygame.image.load('Assets/dirt2.png')
        grass2_img = pygame.image.load('Assets/grass2.png')

        platform_x = pygame.image.load('Assets/platform_x.png')
        platform_y = pygame.image.load('Assets/platform_y.png')

        tileset = pygame.image.load('Assets/tileset.png').convert_alpha()
        sprite_sheet = Spritesheet(tileset)

        wall_topleft = sprite_sheet.get_image(1, 0, 16, 16, 2, BLACK)
        wall_top = sprite_sheet.get_image(2, 0, 16, 16, 2, BLACK)
        wall_topright = sprite_sheet.get_image(3, 0, 16, 16, 2, BLACK)
        wall_left = sprite_sheet.get_image(4, 0, 16, 16, 2, BLACK)
        wall_right = sprite_sheet.get_image(5, 0, 16, 16, 2, BLACK)
        wall_botleft = sprite_sheet.get_image(0, 1, 16, 16, 2, BLACK)
        wall_bot = sprite_sheet.get_image(1, 1, 16, 16, 2, BLACK)
        wall_botright = sprite_sheet.get_image(2, 1, 16, 16, 2, BLACK)
        box = sprite_sheet.get_image(5, 1, 16, 16, 2, BLACK)

        wall1_topleft = sprite_sheet.get_image(0, 4, 16, 16, 2, BLACK)
        wall1_top = sprite_sheet.get_image(1, 4, 16, 16, 2, BLACK)
        wall1_topright = sprite_sheet.get_image(2, 4, 16, 16, 2, BLACK)
        wall1_left = sprite_sheet.get_image(3, 4, 16, 16, 2, BLACK)
        wall1_right = sprite_sheet.get_image(4, 4, 16, 16, 2, BLACK)
        wall1_botleft = sprite_sheet.get_image(5, 4, 16, 16, 2, BLACK)
        wall1_bot = sprite_sheet.get_image(0, 5, 16, 16, 2, BLACK)
        wall1_botright = sprite_sheet.get_image(1, 5, 16, 16, 2, BLACK)
        wall1_connect1 = sprite_sheet.get_image(2, 5, 16, 16, 2, BLACK)
        wall1_connect2 = sprite_sheet.get_image(3, 5, 16, 16, 2, BLACK)
        wall1_connect3 = sprite_sheet.get_image(4, 5, 16, 16, 2, BLACK)
        wall1_connect4 = sprite_sheet.get_image(5, 5, 16, 16, 2, BLACK)
        box1 = sprite_sheet.get_image(5, 6, 16, 16, 2, BLACK)
        stick1 = sprite_sheet.get_image(3, 3, 16, 16, 2, BLACK)

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = wall_topleft
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = wall_top
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = wall_topright
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    img = wall_left
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 5:
                    img = wall_right
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 6:
                    img = wall_botleft
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 7:
                    img = wall_bot
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 8:
                    img = wall_botright
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 9:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 10:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 11:
                    img = box
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 12:
                    spike = Spike(col_count * tile_size, row_count * tile_size)
                    spike_group.add(spike)
                if tile == 13:
                    img = pygame.transform.scale(stick_img, (96, 10))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 14:
                    exit = Exit(col_count * tile_size, row_count * tile_size - 32)
                    exit_group.add(exit)
                if tile == 15:
                    lava = Lava(col_count * tile_size, row_count * tile_size)
                    lava_group.add(lava)
                if tile == 19:
                    coin = Coin(col_count * tile_size + 16, row_count * tile_size)
                    coin_group.add(coin)
                if tile == 20:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 21:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 23:
                    img = stick1
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 24:
                    img = wall1_topleft
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 25:
                    img = wall1_top
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 26:
                    img = wall1_topright
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 27:
                    img = wall1_left
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 28:
                    img = wall1_right
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 29:
                    img = wall1_botleft
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 30:
                    img = wall1_bot
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 31:
                    img = wall1_botright
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 32:
                    img = wall1_connect1
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 33:
                    img = wall1_connect2
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 34:
                    img = wall1_connect3
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 35:
                    img = wall1_connect4
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 36:
                    img = pygame.transform.scale(grass2_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 37:
                    img = pygame.transform.scale(dirt2_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 38:
                    img = pygame.transform.scale(grass1_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 39:
                    img = pygame.transform.scale(dirt1_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 41:
                    img = box1
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)


                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, BLACK, tile[1], 1)


class Platform (pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/platform.png')
        self.image = pygame.transform.scale(img, (64, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 60:
            self.move_direction *= -1
            self.move_counter *= -1


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/spike.png')
        self.image = pygame.transform.scale(img, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/lava.png')
        self.image = pygame.transform.scale(img, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/coin.png')
        self.image = pygame.transform.scale(img, (22, 22))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('Assets/exit.png')
        self.image = pygame.transform.scale(img, (44, 64))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def controls_text():
    draw_text('CONTROLS', header, WHITE, tile_size * 12, tile_size * 1)
    draw_text('Use LEFT and RIGHT arrow keys to move.', header2, WHITE, tile_size * 3, tile_size * 4)
    draw_text('Use SPACE to jump.', header2, WHITE, tile_size * 3, (tile_size * 6) - 16)
    draw_text('Use MOUSE to select your answer.', header2, WHITE, tile_size * 3, tile_size * 7)
    draw_text('Use RIGHT CLICK to confirm your answer.', header2, WHITE, tile_size * 3, (tile_size * 9) - 16)
    draw_text('Avoid spikes and lava pools.', header2, WHITE, tile_size * 3, (tile_size * 11) - 16)
    draw_text('Reach the door at the end.', header2, WHITE, tile_size * 3, tile_size * 12)
    draw_text('Answer the prompts and learn!', header2, WHITE, tile_size * 3, (tile_size * 14) - 16)
    draw_text('MOVE LEFT    MOVE RIGHT', header2, WHITE, (tile_size * 20) + 16, tile_size * 9)
    draw_text('JUMP', header2, WHITE, (tile_size * 23) + 20, tile_size * 12)
    pygame.draw.line(screen, WHITE, (tile_size * 2, tile_size * 3), (tile_size * 30, tile_size * 3), 5)
    pygame.draw.line(screen, WHITE, (tile_size * 17, tile_size * 4), (tile_size * 17, tile_size * 16), 5)
    pygame.draw.line(screen, WHITE, (tile_size * 2, (tile_size * 9) + 24), (tile_size * 16, (tile_size * 9) + 24), 5)


def question_1():
    draw_text('Checkpoint reached! Answer the question to proceed to next level.', text, WHITE, tile_size * 2, tile_size * 1)
    pygame.draw.line(screen, WHITE, (tile_size * 2, tile_size * 2), (tile_size * 30, tile_size * 2), 5)
    draw_text('PASSWORD SECURITY!', header, WHITE, tile_size * 7, tile_size * 3)
    draw_text('WHICH PASSWORD IS THE STRONGEST?', header1, WHITE, tile_size * 7, tile_size * 6)


def question_2():
    draw_text('Checkpoint reached! Answer the question to proceed to next level.', text, WHITE, tile_size * 2, tile_size * 1)
    pygame.draw.line(screen, WHITE, (tile_size * 2, tile_size * 2), (tile_size * 30, tile_size * 2), 5)
    draw_text('PASSWORD SECURITY!', header, WHITE, tile_size * 7, tile_size * 3)
    draw_text('IDENTIFY THE BEST WAY TO REMEMBER YOUR PASSWORD', header1, WHITE, tile_size * 3, tile_size * 6)


def question_3():
    draw_text('Checkpoint reached! Answer the question to proceed to next level.', text, WHITE, tile_size * 2, tile_size * 1)
    pygame.draw.line(screen, WHITE, (tile_size * 2, tile_size * 2), (tile_size * 30, tile_size * 2), 5)
    draw_text('PASSWORD SECURITY!', header, WHITE, tile_size * 7, tile_size * 3)
    draw_text('SHOULD YOU REUSE YOUR PASSWORD?', header1, WHITE, tile_size * 7, tile_size * 6)


def question_4():
    draw_text('Checkpoint reached! Answer the question to proceed to next level.', text, WHITE, tile_size * 2, tile_size * 1)
    pygame.draw.line(screen, WHITE, (tile_size * 2, tile_size * 2), (tile_size * 30, tile_size * 2), 5)
    draw_text('PASSWORD SECURITY!', header, WHITE, tile_size * 7, tile_size * 3)
    draw_text('WHAT IS THE BEST WAY TO PROTECT YOUR PASSWORD?', header1, WHITE, (tile_size * 3) + 16, tile_size * 6)


def question_5():
    draw_text('Final checkpoint!', text, WHITE, tile_size * 2, tile_size * 1)
    pygame.draw.line(screen, WHITE, (tile_size * 2, tile_size * 2), (tile_size * 30, tile_size * 2), 5)
    draw_text('PASSWORD SECURITY!', header, WHITE, tile_size * 7, tile_size * 3)
    draw_text('WHAT SHOULD YOU DO AFTER LOGGING IN?', header1, WHITE, tile_size * 6, tile_size * 6)


def draw_bg():
    bgw = pygame.transform.scale(pygame.image.load(f'Assets/bg.png'), (64, 64))
    for i in range(1, 15):
        for j in range(1, 8):
            screen.blit(bgw, ((i * 64), (j * 64)))


player = Player(64, screen_height - 128)

platform_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

if path.exists(f'Assets/level{level}_data'):
    pickle_in = open(f'Assets/level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


enter_button = Button((tile_size * 22) + 26, tile_size * 14, enter_img)
restart_button = Button(tile_size * 14, tile_size * 11, restart_img)
start_button = Button(tile_size * 5, tile_size * 13, start_img)
exit_button = Button(tile_size * 21, tile_size * 13, exit_img)
exit2_button = Button((tile_size * 13) + 24, tile_size * 11, exit2_img)
next_button = Button(tile_size * 28, tile_size * 2, next_img)

choice1 = Button_choice("@1l0vEsH0k0l8t!", 300, 40, (350, 250))
choice2 = Button_choice("zaq12wsx", 300, 40, (350, 300))
choice3 = Button_choice("password", 300, 40, (350, 350))
choice4 = Button_choice("ItzAGurl", 300, 40, (350, 400))

choice5 = Button_choice("Reuse password", 450, 40, (290, 250))
choice6 = Button_choice("Write it on the paper or notebook", 450, 40, (290, 300))
choice7 = Button_choice("Use a secure password manager", 450, 40, (290, 350))
choice8 = Button_choice("Tell your friend to remember it with you", 450, 40, (290, 400))

choice9 = Button_choice("Yes", 400, 40, (310, 250))
choice10 = Button_choice("No", 400, 40, (310, 300))
choice11 = Button_choice("Yes, but add a few more characters", 400, 40, (310, 350))
choice12 = Button_choice("Yes, but remove a few more character", 400, 40, (310, 400))

choice13 = Button_choice("Use an antivirus", 500, 40, (270, 250))
choice14 = Button_choice("Use your hand to cover your password while typing", 500, 40, (270, 300))
choice15 = Button_choice("Use Two-Factor Authentication", 500, 40, (270, 350))
choice16 = Button_choice("Use a harder password", 500, 40, (270, 400))

choice17 = Button_choice("Save your password onto the browser", 400, 40, (310, 250))
choice18 = Button_choice("Log out after use", 400, 40, (310, 300))
choice19 = Button_choice("Check remember password", 400, 40, (310, 350))
choice20 = Button_choice("Change password every use", 400, 40, (310, 400))

run = True
while run:

    clock.tick(fps)

    screen.fill(bg)
    screen.blit(bg_img, (0,0))

    if main_menu:
        if exit_button.draw():
            click_fx.play()
            run = False
        if start_button.draw():
            click_fx.play()
            main_menu = False

    else:
        screen.blit(controls_img, (0, 0))
        controls_text()

        if controls:
            if enter_button.draw():
                click_fx.play()
                controls = False

        else:
            screen.fill(bg)
            draw_bg()
            world.draw()
            screen.blit(coin_img, (60, 16))

            if game_over == 0:
                platform_group.update()
                if pygame.sprite.spritecollide(player, coin_group, True):
                    score += 1
                    coin_fx.play()
                draw_text(' x ' + str(score), text, WHITE, 85, 20)

            platform_group.draw(screen)
            spike_group.draw(screen)
            lava_group.draw(screen)
            coin_group.draw(screen)
            exit_group.draw(screen)

            game_over = player.update(game_over)

            if game_over == -1:
                if restart_button.draw():
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

            if game_over == 2:
                screen.fill(bg)
                if level == 1:
                    if question == True:
                        question_1()
                        if choice1.draw():
                            correct_fx.play()
                            question = False

                        elif choice2.draw() or choice3.draw() or choice4.draw():
                            wrong_fx.play()
                    else:
                        screen.blit(info1, (0, 0))
                        if next_button.draw():
                            click_fx.play()
                            level = 2
                            world_data = []
                            world = reset_level(level)
                            game_over = 0
                            question = True

                if level == 2:
                    if question == True:
                        question_2()
                        if choice7.draw():
                            correct_fx.play()
                            question = False
                        elif choice5.draw() or choice6.draw() or choice8.draw():
                            wrong_fx.play()
                            wrong_fx.play()
                    else:
                        screen.blit(info2, (0, 0))
                        if next_button.draw():
                            click_fx.play()
                            level = 3
                            world_data = []
                            world = reset_level(level)
                            game_over = 0
                            question = True

                if level == 3:
                    if question == True:
                        question_3()
                        if choice10.draw():
                            correct_fx.play()
                            question = False
                        elif choice9.draw() or choice11.draw() or choice12.draw():
                            wrong_fx.play()
                    else:
                        screen.blit(info3, (0, 0))
                        if next_button.draw():
                            click_fx.play()
                            level = 4
                            world_data = []
                            world = reset_level(level)
                            game_over = 0
                            question = True

                if level == 4:
                    if question == True:
                        question_4()
                        if choice15.draw():
                            correct_fx.play()
                            question = False
                        elif choice13.draw() or choice14.draw() or choice16.draw():
                            wrong_fx.play()
                    else:
                        screen.blit(info4, (0, 0))
                        if next_button.draw():
                            click_fx.play()
                            level = 5
                            world_data = []
                            world = reset_level(level)
                            game_over = 0
                            question = True

                if level == 5:
                    if question == True:
                        question_5()
                        if choice18.draw():
                            correct_fx.play()
                            question = False
                        elif choice17.draw() or choice19.draw() or choice20.draw():
                            wrong_fx.play()
                    else:
                        screen.blit(info5, (0, 0))
                        if complete == True:
                            if next_button.draw():
                                victory_fx.play()
                                complete = False
                        else:
                            screen.blit(end, (0,0))
                            if exit2_button.draw():
                                run = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

    pygame.display.update()