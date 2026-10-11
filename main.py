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


async def main():
    class Ship:
        def __init__(self, pos: pygame.math.Vector2, angle: float):
            self.pos = pos
            self.angle_rads = angle
            self.vel = pygame.math.Vector2(0, 5)

        def move(self):
            self.pos += self.vel
            self.vel.y += 0.5

        def draw(self):
            draw_at = pygame.math.Vector2(self.pos.x, HEIGHT / 2)
            pygame.draw.polygon(screen, (255, 255, 255), [draw_at + pygame.math.Vector2(15, 0).rotate_rad(self.angle_rads), draw_at + pygame.math.Vector2(10, 0).rotate_rad(self.angle_rads + 2.5), draw_at + pygame.math.Vector2(10, 0).rotate_rad(self.angle_rads - 2.5)])

    class SentryDrone:
        PATROL_SPEED = 45
        CHASE_ACCEL = 120
        MAX_SPEED = 100
        VIEW_RANGE = 250
        VIEW_DOT = 0.7
        BOLT_SPEED = 250
        FIRE_INTERVAL = 1.0
        LOST_TARGET_TIME_LIMIT = 2.0
        ARROW_SIDE_ANGLE = 2.5
        VISION_LENGTH = 100
        RADIUS = 14

        def __init__(self, pos: pygame.math.Vector2, patrol_min_x: float, patrol_max_x: float):
            self.pos = pygame.math.Vector2(pos)
            self.vel = pygame.math.Vector2()
            self.patrol_min_x = patrol_min_x
            self.patrol_max_x = patrol_max_x
            self.facing = pygame.math.Vector2(1, 0)
            self.state = "PATROL"
            self.lost_target_time = 0.0
            self.fire_timer = self.FIRE_INTERVAL

        def see(self, player_pos: pygame.math.Vector2):
            to_player = player_pos - self.pos
            distance = to_player.length()
            return 0 < distance < self.VIEW_RANGE and self.facing.dot(to_player.normalize()) > self.VIEW_DOT

        def update(self, player_pos: pygame.math.Vector2, dt: float):
            player_seen = self.see(player_pos)
            shot = None

            if self.state == "PATROL" and player_seen:
                self.state = "ATTACK"
                self.lost_target_time = 0.0

            if self.state == "ATTACK":
                if player_seen:
                    self.lost_target_time = 0.0
                    direction = (player_pos - self.pos).normalize()
                    self.facing = direction
                    self.vel += direction * self.CHASE_ACCEL * dt
                    self.vel = self.vel.clamp_magnitude(self.MAX_SPEED)
                    self.fire_timer -= dt
                    if self.fire_timer <= 0:
                        self.fire_timer = self.FIRE_INTERVAL
                        shot = (self.pos.copy(), direction * self.BOLT_SPEED)
                else:
                    self.lost_target_time += dt
                    self.vel *= max(0.0, 1.0 - 2.0 * dt)
                    if self.lost_target_time >= self.LOST_TARGET_TIME_LIMIT:
                        self.state = "PATROL"
                        self.lost_target_time = 0.0
                        self.fire_timer = self.FIRE_INTERVAL
                        self.vel.update(0, 0)
                        self.facing.update(1 if self.facing.x >= 0 else -1, 0)

                if self.state == "ATTACK":
                    self.pos += self.vel * dt
                    return shot

            self.vel.x = self.facing.x * self.PATROL_SPEED
            self.pos.x += self.vel.x * dt
            if self.pos.x <= self.patrol_min_x:
                self.pos.x = self.patrol_min_x
                self.facing.update(1, 0)
            elif self.pos.x >= self.patrol_max_x:
                self.pos.x = self.patrol_max_x
                self.facing.update(-1, 0)
            return shot

        def draw(self, camera_y: float = 0):
            draw_at = pygame.math.Vector2(self.pos.x, self.pos.y - camera_y)
            pygame.draw.polygon(screen, (255, 80, 80), [draw_at + self.facing * 15, draw_at + self.facing.rotate_rad(self.ARROW_SIDE_ANGLE) * 10, draw_at + self.facing.rotate_rad(-self.ARROW_SIDE_ANGLE) * 10])

    ship = Ship(pygame.math.Vector2(WIDTH / 2, HEIGHT / 2), -math.pi / 2)
    drone = SentryDrone(pygame.math.Vector2(WIDTH / 2 + 100, ship.pos.y - 220), patrol_min_x=100, patrol_max_x=WIDTH - 100)
    fuel_image = pygame.image.load("assets/fuel_cell.png").convert_alpha()
    fuel_image = pygame.transform.scale(fuel_image, (50, 50))

    class FuelCell:
        def __init__(self, pos):
            self.pos = pos

        def draw(self):
            screen.blit(fuel_image, self.pos)

    class Obstacle:
        def __init__(self, x, y, width, height):
            self.rect = pygame.Rect(x, y, width, height)
            self.color = (181, 18, 45)

        def draw(self, camera_y):
            draw_rect = self.rect.copy()
            draw_rect.y -= camera_y
            pygame.draw.rect(screen, self.color, draw_rect)

    def generate_obstacle(y):
            obstacle_type = random.randint(1,3)
            height = 40
            if obstacle_type == 1:
                width = random.randint(50, 150)
                x_pos = random.randint(0, WIDTH - width)
                return [Obstacle(x_pos, y, width, height)]
            elif obstacle_type == 2:
                side = random.choice(['left', 'right'])
                gap = random.randint(150,250)
                first_width = random.randint(150, 300)
                second_width = random.randint(150, 300)

                if side == 'left':
                    second_x = first_width + gap
                    return [Obstacle(0, y, first_width, height), Obstacle(second_x, y, second_width, height)]
                else:
                    first_x = WIDTH - first_width
                    second_x = first_x - gap - second_width
                    return [Obstacle(second_x, y, second_width, height), Obstacle(first_x, y, first_width, height)]
            else:
                gap = random.randint(150, 250)
                first_width = random.randint(150, 300)
                second_width = random.randint(150, 300)
                return [Obstacle(0, y, first_width, height), Obstacle(WIDTH - second_width, y, second_width, height)]

    obstacles = []
    for y in range(800, 30000, 400):
        obstacles.extend(generate_obstacle(y))
    
    running = True
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
            ship.vel += pygame.math.Vector2(math.cos(ship.angle_rads), math.sin(ship.angle_rads)) * 0.3
        ship.move()
        dt = clock.tick(60) / 1000
        drone.update(ship.pos, dt)

        screen.fill((0, 0, 0))
        ship.draw()
        camera_y = ship.pos.y - HEIGHT / 2
        for obs in obstacles:
            obs.draw(camera_y)
        drone.draw(camera_y)
        pygame.display.flip()
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
