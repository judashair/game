import pygame
from pygame import mixer
import pickle
from os import path



pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()  # ����������� ������ � �������
pygame.init()  # ����������� ������

clock = pygame.time.Clock()
fps = 60  # ��������

screen_width = 700  # ������ ���� ��������
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("NAME OF GAME")  # �����

font = pygame.font.SysFont('COURNEUF REGULAR', 70)
font_score = pygame.font.SysFont('COURNEUF REGULAR', 30)  # �����

tile_size = 35  # ����� �����
game_over = 0
main_menu = True
level = 0  # ���������� �����
max_levels = 7  # ����������� �-�� ����
score = 0  # �������

pink = (132, 89, 107)   # ���� �������
blue = (220, 240, 247)  # ���� ������
# ���
background_img = pygame.image.load('image/night_bg.jpg')

# ������
restart_img = pygame.image.load('image/restart.png')
restart_img = pygame.transform.scale(restart_img, (100, 40))
start_img = pygame.image.load('image/start.png')
start_img = pygame.transform.scale(start_img, (150, 70))
exit_img = pygame.image.load('image/exit.png')
exit_img = pygame.transform.scale(exit_img, (130, 50))

# ������
# pygame.mixer.music.load('back_m.wav')
# pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('sound/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sound/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('sound/game_over.wav')
game_over_fx.set_volume(0.5)

def world_data(level):
    world_data = None
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)

    return world_data