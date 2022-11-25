import pygame

pygame.init()

# Constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

WINDOW_SIZE = (1280, 720)
WINDOW_TITLE = "Pygame Tutorial"

HORIZONTAL = 1
UP = 2
DOWN = 0

FRAME_RATE = 60
ANIMATION_FRAME_RATE = 10

WINDOW = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption(WINDOW_TITLE)

CLOCK = pygame.time.Clock()

background = pygame.transform.scale(pygame.image.load("assets/background.png"), WINDOW_SIZE)

objects = []


class Object:
    def __init__(self, x, y, width, height, image):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.velocity = [0, 0]

        objects.append(self)

    def draw(self):
        WINDOW.blit(pygame.transform.scale(self.image, (self.width, self.height)), (self.x, self.y))

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.draw()


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
        image = pygame.transform.scale(self.tileset[self.frames[self.frame]][self.direction], (self.width, self.height))

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


player_input = {"left": False, "right": False, "up": False, "down": False}


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


# Objects
#test_object = Object(400, 400, 50, 50, pygame.image.load("assets/heart.png"))
#test_entity = Entity(400, 400, 50, 50, "assets/player-Sheet.png", 5)
player = Player(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, 75, 75, "assets/player-Sheet.png", 5)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            check_input(event.key, True)
        elif event.type == pygame.KEYUP:
            check_input(event.key, False)

    player.velocity[0] = player_input["right"] - player_input["left"]
    player.velocity[1] = player_input["down"] - player_input["up"]

    WINDOW.blit(background, (0, 0))

    for obj in objects:
        obj.update()

    CLOCK.tick(FRAME_RATE)
    pygame.display.update()
