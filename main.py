import random
import pygame

# Game Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750


PLAYER_SPEED = 450
BULLET_SPEED = 900
ENEMY_BULLET_SPEED = 400


PLAYER_TARGET_WIDTH = 120
ENEMY_TARGET_WIDTH = 50
BULLET_SIZE = (10, 15)


ROWS = 5
COLS = 10
GRID_START_X = 100
GRID_START_Y = 30
GRID_CELL_WIDTH = 70
GRID_CELL_HEIGHT = 60


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders: Blade Runner Protocol")
clock = pygame.time.Clock()


def scale_by_width(img, target_width):

    original_rect = img.get_rect()

    aspect_ratio = original_rect.height / original_rect.width

    target_height = int(target_width * aspect_ratio)

    return pygame.transform.scale(img, (target_width, target_height))


try:
    raw_player = pygame.image.load("ship.png").convert_alpha()
    player_img = scale_by_width(raw_player, PLAYER_TARGET_WIDTH)
except FileNotFoundError:
    print("Error: Couldn't find ship.png")
    player_img = pygame.Surface((60, 80))
    player_img.fill((0, 255, 0))


player_rect = player_img.get_rect(midbottom=(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30))


try:
    raw_bullet = pygame.image.load("bullet.png").convert_alpha()
    bullet_img = pygame.transform.scale(raw_bullet, BULLET_SIZE)
except FileNotFoundError:
    bullet_img = pygame.Surface(BULLET_SIZE)
    bullet_img.fill((255, 50, 50))


enemy_images = []
for i in range(1, 6):

    filename = f"basic_enemy{i}.png"
    try:
        raw_img = pygame.image.load(filename).convert_alpha()

        scaled_img = scale_by_width(raw_img, ENEMY_TARGET_WIDTH)
        enemy_images.append(scaled_img)
    except FileNotFoundError:
        pass


if not enemy_images:
    fallback = pygame.Surface((40, 40))
    fallback.fill((255, 0, 0))
    enemy_images.append(fallback)


# Classes
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.y = float(self.rect.y)
        self.speed = BULLET_SPEED

    def update(self, dt):
        self.y -= self.speed * dt
        self.rect.y = int(self.y)

        if self.rect.bottom < 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    # class Bullet(pygame.rect):

    def __init__(self, center_x, center_y, image):
        super().__init__()
        self.image = image

        self.rect = self.image.get_rect(center=(center_x, center_y))

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed = 100

    def update(self, dt, direction):
        self.x += self.speed * dt * direction
        self.rect.x = int(self.x)


# Game Variables
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_pos_x = float(player_rect.x)
running = True
delta_time = 0.0


# Grid Generation
def create_grid():

    for row in range(ROWS):
        for col in range(COLS):

            cell_center_x = (
                GRID_START_X + (col * GRID_CELL_WIDTH) + (GRID_CELL_WIDTH / 2)
            )
            cell_center_y = (
                GRID_START_Y + (row * GRID_CELL_HEIGHT) + (GRID_CELL_HEIGHT / 2)
            )

            img = random.choice(enemy_images)

            enemy = Enemy(cell_center_x, cell_center_y, img)
            enemies.add(enemy)


create_grid()

enemy_move_direction = 1  # 1: Right, -1: Left


# Game Loop
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:

                bullets.add(Bullet(player_rect.centerx, player_rect.top, bullet_img))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos_x > 0:
        player_pos_x -= PLAYER_SPEED * delta_time
    if keys[pygame.K_RIGHT] and player_pos_x < SCREEN_WIDTH - player_rect.width:
        player_pos_x += PLAYER_SPEED * delta_time
    player_rect.x = int(player_pos_x)

    bullets.update(delta_time)
    enemies.update(delta_time, enemy_move_direction)

    basic_enemy_hits = pygame.sprite.groupcollide(bullets, enemies, True, True)

    move_down = False  # Move down check

    for enemy in enemies:
        if enemy_move_direction == 1 and enemy.rect.right >= SCREEN_WIDTH:
            enemy_move_direction = -1
            move_down = True
            break
        elif enemy_move_direction == -1 and enemy.rect.left <= 0:
            enemy_move_direction = 1
            move_down = True
            break

    if move_down:
        for enemy in enemies:
            enemy.rect.y += 20
            enemy.y = float(enemy.rect.y)

    screen.fill((10, 15, 25))

    screen.blit(player_img, player_rect)

    bullets.draw(screen)
    enemies.draw(screen)

    pygame.display.flip()

    # Time Management
    dt_ms = clock.tick(60)
    delta_time = dt_ms / 1000.0

    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()
