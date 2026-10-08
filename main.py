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
            self.vel = pygame.math.Vector2(0, 0)

        def move(self):
            self.pos += self.vel
            self.vel *= 0.97

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

    running = True
    ship = Ship(pygame.math.Vector2(WIDTH / 2, HEIGHT / 2), -math.pi / 2)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ship.angle_rads -= math.radians(5)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ship.angle_rads += math.radians(5)
        if keys[pygame.K_SPACE]:
            ship.vel += (
                pygame.math.Vector2(
                    math.cos(ship.angle_rads), math.sin(ship.angle_rads)
                )
                * 0.3
            )
        ship.move()
        screen.fill((0, 0, 0))
        ship.draw()
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
