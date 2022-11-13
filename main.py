import pygame
import random
from itertools import repeat

pygame.init()
pygame.font.get_init()

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

WINDOW_SIZE = (1280, 720)
WINDOW_TITLE = "Baller Knight"

FRAME_RATE = 144

BOUNDS_X = (66, 1214)
BOUNDS_Y = (50, 620)

DOWN, HORIZONTAL, UP = 0, 1, 2

PLAYER_SIZE = ENEMY_SIZE = PARTICLES_SIZE = (72, 72)
BULLET_SIZE = (16, 16)
CURSOR_MIN_SIZE = 50
CURSOR_INCREASE_EFFECT = 25
CURSOR_SHRINK_SPEED = 3

BACKGROUND = "assets/background.png"
PLAYER_TILESET = "assets/player-Sheet.png"
ENEMY_TILESET = "assets/enemy-Sheet.png"
BULLET = "assets/bullet.png"
CURSOR = "assets/cursor.png"
HEART_FULL = "assets/heart.png"
HEART_EMPTY = "assets/heart_empty.png"
PARTICLES = "assets/particles.png"

SAVE_FILE = "save_file.txt"

START_GAME_TEXT = "Press 'SPACE' to Start!"
GAME_OVER_TEXT = "Game Over! Press 'R' to Restart."

# Game Settings
DIFFICULTY = 1
PLAYER_MAX_HEALTH = 3
ENEMY_MAX_HEALTH = 3
BULLET_SPEED = 10
ENEMY_SPAWN_DISTANCE = 250


shake_window = pygame.display.set_mode(WINDOW_SIZE)
window = shake_window.copy()
clock = pygame.time.Clock()

text_font = pygame.font.Font("assets/font.otf", 32)

objects = []

offset = repeat((0, 0))


class Object:
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = None if image is None else pygame.image.load(image).convert_alpha()
        self.collider = [width, height]
        self.velocity = [0, 0]
        objects.append(self)

    def draw(self):
        window.blit(pygame.transform.scale(self.image, (self.width, self.height)), (self.x, self.y))

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.draw()

    def get_center(self):
        return self.x + self.width / 2, self.y + self.height / 2


class Entity(Object):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, None)
        self.speed = speed

        self.tileset = load_tileset(tileset, 16, 16)
        self.direction = 0
        self.flipX = False
        self.frame = 0
        self.frames = [0, 1, 0, 2]
        self.frame_timer = 0

    def change_direction(self):
        if self.velocity[0] < 0:
            self.direction = HORIZONTAL
            self.flipX = True
        elif self.velocity[0] > 0:
            self.direction = HORIZONTAL
            self.flipX = False
        elif self.velocity[1] > 0:
            self.direction = DOWN
        elif self.velocity[1] < 0:
            self.direction = UP

    def draw(self):
        img = pygame.transform.scale(self.tileset[self.frames[self.frame]][self.direction], (self.width, self.height))

        self.change_direction()

        img = pygame.transform.flip(img, self.flipX, False)
        window.blit(img, (self.x, self.y))

        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.frame = 0
            return

        self.frame_timer += 1

        if self.frame_timer < 10:
            return

        self.frame += 1
        if self.frame >= 4:
            self.frame = 0

        self.frame_timer = 0


def load_tileset(filename, width, height):
    image = pygame.image.load(filename).convert_alpha()
    image_width, image_height = image.get_size()
    tileset = []
    for tile_x in range(0, image_width // width):
        line = []
        tileset.append(line)
        for tile_y in range(0, image_height // height):
            rect = (tile_x * width, tile_y * height, width, height)
            line.append(image.subsurface(rect))
    return tileset


class Player(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.health = self.max_health = PLAYER_MAX_HEALTH


class Enemy(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.m_width = width
        self.m_height = height
        self.width = 0
        self.height = 0
        self.grow_speed = 2

        self.collider = [width / 1.8, height / 1.2]
        self.health = ENEMY_MAX_HEALTH
        enemies.append(self)

    def update(self):
        if self.width < self.m_width:
            self.width += self.grow_speed
        if self.height < self.m_height:
            self.height += self.grow_speed

        player_center = player.get_center()
        self.velocity = [player_center[0] - self.x, player_center[1] - self.y]
        length = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        self.velocity = [self.velocity[0] / length, self.velocity[1] / length]
        self.velocity = [self.velocity[0] * self.speed, self.velocity[1] * self.speed]

        super().update()

    def change_direction(self):
        if self.velocity[0] < 0:
            self.direction = HORIZONTAL
            self.flipX = True
        elif self.velocity[0] > 0:
            self.direction = HORIZONTAL
            self.flipX = False

        if self.velocity[1] > self.velocity[0] > 0:
            self.direction = DOWN
        elif self.velocity[1] < self.velocity[0] < 0:
            self.direction = UP

    def take_damage(self, damage):
        self.health -= damage
        if self.health > 0:
            return

        global score, offset
        score += 1
        offset = screen_shake(6, 7)
        spawn_particles(self.x, self.y)

        self.destroy()

    def destroy(self):
        objects.remove(self)
        enemies.remove(self)


# Objects
global player, bullets
target = Object(100, 100, CURSOR_MIN_SIZE, CURSOR_MIN_SIZE, CURSOR)
enemies = []
particles = []

# Game Variables
global score, high_score, save_file

has_game_started = False
is_game_over = False


# Functions
def load_high_score():
    global high_score, save_file
    save_file = open(SAVE_FILE, "r")
    high_score = int(save_file.read())
    save_file.close()


def start():
    global player, bullets, score
    player = Player(WINDOW_SIZE[0] / 2 - 37.5, WINDOW_SIZE[1] / 2 - 37.5, 75, 75, PLAYER_TILESET, 4)
    player.collider = [player.width / 2, player.height / 1.5]

    bullets = []

    score = 0
    load_high_score()


def game_over():
    global is_game_over, high_score, save_file
    if score > high_score:
        save_file = open(SAVE_FILE, "w")
        save_file.write(str(score))
        save_file.close()

    is_game_over = True


def shoot():
    player_center = player.get_center()
    bullet = Object(player_center[0], player_center[1], BULLET_SIZE[0], BULLET_SIZE[1], BULLET)
    bullet.velocity = [target.x - bullet.x, target.y - bullet.y]

    length = (bullet.velocity[0] ** 2 + bullet.velocity[1] ** 2) ** 0.5

    bullet.velocity = [bullet.velocity[0] / length, bullet.velocity[1] / length]
    bullet.velocity = [bullet.velocity[0] * BULLET_SPEED, bullet.velocity[1] * BULLET_SPEED]

    bullets.append(bullet)

    target.width += CURSOR_INCREASE_EFFECT
    target.height += CURSOR_INCREASE_EFFECT


def restart():
    global player, enemies, bullets, particles, objects, score, is_game_over

    objects.remove(player)

    start()

    for x in enemies:
        x.destroy()

    for x in bullets:
        objects.remove(x)
        bullets.remove(x)
        
    for x in particles:
        objects.remove(x)
        particles.remove(x)

    score = 0
    load_high_score()
    is_game_over = False


def check_collisions(obj1, obj2):
    if obj1.x + obj1.collider[0] > obj2.x and obj1.x < obj2.x + obj2.collider[0]:
        return obj1.y + obj1.collider[1] > obj2.y and obj1.y < obj2.y + obj2.collider[1]
    return False


def handle_event(evt):
    if evt.type == pygame.QUIT:
        exit()
    elif evt.type == pygame.KEYDOWN:
        if evt.key == pygame.K_a:
            player.velocity[0] = -player.speed
        elif evt.key == pygame.K_d:
            player.velocity[0] = player.speed
        elif evt.key == pygame.K_w:
            player.velocity[1] = -player.speed
        elif evt.key == pygame.K_s:
            player.velocity[1] = player.speed
        elif evt.key == pygame.K_r:
            restart()
        elif evt.key == pygame.K_SPACE:
            global has_game_started
            has_game_started = True
    elif evt.type == pygame.KEYUP:
        if evt.key == pygame.K_a or evt.key == pygame.K_d:
            player.velocity[0] = 0
        elif evt.key == pygame.K_w or evt.key == pygame.K_s:
            player.velocity[1] = 0
    elif evt.type == pygame.MOUSEBUTTONDOWN:
        shoot()


def display_ui():
    if not has_game_started:
        game_over_text = text_font.render(START_GAME_TEXT, True, BLACK)
        window.blit(game_over_text, (WINDOW_SIZE[0] / 2 - game_over_text.get_width() / 2,
                                     WINDOW_SIZE[1] / 2 - game_over_text.get_height() / 2))
        return

    for i in range(player.max_health):
        img = pygame.image.load(HEART_EMPTY if i >= player.health else HEART_FULL)
        img = pygame.transform.scale(img, (50, 50))
        window.blit(img, (i * 50 + WINDOW_SIZE[0] / 2 - player.max_health * 25, 25))

    score_text = text_font.render(f'Score: {score}', True, BLACK)
    window.blit(score_text, (score_text.get_width() / 2, 0 + 25))

    high_score_text = text_font.render(f'High Score: {high_score}', True, BLACK)
    window.blit(high_score_text, (WINDOW_SIZE[0] - high_score_text.get_width() - 75, 0 + 25))

    if is_game_over:
        game_over_text = text_font.render(GAME_OVER_TEXT, True, BLACK)
        window.blit(game_over_text, (WINDOW_SIZE[0] / 2 - game_over_text.get_width() / 2,
                                     WINDOW_SIZE[1] / 2 - game_over_text.get_height() / 2))


def enemy_spawner():
    if len(enemies) > (score + 10) // (10 / DIFFICULTY):
        return
    randomX = random.randint(BOUNDS_X[0], BOUNDS_X[1] - ENEMY_SIZE[0])
    randomY = random.randint(BOUNDS_Y[0], BOUNDS_Y[1] - ENEMY_SIZE[1])
    en = Enemy(randomX, randomY, ENEMY_SIZE[0], ENEMY_SIZE[1], ENEMY_TILESET, 1.5)
    player_center = player.get_center()
    if abs(player_center[0] - en.x) < ENEMY_SPAWN_DISTANCE and abs(player_center[1] - en.y) < ENEMY_SPAWN_DISTANCE:
        objects.remove(en)
        enemies.remove(en)


def screen_shake(intensity, amplitude=20):
    s = -1
    for _ in range(0, 3):
        for x in range(0, amplitude, intensity):
            yield x * s, 0
        for x in range(amplitude, 0, intensity):
            yield x * s, 0
        s *= -1
    while True:
        yield 0, 0


def spawn_particles(x, y):
    particle = Object(x, y, PARTICLES_SIZE[0], PARTICLES_SIZE[1], PARTICLES)
    particles.append(particle)


def update_screen():
    clock.tick(FRAME_RATE)
    shake_window.blit(window, next(offset))
    pygame.display.update()


player_tileset = load_tileset(PLAYER_TILESET, 16, 16)
pygame.display.set_icon(player_tileset[0][0])
pygame.display.set_caption(WINDOW_TITLE)

start()

# Game loop
while True:
    for event in pygame.event.get():
        handle_event(event)

    player.x = max(BOUNDS_X[0], min(player.x, BOUNDS_X[1] - player.width))
    player.y = max(BOUNDS_Y[0], min(player.y, BOUNDS_Y[1] - player.height))

    background = pygame.transform.scale(pygame.image.load(BACKGROUND), (1280, 720))
    window.blit(background, (0, 0))

    display_ui()

    if not has_game_started:
        update_screen()
        continue

    if player.health <= 0:
        if not is_game_over:
            game_over()
        pygame.mouse.set_visible(True)
        update_screen()
        continue

    objects.remove(target)
    objects.sort(key=lambda o: o.y)
    objects.append(target)

    for p in particles:
        p.image.set_alpha(p.image.get_alpha() - 1)
        if p.image.get_alpha() == 0:
            objects.remove(p)
            particles.remove(p)
            continue
        objects.remove(p)
        objects.insert(0, p)

    pygame.mouse.set_visible(False)
    mousePos = pygame.mouse.get_pos()
    target.x = mousePos[0] - target.width / 2
    target.y = mousePos[1] - target.height / 2

    if target.width > CURSOR_MIN_SIZE:
        target.width -= CURSOR_SHRINK_SPEED
    if target.height > CURSOR_MIN_SIZE:
        target.height -= CURSOR_SHRINK_SPEED

    for obj in objects:
        obj.update()

    for b in bullets:
        if BOUNDS_X[0] <= b.x <= BOUNDS_X[1] and BOUNDS_Y[0] <= b.y <= BOUNDS_Y[1]:
            continue
        bullets.remove(b)
        objects.remove(b)
        pygame.mouse.set_visible(True)
        del b

    for e in enemies:
        if check_collisions(e, player):
            player.health -= 1
            objects.remove(e)
            enemies.remove(e)
            global offset
            offset = screen_shake(5)
            spawn_particles(e.x, e.y)
            continue
        for b in bullets:
            if check_collisions(e, b):
                e.take_damage(1)
                bullets.remove(b)
                objects.remove(b)

    enemy_spawner()
    update_screen()
