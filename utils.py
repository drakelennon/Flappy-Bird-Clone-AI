import pygame
import math


# utils

def escalar_imagem(img, fator):
    tamanho = round(img.get_width() * fator), round(img.get_height() * fator)
    return pygame.transform.scale(img, tamanho)


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx ** 2 + dy ** 2)

def cores(name):
    if name == 'BLACK':
        cor = (0, 0, 0)
    elif name == 'YELLOW':
        cor = (255, 255, 0)
    elif name == 'RED':
        cor = (255, 0, 0)
    elif name == 'BLUE':
        cor = (0, 0, 255)
    elif name == 'GREEN':
        cor = (0, 255, 0)
    elif name == 'WHITE':
        cor = (255, 255, 255)
    else:
        cor = (0, 0, 0)

    return cor
