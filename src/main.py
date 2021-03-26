from collections import namedtuple
from pathlib import Path
from typing import Any, List

import pygame
from pygame import display, draw, font, image, mixer, time, transform

font.init()
HEALTH_FONT = font.SysFont("comicsans", 40)
WINNER_FONT = font.SysFont("comicsans", 100)

mixer.init()
MISSILE_HIT_SOUND = mixer.Sound(Path("src", "Assets", "hit.mp3"))
MISSILE_FIRE_SOUND = mixer.Sound(Path("src", "Assets", "fire.mp3"))

TITLE = "Spaceship Battle!"
WIDTH, HEIGHT = 900, 500
BORDER = 6
WINDOW = display.set_mode((WIDTH, HEIGHT))
FPS = 60

CENTER_RECT = pygame.Rect((WIDTH - BORDER // 2) // 2, 0, BORDER, HEIGHT)

Spaceship = namedtuple("Spaceship", "width height")
SPACESHIP_DIMENSIONS = Spaceship(width=55, height=55)
ROTATION = 90
SPACESHIP_VELOCITY = 5

Missile = namedtuple("Missle", "width height")
MISSILE_DIMENSIONS = Missile(width=12, height=6)
MISSILE_VELOCITY = 7
MAX_MISSILES = 3

RED_HIT = pygame.USEREVENT + 1
YELLOW_HIT = pygame.USEREVENT + 2

Color = namedtuple("Color", "r g b")
WHITE = Color(r=255, g=255, b=255)
BLACK = Color(r=0, g=0, b=0)
GRAY = Color(r=69, g=69, b=69)
RED = Color(r=255, g=0, b=0)
YELLOW = Color(r=255, g=255, b=0)

RED_SPACESHIP_IMAGE = image.load(Path("src", "Assets", "spaceship_red.png"))
RED_SPACESHIP = transform.rotate(
    transform.scale(RED_SPACESHIP_IMAGE, SPACESHIP_DIMENSIONS), ROTATION
)

YELLOW_SPACESHIP_IMAGE = image.load(Path("src", "Assets", "spaceship_yellow.png"))
YELLOW_SPACESHIP = transform.rotate(
    transform.scale(YELLOW_SPACESHIP_IMAGE, SPACESHIP_DIMENSIONS), -ROTATION
)

SPACE = transform.scale(image.load(Path("src", "Assets", "space.png")), (WIDTH, HEIGHT))

display.set_caption(TITLE)


def main():
    red = pygame.Rect(100, 300, SPACESHIP_DIMENSIONS.width, SPACESHIP_DIMENSIONS.height)
    yellow = pygame.Rect(745, 300, SPACESHIP_DIMENSIONS.width, SPACESHIP_DIMENSIONS.height)

    red_missiles = list()
    yellow_missiles = list()

    red_health = 10
    yellow_health = 10

    clock = time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(red_missiles) < MAX_MISSILES:
                    missile = pygame.Rect(
                        red.x + red.width,
                        red.y + (red.height // 2) - (MISSILE_DIMENSIONS.height // 2),
                        MISSILE_DIMENSIONS.width,
                        MISSILE_DIMENSIONS.height,
                    )
                    red_missiles.append(missile)
                    MISSILE_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(yellow_missiles) < MAX_MISSILES:
                    missile = pygame.Rect(
                        yellow.x,
                        yellow.y + (yellow.height // 2) - (MISSILE_DIMENSIONS.height // 2),
                        MISSILE_DIMENSIONS.width,
                        MISSILE_DIMENSIONS.height,
                    )
                    yellow_missiles.append(missile)
                    MISSILE_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                MISSILE_HIT_SOUND.play()

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                MISSILE_HIT_SOUND.play()

        winner = ""
        if red_health <= 0:
            winner = "Yellow"
        if yellow_health <= 0:
            winner = "Red"

        if winner != "":
            draw_winner(text=f"{winner} Wins!")
            break

        keys_pressed = pygame.key.get_pressed()
        red_movement_handler(keys_pressed, red)
        yellow_movement_handler(keys_pressed, yellow)

        missile_handler(red_missiles, yellow_missiles, red, yellow)

        draw_window(
            red=red,
            yellow=yellow,
            red_missiles=red_missiles,
            yellow_missiles=yellow_missiles,
            red_health=red_health,
            yellow_health=yellow_health,
        )

    main()


def missile_handler(
    red_missiles: List[pygame.Rect],
    yellow_missiles: List[pygame.Rect],
    red: pygame.Rect,
    yellow: pygame.Rect,
) -> None:
    for missile in red_missiles:
        missile.x += MISSILE_VELOCITY
        if yellow.colliderect(missile):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_missiles.remove(missile)
        elif missile.x + MISSILE_DIMENSIONS.width > WIDTH:
            red_missiles.remove(missile)

    for missile in yellow_missiles:
        missile.x -= MISSILE_VELOCITY
        if red.colliderect(missile):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_missiles.remove(missile)
        elif missile.x < 0:
            yellow_missiles.remove(missile)


def red_movement_handler(keys_pressed: List[Any], red: pygame.Rect) -> None:
    if keys_pressed[pygame.K_a] and red.x - SPACESHIP_VELOCITY > 0:  # LEFT
        red.x -= SPACESHIP_VELOCITY
    if (
        keys_pressed[pygame.K_d]
        and red.x + (SPACESHIP_VELOCITY + SPACESHIP_DIMENSIONS.width) < CENTER_RECT.x
    ):  # RIGHT
        red.x += SPACESHIP_VELOCITY
    if keys_pressed[pygame.K_w] and red.y - SPACESHIP_VELOCITY > 0:  # UP
        red.y -= SPACESHIP_VELOCITY
    if (
        keys_pressed[pygame.K_s]
        and red.y + (SPACESHIP_VELOCITY + SPACESHIP_DIMENSIONS.height) < HEIGHT
    ):  # DOWN
        red.y += SPACESHIP_VELOCITY


def yellow_movement_handler(keys_pressed: List[Any], yellow: pygame.Rect) -> None:
    if (
        keys_pressed[pygame.K_LEFT]
        and yellow.x - SPACESHIP_VELOCITY > CENTER_RECT.x + CENTER_RECT.width
    ):  # LEFT
        yellow.x -= SPACESHIP_VELOCITY
    if (
        keys_pressed[pygame.K_RIGHT]
        and yellow.x + (SPACESHIP_VELOCITY + SPACESHIP_DIMENSIONS.width) < WIDTH
    ):  # RIGHT
        yellow.x += SPACESHIP_VELOCITY
    if keys_pressed[pygame.K_UP] and yellow.y - SPACESHIP_VELOCITY > 0:  # UP
        yellow.y -= SPACESHIP_VELOCITY
    if (
        keys_pressed[pygame.K_DOWN]
        and yellow.y + (SPACESHIP_VELOCITY + SPACESHIP_DIMENSIONS.height) < HEIGHT
    ):  # DOWN
        yellow.y += SPACESHIP_VELOCITY


def draw_winner(text: str) -> None:
    draw_text = WINNER_FONT.render(text, True, WHITE)
    WINDOW.blit(
        draw_text,
        (WIDTH // 2 - draw_text.get_width() // 2, HEIGHT // 2 - draw_text.get_height() // 2),
    )
    display.update()
    time.delay(5000)


def draw_window(
    red: pygame.Rect,
    yellow: pygame.Rect,
    red_missiles: List[pygame.Rect],
    yellow_missiles: List[pygame.Rect],
    red_health: int,
    yellow_health: int,
) -> None:
    WINDOW.blit(SPACE, (0, 0))
    draw.rect(WINDOW, BLACK, CENTER_RECT)

    red_health_text = HEALTH_FONT.render(f"Health: {red_health}", True, WHITE)
    yellow_health_text = HEALTH_FONT.render(f"Health: {yellow_health}", True, WHITE)
    WINDOW.blit(red_health_text, (10, 10))
    WINDOW.blit(yellow_health_text, (WIDTH - yellow_health_text.get_width() - 10, 10))

    WINDOW.blit(RED_SPACESHIP, (red.x, red.y))
    WINDOW.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))

    for missile in red_missiles:
        draw.rect(WINDOW, RED, missile)

    for missile in yellow_missiles:
        draw.rect(WINDOW, YELLOW, missile)

    display.update()


if __name__ == "__main__":
    main()
