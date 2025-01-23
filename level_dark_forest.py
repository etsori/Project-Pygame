import os
import pygame

pygame.init()

FPS = 30
width, height = 800, 600
SPEED = 3
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

        # Гравитация если не на платформе
        if not on_ground and self.rect.bottom < height:
            self.is_jumping = True

        # Не выходить за нижнюю границу экрана
        if self.rect.bottom >= height:
            self.rect.bottom = height
            self.is_jumping = False
            self.velocity_y = 0

        # Камера центрируется на игроке
        camera_x = max(0, self.rect.centerx - width // 2)


walk_image = load_image('sprite_knight/k_walkjpg.png')
k_image = load_image('sprite_knight/knight.png')
background = pygame.transform.scale(load_image('dark_forest.jpg'), (width * 4, height))

platform_image = pygame.image.load(os.path.join("data", "plat_unfon3.png")).convert_alpha()
platform_image = pygame.transform.scale(platform_image, (200, 60))
platform_image.set_colorkey((255, 255, 255))

platforms = [
    {"rect": pygame.Rect(0, height - 50, width * 4, 50), "image": None},  # нижняя платформа
    {"rect": pygame.Rect(300, 400, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(600, 270, 150, 20), "image": platform_image},
    {"rect": pygame.Rect(950, 200, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(1300, 400, 200, 20), "image": platform_image},
    {"rect": pygame.Rect(1600, 270, 150, 20), "image": platform_image},
    {"rect": pygame.Rect(1950, 200, 200, 20), "image": platform_image},
]
knight = Player(walk_image, k_image, 6, 1, 100, 490)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    screen.blit(background, (-camera_x, 0))

    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

    pygame.display.update()
    clock.tick(FPS)
