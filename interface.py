from utils import *
import pygame
import sys
import time
import math
import random


def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()


def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    # print(click)
    pygame.draw.rect(screen, ic, (x, y, w, h))
    if click[0] == 1 and action != None:
        action()
    smalltext = pygame.font.SysFont("monospace", 20)
    textsurf, textrect = text_objects(msg, smalltext)
    textrect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(textsurf, textrect)


def quitgame():
    pygame.quit()
    quit()


def save():
    global saved
    saved = time.time()

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)
base = (320, 470)  # base position

pygame.init()
display_width = 800
display_height = 600
screen = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('KSP Autopilot')
myfont = pygame.font.SysFont("monospace", 20)
myfont2 = pygame.font.SysFont("monospace", 40)

pygame.mixer.init()
run = True

#pygame.draw.lines(screen, color, closed, pointlist, thickness)
#pygame.draw.rect(screen, green, (a,a,10,5), 2)
#pygame.draw.circle(screen, green, (c,c), 5, 2)
#pygame.draw.arc(screen, color, (5,5,2,2), 0, stop_angle, thickness)

saved = 0
while run:
    for event in pygame.event.get():
        print event
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = event.button
            print mouse
        else:
            mouse = 0

    screen.fill(white)
    pygame.draw.rect(screen, black, (10, 20, 240, 40), 1)
    pygame.draw.rect(screen, black, (10, 60, 240, 40), 1)
    thetime = myfont2.render(str(int(time.time())), 1, black)
    screen.blit(thetime, ([10, 20]))
    screen.blit(myfont2.render(str(int(saved)), 1, black), ([10, 60]))
    button("Do it", 150, 450, 100, 50, green, red, save)

    pygame.display.update()
    time.sleep(float(0.1))

pygame.display.quit()
pygame.quit()
