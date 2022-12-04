import pygame
import random
from itertools import repeat

pygame.init()
pygame.font.get_init()

TEXT_FONT = pygame.font.Font("assets/font.otf", 32)

# Constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

WINDOW_SIZE = (1280, 720)
WINDOW_TITLE = "Pygame Tutorial"

BOUNDS_X = (66, 1214)
BOUNDS_Y = (50, 620)

HORIZONTAL = 1
UP = 2
DOWN = 0

FRAME_RATE = 60
ANIMATION_FRAME_RATE = 10

SHAKE_WINDOW = pygame.display.set_mode(WINDOW_SIZE)
WINDOW = SHAKE_WINDOW.copy()
pygame.display.set_caption(WINDOW_TITLE)

CLOCK = pygame.time.Clock()

background = pygame.transform.scale(pygame.image.load("assets/background.png"), WINDOW_SIZE)

objects = []
bullets = []
enemies = []
particles = []

offset = repeat((0, 0))


class Object:
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.velocity = [0, 0]
        self.collider = [width, height]

        objects.append(self)

    def draw(self):
        WINDOW.blit(pygame.transform.scale(self.image, (self.width, self.height)), (self.x, self.y))

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
        image = pygame.transform.scale(self.tileset[self.frames[self.frame]][self.direction],
                                       (self.width, self.height))

        self.change_direction()

        image = pygame.transform.flip(image, self.flipX, False)
        WINDOW.blit(image, (self.x, self.y))

        if self.velocity[0] == 0 and self.velocity[1] == 0:
            self.frame = 0
            return

        self.frame_timer += 1

        if self.frame_timer < ANIMATION_FRAME_RATE:
            return

        self.frame += 1
        if self.frame >= len(self.frames):
            self.frame = 0

        self.frame_timer = 0

    def update(self):
        self.x += self.velocity[0] * self.speed
        self.y += self.velocity[1] * self.speed
        self.draw()


class Player(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.health = self.max_health = 3

    def update(self):
        super().update()

        self.x = max(BOUNDS_X[0], min(self.x, BOUNDS_X[1] - self.width))
        self.y = max(BOUNDS_Y[0], min(self.y, BOUNDS_Y[1] - self.height))


class Enemy(Entity):
    def __init__(self, x, y, width, height, tileset, speed):
        super().__init__(x, y, width, height, tileset, speed)
        self.max_width = width
        self.max_height = height
        self.width = 0
        self.height = 0

        self.health = 3
        self.collider = [width / 2.5, height / 1.5]
        enemies.append(self)

        self.start_timer = 0

    def cooldown(self):
        if self.start_timer < 1:
            self.start_timer += 0.03
            self.x -= 1
            self.y -= 1
        self.width = int(self.max_width * self.start_timer)
        self.height = int(self.max_height * self.start_timer)

    def update(self):
        player_center = player.get_center()
        enemy_center = self.get_center()

        self.velocity = [player_center[0] - enemy_center[0], player_center[1] - enemy_center[1]]

        magnitude = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        self.velocity = [self.velocity[0] / magnitude * self.speed, self.velocity[1] / magnitude * self.speed]

        self.cooldown()
        if self.start_timer < 1:
            self.velocity = [0, 0]

        super().update()

    def change_direction(self):
        super().change_direction()

        if self.velocity[1] > self.velocity[0] > 0:
            self.direction = DOWN
        elif self.velocity[1] < self.velocity[0] < 0:
            self.direction = UP

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            global score
            score += 1
            self.destroy()

    def destroy(self):
        spawn_particles(self.x, self.y)
        global offset
        offset = screen_shake(5, 20)
        objects.remove(self)
        enemies.remove(self)


def check_input(key, value):
    if key == pygame.K_LEFT or key == pygame.K_a:
        player_input["left"] = value
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        player_input["right"] = value
    elif key == pygame.K_UP or key == pygame.K_w:
        player_input["up"] = value
    elif key == pygame.K_DOWN or key == pygame.K_s:
        player_input["down"] = value


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


def enemy_spawner():
    while True:
        for i in range(60):
            yield
        randomX = random.randint(BOUNDS_X[0], BOUNDS_X[1] - 75)
        randomY = random.randint(BOUNDS_Y[0], BOUNDS_Y[1] - 75)
        enemy = Enemy(randomX, randomY, 75, 75, "assets/enemy-Sheet.png", 2)
        player_center = player.get_center()
        while abs(player_center[0] - enemy.x) < 250 and abs(player_center[1] - enemy.y) < 250:
            enemy.x = random.randint(BOUNDS_X[0], BOUNDS_X[1] - 75)
            enemy.y = random.randint(BOUNDS_Y[0], BOUNDS_Y[1] - 75)


def spawn_particles(x, y):
    particle = Object(x, y, 75, 75, pygame.image.load("assets/particles.png"))
    particles.append(particle)


def screen_shake(intensity, amplitude):
    s = -1
    for i in range(0, 3):
        for x in range(0, amplitude, intensity):
            yield x * s, 0
        for x in range(amplitude, 0, intensity):
            yield x * s, 0
        s *= -1
    while True:
        yield 0, 0


score = 0

is_game_over = False
player_input = {"left": False, "right": False, "up": False, "down": False}

# Objects
player = Player(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, 75, 75, "assets/player-Sheet.png", 5)
target = Object(0, 0, 50, 50, pygame.image.load("assets/cursor.png"))
spawner = enemy_spawner()

pygame.mouse.set_visible(False)


def shoot():
    global target

    player_center = player.get_center()
    bullet = Object(player_center[0], player_center[1], 16, 16, pygame.image.load("assets/bullet.png"))

    target_center = target.get_center()
    bullet.velocity = [target_center[0] - player_center[0], target_center[1] - player_center[1]]

    magnitude = (bullet.velocity[0] ** 2 + bullet.velocity[1] ** 2) ** 0.5

    bullet.velocity = [bullet.velocity[0] / magnitude * 10, bullet.velocity[1] / magnitude * 10]

    bullets.append(bullet)

    target.width += 20
    target.height += 20


def check_collisions(obj1, obj2):
    x1, y1 = obj1.get_center()
    x2, y2 = obj2.get_center()
    w1, h1 = obj1.collider[0] / 2, obj1.collider[1] / 2
    w2, h2 = obj2.collider[0] / 2, obj2.collider[1] / 2
    if x1 + w1 > x2 - w2 and x1 - w1 < x2 + w2:
        return y1 + h1 > y2 - h2 and y1 - h1 < y2 + h2
    return False


def display_ui():
    for i in range(player.max_health):
        img = pygame.image.load("assets/heart_empty.png" if i >= player.health else "assets/heart.png")
        img = pygame.transform.scale(img, (50, 50))
        WINDOW.blit(img, (i * 50 + WINDOW_SIZE[0] / 2 - player.max_health * 25, 25))

    score_text = TEXT_FONT.render(f'Score: {score}', True, BLACK)
    WINDOW.blit(score_text, (score_text.get_width() / 2, 25))

    if is_game_over:
        game_over_text = TEXT_FONT.render("Game over!", True, BLACK)
        WINDOW.blit(game_over_text, (WINDOW_SIZE[0] / 2 - game_over_text.get_width() / 2,
                                     WINDOW_SIZE[1] / 2 - game_over_text.get_height() / 2))


def update_screen():
    CLOCK.tick(FRAME_RATE)
    SHAKE_WINDOW.blit(WINDOW, next(offset))
    pygame.display.update()


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            check_input(event.key, True)
        elif event.type == pygame.KEYUP:
            check_input(event.key, False)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            shoot()

    mousePos = pygame.mouse.get_pos()
    target.x = mousePos[0] - target.width / 2
    target.y = mousePos[1] - target.height / 2

    player.velocity[0] = player_input["right"] - player_input["left"]
    player.velocity[1] = player_input["down"] - player_input["up"]

    WINDOW.blit(background, (0, 0))

    display_ui()

    if is_game_over:
        pygame.mouse.set_visible(True)
        update_screen()
        continue

    next(spawner)

    if player.health <= 0:
        if not is_game_over:
            is_game_over = True

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

    if target.width > 50:
        target.width -= 2
        target.height -= 2

    for obj in objects:
        obj.update()

    for b in bullets:
        if BOUNDS_X[0] <= b.x <= BOUNDS_X[1] and BOUNDS_Y[0] <= b.y <= BOUNDS_Y[1]:
            continue
        bullets.remove(b)
        objects.remove(b)

    for e in enemies:
        if check_collisions(player, e):
            player.health -= 1
            e.destroy()
            continue
        for b in bullets:
            if check_collisions(b, e):
                e.take_damage(1)
                bullets.remove(b)
                objects.remove(b)

    update_screen()
