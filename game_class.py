import pygame
from pygame import mixer
import pickle
from os import path
from conc import *


# ������� ��� ������ ������
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# ������� ��� �������� ����
def reset_level(level):
    global world_data
    player.reset(65, screen_height - 100)
    # ����� ���
    blob_group.empty()
    platform_group.empty()
    star_group.empty()
    lava_group.empty()
    exit_group.empty()

    # ������������ ���� � ��������� ����
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)  # ����������� ����

    score_star = Star(tile_size // 2, tile_size // 2)
    star_group.add(score_star)

    return world

# def draw_grid():  #  ������� ��� ������� �������� �����
#     for line in range(0, 20):
#         pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
#         pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))
# ��� ������ ������/��������


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    # ����� ������ �������
    def draw(self):
        action = False

        # �� ������
        pos = pygame.mouse.get_pos()

        # �������� �� ������ �� ������ � ������
        if self.rect.collidepoint(pos):  # �� ������ �� ������
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked is False:  # ���� ������� ���� (0) ������� ����
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)

        return action


class Player():  # ���� ���������
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 8
        col_thresh = 20

        if game_over == 0:  # ���� �� �������
            # ���������
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped is False and self.in_air is False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] is False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] is False and key[pygame.K_RIGHT] is False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:  # ��� ����������� � ���� �������� ���� ���������� ������
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # ���������
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # �����
            self.in_air = True
            for tile in world.tile_list:
                # x direction collision
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # y direction collision
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # �������� �� ��� ������ - ������
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # ������
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False  # ������ ����� ���� ���

            # ����� � ����
            if pygame.sprite.spritecollide(self, blob_group, False):  # ���� �������� �� ������ - �������
                game_over = -1
                game_over_fx.play()

            # ����� � �����
            if pygame.sprite.spritecollide(self, lava_group, False):  # �� ���� ��� ����
                game_over = -1
                game_over_fx.play()

            if pygame.sprite.spritecollide(self, exit_group, False):  # ���� �������� �� ������ - ��������� �����
                game_over = 1

            # ����� � ����������
            for platform in platform_group:
                # x direction
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # y direction
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # �� �� ����������
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # �� �� ��������
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # ��� � �� �� ��������
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:  # ���� ������� - ���������� �������
            self.image = self.dead_image
            self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 150, screen_height // 5)   # ����� ��� ��������
            if self.rect.y > 200:
                self.rect.y -= 5

        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'image/gg{num}.png')
            img_right = pygame.transform.scale(img_right, (32, 60))  # ��������� ����
            img_left = pygame.transform.flip(img_right, True, False)  # ���������� ���� ����������� � ������ �������
            self.images_right.append(img_right)
            self.images_left.append(img_left)
            # ���� ���� ���������
        self.dead_image = pygame.image.load('image/dead.png')
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


class World():  # ���� ����
    def __init__(self, data):
        self.tile_list = []

        cake_img = pygame.image.load('image/cake.png')
        cream_img = pygame.image.load('image/cream.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:  # ��� ���������� ����� ���� � ������� ����� 1
                    img = pygame.transform.scale(cake_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:  # ��� 2
                    img = pygame.transform.scale(cream_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:  # ��� 3 - �����
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 5)
                    blob_group.add(blob)
                if tile == 4:   # ��������� ������/����
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:  # ��������� �����/����
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:  # ����
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:  # ����
                    star = Star(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    star_group.add(star)
                if tile == 8:  # �����
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):  # ���� ������
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('image/enemy.png')
        self.image = pygame.transform.scale(self.image, (30, 30))  # ��������� ����������
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1  # ���
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_counter > 30:  # ��� �� �������� �� ��� �����
            self.move_direction *= -1
            self.move_counter *= -1


class Platform(pygame.sprite.Sprite):  # ��� ���������
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('image/cake_half.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x   # ��� ������/����
        self.move_y = move_y  # ����� ����

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if self.move_counter > 35:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):  # ��� ����
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('image/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))  # ��������� ����������
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Star(pygame.sprite.Sprite):   # ����
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('image/star.png')
        self.image = pygame.transform.scale(img, (tile_size // 1.1, tile_size // 1.1))  # ��������� ����������
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):  # ��� �������� �� ����� �����
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('image/door.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))  # ��������� ����������
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(65, screen_height - 100)  # �� ����� ��������� �� ������� ���

blob_group = pygame.sprite.Group()  # ����������� ������
platform_group = pygame.sprite.Group()  # ����������� ��������
lava_group = pygame.sprite.Group()  # ����������� ����
star_group = pygame.sprite.Group()  # ����������� ����
exit_group = pygame.sprite.Group()  # ������� �� ����� �����

score_star = Star(tile_size // 2, tile_size // 2)   # �-�� ����
star_group.add(score_star)

# ������������ ���� � ��������� ����
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)

world = World(world_data)  # ����������� ����

# ��������� ������
restart_button = Button(screen_width // 2 - 50, screen_height // 2, restart_img)
start_button = Button(screen_width // 2 - 200, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 80, screen_height // 1.96, exit_img)