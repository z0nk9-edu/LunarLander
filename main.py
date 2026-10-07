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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()
    sys.exit()


asyncio.run(main())
