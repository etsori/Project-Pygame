import os
import pygame

# Инициализация Pygame
pygame.init()

# Константы
FPS = 60
width, height = 800, 600
SPEED = 4  # Плавная скорость движения
GRAVITY = 0.6  # Гравитация
JUMP_STRENGTH = 12  # Сила прыжка
camera_x = 0  # Смещение камеры

# Экран и таймер
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Knight Adventure")
clock = pygame.time.Clock()

# Группы спрайтов
all_sprites = pygame.sprite.Group()


# Функция загрузки изображений
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Player(AnimatedSprite):
    def __init__(self, walk_sheet, idle_sheet, attack_sheet, columns, rows, x, y):
        super().__init__(walk_sheet, columns, rows, x, y)
        self.speed = SPEED
        self.direction = 1  # 1 - вправо, -1 - влево
        self.is_jumping = False
        self.velocity_y = 0  # Вертикальная скорость
        self.walk_frames = self.frames
        self.idle_frames = self.cut_sheet(idle_sheet, columns, rows)
        self.attack_frames = self.cut_sheet(attack_sheet, columns, rows)
        self.state = 'idle'  # idle, walk, attack

    def update(self):
        keys = pygame.key.get_pressed()
        self.velocity_y += GRAVITY  # Гравитация всегда

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = -1
            self.state = 'walk'
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 1
            self.state = 'walk'
        elif keys[pygame.K_SPACE]:  # Атака
            self.state = 'attack'
        else:
            self.state = 'idle'

        # Прыжок
        if not self.is_jumping and keys[pygame.K_UP]:
            self.is_jumping = True
            self.velocity_y = -JUMP_STRENGTH

        self.rect.y += self.velocity_y

        # Проверка на платформы
        self.check_collision()

        # Выбор нужной анимации
        if self.state == 'walk':
            self.frames = self.walk_frames
        elif self.state == 'attack':
            self.frames = self.attack_frames
        else:
            self.frames = self.idle_frames

        super().update()
        self.image = pygame.transform.flip(self.frames[self.cur_frame], self.direction == -1, False)

    def check_collision(self):
        global camera_x
        on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform["rect"]) and self.velocity_y > 0:
                self.rect.bottom = platform["rect"].top
                self.velocity_y = 0
                self.is_jumping = False
                on_ground = True

        if not on_ground and self.rect.bottom < height:
            self.is_jumping = True

        if self.rect.bottom >= height:
            self.rect.bottom = height
            self.is_jumping = False
            self.velocity_y = 0

        camera_x = max(0, self.rect.centerx - width // 2)


# Загрузка изображений
walk_image = load_image('sprite_knight/k_walkjpg.png')
idle_image = load_image('sprite_knight/knight.png')
attack_image = load_image('sprite_knight/k_attack.png')
background = pygame.transform.scale(load_image('dark_forest.jpg'), (width * 2, height))

# Загрузка изображения платформы
platform_image = pygame.image.load(os.path.join("data", "platform.png")).convert_alpha()
platform_image = pygame.transform.scale(platform_image, (200, 40))
platform_image.set_colorkey((255, 255, 255))

# Список платформ (более аккуратный дизайн)
platforms = [
    {"rect": pygame.Rect(0, height - 50, width * 2, 50), "image": None},  # Земля
    {"rect": pygame.Rect(300, 450, 200, 40), "image": platform_image},  # Средняя платформа
    {"rect": pygame.Rect(700, 350, 200, 40), "image": platform_image},  # Верхняя платформа
    {"rect": pygame.Rect(1100, 500, 200, 40), "image": platform_image},  # Дальняя платформа
]

# Создание игрока
knight = Player(walk_image, idle_image, attack_image, 6, 1, 100, height - 100)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    # Отрисовка фона с учетом смещения камеры
    screen.blit(background, (-camera_x, 0))

    # Отрисовка платформ
    for platform in platforms:
        if platform["image"]:
            screen.blit(platform["image"], (platform["rect"].x - camera_x, platform["rect"].y))

    # Отрисовка игрока с учетом камеры
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
