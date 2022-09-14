import clipboard as c
import os
from secrets import choice
import pygame
from pygame.locals import *
from sys import exit
import random
from tkinter import *
import mysql.connector as mysql

record = 0
'''
#janela de login
def enter():
    nome = e_nome.get()
    c.copy(nome)
    con=mysql.connect(host='localhost',user='root',password='',database='test')
    cursor = con.cursor()
    cursor.execute("insert into dinosauro values(' " + nome +" ', ' " + str(record) +" ')")
    cursor.execute('commit')
    con.close()
    r.destroy()


r=Tk()
r.geometry('300x200')
r.title('Interface com Banco de Dados')

player=Label(r,text='Entre com seu Nome')
player.place(x=20,y=30)

e_nome=Entry()
e_nome.place(x=22,y=50)

inserir=Button(r,text='Enter', command=enter)
inserir.place(x=20,y=80)

r.mainloop()

'''


pygame.init()
pygame.mixer.init()


diretorio_princiapal = os.path.dirname(__file__)
diretorio_imagens = os.path.join(diretorio_princiapal, 'img')
diretorio_sons = os.path.join(diretorio_princiapal, 'som')


#tela e e tela de fundo
largura = 640
altura = 480

tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption('Dinossaur')
BRANCA = (255,255,255)



sprite_sheet = pygame.image.load(os.path.join(diretorio_imagens, 'dinoSprites.png')).convert_alpha()
som_colisao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'sons_death_sound.wav'))
som_colisao.set_volume(1)

som_pontuacao = pygame.mixer.Sound(os.path.join(diretorio_sons, 'sons_score_sound.wav'))
som_pontuacao.set_volume(1)




colidiu = False

escolha_obstaculo = choice([0, 1])

pontos = 0

velocidade_jogo = 10

def printar(msg, tamanho, cor):
    fonte = pygame.font.SysFont('arial', tamanho, True, False)
    mensagem = f'{msg}'
    texto_formatado = fonte.render(mensagem, True, cor)
    return texto_formatado


def reiniciar_jogo():
    global pontos, velocidade_jogo, colidiu, escolha_obstaculo
    pontos = 0
    velocidade_jogo =  10
    colidiu = False
    dino.rect.y = altura - 64 - 96/2
    dino.pulo = False
    dino_voador.rect.x = largura
    cacto.rect.x = largura
    escolha_obstaculo = choice([0, 1])
    


#jogador
class Dino(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.som_pulo = pygame.mixer.Sound(os.path.join(diretorio_sons, 'sons_jump_sound.wav'))
        self.som_pulo.set_volume(1)
        self.imagens_dinossauro = []
        for i in range(3):
            img = sprite_sheet.subsurface((i*32,0), (32, 32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_y_inicial = altura - 64 - 96/2
        self.rect.center = (70, altura-64)
        self.pulo = False


    def pular(self):
        self.pulo = True
        self.som_pulo.play()


    def update(self):
        if self.pulo == True:
            if self.rect.y <= 615:
                self.pulo = False
            self.rect.y = -20
        else:
            if self.rect.y < self.pos_y_inicial:
                self.rect.y += 20
            else:
                self.rect.y = self.pos_y_inicial

        if self.index_lista > 2:
            self.index_lista = 0
        self.index_lista += 0.25
        self.image = self.imagens_dinossauro[int(self.index_lista)]




#ambiente
class Nuvens(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((7*32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*3, 32*3))
        self.rect = self.image.get_rect()
        self.rect.y = random.randrange(50, 200, 50)
        self.rect.x = largura - random.randrange(30, 300, 90)
    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.y = random.randrange(50, 200, 50)
            self.rect.x = largura
        self.rect.x -= velocidade_jogo



class Cacto(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((5*32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstaculo
        self.rect.center = (largura, altura-64)
        self.rect.x = largura

    def update(self):
        if self.escolha== 0:
            if self.rect.topright[0] < 0:
                self.rect.x = largura
            self.rect.x -= velocidade_jogo

class DinoVoador(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imagens_dinossauro = []
        for i in range(3,5):
            img = sprite_sheet.subsurface((i*32, 0), (32, 32))
            img = pygame.transform.scale(img, (32*3, 32*3))
            self.imagens_dinossauro.append(img)

        self.index_lista = 0
        self.image = self.imagens_dinossauro[self.index_lista]
        self.mask = pygame.mask.from_surface(self.image)
        self.escolha = escolha_obstaculo
        self.rect = self.image.get_rect()
        self.rect.center = (largura, 300)
        self.rect.x = largura

    def update(self):
        if self.escolha == 1:
            if self.rect.topright[0] < 0:
                 self.rect.x = largura
            self.rect.x -= velocidade_jogo

        if self.index_lista > 1:
            self.index_lista = 0
        self.index_lista += 0.20
        self.image = self.imagens_dinossauro[int(self.index_lista)]




#Chao
class Chao(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        pygame.sprite.Sprite.__init__(self)
        self.image = sprite_sheet.subsurface((6*32, 0), (32, 32))
        self.image = pygame.transform.scale(self.image, (32*2, 32*2))
        self.rect = self.image.get_rect()
        self.rect.y = altura - 64
        self.rect.x = pos_x *64

    def update(self):
        if self.rect.topright[0] < 0:
            self.rect.x = largura
        self.rect.x -= 10




todas_as_sprites = pygame.sprite.Group()
dino = Dino()
todas_as_sprites.add(dino)

for i in range(3):
    nuvem = Nuvens()
    todas_as_sprites.add(nuvem)

for j in range(17):
    chao = Chao(j)
    todas_as_sprites.add(chao)

cacto = Cacto()
todas_as_sprites.add(cacto)

dino_voador = DinoVoador()
todas_as_sprites.add(dino_voador)

grupo_obstaculos = pygame.sprite.Group()
grupo_obstaculos.add(cacto)
grupo_obstaculos.add(dino_voador)



#relogio
relogio = pygame.time.Clock()



while True:
    relogio.tick(30)
    tela.fill(BRANCA)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()
        if event.type == KEYDOWN:
            if event.key == K_SPACE and colidiu == False:
                if dino.rect.y != dino.pos_y_inicial:
                    pass
                else:
                    dino.pular()

            if event.key == K_f and colidiu == True:
                reiniciar_jogo()

    colisoes = pygame.sprite.spritecollide(dino, grupo_obstaculos, False, pygame.sprite.collide_mask)

    todas_as_sprites.draw(tela)
    
    if cacto.rect.topright[0] <= 0 or dino_voador.rect.topright[0] <= 0:
        escolha_obstaculo = choice([0, 1])
        cacto.rect.x = largura
        dino_voador.rect.x = largura
        cacto.escolha = escolha_obstaculo
        dino_voador.escolha = escolha_obstaculo

    if colisoes and colidiu == False:
        som_colisao.play()
        colidiu = True

    if colidiu == True:
        if pontos % 100 == 0:
            pontos += 1
        if record < pontos:
            record = pontos
        game_over = printar("YOU DIE", 60, (255,0,0))
        tela.blit(game_over, (largura/2, altura/2))
        F = printar('Press F to Pay Respects', 20, (0,0,0))
        tela.blit(F, (largura/2+15, altura/2+80))
        '''nome = c.paste()
        con=mysql.connect(host='localhost',user='root',password='',database='test')
        cursor = con.cursor()
        cursor.execute("update dinosauro set pontos=' "+ str(record) +" ' where nome =' "+ nome +" '")
        cursor.execute('commit')
        con.close()'''

        

    else:
        pontos += 1
        todas_as_sprites.update()
        pontuacao = printar(pontos, 35, (0,0,0))


    if pontos % 100 == 0:
        som_pontuacao.play()
        if velocidade_jogo >= 23:
            velocidade_jogo += 0
        else:
            velocidade_jogo += 1

        

    tela.blit(pontuacao, (520, 30))



    pygame.display.flip()







'''Easter egg
def pular(self):
        self.pulo = True


def update(self):
     if self.pulo == True:
        self.rect.y -= 20
'''