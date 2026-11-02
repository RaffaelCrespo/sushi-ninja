
import pygame
import random
import sys
import os
import math
from typing import TypedDict
from pygame import gfxdraw


# Inicialização
pygame.init()
pygame.mixer.init()


# Configurações
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Sushi Ninja - Raffael Crespo")
pygame.mouse.set_visible(False)


# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDE = (0, 255, 0)


# Status
MENU, JOGANDO, GAME_OVER, PAUSADO = 0, 1, 2, 3
estado = MENU


# Caminhos dos arquivos
def resource_path(relative_path):
    """Retorna o caminho absoluto de um recurso do jogo."""
    base_path = getattr(
        sys,
        "_MEIPASS",
        os.path.dirname(os.path.abspath(__file__))
    )
    return os.path.join(base_path, relative_path)


# Tipagem das partículas
class Particula(TypedDict):
    x: float
    y: float
    vel_x: float
    vel_y: float
    tamanho: int
    cor: tuple[int, int, int]
    vida: int


# Carregamento dos recursos
def carregar_assets():
    img_dir = "assets/img"
    snd_dir = "assets/snd"

    def carregar_imagem(nome: str, escala: float = 1.0) -> pygame.Surface:
        try:
            caminho = resource_path(os.path.join(img_dir, nome))
            imagem = pygame.image.load(caminho).convert_alpha()

            tamanho = (
                int(imagem.get_width() * escala),
                int(imagem.get_height() * escala)
            )

            return pygame.transform.scale(imagem, tamanho)

        except (pygame.error, OSError):
            superficie = pygame.Surface(
                (100, 100),
                pygame.SRCALPHA
            )

            cor = VERDE if "sushi" in nome else VERMELHO

            pygame.draw.rect(
                superficie,
                cor,
                (0, 0, 100, 100),
                border_radius=10
            )

            pygame.draw.rect(
                superficie,
                BRANCO,
                (0, 0, 100, 100),
                2,
                border_radius=10
            )

            texto = pygame.font.SysFont("Arial", 12).render(
                nome.split(".")[0],
                True,
                PRETO
            )

            superficie.blit(
                texto,
                texto.get_rect(center=(50, 50))
            )

            return superficie

    def carregar_som(nome: str) -> pygame.mixer.Sound:
        try:
            caminho = resource_path(os.path.join(snd_dir, nome))
            return pygame.mixer.Sound(caminho)

        except (pygame.error, OSError):
            return pygame.mixer.Sound(
                buffer=bytes([128] * 1000)
            )

    return {
        "coracao": carregar_imagem("coracao.png", 0.08),

        "sushis": [
            carregar_imagem(f"sushi{i + 1}.png", 1.5)
            for i in range(7)
        ],

        "objetos": [
            carregar_imagem("teddy.png"),
            carregar_imagem("pendrive.png", 0.2),
            carregar_imagem("bola.png", 0.7),
            carregar_imagem("nokia.png", 1.2),
            carregar_imagem("sapato.png", 1.8)
        ],

        "fundo_menu": carregar_imagem("menu_background.jpg"),
        "fundo_jogo": carregar_imagem("game_background.jpg"),
        "shuriken": carregar_imagem("shuriken.png", 0.3),

        "sons": {
            "corte": carregar_som("slice.wav"),
            "corte_sushi": carregar_som("sushi_cut.wav"),
            "corte_objeto": carregar_som("object_cut.wav"),
            "perde_vida": carregar_som("lose_life.wav"),
            "game_over": carregar_som("game_over.wav")
        }
    }


assets = carregar_assets()


# Fontes
fonte = pygame.font.SysFont("Arial", 36)
fonte_grande = pygame.font.SysFont("Arial", 72)


# Partículas
particulas: list[Particula] = []


def criar_particulas(pos, cor, q=20):
    novas_particulas: list[Particula] = [
        {
            "x": pos[0],
            "y": pos[1],
            "vel_x": random.uniform(-5, 5),
            "vel_y": random.uniform(-10, -5),
            "tamanho": random.randint(2, 5),
            "cor": cor,
            "vida": random.randint(20, 40)
        }
        for _ in range(q)
    ]

    particulas.extend(novas_particulas)


def atualizar_particulas():
    for i in range(len(particulas) - 1, -1, -1):
        particula = particulas[i]

        particula["x"] += particula["vel_x"]
        particula["y"] += particula["vel_y"]
        particula["vida"] -= 1

        if particula["vida"] <= 0:
            particulas.pop(i)


def desenhar_particulas():
    for particula in particulas:
        alpha = min(255, particula["vida"] * 6)

        gfxdraw.filled_circle(
            tela,
            int(particula["x"]),
            int(particula["y"]),
            particula["tamanho"],
            (*particula["cor"], alpha)
        )


# Definição das classes
class Item:
    def __init__(self, tipo_item, x=None):
        self.tipo = tipo_item

        self.imagem = random.choice(
            assets["sushis"]
            if tipo_item == "sushi"
            else assets["objetos"]
        )

        self.pontos = 10 if tipo_item == "sushi" else -5

        self.x = (
            x if x is not None
            else random.randint(50, LARGURA - 50)
        )

        self.y = ALTURA + 50

        self.velocidade_y = random.uniform(-25, -15)
        self.velocidade_x = random.uniform(-3, 3)

        self.gravidade = 0.5
        self.angulo = 0
        self.velocidade_rotacao = random.uniform(-5, 5)

        self.cortado = False
        self.tempo_vida = 30

        self.mask = pygame.mask.from_surface(self.imagem)

    def update(self):
        if not self.cortado:
            self.velocidade_y += self.gravidade

            self.x += self.velocidade_x
            self.y += self.velocidade_y

            self.angulo += self.velocidade_rotacao

        else:
            self.tempo_vida -= 1

            self.velocidade_y += self.gravidade * 0.5

            self.x += self.velocidade_x * 2
            self.y += self.velocidade_y * 2

            self.angulo += self.velocidade_rotacao * 2

        return (
            self.tempo_vida <= 0
            or self.y > ALTURA + 100
        )

    def draw(self):
        imagem_rotacionada = pygame.transform.rotate(
            self.imagem,
            self.angulo
        )

        tela.blit(
            imagem_rotacionada,
            imagem_rotacionada.get_rect(
                center=(self.x, self.y)
            )
        )

    def cortar(self):
        self.cortado = True

        self.velocidade_x = random.uniform(-8, 8)
        self.velocidade_y = random.uniform(-15, -8)
        self.velocidade_rotacao = random.uniform(-15, 15)

        criar_particulas(
            (self.x, self.y),
            VERDE if self.tipo == "sushi" else VERMELHO
        )

        assets["sons"][
            "corte_sushi" if self.tipo == "sushi"
            else "corte_objeto"
        ].play()

        return self.pontos


class Rastro:
    def __init__(self):
        self.pontos = []
        self.tempo_vida = 15

    def add_ponto(self, pos):
        self.pontos.append(pos)

        if len(self.pontos) > 5:
            self.pontos.pop(0)

    def update(self):
        self.tempo_vida -= 1
        return self.tempo_vida <= 0

    def draw(self):
        if len(self.pontos) > 1:
            pygame.draw.lines(
                tela,
                BRANCO,
                False,
                self.pontos,
                3
            )


# Listas do jogo
itens: list[Item] = []
rastros: list[Rastro] = []


# Funções do jogo
def reiniciar_jogo():
    global vidas
    global pontuacao
    global tempo_ultimo_item

    vidas = 4
    pontuacao = 0

    itens.clear()
    particulas.clear()
    rastros.clear()

    tempo_ultimo_item = 0

    pygame.mixer.music.stop()

    caminho_musica = resource_path(
        os.path.join("assets", "snd", "game_music.wav")
    )

    pygame.mixer.music.load(caminho_musica)
    pygame.mixer.music.play(-1)


def calcular_dificuldade(pontos):
    nivel = min(10, pontos // 100)

    return {
        "spawn_delay": max(10, 30 - nivel * 2),
        "prob_objeto": min(0.4, 0.1 + nivel * 0.03)
    }


def render_texto_com_sombra(
    fonte_texto,
    texto,
    cor,
    cor_sombra=PRETO
):
    texto_sombra = fonte_texto.render(
        texto,
        True,
        cor_sombra
    )

    texto_normal = fonte_texto.render(
        texto,
        True,
        cor
    )

    return texto_sombra, texto_normal


# Telas do jogo
def desenhar_menu():
    tela.blit(assets["fundo_menu"], (0, 0))

    sombra_renderizada, titulo = render_texto_com_sombra(
        fonte_grande,
        "SUSHI NINJA",
        BRANCO
    )

    tela.blit(
        sombra_renderizada,
        (
            LARGURA // 2 - titulo.get_width() // 2 + 2,
            102
        )
    )

    tela.blit(
        titulo,
        (
            LARGURA // 2 - titulo.get_width() // 2,
            100
        )
    )

    textos = [
        "CONTROLES:",
        "- Mova o mouse para controlar a shuriken",
        "- Clique e arraste para cortar os sushis",
        "- Corte os sushis para ganhar pontos (+10)",
        "- Evite cortar os objetos errados (-5 pontos)",
        "- Você tem 4 vidas no total"
    ]

    for i, texto in enumerate(textos):
        sombra_renderizada, texto_render = render_texto_com_sombra(
            fonte,
            texto,
            BRANCO
        )

        tela.blit(
            sombra_renderizada,
            (
                LARGURA // 2 - texto_render.get_width() // 2 + 2,
                200 + i * 40 + 2
            )
        )

        tela.blit(
            texto_render,
            (
                LARGURA // 2 - texto_render.get_width() // 2,
                200 + i * 40
            )
        )

    sombra_renderizada, iniciar = render_texto_com_sombra(
        fonte,
        "CLIQUE PARA COMECAR",
        BRANCO
    )

    tela.blit(
        sombra_renderizada,
        (
            LARGURA // 2 - iniciar.get_width() // 2 + 2,
            502
        )
    )

    tela.blit(
        iniciar,
        (
            LARGURA // 2 - iniciar.get_width() // 2,
            500
        )
    )


def desenhar_jogo():
    tela.blit(assets["fundo_jogo"], (0, 0))

    desenhar_particulas()

    for rastro in rastros:
        rastro.draw()

    for item in itens:
        item.draw()

    coordenadas_shuriken = pygame.mouse.get_pos()

    shuriken = pygame.transform.rotate(
        assets["shuriken"],
        pygame.time.get_ticks() / 10 % 360
    )

    tela.blit(
        shuriken,
        shuriken.get_rect(center=coordenadas_shuriken)
    )

    sombra_renderizada, pontos = render_texto_com_sombra(
        fonte,
        f"Pontos: {pontuacao}",
        BRANCO
    )

    tela.blit(sombra_renderizada, (21, 21))
    tela.blit(pontos, (20, 20))

    for i in range(vidas):
        tela.blit(
            assets["coracao"],
            (20 + i * 40, 70)
        )


def desenhar_game_over():
    tela.blit(assets["fundo_jogo"], (0, 0))

    sombra_renderizada, game_over = render_texto_com_sombra(
        fonte_grande,
        "VOCÊ PERDEU!",
        VERMELHO
    )

    tela.blit(
        sombra_renderizada,
        (
            LARGURA // 2 - game_over.get_width() // 2 + 2,
            202
        )
    )

    tela.blit(
        game_over,
        (
            LARGURA // 2 - game_over.get_width() // 2,
            200
        )
    )

    sombra_renderizada, pontos = render_texto_com_sombra(
        fonte,
        f"Pontuação final: {pontuacao}",
        BRANCO
    )

    tela.blit(
        sombra_renderizada,
        (
            LARGURA // 2 - pontos.get_width() // 2 + 2,
            302
        )
    )

    tela.blit(
        pontos,
        (
            LARGURA // 2 - pontos.get_width() // 2,
            300
        )
    )

    sombra_renderizada, reiniciar = render_texto_com_sombra(
        fonte,
        "Clique para voltar ao menu",
        BRANCO
    )

    tela.blit(
        sombra_renderizada,
        (
            LARGURA // 2 - reiniciar.get_width() // 2 + 2,
            402
        )
    )

    tela.blit(
        reiniciar,
        (
            LARGURA // 2 - reiniciar.get_width() // 2,
            400
        )
    )


# Inicialização das variáveis
vidas = 0
pontuacao = 0
tempo_ultimo_item = 0

mouse_pressionado = False
mouse_pos_anterior = None
mouse_pos_inicio = None

reiniciar_jogo()


# Loop principal
clock = pygame.time.Clock()

while True:
    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if estado == MENU:
                estado = JOGANDO
                reiniciar_jogo()

            elif estado == GAME_OVER:
                estado = MENU

            elif estado == JOGANDO:
                mouse_pressionado = True
                mouse_pos_inicio = pygame.mouse.get_pos()

                assets["sons"]["corte"].play()

        if (
            evento.type == pygame.MOUSEBUTTONUP
            and estado == JOGANDO
        ):
            mouse_pressionado = False
            mouse_pos_anterior = None
            mouse_pos_inicio = None

        if (
            evento.type == pygame.KEYDOWN
            and evento.key == pygame.K_ESCAPE
        ):
            if estado == JOGANDO:
                estado = PAUSADO

            elif estado == PAUSADO:
                estado = JOGANDO

    if estado == JOGANDO:
        dificuldade = calcular_dificuldade(pontuacao)

        tempo_ultimo_item += 1

        if tempo_ultimo_item >= dificuldade["spawn_delay"]:
            novo_tipo = (
                "sushi"
                if random.random() < (1 - dificuldade["prob_objeto"])
                else "objeto"
            )

            itens.append(Item(novo_tipo))
            tempo_ultimo_item = 0

        # Atualização dos elementos
        itens = [
            item
            for item in itens
            if not item.update()
        ]

        rastros = [
            rastro
            for rastro in rastros
            if not rastro.update()
        ]

        atualizar_particulas()

        if mouse_pressionado:
            posicao_mouse_atual = pygame.mouse.get_pos()

            if (
                mouse_pos_anterior
                and math.dist(
                    posicao_mouse_atual,
                    mouse_pos_anterior
                ) > 10
            ):
                rastro = Rastro()

                rastro.add_ponto(mouse_pos_anterior)
                rastro.add_ponto(posicao_mouse_atual)

                rastros.append(rastro)

            mouse_pos_anterior = posicao_mouse_atual

            if mouse_pos_inicio and mouse_pos_anterior:
                for item in itens:
                    if not item.cortado:
                        linha = pygame.Surface(
                            (LARGURA, ALTURA),
                            pygame.SRCALPHA
                        )

                        pygame.draw.line(
                            linha,
                            BRANCO,
                            mouse_pos_inicio,
                            mouse_pos_anterior,
                            5
                        )

                        if pygame.mask.from_surface(linha).overlap(
                            item.mask,
                            (
                                int(
                                    item.x
                                    - item.imagem.get_width() // 2
                                ),
                                int(
                                    item.y
                                    - item.imagem.get_height() // 2
                                )
                            )
                        ):
                            pontuacao += item.cortar()

                            if item.pontos < 0:
                                vidas -= 1

                                assets["sons"]["perde_vida"].play()

                                if vidas <= 0:
                                    estado = GAME_OVER

                                    assets["sons"]["game_over"].play()

    # Renderização
    if estado == MENU:
        desenhar_menu()

    elif estado == JOGANDO:
        desenhar_jogo()

    elif estado == GAME_OVER:
        desenhar_game_over()

    elif estado == PAUSADO:
        desenhar_jogo()

        overlay = pygame.Surface(
            (LARGURA, ALTURA),
            pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 128))
        tela.blit(overlay, (0, 0))

        superficie_sombra, pausa = render_texto_com_sombra(
            fonte_grande,
            "PAUSADO",
            BRANCO
        )

        tela.blit(
            superficie_sombra,
            (
                LARGURA // 2 - pausa.get_width() // 2 + 2,
                ALTURA // 2 - 48
            )
        )

        tela.blit(
            pausa,
            (
                LARGURA // 2 - pausa.get_width() // 2,
                ALTURA // 2 - 50
            )
        )

    pygame.display.flip()
    clock.tick(60)
