import pygame
import os
import time

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Legend of the Knight ~ The gloomy castle")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

background = pygame.image.load(os.path.join("data", "background", "dark_forest.jpg"))  # Фон уровня
background = pygame.transform.scale(background, (WIDTH * 4, HEIGHT))

finish_level_image = pygame.image.load(os.path.join("data", "finish_level.jpg")).convert_alpha()
finish_level_image = pygame.transform.scale(finish_level_image, (WIDTH, HEIGHT))  # Масштабируем изображение


sprite_sheet = pygame.image.load(os.path.join("data", "sprite_knight", "k_walkjpg.png")).convert_alpha()


frame_width = sprite_sheet.get_width() // 6  # Ширина одного кадра
frame_height = sprite_sheet.get_height()  # Высота кадра
frames_right = []
frames_left = []

for i in range(6):
    frame = sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    frames_right.append(frame)
    frames_left.append(pygame.transform.flip(frame, True, False))  # Отражаем кадр для движения влево

# Загрузка спрайтового листа для атаки
attack_sprite_sheet = pygame.image.load(os.path.join("data", "levels", "knight_fighting.png")).convert_alpha()

# Разделение спрайтового листа для атаки на кадры
attack_frame_width = attack_sprite_sheet.get_width() // 4  # Ширина одного кадра
attack_frame_height = attack_sprite_sheet.get_height()  # Высота кадра
attack_frames_right = []
attack_frames_left = []

frame = attack_sprite_sheet.subsurface(pygame.Rect(0, 0, 105, attack_frame_height))
attack_frames_right.append(frame)
attack_frames_left.append(pygame.transform.flip(frame, True, False))  # Отражаем кадр для движения влево

frame = attack_sprite_sheet.subsurface(pygame.Rect(105, 0, 108, attack_frame_height))
attack_frames_right.append(frame)
attack_frames_left.append(pygame.transform.flip(frame, True, False))  # Отражаем кадр для движения влево

frame = attack_sprite_sheet.subsurface(pygame.Rect(213, 0, 134, attack_frame_height))
attack_frames_right.append(frame)
attack_frames_left.append(pygame.transform.flip(frame, True, False))  # Отражаем кадр для движения влево

frame = attack_sprite_sheet.subsurface(pygame.Rect(347, 0, 132, attack_frame_height))
attack_frames_right.append(frame)
attack_frames_left.append(pygame.transform.flip(frame, True, False))  # Отражаем кадр для движения влево

current_frame = 0
animation_speed = 0.2
frame_timer = 0

is_attacking = False
attack_frame_timer = 0
attack_animation_speed = 0.2
current_attack_frame = 0

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

# Скорости и гравитация
player_speed = 5
jump_speed = -15
gravity = 0.8
player_velocity_y = 0
is_jumping = False

camera_x = 0

game_over = False

# Жизни персонажа
lives = 5

class Enemy:
    def __init__(self, sprite_sheet_path, x, y, min_x, max_x, speed, scale_factor=1.0):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.scale_factor = scale_factor  
        self.frames = self.load_frames()
        self.current_frame = 0
        self.frame_timer = 0
        self.animation_speed = 0.2
        self.rect = self.frames[0].get_rect(topleft=(x, y))
        self.min_x = min_x
        self.max_x = max_x
        self.speed = speed
        self.direction = 1  
        self.active = True
        self.last_collision_time = 0

    def load_frames(self):
        frames = []
        frame_width = self.sprite_sheet.get_width() // 3
        frame_height = self.sprite_sheet.get_height() // 4
        for row in range(4):
            for col in range(3):
                frame = self.sprite_sheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (int(frame_width * self.scale_factor), int(frame_height * self.scale_factor)))
                frames.append(frame)
        return frames

    def update(self):
        if self.active:
            self.rect.x += self.speed * self.direction
            if self.rect.right >= self.max_x or self.rect.left <= self.min_x:
                self.direction *= -1  

            self.frame_timer += delta_time
            if self.frame_timer >= self.animation_speed:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen):
        if self.active:
            screen.blit(self.frames[self.current_frame], (self.rect.x - camera_x, self.rect.y))

enemy1 = Enemy(os.path.join("data", "enemies", "ghost_unfon.png"), 100, HEIGHT - 150, 30, WIDTH // 2, 2, scale_factor=1.5)
enemy2 = Enemy(os.path.join("data", "enemies", "pumpking_unfon.png"), WIDTH // 2, HEIGHT - 150, 400, WIDTH * 4 - 100, 2, scale_factor=1.5)
enemies = [enemy1, enemy2]

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

        if keys[pygame.K_UP] and not is_jumping:
            is_jumping = True
            player_velocity_y = jump_speed

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            is_attacking = True
        else:
            is_attacking = False

      
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

        
        for enemy in enemies[:]: 
            if enemy.active and player_rect.colliderect(enemy.rect):
                if is_attacking:
                    enemies.remove(enemy) 
                else:
                    lives -= 1
                    enemy.active = False
                    enemy.last_collision_time = time.time()
                    if lives <= 0:
                        game_over = True

        # Активация врагов через 3 секунды
        current_time = time.time()
        for enemy in enemies:
            if not enemy.active and current_time - enemy.last_collision_time >= 3:
                enemy.active = True


    screen.fill(BLACK)

    screen.blit(background, (-camera_x, 0))

    for platform in platforms:
        if platform["image"]:  
            screen.blit(platform["image"], (platform["rect"].x - camera_x, platform["rect"].y))
        else:  
            pygame.draw.rect(screen, BLACK, (platform["rect"].x - camera_x, platform["rect"].y, platform["rect"].width, platform["rect"].height))

  
    if not game_over:
        if is_attacking:

            attack_frame_timer += delta_time
            if attack_frame_timer >= attack_animation_speed:
                attack_frame_timer = 0
                current_attack_frame = (current_attack_frame + 1) % len(attack_frames_right)
            if direction == "right":
                screen.blit(attack_frames_right[current_attack_frame], (player_rect.x - camera_x, player_rect.y))
            else:
                screen.blit(attack_frames_left[current_attack_frame], (player_rect.x - camera_x, player_rect.y))
        else:
            frame_timer += delta_time
            if frame_timer >= animation_speed:
                frame_timer = 0
                current_frame = (current_frame + 1) % len(frames_right)
            if direction == "right":
                screen.blit(frames_right[current_frame], (player_rect.x - camera_x, player_rect.y))
            else:
                screen.blit(frames_left[current_frame], (player_rect.x - camera_x, player_rect.y))
    else:
        screen.blit(finish_level_image, (0, 0))

    if not game_over:
        for enemy in enemies:
            enemy.update()
            enemy.draw(screen)

    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (10, 10))

    pygame.display.flip()

pygame.quit()
