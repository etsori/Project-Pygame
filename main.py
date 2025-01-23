import os
import sys
import sqlite3
import pygame
import importlib.util

# Инициализация Pygame
pygame.init()
size = width, height = 800, 400
screen = pygame.display.set_mode(size)
FPS = 50
clock = pygame.time.Clock()

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    # Таблица для зарегистрированных пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    # Таблица для прогресса
    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (user_id INTEGER, level INTEGER, completed BOOLEAN)''')
    conn.commit()
    conn.close()

init_db()

# Функции для работы с базой данных
def register_user(username, password):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return c.lastrowid  # Возвращаем ID нового пользователя
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def get_user_progress(user_id):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("SELECT level, completed FROM progress WHERE user_id = ?", (user_id,))
    progress = c.fetchall()
    conn.close()
    return progress

def update_progress(user_id, level, completed):
    conn = sqlite3.connect('game.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO progress (user_id, level, completed) VALUES (?, ?, ?)",
              (user_id, level, completed))
    conn.commit()
    conn.close()

# Загрузка изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

# Завершение работы
def terminate():
    pygame.quit()
    sys.exit()

# Отрисовка текста
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

# Экран заставки
def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Нажмите любую клавишу для старта"]

    fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        font = pygame.font.SysFont('serif', 30)
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # Начинаем игру
        pygame.display.flip()
        clock.tick(FPS)

# Экран регистрации
def registration_screen():
    username = ""
    password = ""
    input_active = "username"  # Определяем, какое поле активно
    cursor_visible = True
    cursor_timer = 0

    while True:
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        draw_text(screen, "Регистрация", pygame.font.SysFont('serif', 50), (255, 255, 255), 300, 50)
        draw_text(screen, "Логин: " + username + ("|" if cursor_visible and input_active == "username" else ""), pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 150)
        draw_text(screen, "Пароль: " + "*" * len(password) + ("|" if cursor_visible and input_active == "password" else ""), pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 200)
        draw_text(screen, "Нажмите Enter для подтверждения", pygame.font.SysFont('serif', 20), (255, 255, 255), 250, 250)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username and password:
                        user_id = register_user(username, password)
                        if user_id:
                            print(f"Пользователь {username} зарегистрирован с ID: {user_id}")
                            return
                        else:
                            draw_text(screen, "Ошибка: пользователь уже существует", pygame.font.SysFont('serif', 20), (255, 0, 0), 250, 300)
                    else:
                        draw_text(screen, "Ошибка: заполните все поля", pygame.font.SysFont('serif', 20), (255, 0, 0), 250, 300)
                elif event.key == pygame.K_BACKSPACE:
                    if input_active == "username" and len(username) > 0:
                        username = username[:-1]
                    elif input_active == "password" and len(password) > 0:
                        password = password[:-1]
                elif event.key == pygame.K_TAB:
                    input_active = "password" if input_active == "username" else "username"
                else:
                    if event.unicode.isalnum():
                        if input_active == "username" and len(username) < 10:
                            username += event.unicode
                        elif input_active == "password" and len(password) < 10:
                            password += event.unicode

        cursor_timer += 1
        if cursor_timer >= 30:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        pygame.display.flip()
        clock.tick(FPS)

# Экран входа
def login_screen():
    username = ""
    password = ""
    input_active = "username"  # Определяем, какое поле активно
    cursor_visible = True
    cursor_timer = 0

    while True:
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        draw_text(screen, "Вход", pygame.font.SysFont('serif', 50), (255, 255, 255), 300, 50)
        draw_text(screen, "Логин: " + username + ("|" if cursor_visible and input_active == "username" else ""), pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 150)
        draw_text(screen, "Пароль: " + "*" * len(password) + ("|" if cursor_visible and input_active == "password" else ""), pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 200)
        draw_text(screen, "Нажмите Enter для подтверждения", pygame.font.SysFont('serif', 20), (255, 255, 255), 250, 250)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if username and password:
                        user_id = login_user(username, password)
                        if user_id:
                            print(f"Пользователь {username} вошел с ID: {user_id}")
                            return user_id
                        else:
                            draw_text(screen, "Ошибка: неверный логин или пароль", pygame.font.SysFont('serif', 20), (255, 0, 0), 250, 300)
                    else:
                        draw_text(screen, "Ошибка: заполните все поля", pygame.font.SysFont('serif', 20), (255, 0, 0), 250, 300)
                elif event.key == pygame.K_BACKSPACE:
                    if input_active == "username" and len(username) > 0:
                        username = username[:-1]
                    elif input_active == "password" and len(password) > 0:
                        password = password[:-1]
                elif event.key == pygame.K_TAB:
                    input_active = "password" if input_active == "username" else "username"
                else:
                    if event.unicode.isalnum():
                        if input_active == "username" and len(username) < 10:
                            username += event.unicode
                        elif input_active == "password" and len(password) < 10:
                            password += event.unicode

        cursor_timer += 1
        if cursor_timer >= 30:
            cursor_visible = not cursor_visible
            cursor_timer = 0

        pygame.display.flip()
        clock.tick(FPS)

# Экран уровней
def levels_screen(user_id):
    while True:
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        draw_text(screen, "Выберите уровень", pygame.font.SysFont('serif', 50), (255, 255, 255), 250, 50)

        # Кнопки уровней в виде квадратов
        progress = get_user_progress(user_id)
        for i in range(1, 4):
            color = (0, 255, 0) if any(p[0] == i and p[1] for p in progress) else (128, 128, 128)
            pygame.draw.rect(screen, color, (300, 150 + i * 50, 50, 50))
            draw_text(screen, str(i), pygame.font.SysFont('serif', 30), (255, 255, 255), 320, 160 + i * 50)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for i in range(1, 4):
                    if 300 <= x <= 350 and 150 + i * 50 <= y <= 200 + i * 50:
                        update_progress(user_id, i, True)  # Сохраняем прогресс
                        print(f"Выбран уровень {i}")
                        start_level(i)  # Запуск уровня

        pygame.display.flip()
        clock.tick(FPS)

# Главное меню
def main_menu():
    while True:
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        draw_text(screen, "Играть", pygame.font.SysFont('serif', 50), (255, 255, 255), 300, 50)
        draw_text(screen, "1. Регистрация", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 150)
        draw_text(screen, "2. Вход", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 200)
        draw_text(screen, "3. Правила игры", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 250)
        draw_text(screen, "4. Выход", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 300)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 300 <= x <= 500:
                    if 50 <= y <= 100:
                        start_level(1)  # Запуск уровня 1
                    elif 150 <= y <= 180:
                        registration_screen()
                    elif 200 <= y <= 230:
                        user_id = login_screen()
                        if user_id:
                            levels_screen(user_id)
                    elif 250 <= y <= 280:
                        rules_screen()
                    elif 300 <= y <= 330:
                        terminate()

        pygame.display.flip()
        clock.tick(FPS)

# Экран правил игры
def rules_screen():
    while True:
        screen.fill((0, 0, 0))
        fon = pygame.transform.scale(load_image('start.jpg'), (width, height))
        screen.blit(fon, (0, 0))

        draw_text(screen, "Правила игры", pygame.font.SysFont('serif', 50), (255, 255, 255), 250, 50)
        draw_text(screen, "1. Правило 1", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 150)
        draw_text(screen, "2. Правило 2", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 200)
        draw_text(screen, "3. Правило 3", pygame.font.SysFont('serif', 30), (255, 255, 255), 300, 250)
        draw_text(screen, "Нажмите любую клавишу для возврата", pygame.font.SysFont('serif', 20), (255, 255, 255), 250, 300)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)

# Запуск уровня
def start_level(level):
    level_file = f"level{level}.py"
    if not os.path.exists(level_file):
        print(f"Файл уровня '{level_file}' не найден")
        return

    # Динамическая загрузка модуля уровня
    spec = importlib.util.spec_from_file_location(f"level{level}", level_file)
    level_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(level_module)

    # Запуск уровня
    if hasattr(level_module, "run_level"):
        level_module.run_level()  # Запуск функции уровня
    else:
        print(f"Функция 'run_level' не найдена в файле '{level_file}'")

    # После завершения уровня переходим на следующий
    if level < 3:  # Если это не последний уровень
        start_level(level + 1)  # Переход на следующий уровень

# Основной цикл
running = True
main_menu()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()