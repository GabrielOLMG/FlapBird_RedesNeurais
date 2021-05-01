'''
        -> Para Ativar a venv basta fazer: FlapBird\Scripts\activate.bat
        -> py FlapBirdP.py
        -> Objetos que queremos criar: Canos, Passaros, Chão
'''

import pygame
import neat
import time
import os
import random
from abc import ABCMeta, abstractmethod
pygame.font.init()
#-------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------#

LARGURA    = 500
ALTURA     = 800
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens','bird1.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens','bird2.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens','bird3.png')))
            ]# pygame.transform.scale2x aumenta o tamanho da imagem
PIPE_IMG  = pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens','pipe.png'))) # Cano
BASE_IMG  = pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens','base.png'))) #Chão
BG_IMG    = pygame.transform.scale2x(pygame.image.load(os.path.join('Imagens','bg.png')))   #Fundo



#-------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------#
tela = pygame.display.set_mode((LARGURA,ALTURA),0)
fonte = pygame.font.SysFont("arial", 32, True, False)
#-------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------#


class Bird:
    IMGS = BIRD_IMGS
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.altura = y
        self.img = 0
        self.i = 1 #para dizer se as imagens estao crescendo ou decrescendo
        self.tempo_movimentando = 0 #Tempo em q o passaro esta se mexendo em uma determinada direção 
        self.img_atual = self.IMGS[self.img] 
        self.velocidade = 0
        self.estado = 1 #0 ->gameover, 1->jogando
        
    def pintar(self,tela):
        if self.estado == 1:
            self.pintar_jogando(tela)
        elif self.estado == 0:
            self.pintar_jogando(tela)
            self.pintar_gameover(tela)
    
    def pintar_gameover(self,tela):
        pass

    def pintar_jogando(self,tela):
        if self.estado  == 1:
            if 0< self.img < 2 and self.i == 1:
                self.img += 1
            elif 0< self.img < 2 and self.i == -1:
                self.img -= 1
            elif self.img == 2:
                self.i = -1
                self.img -= 1
            elif self.img == 0:
                self.i = 1
                self.img += 1
        
        
        self.img_atual = self.IMGS[self.img] 
        tela.blit(self.img_atual,(self.x,self.y))

    def pular(self):
        self.tempo_movimentando = 0
        self.velocidade = -10.5
        self.altura = self.y
    
    def movimento(self):
        if self.estado == 1:
            self.movimento_jogando()
        elif self.estado == 0:
            self.movimento_gameover()

    def movimento_gameover(self):
        pass

    def movimento_jogando(self):
        self.tempo_movimentando += 1
        
        dd = self.velocidade * self.tempo_movimentando + 3* self.tempo_movimentando**2 #Distancia Deslocada(Formula fisica da aceleração : VAriaçãoDeslocamento = VelocidadeInicial*TempoDeMovimento + 0.5 * aceleração *TempoDeMovimento)
        #dd = dd*1.1 if dd >=0 else dd # Fiz isso para ele cair 10% mais rapido do que ele ja iria cair

        if dd >= 30: #se a distancia deslocada passar de 16, ele não irar aumentar mais
            dd = 30
        if dd < 0:
            dd -= 12
      
        self.y = self.y + dd

    def processar_eventos(self,eventos):
        for e in eventos:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_w or e.key == pygame.K_UP:
                    self.pular()
                elif e.key == pygame.K_r:
                    self.x, self.y = (200,200)

    def get_mask(self): #funcao que iremos usar para verificar colisão <Ver video : Python Flappy Bird AI Tutorial (with NEAT) - Pixel Perfect Collision w/ Pygame pare entender oq é essa mascara
        return pygame.mask.from_surface(self.img_atual)

class Pipe:
    ESPACO_ENTRE_CANOS = 150
    VEL = 5
    def __init__(self, x):
        self.x = x
        self.altura = 0

        self.top = 0 #onde a parte de cima do cano vai ser desenhada
        self.bot = 0 #onde a parte de baixo do cano vai ser desenhada

        self.cano_top = pygame.transform.flip(PIPE_IMG,False,True) # Vira o cano
        self.cano_bot = PIPE_IMG

        self.passou = False #FAlse se o bird ja passou o cano ou não
        self.determina_altura() #vai determinar onde o cano d cima e o d baixo vão ser desenhados
        self.estado = 1

    def determina_altura(self):
        self.altura = random.randrange(50,450)
        self.top = self.altura - self.cano_top.get_height()
        self.bot = self.altura + self.ESPACO_ENTRE_CANOS

    def movimento(self):
        if self.estado == 1:
            self.movimento_jogando()
        elif self.estado == 0:
            self.movimento_gameover()

    def movimento_gameover(self):
        pass

    def movimento_jogando(self):
        self.x -= self.VEL
    
    def pintar_texto_centro(self,texto,tela):
        texto_img = fonte.render(texto,True, (255,255,255))
        texto_x = (tela.get_width() - texto_img.get_width()) // 2
        texto_y = (tela.get_height() - texto_img.get_height()) //2 
        tela.blit(texto_img,(texto_x,texto_y))

    def pintar(self,tela):
        if self.estado == 1:
            self.pintar_jogando(tela)
        elif self.estado == 0:
            self.pintar_jogando(tela)
            self.pintar_gameover(tela)
    
    def pintar_gameover(self,tela):
        self.pintar_texto_centro("G A M E   O V E R", tela)

    def pintar_jogando(self,tela):
        tela.blit(self.cano_top,(self.x,self.top))
        tela.blit(self.cano_bot,(self.x,self.bot))

    def colisao(self, bird):
        bird_mask = bird.get_mask()
        top_mask  = pygame.mask.from_surface(self.cano_top)
        bot_mask  = pygame.mask.from_surface(self.cano_bot) 

        #Vamos calcular O quão longe as "mask" estão longe uma da outra
        top_deslocamento = (self.x - bird.x, self.top - round(bird.y))
        bot_deslocamento = (self.x - bird.x, self.bot - round(bird.y))

        b_point = bird_mask.overlap(bot_mask, bot_deslocamento)#ponto de colisao entre a bird_mask e o bot_pipe usando com base o quão longe o passado esta do bot_pipe, por isso usamos bot_deslocamento|rotorna None se n ouver  colisao
        t_point = bird_mask.overlap(top_mask, top_deslocamento)

        if b_point or t_point:
            return True
        else: 
            return False

class Base:
    VEL = 5
    LARGURA = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self,y):
        self.y = y
        self.x1 = 0 #primeira imagem que ira aparecer na tela
        self.x2 = self.LARGURA # segunda iamgem que estara escondida e que ira entrar ao msm tempo que a imagem um começar a sair
        self.estado = 1

    def movimento(self):
        if self.estado == 1:
            self.movimento_jogando()
        elif self.estado == 0:
            self.movimento_gameover()

    def movimento_gameover(self):
        pass

    def movimento_jogando(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA

        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA 
    
    def pintar(self,tela):
        if self.estado == 1:
            self.pintar_jogando(tela)
        elif self.estado == 0:
            self.pintar_jogando(tela)
            self.pintar_gameover(tela)
    
    def pintar_gameover(self,tela):
        pass

    def pintar_jogando(self,tela):
        tela.blit(self.IMG,(self.x1,self.y))
        tela.blit(self.IMG,(self.x2,self.y))
#-------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------#
def draw_window(tela, bird,pipes,base,score):
    tela.blit(BG_IMG,(0,0))
    bird.pintar(tela)
    for pipe in pipes:
        pipe.pintar(tela)
    base.pintar(tela)

    text_score = fonte.render("Score: {0}".format(score),1,(255,255,255))
    tela.blit(text_score,(LARGURA - 10 - text_score.get_width(),10))

    pygame.display.update()




def main():
    score = 0
    bird = Bird(230,350)
    pipes = [Pipe(600)]
    base = Base(730)
    clock = pygame.time.Clock()
    while True:
        #clock.tick(30) #30 ticks por segundo
        # Calcula as regras
        rem = []
        add_pipe = False
        colisao = 0
        for pipe in pipes:
            if pipe.colisao(bird):
                pipe.estado = 0
                base.estado = 0
                bird.estado = 0
                colisao = 1
                break
            if pipe.x + pipe.cano_top.get_width() < 0 : #Se ele estiver fora da tela
                rem.append(pipe)
            if not pipe.passou and pipe.x < bird.x:
                pipe.passou = True
                add_pipe = True

            pipe.movimento()
        
        if add_pipe and not colisao:
            score += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)


        if bird.y + bird.img_atual.get_height() >= base.y:
            pipe.estado = 0
            base.estado = 0
            bird.estado = 0

        base.movimento()
        bird.movimento()

        # Pinta a tela
        draw_window(tela,bird,pipes,base,score)

        # Captura os eventos
        eventos = pygame.event.get()
        bird.processar_eventos(eventos)

        for e in eventos:
            if e.type is pygame.QUIT:
                exit()
            if bird.estado == 0 and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    main()

main()
    


