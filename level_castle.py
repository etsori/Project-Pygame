import pygame
import os


pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Legend of the Knight ~ The gloomy castle")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

background = pygame.image.load(os.path.join("data", "background", "hall.jpg"))  # Фон уровня
background = pygame.transform.scale(background, (WIDTH * 4, HEIGHT))

finish_level_image = pygame.image.load(os.path.join("data", "finish_level.jpg")).convert_alpha()
finish_level_image = pygame.transform.scale(finish_level_image, (WIDTH, HEIGHT))  # Масштабируем изображение

sprite_sheet = pygame.image.load(os.path.join("data/levels/k_walkjpg.png")).convert_alpha()

frame_width = sprite_sheet.get_width() // 6  # Ширина одного кадра
frame_height = sprite_sheet.get_height()  # Высота кадра
frames_right = []
frames_left = []

for i in range(6):
    frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    frames_right.append(frame)
    frames_left.append(pygame.transform.flip(frame, True, False))  # Отражаем кадр для движения влево

# Анимация персонажа
current_frame = 0
animation_speed = 0.2
frame_timer = 0

# Позиция и размеры персонажа
player_rect = frames_right[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))

direction = "right"

platform_image = pygame.image.load(os.path.join("data", "plat_unfon3.png")).convert_alpha()
platform_image = pygame.transform.scale(platform_image, (200, 60))
platform_image.set_colorkey((255, 255, 255))

platforms = [
    {"rect": pygame.Rect(0, HEIGHT - 50, WIDTH * 4, 50), "image": None},  # нижняя платформа
    {"rect": pygame.Rect(300, 400, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(600, 270, 150, 20), "image": platform_image},
    {"rect": pygame.Rect(950, 200, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(1300, 400, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(1600, 270, 150, 20), "image": platform_image},
    {"rect": pygame.Rect(1950, 200, 200, 20), "image": platform_image},
]

player_speed = 5
jump_speed = -15
gravity = 0.8
player_velocity_y = 0
is_jumping = False

camera_x = 0

game_over = False

running = True
clock = pygame.time.Clock()
while running:
    delta_time = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= player_speed
            direction = "left"
        elif keys[pygame.K_RIGHT]:
            player_rect.x += player_speed
            direction = "right"
        else:
            pass

        if keys[pygame.K_SPACE] and not is_jumping:
            is_jumping = True
            player_velocity_y = jump_speed

        # Гравитация
        player_velocity_y += gravity
        player_rect.y += player_velocity_y

        for platform in platforms:
            if player_rect.colliderect(platform["rect"]) and player_velocity_y > 0:
                player_rect.bottom = platform["rect"].top
                player_velocity_y = 0
                is_jumping = False

        camera_x = max(0, player_rect.centerx - WIDTH // 2)
        if camera_x > background.get_width() - WIDTH:
            camera_x = background.get_width() - WIDTH

        if player_rect.right >= background.get_width():
            game_over = True

    screen.fill(BLACK)

    screen.blit(background, (-camera_x, 0))

    # Отрисовка платформ с учётом камеры
    for platform in platforms:
        if platform["image"]:  # Если есть изображение платформы
            screen.blit(platform["image"], (platform["rect"].x - camera_x, platform["rect"].y))
        else:  # Если платформа без изображения (основная платформа)
            pygame.draw.rect(screen, BLACK, (platform["rect"].x - camera_x, platform["rect"].y, platform["rect"].width, platform["rect"].height))

    # Анимация персонажа
    if not game_over:
        frame_timer += delta_time
        if frame_timer >= animation_speed:
            frame_timer = 0
            current_frame = (current_frame + 1) % len(frames_right)  # Переключение на следующий кадр

        # Отрисовка персонажа в зависимости от направления
        if direction == "right":
            screen.blit(frames_right[current_frame], (player_rect.x - camera_x, player_rect.y))
        else:
            screen.blit(frames_left[current_frame], (player_rect.x - camera_x, player_rect.y))
    else:
        # Отображение поздравления
        screen.blit(finish_level_image, (0, 0))

    pygame.display.flip()

pygame.quit()