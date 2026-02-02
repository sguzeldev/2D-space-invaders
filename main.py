import pygame

# Game Variables
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
PLAYER_SPEED = 640
PLAYER_WIDTH = 120
PLAYER_HEIGHT = 120
BULLET_WIDTH = 10
BULLET_HEIGHT = 20
BULLET_SPEED = 960

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders - Dev Build")
clock = pygame.time.Clock()


raw_player_img = pygame.image.load("ship.png").convert_alpha()
player_img = pygame.transform.scale(raw_player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
player_rect = player_img.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))

raw_bullet_img = pygame.image.load("bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(raw_bullet_img, (BULLET_WIDTH, BULLET_HEIGHT))

bullets = []

player_pos_x = float(player_rect.x)

running = True
delta_time = 0.0


class Bullet:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = BULLET_SPEED
        self.y = float(self.rect.y)

    def update(self, delta_time):
        self.y -= self.speed * delta_time
        self.rect.y = int(self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                new_bullet = Bullet(player_rect.centerx, player_rect.top, bullet_img)
                bullets.append(new_bullet)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] and player_pos_x > 0:
        player_pos_x -= PLAYER_SPEED * delta_time

    if keys[pygame.K_RIGHT] and player_pos_x < SCREEN_WIDTH - player_img.get_width():
        player_pos_x += PLAYER_SPEED * delta_time

    player_rect.x = int(player_pos_x)

    for bullet in bullets[:]:
        bullet.update(delta_time)
        if bullet.rect.bottom < 0:
            bullets.remove(bullet)

    screen.fill((0, 0, 0))
    screen.blit(player_img, player_rect)

    for bullet in bullets:
        bullet.draw(screen)

    pygame.display.flip()

    delta_time = clock.tick(60) / 1000

    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()
