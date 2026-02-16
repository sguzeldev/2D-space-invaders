import random
import pygame
import math

# Game Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750


PLAYER_SPEED = 450
PLAYER_BULLET_SPEED = 900
BASIC_ENEMY_BULLET_SPEED = 500


PLAYER_TARGET_WIDTH = 120
ENEMY_TARGET_WIDTH = 50
PLAYER_BULLET_SIZE = (10, 15)
ENEMY_BULLET_SIZE = (12, 12)


ROWS = 5
COLS = 10
GRID_START_X = 100
GRID_START_Y = 30
GRID_CELL_WIDTH = 70
GRID_CELL_HEIGHT = 60


pygame.init()
game_font = pygame.font.SysFont("Arial", 30)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders: Blade Runner Protocol")
clock = pygame.time.Clock()


def scale_by_width(img, target_width):

    original_rect = img.get_rect()

    aspect_ratio = original_rect.height / original_rect.width

    target_height = int(target_width * aspect_ratio)

    return pygame.transform.scale(img, (target_width, target_height))


try:
    raw_player = pygame.image.load("img/ship.png").convert_alpha()
    player_img = scale_by_width(raw_player, PLAYER_TARGET_WIDTH)
except FileNotFoundError:
    print("Error: Couldn't find ship.png")
    player_img = pygame.Surface((60, 80))
    player_img.fill((0, 255, 0))


try:
    raw_bullet = pygame.image.load("img/bullet.png").convert_alpha()
    player_bullet_img = pygame.transform.scale(raw_bullet, PLAYER_BULLET_SIZE)
except FileNotFoundError:
    player_bullet_img = pygame.Surface(PLAYER_BULLET_SIZE)
    player_bullet_img.fill((255, 50, 50))

try:
    raw_basic_enemy_bullet = pygame.image.load("img/enemy_bullet.png").convert_alpha()
    basic_enemy_bullet_img = pygame.transform.scale(
        raw_basic_enemy_bullet, ENEMY_BULLET_SIZE
    )
except FileNotFoundError:
    basic_enemy_bullet_img = pygame.Surface(ENEMY_BULLET_SIZE)
    basic_enemy_bullet_img.fill((0, 0, 255))


enemy_images = []
for i in range(1, 6):

    filename = f"img/basic_enemy{i}.png"
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
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.pos_x = float(self.rect.x)
        self.speed = speed

        self.last_shot_time = 0
        self.player_shoot_delay = 500  # ms

        self.health = 3  # bullets
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.pos_x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.pos_x += self.speed * dt

        if self.pos_x < 0:
            self.pos_x = 0
        elif self.pos_x > SCREEN_WIDTH - self.rect.width:
            self.pos_x = SCREEN_WIDTH - self.rect.width

        self.rect.x = int(self.pos_x)

    def shoot(self, current_time, bullet_group, bullet_image):

        if current_time - self.last_shot_time > self.player_shoot_delay:
            new_bullet = Bullet(
                self.rect.centerx,
                self.rect.top,
                bullet_image,
                0,
                -PLAYER_BULLET_SPEED,
            )
            bullet_group.add(new_bullet)
            self.last_shot_time = current_time


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, image, velocity_x, velocity_y):
        super().__init__()

        self.image = image

        self.rect = self.image.get_rect(center=(x, y))

        self.pos_x = float(self.rect.centerx)
        self.pos_y = float(self.rect.centery)

        self.vx = velocity_x
        self.vy = velocity_y

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos_x += self.vx * dt
        self.pos_y += self.vy * dt

        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        if (
            self.rect.bottom < 0
            or self.rect.top > SCREEN_WIDTH
            or self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
        ):
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):

    def __init__(self, center_x, center_y, image):
        super().__init__()
        self.image = image

        self.rect = self.image.get_rect(center=(center_x, center_y))

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed = 100
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt, direction):
        self.x += self.speed * dt * direction
        self.rect.x = int(self.x)

    def shoot(self, bullet_group, bullet_image, target_pos):
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery

        distance = math.hypot(dx, dy)

        if distance > 0:
            vx = (dx / distance) * BASIC_ENEMY_BULLET_SPEED
            vy = (dy / distance) * BASIC_ENEMY_BULLET_SPEED
        else:
            vx = 0
            vy = BASIC_ENEMY_BULLET_SPEED

        new_bullet = Bullet(
            self.rect.centerx,
            self.rect.bottom,
            bullet_image,
            vx,
            vy,
        )
        bullet_group.add(new_bullet)


# Game Variables
player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30, player_img, PLAYER_SPEED)
player_group = pygame.sprite.GroupSingle(player)

bullets = pygame.sprite.Group()  # Player Bullets
basic_enemy_bullets = pygame.sprite.Group()  # Basic Enemy Bullets
basic_enemies = pygame.sprite.Group()


last_basic_enemy_shot_time = 0
BASIC_ENEMY_SHOOT_COOLDOWN = 1000  # ms

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
            basic_enemies.add(enemy)


create_grid()

enemy_move_direction = 1  # 1: Right, -1: Left


# Game Loop
while running:

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player_group.sprite.shoot(current_time, bullets, player_bullet_img)

    if current_time - last_basic_enemy_shot_time > BASIC_ENEMY_SHOOT_COOLDOWN:
        if len(basic_enemies) > 0:
            attacking_enemy = random.choice(basic_enemies.sprites())
            target_location = player_group.sprite.rect.center
            attacking_enemy.shoot(
                basic_enemy_bullets, basic_enemy_bullet_img, target_location
            )

            last_basic_enemy_shot_time = current_time
            BASIC_ENEMY_SHOOT_COOLDOWN = random.randint(500, 1500)

    player_group.update(delta_time)

    bullets.update(delta_time)
    basic_enemy_bullets.update(delta_time)
    basic_enemies.update(delta_time, enemy_move_direction)

    # Collisions

    basic_enemy_hits = pygame.sprite.groupcollide(
        bullets, basic_enemies, True, True, pygame.sprite.collide_mask
    )  # Player Bullet -> Basic Enemy

    if pygame.sprite.spritecollide(
        player_group.sprite, basic_enemy_bullets, True, pygame.sprite.collide_mask
    ):  # Enemy Bullet -> Player
        player_group.sprite.health -= 1
        print(f"GOT HIT! Health Left: {player_group.sprite.health}")
        if player_group.sprite.health <= 0:
            print("Game Over")
            running = False

    move_down = False  # Move down check

    for enemy in basic_enemies:
        if enemy_move_direction == 1 and enemy.rect.right >= SCREEN_WIDTH:
            enemy_move_direction = -1
            move_down = True
            break
        elif enemy_move_direction == -1 and enemy.rect.left <= 0:
            enemy_move_direction = 1
            move_down = True
            break

    if move_down:
        for enemy in basic_enemies:
            enemy.rect.y += 20
            enemy.y = float(enemy.rect.y)

    screen.fill((10, 15, 25))

    player_group.draw(screen)
    basic_enemy_bullets.draw(screen)
    bullets.draw(screen)
    basic_enemies.draw(screen)

    fps = str(int(clock.get_fps()))
    fps_text = game_font.render(fps, True, pygame.Color("coral"))
    screen.blit(fps_text, (10, 0))

    pygame.display.flip()

    # Time Management
    dt_ms = clock.tick(60)
    delta_time = dt_ms / 1000.0

    delta_time = max(0.001, min(0.1, delta_time))

pygame.quit()
