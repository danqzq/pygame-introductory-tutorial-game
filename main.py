import pygame

pygame.init()

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

WINDOW_SIZE = (1280, 720)
WINDOW_TITLE = "Pygame Tutorial"

FRAME_RATE = 144

PLAYER_SIZE = (72, 72)

window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()


player_x = WINDOW_SIZE[0] / 2 - PLAYER_SIZE[0] / 2
player_y = WINDOW_SIZE[1] / 2 - PLAYER_SIZE[1] / 2
player_velocity = [0, 0]
player_speed = 5


def handle_event(evt):
    if evt.type == pygame.QUIT:
        exit()
    elif evt.type == pygame.KEYDOWN:
        if evt.key == pygame.K_a:
            player_velocity[0] = -player_speed
        elif evt.key == pygame.K_d:
            player_velocity[0] = player_speed
        elif evt.key == pygame.K_w:
            player_velocity[1] = -player_speed
        elif evt.key == pygame.K_s:
            player_velocity[1] = player_speed
    elif evt.type == pygame.KEYUP:
        if evt.key == pygame.K_a or evt.key == pygame.K_d:
            player_velocity[0] = 0
        elif evt.key == pygame.K_w or evt.key == pygame.K_s:
            player_velocity[1] = 0


# Game loops
while True:
    for event in pygame.event.get():
        handle_event(event)

    window.fill(WHITE)

    pygame.draw.rect(window, RED, (0, 0, 100, 100))
    pygame.draw.ellipse(window, BLACK, (player_x, player_y, PLAYER_SIZE[0], PLAYER_SIZE[1]))

    player_x += player_velocity[0]
    player_y += player_velocity[1]

    clock.tick(FRAME_RATE)
    pygame.display.update()
