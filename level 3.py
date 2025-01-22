import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Legend of the Knight")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Загрузка изображений
try:
    bg = pygame.image.load('dragon.jpg')  # Фон
    player_sheet = pygame.image.load('data/sprite_knight\k_walkjpg.png').convert_alpha()  # Спрайтовый лист для игрока
    platform_image = pygame.image.load('start.jpg')  # Платформа
    dragon_image = pygame.image.load('dragon.png').convert_alpha()  # Дракон
    spike_image = pygame.image.load('spike.png').convert_alpha()  # Шипы
    fireball_sheet = pygame.image.load('fireball.png').convert_alpha()  # Спрайтовый лист для огненных шаров
except FileNotFoundError as e:
    print(f"Ошибка загрузки изображений: {e}")
    sys.exit()

# Класс для анимированных спрайтов
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.animation_speed = 10  # Скорость анимации
        self.frame_counter = 0

    def cut_sheet(self, sheet, columns, rows):
        frame_width = sheet.get_width() // columns
        frame_height = sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (frame_width * i, frame_height * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, (frame_width, frame_height))))

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]
            self.frame_counter = 0

# Класс игрока
class Player(AnimatedSprite):
    def __init__(self):
        super().__init__(player_sheet, 6, 1, 100, 500)  # 6 кадров в спрайтовом листе
        self.change_x = 0
        self.change_y = 0
        self.level = None
        self.right = True
        self.lives = 5  # Количество жизней
        self.coins = 0  # Количество монеток
        self.attacking = False  # Атака

    def update(self):
        super().update()
        # Гравитация
        self.calc_grav()

        # Движение по горизонтали
        self.rect.x += self.change_x

        # Проверка столкновений с платформами
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right

        # Движение по вертикали
        self.rect.y += self.change_y

        # Проверка столкновений с платформами
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
                self.change_y = 0
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
                self.change_y = 0

        # Проверка столкновения с шипами
        spike_hit_list = pygame.sprite.spritecollide(self, self.level.spike_list, False)
        if spike_hit_list:
            self.lives -= 1
            if self.lives <= 0:
                print("Игра окончена!")
                pygame.quit()
                sys.exit()

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.35

        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    def go_left(self):
        self.change_x = -6
        if self.right:
            self.flip()
            self.right = False

    def go_right(self):
        self.change_x = 6
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        self.change_x = 0

    def flip(self):
        # Переворот изображения
        self.image = pygame.transform.flip(self.image, True, False)

    def attack(self):
        self.attacking = True
        # Логика атаки (например, проверка столкновения с драконом)
        if self.level.dragon and pygame.sprite.collide_rect(self, self.level.dragon):
            self.level.dragon.take_damage()

# Класс платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

# Класс шипов
class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = spike_image
        self.rect = self.image.get_rect(topleft=(x, y))

# Класс монетки
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)  # Прозрачная поверхность
        pygame.draw.circle(self.image, YELLOW, (10, 10), 10)  # Желтый кружок
        self.rect = self.image.get_rect(topleft=(x, y))

# Класс анимированного огненного шара
class AnimatedFireball(AnimatedSprite):
    def __init__(self, x, y, direction):
        super().__init__(fireball_sheet, 4, 1, x, y)  # 4 кадра в спрайтовом листе
        self.speed = -10 if direction == "left" else 10  # Скорость огненного шара
        self.direction = direction

    def update(self):
        super().update()
        self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH:
            self.kill()

# Класс дракона
class Dragon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = dragon_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 3  # Здоровье дракона
        self.fireballs = pygame.sprite.Group()  # Группа огненных шаров
        self.fireball_cooldown = 2000  # Задержка между выстрелами (2 секунды)
        self.last_shot_time = pygame.time.get_ticks()

    def update(self, player):
        # Стрельба огненными шарами, если игрок в зоне видимости
        if abs(self.rect.x - player.rect.x) < 500:  # Зона видимости дракона
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.fireball_cooldown:
                self.shoot_fireball(player)
                self.last_shot_time = current_time

        self.fireballs.update()

    def shoot_fireball(self, player):
        # Определяем направление огненного шара
        direction = "left" if player.rect.x < self.rect.x else "right"
        fireball = AnimatedFireball(self.rect.x, self.rect.y + 50, direction)
        self.fireballs.add(fireball)

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            print("Дракон побежден!")
            pygame.quit()
            sys.exit()

# Класс уровня
class Level:
    def __init__(self, player):
        self.platform_list = pygame.sprite.Group()
        self.coin_list = pygame.sprite.Group()
        self.spike_list = pygame.sprite.Group()
        self.player = player
        self.world_shift = 0
        self.dragon = None

    def update(self):
        self.platform_list.update()
        self.coin_list.update()
        self.spike_list.update()
        if self.dragon:
            self.dragon.update(self.player)

    def draw(self, screen):
        screen.blit(bg, (self.world_shift // 3, 0))
        self.platform_list.draw(screen)
        self.coin_list.draw(screen)
        self.spike_list.draw(screen)
        if self.dragon:
            screen.blit(self.dragon.image, self.dragon.rect)
            self.dragon.fireballs.draw(screen)

    def shift_world(self, shift_x):
        self.world_shift += shift_x
        for platform in self.platform_list:
            platform.rect.x += shift_x
        for coin in self.coin_list:
            coin.rect.x += shift_x
        for spike in self.spike_list:
            spike.rect.x += shift_x
        if self.dragon:
            self.dragon.rect.x += shift_x

# Уровень 1
class Level_01(Level):
    def __init__(self, player):
        Level.__init__(self, player)

        level = [
            [210, 32, 500, 500],
            [210, 32, 800, 400],
            [210, 32, 1200, 300],
            [210, 32, 1600, 500],
            [210, 32, 2000, 400],
            [210, 32, 2400, 300],
            [210, 32, 2800, 500],
        ]

        for platform in level:
            block = Platform(platform[0], platform[1], platform[2], platform[3])
            self.platform_list.add(block)

        # Добавляем монетки
        coins = [
            [600, 450],
            [900, 350],
            [1300, 250],
            [1700, 450],
            [2100, 350],
            [2500, 250],
        ]

        for coin in coins:
            coin_obj = Coin(coin[0], coin[1])
            self.coin_list.add(coin_obj)

        # Добавляем шипы
        spikes = [
            [700, 550],
            [1000, 450],
            [1900, 500],
        ]

        for spike in spikes:
            spike_obj = Spike(spike[0], spike[1])
            self.spike_list.add(spike_obj)

        # Добавляем дракона в конце уровня
        self.dragon = Dragon(2800, 300)  # Дракон летает в воздухе

# Основная функция
def main():
    player = Player()
    level = Level_01(player)
    player.level = level

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    clock = pygame.time.Clock()
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_SPACE:  # Атака
                    player.attack()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        # Сдвиг мира, если игрок достигает середины экрана
        if player.rect.x >= 500:
            diff = player.rect.x - 500
            player.rect.x = 500
            level.shift_world(-diff)

        # Проверка сбора монеток
        coin_hit_list = pygame.sprite.spritecollide(player, level.coin_list, True)
        for coin in coin_hit_list:
            player.coins += 1
            print(f"Монеток собрано: {player.coins}")

        # Проверка столкновения с огненными шарами
        if level.dragon:
            fireball_hit_list = pygame.sprite.spritecollide(player, level.dragon.fireballs, True)
            if fireball_hit_list:
                player.lives -= 1
                if player.lives <= 0:
                    print("Игра окончена!")
                    done = True

        all_sprites.update()
        level.update()

        screen.fill(WHITE)
        level.draw(screen)
        all_sprites.draw(screen)

        # Отображение жизней (красные сердечки)
        font = pygame.font.Font(None, 36)
        lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
        screen.blit(lives_text, (10, 10))

        # Рисуем красные сердечки
        heart_radius = 10
        heart_spacing = 30
        for i in range(player.lives):
            pygame.draw.circle(screen, RED, (20 + i * heart_spacing, 50), heart_radius)

        # Отображение монеток
        coins_text = font.render(f"Монетки: {player.coins}", True, YELLOW)
        screen.blit(coins_text, (10, 80))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()