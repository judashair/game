# coding=utf8

from game_class import *
from conc import *
# from conc import main_menu, game_over, score, level, world_data

world_data = world_data(level)
world = World(world_data)
run = True
while run:  # запуск гри
    clock.tick(fps)

    screen.blit(background_img, (0, 0))  # фон

    if main_menu is True:  # вивід головного меню
        if exit_button.draw():  # якщо ексіт - вихід з гри
            run = False
        if start_button.draw():  # якщо старт - початок гри
            main_menu = False

    else:
        world.draw()  # світ

        if game_over == 0:  # якщо гра йде - відображати
            blob_group.update()  # вороги
            platform_group.update()  # платформа
            if pygame.sprite.spritecollide(player, star_group, True):  # забирає зірки коли персонаж їх забрав
                score += 1
                coin_fx.play()  # музика збирання зірок
            draw_text(' x ' + str(score), font_score, pink, tile_size - 10, 10)

        blob_group.draw(screen)  # показ ворогів на екрані
        platform_group.draw(screen)  # показ платформ
        lava_group.draw(screen)  # для лави
        star_group.draw(screen)  # зірки
        exit_group.draw(screen)  # перехід

        game_over = player.update(game_over)  # персонаж програв

        if game_over == -1:  # якщо помирає - кнопка рестарт і все спочатку
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        if game_over == 1:  # перехід на інший рівень поки рівні не закінчаться
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:  # коли пройшов всі рівні - починає спочатку + текст перемоги
                draw_text('YOU WIN!', font, blue, (screen_width // 2) - 100, screen_height // 5)
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

                #  draw_grid()

    for event in pygame.event.get():  # вихід з гри
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
