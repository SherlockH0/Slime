import pygame
import numpy
from random import randrange
from cv2 import GaussianBlur

texture = pygame.image.load("texture.png")


WIDTH, HEIGHT = 1600, 845
STARTING_POS = WIDTH / 2, HEIGHT / 2
MAX_ITER = 20
TICK = 10
ticker = 0
currentColor = 0
currentIter = 0
agentsNum = 2**currentIter


def pixel_map_to_pos_map(pixelMap):
    out = []
    for x in range(len(pixelMap)):
        for y in range(len(pixelMap[x])):
            out.append((x, y))
    return out


def get_color():
    textureWidth = texture.get_size()[0]
    pixelPos = int(textureWidth / (MAX_ITER + 1) * currentIter), 1
    rawColor = texture.get_at(pixelPos)
    color = rawColor[0], rawColor[1], rawColor[2]
    return color


def update():
    global currentIter
    agentsNum = 2**currentIter

    for i in range(agentsNum):
        agentPos = randrange(WIDTH), randrange(HEIGHT)
        pixelMap[agentPos[0]][agentPos[1]] = currentColor
    currentIter += 1


pixelMap = numpy.full((WIDTH, HEIGHT, 3), 0, numpy.uint8)
spacesMap = pixel_map_to_pos_map(pixelMap)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("black")

    if ticker >= TICK and currentIter < MAX_ITER:
        update()
        ticker = 0
    currentColor = get_color()
    pygame.surfarray.blit_array(screen, GaussianBlur(pixelMap, (5, 5), 1))
    pygame.display.set_caption('FPS: %i , Iteration: %s' %
                               (clock.get_fps(), currentIter))
    pygame.display.flip()

    clock.tick()
    ticker += 1


pygame.quit()
