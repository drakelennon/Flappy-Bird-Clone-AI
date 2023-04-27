import random

import pygame
import neat
import os
import pickle
import sys
from utils import escalar_imagem, distance, cores

pygame.init()

TELA_LARG = 900
TELA_ALTU = 600
TELA = pygame.display.set_mode((TELA_LARG, TELA_ALTU))
pygame.display.set_caption('FlappyAI')

# imgs
BACK_RAW = pygame.image.load(os.path.join('imgs', 'back.png')).convert_alpha()
BASE_RAW = pygame.image.load(os.path.join('imgs', 'base.png')).convert_alpha()
PIPES_RAW = [pygame.image.load(os.path.join('imgs', 'pipe1.png')).convert_alpha(),
             pygame.image.load(os.path.join('imgs', 'pipe2.png')).convert_alpha()]

AZUL_RAW = [pygame.image.load(os.path.join('imgs', 'blue1.png')).convert_alpha(),
            pygame.image.load(os.path.join('imgs', 'blue2.png')).convert_alpha(),
            pygame.image.load(os.path.join('imgs', 'blue3.png')).convert_alpha()]
VERMELHO_RAW = [pygame.image.load(os.path.join('imgs', 'red1.png')).convert_alpha(),
                pygame.image.load(os.path.join('imgs', 'red2.png')).convert_alpha(),
                pygame.image.load(os.path.join('imgs', 'red3.png')).convert_alpha()]
AMARELO_RAW = [pygame.image.load(os.path.join('imgs', 'yellow1.png')).convert_alpha(),
               pygame.image.load(os.path.join('imgs', 'yellow2.png')).convert_alpha(),
               pygame.image.load(os.path.join('imgs', 'yellow3.png')).convert_alpha()]

AZUL = [escalar_imagem(AZUL_RAW[0], 1.5),
        escalar_imagem(AZUL_RAW[1], 1.5),
        escalar_imagem(AZUL_RAW[2], 1.5)]
VERMELHO = [escalar_imagem(VERMELHO_RAW[0], 1.5),
            escalar_imagem(VERMELHO_RAW[1], 1.5),
            escalar_imagem(VERMELHO_RAW[2], 1.5)]
AMARELO = [escalar_imagem(AMARELO_RAW[0], 1.5),
           escalar_imagem(AMARELO_RAW[1], 1.5),
           escalar_imagem(AMARELO_RAW[2], 1.5)]
BASE = escalar_imagem(BASE_RAW, 1.5)
PIPES = [escalar_imagem(PIPES_RAW[0], 1.5),
         escalar_imagem(PIPES_RAW[1], 1.5)]
PIPES_INVERT = [pygame.transform.flip(PIPES[0], False, True),
                pygame.transform.flip(PIPES[1], False, True)]

# const and globals

birds_killed = 0
recorde = 0
FONT = pygame.font.SysFont('comicsansms', 20, True, False)


# classes
class Bird:
    X = 100
    VEL_PULO = 8.5
    IMG_B = AZUL
    IMG_R = VERMELHO
    IMG_Y = AMARELO

    def __init__(self):
        self.rand = random.randint(0, 2)
        if self.rand == 0:
            self.img = self.IMG_B[0]
        elif self.rand == 1:
            self.img = self.IMG_R[0]
        else:
            self.img = self.IMG_Y[0]
        self.x = self.X
        self.y = 280
        self.height = self.y
        self.vel_pulo = self.VEL_PULO
        self.vel = 0
        self.rect = self.img.get_rect()
        self.mod = 0
        self.PULO = False
        self.pontos = 0

    def update(self):
        self.rect = self.img.get_rect()
        if self.rand == 0:
            self.img = self.IMG_B[self.mod // 5]
        elif self.rand == 1:
            self.img = self.IMG_R[self.mod // 5]
        else:
            self.img = self.IMG_Y[self.mod // 5]
        self.rect.x, self.rect.y = self.x, self.y
        """if self.PULO is True:
            self.pulo()"""
        self.mod += 1
        self.y += self.vel
        self.vel += .5
        if self.vel >= 14:
            self.vel = 14
        if self.mod >= 15:
            self.mod = 0
        self.pontos += 1

    def pulo(self):
        self.vel = -6.5

    def draw(self, tela):
        tela.blit(self.img, (self.rect.x, self.rect.y))
        # pygame.draw.rect(tela, (255, 255, 255), self.rect, 3)


class Cano:
    IMG = PIPES
    IMG2 = PIPES_INVERT
    ABERTURA = 120

    def __init__(self):
        self.rand = random.randint(0, 1)
        self.rand_y = random.randint(300, 550)
        self.img = self.IMG[self.rand]
        self.img2 = self.IMG2[self.rand]
        self.rect = self.img.get_rect()
        self.rect2 = self.img2.get_rect()
        self.x = TELA_LARG + 10
        self.y = self.rand_y
        self.rect.x, self.rect.y = self.x, self.y
        self.x2 = self.x
        self.y2 = (self.y - self.img2.get_height()) - self.ABERTURA
        self.rect2.x, self.rect2.y = self.x, self.y2
        self.velocidade = 7

    def update(self):
        self.rect2.x, self.rect2.y = self.x, self.y2
        self.rect.x, self.rect.y = self.x, self.y
        self.x -= self.velocidade

    def draw(self, tela):
        tela.blit(self.img, (self.rect.x, self.rect.y))
        tela.blit(self.img2, (self.rect2.x, self.rect2.y))
        """pygame.draw.rect(tela, (255, 255, 255), self.rect, 3)
        pygame.draw.rect(tela, (255, 255, 255), self.rect2, 3)"""


def remove_bird(i):
    global birds_killed
    birds.pop(i)
    ge.pop(i)
    redes.pop(i)
    birds_killed += 1


def eval_genomes(genomes, config):
    global birds, ge, redes, cano, canos, bird, dist_top_x, dist_top_y, dist_bot_x, dist_bot_y, recorde
    clock = pygame.time.Clock()
    birds = []
    canos = []
    ge = []
    redes = []
    pontuacao = []

    player = Bird()

    def stats():
        text1 = FONT.render(f'Geração: {p.generation}', True, (255, 255, 255))
        text2 = FONT.render(f'Pontos: {max(pontuacao)}', True, (255, 255, 255))
        text3 = FONT.render(f'Recorde: {recorde}', True, (255, 255, 255))
        text4 = FONT.render(f'Já Morreram: {birds_killed}', True, (255, 255, 255))
        text5 = FONT.render(f'Ainda Vivos: {str(len(birds))}', True, (255, 255, 255))

        TELA.blit(text1, (10, 10))
        TELA.blit(text2, (10, 35))
        TELA.blit(text3, (10, 60))
        TELA.blit(text4, (10, 85))
        TELA.blit(text5, (10, 110))

    for genome_id, genome in genomes:
        birds.append(Bird())
        ge.append(genome)
        rede = neat.nn.FeedForwardNetwork.create(genome, config)
        redes.append(rede)
        genome.fitness = 0

    rodando = True
    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.pulo()
                if event.key == pygame.K_RETURN:
                    main()

        TELA.fill((0, 0, 0))

        for bird in birds:
            bird.update()
            bird.draw(TELA)

        # player.update()
        # player.draw(TELA)

        if len(canos) == 0:
            canos.append(Cano())

        for i, cano in enumerate(canos):
            if len(canos) == 1 and cano.rect.x < TELA_LARG / 2:
                canos.append(Cano())

            if len(canos) == 2 and cano.rect.x < TELA_LARG / 99:
                canos.append(Cano())

        for i, bird in enumerate(birds):
            pontuacao.append(bird.pontos)
            if recorde < max(pontuacao):
                recorde = max(pontuacao)

            ge[i].fitness += 1
            try:
                if bird.rect.bottom < 0:
                    ge[i].fitness -= 100
                    remove_bird(i)
                elif bird.rect.top > TELA_ALTU:
                    ge[i].fitness -= 100
                    remove_bird(i)

                if bird.pontos % 100 == 0:
                    ge[i].fitness += 100
            except:
                pass

            for cano in canos:
                if cano.rect.right < 10:
                    canos.remove(cano)

                if bird.rect.colliderect(cano.rect) is True or bird.rect.colliderect(cano.rect2) is True:
                    ge[i].fitness -= 100
                    remove_bird(i)

        # pygame.draw.line(TELA, (255, 255, 255), canos[0].rect2.bottomleft, bird.rect.center)
        # pygame.draw.line(TELA, (255, 255, 255), canos[0].rect.topleft, bird.rect.center)

        if len(birds) == 0:
            break

        for i, bird in enumerate(birds):
            for cano in canos:
                dist_top_x = bird.rect.center[0] - canos[0].rect2.bottomleft[0]
                dist_top_y = bird.rect.center[1] - canos[0].rect2.bottomleft[1]
                dist_bot_x = bird.rect.center[0] - canos[0].rect.x
                dist_bot_y = bird.rect.center[1] - canos[0].rect.y

                if bird.rect.center < cano.rect.topleft and bird.rect.center < cano.rect.bottomleft:
                    pygame.draw.line(TELA, cores('WHITE'), bird.rect.center, cano.rect2.bottomleft, 2)
                    pygame.draw.line(TELA, cores('WHITE'), bird.rect.center, cano.rect.topleft, 2)

            output = redes[i].activate((dist_top_x, dist_top_y, dist_bot_x, dist_bot_y))

            if output[0] > .5:
                bird.pulo()
            else:
                pass

        for cano in canos:
            cano.update()
            cano.draw(TELA)

        stats()
        clock.tick(60)
        pygame.display.update()


# Set up the NEAT Neural Network
def run(config_path):
    global p, winner
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # p = neat.Checkpointer.restore_checkpoint('checkpoints/neat-checkpoint-76')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    statistics = neat.StatisticsReporter()
    p.add_reporter(statistics)
    # p.add_reporter(neat.Checkpointer(5))

    winner = p.run(eval_genomes, 1000)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)


"""def carrega_ia(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
        carrega_ia(winner, config_path)"""

# Start
def main():
    if __name__ == '__main__':
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'C:/Users/drake/PycharmProjects/FlappyAI/config.txt')
        run(config_path)
        # carrega_ia(config_path)

main()