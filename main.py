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
            self.fuel = 1000

        def move(self):
            self.pos += self.vel
            self.vel.y += 0.5

        def draw(self):
            draw_at = pygame.math.Vector2(self.pos.x, HEIGHT / 2)
            # draw ship
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

            # draw fuel bar
            fuel_bar = pygame.Rect(10, self.fuel, 50, HEIGHT)
            pygame.draw.rect(screen, (235, 198, 35), fuel_bar)

    ship = Ship(pygame.math.Vector2(WIDTH / 2, HEIGHT / 2), -math.pi / 2)
    fuel_image = pygame.image.load("assets/fuel_cell.png").convert_alpha()
    fuel_image = pygame.transform.scale(fuel_image, (50, 50))

    class FuelCell:
        def __init__(self, pos):
            self.pos = pos

        def collide(self):
            ship.fuel += 100

        def draw(self):
            screen.blit(fuel_image, self.pos)

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
            ship.vel += (
                pygame.math.Vector2(
                    math.cos(ship.angle_rads), math.sin(ship.angle_rads)
                )
                * 0.3
            )
            ship.fuel -= 1
        ship.move()
        screen.fill((0, 0, 0))
        ship.draw()
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
