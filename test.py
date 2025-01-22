import os
import pygame

# Инициализация Pygame
pygame.init()

# Константы
FPS = 20
WIDTH, HEIGHT = 800, 600
SPEED = 5  # Скорость движения по горизонтали
JUMP_POWER = 15  # Сила прыжка
GRAVITY = 1  # Гравитация

screen = pygame.display.set_mode((WIDTH, HEIGHT))
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


# Класс анимированного спрайта с движением и прыжком
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Физика
        self.velocity_x = 0  # Скорость по оси X
        self.velocity_y = 0  # Скорость по оси Y (для прыжка)
        self.on_ground = False  # Флаг проверки на землю

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.rect.x += self.velocity_x

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        if self.rect.bottom >= HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.velocity_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.velocity_x != 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]

    def move(self, direction):
        if direction == "left":
            self.velocity_x = -SPEED
        elif direction == "right":
            self.velocity_x = SPEED
        elif direction == "stop":
            self.velocity_x = 0

    def jump(self):
        if self.on_ground:
            self.velocity_y = -JUMP_POWER  # Применение силы прыжка
            self.on_ground = False


image_p = load_image('sprite_knight/knight.png')
fon = pygame.transform.scale(load_image('dark_forest.jpg'), (WIDTH, HEIGHT))

knight = AnimatedSprite(image_p, 6, 1, 100, 490)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        knight.move("left")
    elif keys[pygame.K_RIGHT]:
        knight.move("right")
    else:
        knight.move("stop")

    if keys[pygame.K_SPACE]:
        knight.jump()

    all_sprites.update()

    screen.blit(fon, (0, 0))
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
