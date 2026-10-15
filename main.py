import pygame
import random
import math
import asyncio
import sys

pygame.init()


WIDTH = 1000
HEIGHT = 800


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lunar Lander")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)


def display_message(text, y_offset=0):
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y_offset))
    screen.blit(text_surface, text_rect)


async def yes_no_choice(message):
    # Ensure event queue is clean before taking prompt input
    pygame.event.clear()

    choice = None
    while choice is None:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    choice = True
                elif event.key == pygame.K_n:
                    choice = False

        screen.fill((0, 0, 0))
        display_message(message + " (Y/N)")
        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

    return choice


async def main():
    async def reset(message="Do you want to retry?"):
        nonlocal running, ship, drone
        running = await yes_no_choice(message)
        ship = Ship(pygame.math.Vector2(WIDTH / 2, HEIGHT / 2), -math.pi / 2)
        drone = SentryDrone(pygame.math.Vector2(WIDTH / 2 + 100, ship.pos.y - 220))

    class Ship:
        RADIUS = 15

        def __init__(self, pos: pygame.math.Vector2, angle: float):
            self.pos = pos
            self.angle_rads = angle
            self.vel = pygame.math.Vector2(0, 5)
            self.fuel = 1000

        def move(self):
            self.pos += self.vel
            self.vel.y += 0.05
            if self.pos.x <= self.RADIUS:
                self.pos.x = self.RADIUS
                self.vel.x = max(0.0, self.vel.x)
            elif self.pos.x >= WIDTH - self.RADIUS:
                self.pos.x = WIDTH - self.RADIUS
                self.vel.x = min(0.0, self.vel.x)

        def thrust(self):
            if self.fuel > 0:
                self.vel += (
                    pygame.math.Vector2(
                        math.cos(self.angle_rads), math.sin(self.angle_rads)
                    )
                    * 0.3
                )
                self.fuel -= 1

        def draw(self):
            draw_at = pygame.math.Vector2(self.pos.x, HEIGHT / 2)
            pygame.draw.polygon(
                screen,
                (255, 255, 255),
                [
                    draw_at + pygame.math.Vector2(15, 0).rotate_rad(self.angle_rads),
                    draw_at
                    + pygame.math.Vector2(10, 0).rotate_rad(self.angle_rads + 2.5),
                    draw_at
                    + pygame.math.Vector2(10, 0).rotate_rad(self.angle_rads - 2.5),
                ],
            )
            fuel_meter = pygame.Rect(
                25, HEIGHT - 25, 50, -self.fuel / (1000 / (HEIGHT - 50))
            )
            fuel_meter.normalize()
            pygame.draw.rect(
                screen,
                (235, 177, 52),
                fuel_meter,
            )

    class SentryDrone:
        RADIUS = 15
        PATROL_SPEED = 45
        GRAVITY = 220
        THROTTLE_ACCEL = 260
        CHASE_ACCEL = 200
        MAX_SPEED = 200
        VIEW_RANGE = 500
        VIEW_DOT = 0.6
        LOST_TARGET_TIME_LIMIT = 2.0
        ARROW_SIDE_ANGLE = 2.5

        def __init__(self, pos: pygame.math.Vector2):
            self.pos = pygame.math.Vector2(pos)
            self.vel = pygame.math.Vector2()
            self.facing = pygame.math.Vector2(0, 1)
            self.state = "PATROL"
            self.lost_target_time = 0.0

        def see(self, player_pos: pygame.math.Vector2):
            to_player = player_pos - self.pos
            distance = to_player.length()
            return (
                0 < distance < self.VIEW_RANGE
                and self.facing.dot(to_player.normalize()) > self.VIEW_DOT
            )

        def update(self, player_pos: pygame.math.Vector2, dt: float):
            player_seen = self.see(player_pos)

            if self.state == "PATROL" and player_seen:
                self.state = "ATTACK"
                self.lost_target_time = 0.0

            if self.state == "ATTACK":
                if player_seen:
                    self.lost_target_time = 0.0
                    self.facing = (player_pos - self.pos).normalize()
                    self.vel += self.facing * self.CHASE_ACCEL * dt
                    self.vel = self.vel.clamp_magnitude(self.MAX_SPEED)
                else:
                    self.lost_target_time += dt
                    self.vel *= max(0.0, 1.0 - 2.0 * dt)
                    if self.lost_target_time >= self.LOST_TARGET_TIME_LIMIT:
                        self.state = "PATROL"
                        self.vel.update(0, 0)
                        self.facing.update(0, 1)
                self.pos += self.vel * dt
                if self.pos.x <= self.RADIUS:
                    self.pos.x = self.RADIUS
                    self.vel.x = max(0.0, self.vel.x)
                elif self.pos.x >= WIDTH - self.RADIUS:
                    self.pos.x = WIDTH - self.RADIUS
                    self.vel.x = min(0.0, self.vel.x)
                return

            self.facing.update(0, 1)
            self.vel.y += self.GRAVITY * dt
            if self.vel.y > self.PATROL_SPEED:
                self.vel.y = max(self.PATROL_SPEED, self.vel.y - self.THROTTLE_ACCEL * dt)
            self.pos.y += self.vel.y * dt

        def draw(self, camera_y: float):
            draw_at = pygame.math.Vector2(self.pos.x, self.pos.y - camera_y)
            pygame.draw.polygon(
                screen,
                (255, 80, 80),
                [
                    draw_at + self.facing * 15,
                    draw_at + self.facing.rotate_rad(self.ARROW_SIDE_ANGLE) * 10,
                    draw_at + self.facing.rotate_rad(-self.ARROW_SIDE_ANGLE) * 10,
                ],
            )

    running = True
    ship = Ship(pygame.math.Vector2(WIDTH / 2, HEIGHT / 2), -math.pi / 2)
    drone = SentryDrone(pygame.math.Vector2(WIDTH / 2 + 100, ship.pos.y - 220))
    fuel_image = pygame.image.load("assets/fuel_cell.png").convert_alpha()
    fuel_image = pygame.transform.scale(fuel_image, (50, 50))
    FUEL_CELL_SIZE = 50
    FUEL_CELL_VALUE = 50

    class FuelCell:
        def __init__(self, pos):
            self.pos = pos
            self.rect = pygame.Rect(*self.pos, FUEL_CELL_SIZE, FUEL_CELL_SIZE)

        def draw(self, camera_y):
            screen.blit(fuel_image, (self.pos.x, self.pos.y - camera_y))

    class Obstacle:
        HEIGHT = 40

        def __init__(self, x, y, width, height):
            self.rect = pygame.Rect(x, y, width, height)

        def draw(self, camera_y):
            draw_rect = self.rect.copy()
            draw_rect.y -= camera_y
            pygame.draw.rect(screen, (181, 18, 45), draw_rect)

    def generate_obstacle(y):
        obstacle_type = random.randint(1, 3)
        if obstacle_type == 1:
            width = random.randint(100, 400)
            x_pos = random.randint(0, WIDTH - width)
            return [Obstacle(x_pos, y, width, Obstacle.HEIGHT)]
        elif obstacle_type == 2:
            side = random.choice(["left", "right"])
            gap = random.randint(150, 250)
            first_width = random.randint(150, 300)
            second_width = random.randint(150, 300)

            if side == "left":
                second_x = first_width + gap
                return [
                    Obstacle(0, y, first_width, Obstacle.HEIGHT),
                    Obstacle(second_x, y, second_width, Obstacle.HEIGHT),
                ]
            else:
                first_x = WIDTH - first_width
                second_x = first_x - gap - second_width
                return [
                    Obstacle(second_x, y, second_width, Obstacle.HEIGHT),
                    Obstacle(first_x, y, first_width, Obstacle.HEIGHT),
                ]
        else:
            first_width = random.randint(150, 300)
            second_width = random.randint(150, 300)
            return [
                Obstacle(0, y, first_width, Obstacle.HEIGHT),
                Obstacle(WIDTH - second_width, y, second_width, Obstacle.HEIGHT),
            ]

    FLOOR_Y = 15000
    FLOOR_HEIGHT = 60
    SAFE_LANDING_SPEED = 8
    floor_rect = pygame.Rect(0, FLOOR_Y, WIDTH, FLOOR_HEIGHT)

    obstacles = []
    for y in range(800, FLOOR_Y, 400):
        obstacles.extend(generate_obstacle(y))

    fuel_cells = []
    for y in range(200, FLOOR_Y, 400):
        if random.random() > 0.5:
            fuel_cells.append(
                FuelCell(pygame.math.Vector2(random.randint(0, WIDTH), y))
            )

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ship.angle_rads -= math.radians(5)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ship.angle_rads += math.radians(5)
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            ship.thrust()
        ship.move()
        dt = 1 / 60
        drone.update(ship.pos, dt)
        camera_y = ship.pos.y - HEIGHT / 2

        # collisions
        ship_rect = pygame.Rect(0, 0, Ship.RADIUS * 2, Ship.RADIUS * 2)
        ship_rect.center = ship.pos
        for obs in obstacles:
            if obs.rect.colliderect(ship_rect):
                await reset()
                break

        if (ship.pos - drone.pos).length() < Ship.RADIUS + SentryDrone.RADIUS:
            await reset()

        if floor_rect.colliderect(ship_rect):
            if ship.vel.length() <= SAFE_LANDING_SPEED:
                await reset("You landed safely! Play again?")
            else:
                await reset("You crashed! Landing too fast. Retry?")

        remaining_fuel_cells = []
        for cell in fuel_cells:
            if cell.rect.collidepoint(ship.pos):
                ship.fuel += FUEL_CELL_VALUE
            else:
                remaining_fuel_cells.append(cell)
        fuel_cells = remaining_fuel_cells

        # drawing screen
        screen.fill((0, 0, 0))
        floor_draw_rect = floor_rect.copy()
        floor_draw_rect.y -= camera_y
        pygame.draw.rect(screen, (130, 130, 130), floor_draw_rect)
        for obs in obstacles:
            obs.draw(camera_y)
        for cell in fuel_cells:
            cell.draw(camera_y)
        drone.draw(camera_y)
        ship.draw()

        progress = min(max(ship.pos.y / FLOOR_Y, 0.0), 1.0)
        progress_track = pygame.Rect(WIDTH - 75, 25, 50, HEIGHT - 50)
        pygame.draw.rect(screen, (60, 60, 60), progress_track)
        progress_meter = pygame.Rect(
            WIDTH - 75, HEIGHT - 25, 50, -progress * (HEIGHT - 50)
        )
        progress_meter.normalize()
        pygame.draw.rect(screen, (100, 200, 100), progress_meter)

        pygame.display.flip()

        # tick
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
