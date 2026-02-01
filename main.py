import pygame

pygame.init()

(width, height) = (800, 600)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tutorial")
player_img = pygame.image.load("ship.png").convert_alpha()

running = True
delta_time = 0.1
clock = pygame.time.Clock()
x = 0
player_speed = 400
start_x = (width - player_img.width) / 2
start_y = height - player_img.height - 10

while running:
    screen.fill((0, 0, 0))
    screen.blit(player_img, (start_x, start_y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        start_x -= player_speed * delta_time

    if keys[pygame.K_RIGHT]:
        start_x += player_speed * delta_time

    pygame.display.flip()
    delta_time = clock.tick(60) / 1000

    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()
