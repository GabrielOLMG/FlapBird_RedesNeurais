'''
        -> Para Ativar a venv basta fazer: FlapBird\Scripts\activate.bat
        -> py FlapBird_IA.py
        -> Objetos que queremos criar: Canos, Passaros, Chão
'''

import pygame
import neat
import time
import os
import random
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
GEN = 0
MAX_SCORE = 0

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
        
    
    def pintar(self,tela):
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
        self.tempo_movimentando += 1
        
        dd = self.velocidade * self.tempo_movimentando + 3* self.tempo_movimentando**2 #Distancia Deslocada(Formula fisica da aceleração : VAriaçãoDeslocamento = VelocidadeInicial*TempoDeMovimento + 0.5 * aceleração *TempoDeMovimento)
        dd = dd*1.1 if dd >=0 else dd # Fiz isso para ele cair 10% mais rapido do que ele ja iria cair

        if dd >= 30: #se a distancia deslocada passar de 16, ele não irar aumentar mais
            dd = 30
        if dd < 0:
            dd -= 12
      
        self.y = self.y + dd


    def get_mask(self): #funcao que iremos usar para verificar colisão <Ver video : Python Flappy Bird AI Tutorial (with NEAT) - Pixel Perfect Collision w/ Pygame pare entender oq é essa mascara
        return pygame.mask.from_surface(self.img_atual)

class Pipe:
    
    VEL = 5
    def __init__(self, x, espaco):
        self.x = x
        self.altura = 0
        self.ESPACO_ENTRE_CANOS = espaco
        self.top = 0 #onde a parte de cima do cano vai ser desenhada
        self.bot = 0 #onde a parte de baixo do cano vai ser desenhada

        self.cano_top = pygame.transform.flip(PIPE_IMG,False,True) # Vira o cano
        self.cano_bot = PIPE_IMG

        self.passou = False #FAlse se o bird ja passou o cano ou não
        self.determina_altura() #vai determinar onde o cano d cima e o d baixo vão ser desenhados

    def determina_altura(self):
        self.altura = random.randrange(50,450)
        self.top = self.altura - self.cano_top.get_height()
        self.bot = self.altura + self.ESPACO_ENTRE_CANOS

    def movimento(self):
        self.x -= self.VEL

    def pintar(self,tela):
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

    def movimento(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA

        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA 
    
    def pintar(self,tela):
        tela.blit(self.IMG,(self.x1,self.y))
        tela.blit(self.IMG,(self.x2,self.y))
#-------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------# Jogo
def draw_window(tela, birds,pipes,base,score, gen,score_max):
    tela.blit(BG_IMG,(0,0))
    for pipe in pipes:
        pipe.pintar(tela)
    
    for bird in birds:
        bird.pintar(tela)
    base.pintar(tela)

    text_gen = fonte.render("Geracao: {0}".format(gen),1,(255,255,255))
    text_score = fonte.render("Score: {0}".format(score),1,(255,255,255))
    text_vivos = fonte.render("Vivos: {0}".format(len(birds)),1,(255,255,255))
    text_max_score = fonte.render("Recorde: {0}".format(score_max),1,(255,255,255))
    tela.blit(text_gen,(10,10))
    tela.blit(text_score,(LARGURA - 10 - text_score.get_width(),10))
    tela.blit(text_vivos,(10,40))  
    tela.blit(text_max_score,(10,70))   
    pygame.display.update()




def main(genomes, config): #vamos usar o main como nossa fitness_func. PAra isso precisa ter obrigatoriamente esses dois inputs
    global GEN, MAX_SCORE
    
    nets =[]
    ge = []
    birds = []

    for __,g in genomes: # genomes é uma tupla contendo o id e o obj, por isso ignoramosa primeira parte com __
        net = neat.nn.FeedForwardNetwork.create(g, config) #criando uma rede neural para o genoma
        nets.append(net) #coloca na lista
        birds.append(Bird(230,350))
        g.fitness = 0
        ge.append(g)
        #Colocamos tudo na mesma posição, então conseguimos acessar tudo so pela posição do passaro na lista


    x = random.randrange(110,200)
    pipes = [Pipe(600,x)]
    base = Base(730)
    clock = pygame.time.Clock()
    score = 0
    run = True
    while run:
        clock.tick(30) #30 ticks por segundo
        # Calcula as regras
        rem = []

        pipe_ind = 0 #para qual pipe o passaro vai estar olhando
        if len(birds) >0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].cano_top.get_width(): #Se vc passou o pipe 0, então vamos olhar para o segundo pipe
                pipe_ind = 1
        else:
            run = False
            break


        for x,bird in enumerate(birds):
            bird.movimento()
            ge[x].fitness += 0.1 #damos um pouco de pontos por ele ter conseguido sobreviver até agr
            
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].altura), abs(bird.y - pipes[pipe_ind].bot) )) #ativa o neuronio com os input e devolve o output

            if output[0]>0.5: #ja que so temos um neuronio, então o output so vai ter um eleemnto, que esta numa lista
                bird.pular()


        add_pipe = False
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.colisao(bird):
                    ge[x].fitness -=1 #a principio vamos fazer com q toda vez q o bird acertar o cano, ele vai ter o fitness score reduzido, d forma q n iremos favorecer passaros com menos pontuação
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passou and pipe.x < bird.x:
                    pipe.passou = True
                    add_pipe = True
            
            if pipe.x + pipe.cano_top.get_width() < 0 : #Se ele estiver fora da tela
                rem.append(pipe)

            pipe.movimento()
        
        if add_pipe: #Verifica se já pode add outro cano
            score += 1
            if score >= MAX_SCORE:
                MAX_SCORE = score
            for g in ge:
                g.fitness += 1
            x = random.randrange(110,200)    
            pipes.append(Pipe(600,x))

        for r in rem: # remove  os canos da lista
            pipes.remove(r)

        for x,bird in enumerate(birds):
            if bird.y + bird.img_atual.get_height() >= base.y or bird.y < 0: # Verifica Se encostou no cão
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.movimento()
        

        # Pinta a tela
        draw_window(tela,birds,pipes,base,score,GEN, MAX_SCORE)

        # Captura os eventos
        eventos = pygame.event.get()

        for e in eventos:
            if e.type is pygame.QUIT:
                run = False
                pygame.quit()
                quit()
    GEN +=1
    


#-------------------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------------------#Neat


def run(config_path):
    #carregando as configuraçoes
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path) 
    
    #População com as configuraçoes do txt
    p = neat.Population(config) 

    # retorna dados estatisticos sobre o processo
    p.add_reporter(neat.StdOutReporter(True)) 
    stats = neat.StatisticsReporter()
    p.add_reporter(stats) 

    winner = p.run(main,100) #run(A função que iremos usar(Que neste caso é o quanto o passaro percorreu) , quantas geracoes vão usar a funcao)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__) #nos da o diretoria em que estamos
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

