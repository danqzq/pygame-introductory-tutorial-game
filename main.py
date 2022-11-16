import pygame

pygame.init()

# Constants
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

WINDOW_SIZE = (1280, 720)
WINDOW_TITLE = "Pygame Tutorial"

FRAME_RATE = 60

WINDOW = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption(WINDOW_TITLE)

CLOCK = pygame.time.Clock()

player_x = WINDOW_SIZE[0] / 2
player_y = WINDOW_SIZE[1] / 2
player_input = {"left": False, "right": False, "up": False, "down":False}
player_velocity = [0, 0]
player_speed = 5


def check_input(key, value):
    if key == pygame.K_LEFT or key == pygame.K_a:
        player_input["left"] = value
    elif key == pygame.K_RIGHT or key == pygame.K_d:
        player_input["right"] = value
    elif key == pygame.K_UP or key == pygame.K_w:
        player_input["up"] = value
    elif key == pygame.K_DOWN or key == pygame.K_s:
        player_input["down"] = value


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            check_input(event.key, True)
        elif event.type == pygame.KEYUP:
            check_input(event.key, False)

    player_velocity[0] = player_input["right"] - player_input["left"]
    player_velocity[1] = player_input["down"] - player_input["up"]

    WINDOW.fill(WHITE)

    pygame.draw.rect(WINDOW, RED, (600, 600, 200, 100))

    # Player
    pygame.draw.circle(WINDOW, BLACK, (player_x, player_y), 50)

    player_x += player_velocity[0] * player_speed
    player_y += player_velocity[1] * player_speed

    CLOCK.tick(FRAME_RATE)
    pygame.display.update()
