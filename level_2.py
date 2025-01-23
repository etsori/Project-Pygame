import os
import pygame

pygame.init()

FPS = 25
width, height = 800, 600
SPEED = 5
GRAVITY = 0.8
JUMP_STRENGTH = 14
camera_x = 0

screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

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
    def __init__(self, walk_sheet, idle_sheet, columns, rows, x, y):
        super().__init__(walk_sheet, columns, rows, x, y)
        self.speed = SPEED
        self.direction = 1
        self.is_jumping = False
        self.velocity_y = 0
        self.walk_frames = self.frames
        self.idle_frames = self.cut_idle_sheet(idle_sheet, columns, rows)
        self.is_moving = False
        self.lives = 3  # Количество жизней

    def cut_idle_sheet(self, sheet, columns, rows):
        frames = []
        rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (rect.w * i, rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))
        return frames

    def update(self):
        keys = pygame.key.get_pressed()
        self.is_moving = False

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.direction = -1
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.direction = 1
            self.is_moving = True

        if not self.is_jumping:
            if keys[pygame.K_UP]:
                self.is_jumping = True
                self.velocity_y = -JUMP_STRENGTH
        else:
            self.velocity_y += GRAVITY

        self.rect.y += self.velocity_y

        self.check_collision()

        if not self.is_moving:
            self.frames = self.idle_frames
        else:
            self.frames = self.walk_frames

        super().update()
        self.image = pygame.transform.flip(self.frames[self.cur_frame], self.direction == -1, False)

    def check_collision(self):
        global camera_x

        on_ground = False

        # Проверка коллизий с платформами
        for platform in platforms:
            if self.rect.colliderect(platform["rect"]) and self.velocity_y > 0:
                if self.rect.bottom >= platform["rect"].top:
                    self.rect.bottom = platform["rect"].top
                    self.is_jumping = False
                    self.velocity_y = 0
                    on_ground = True

        # Гравитация, если не на платформе
        if not on_ground and self.rect.bottom < height:
            self.is_jumping = True



        # Камера центрируется на игроке
        camera_x = max(0, self.rect.centerx - width // 2)


# Класс врага (дерево)
class Enemy(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, width, height):
        super().__init__()
        self.image = pygame.transform.scale(load_image(image_path), (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen, camera_x):
        screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))


# Загрузка изображений
walk_image = load_image('sprite_knight/k_walkjpg.png')
k_image = load_image('sprite_knight/knight.png')

# Загрузка фона
background_image = load_image('dark_forest.jpg')
background_width = background_image.get_width()
background_height = background_image.get_height()
background = pygame.transform.scale(background_image, (background_width, height))

platform_image = pygame.image.load(os.path.join("data", "plat_unfon3.png")).convert_alpha()
platform_image = pygame.transform.scale(platform_image, (200, 60))
platform_image.set_colorkey((255, 255, 255))

# Платформы (опущены ниже)
platforms = [
    {"rect": pygame.Rect(0, height - 50, width * 4, 50), "image": None},  # Основная платформа внизу
    {"rect": pygame.Rect(300, 450, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(600, 320, 150, 20), "image": platform_image},
    {"rect": pygame.Rect(950, 250, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(1300, 450, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(1600, 320, 150, 20), "image": platform_image},
    {"rect": pygame.Rect(1950, 250, 200, 20), "image": platform_image},
]


knight = Player(walk_image, k_image, 6, 1, 100, 490)

running = True

while running:
    delta_time = clock.tick(FPS) / 1000  # Время в секундах с последнего кадра

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    # Отрисовка фона с повторением
    for i in range(-1, 2):  # Повторяем фон для создания эффекта бесконечности
        screen.blit(background, (i * background_width - camera_x % background_width, 0))

    # Отрисовка платформ
    for platform in platforms:
        if platform["image"]:  # Если есть изображение платформы
            screen.blit(platform["image"], (platform["rect"].x - camera_x, platform["rect"].y))
        else:  # Если платформа без изображения (основная платформа)
            pygame.draw.rect(screen, (0, 0, 0), (
                platform["rect"].x - camera_x, platform["rect"].y, platform["rect"].width, platform["rect"].height))

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    # Отображение жизней
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {knight.lives}", True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))

    pygame.display.update()

pygame.quit()