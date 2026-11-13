#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LORDVERSO · Criador de personagens — build.py
=============================================
Lê as peças da pasta  pecas/  (PNG 1080x1350, fundo transparente),
separa cada uma em  LINHA  (contorno preto) + PINTURAS (máscaras que o
site tinge com a cor escolhida), pinta sozinho o que ainda não foi pintado
e gera o arquivo único  criador.html  (a partir do modelo.html).

Como usar:   python3 build.py
Precisa de:  pip install pillow numpy scipy opencv-python-headless

COMO ADICIONAR UMA PEÇA NOVA
  1. Salve o PNG em pecas/ (mesmo tamanho 1080x1350).
  2. Acrescente uma linha na lista  PECAS  logo abaixo.
  3. Rode  python3 build.py  e abra o criador.html.

COMO PINTAR UMA PEÇA (o que o script entende)
  Cada categoria tem  CORES_DE_PINTURA : a cor EXATA que você usou no
  desenho  ->  qual "papel" ela tem no site (pele, íris, cabelo...).
  Se você pintar uma peça nova com essas mesmas cores, ela já funciona.
  Peças só com linha (orelha, sobrancelha...) ganham pintura automática.
"""
import base64, io, json, os, sys
import numpy as np
import cv2
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(AQUI, "pecas")
W, H = 1080, 1350              # tamanho original das peças
SW, SH = 720, 900              # tamanho que vai pro site (2/3 -> arquivo leve)

# ----------------------------------------------------------------------
# 1) LISTA DE PEÇAS   (chave, nome que aparece no site, arquivo)
# ----------------------------------------------------------------------
PECAS = {
    "head": [("oval", "Oval", "cabeca_oval.png"),
             ("pontudo", "Pontudo", "cabeca_pontudo.png"),
             ("quadrado", "Quadrado", "cabeca_quadrado.png")],
    "eyes": [("palpebra", "Pálpebra", "olhos_palpebra.png"),
             ("bravo", "Bravo", "olhos_bravo.png"),
             ("fechado", "Fechados", "olhos_fechado.png")],
    "ears": [("humana", "Humanas", "orelhas_humana.png"),
             ("elfica", "Élficas curtas", "orelhas_elfica.png"),
             ("elficaL", "Élficas longas", "orelhas_elfica_longa.png")],
    "brows": [("assim", "Assimétrica", "sobrancelha_assimetrica.png"),
              ("suave", "Suave", "sobrancelha_suave.png"),
              ("pontuda", "Pontuda", "sobrancelha_pontuda.png"),
              ("longa", "Longa", "sobrancelha_longa.png")],
    "nose": [("fino", "Fino", "nariz_fino.png"),
             ("pequeno", "Pequeno", "nariz_pequeno.png"),
             ("medio", "Médio", "nariz_medio.png")],
    "mouth": [("labios", "Lábios", "boca_labios.png"),
              ("sorriso", "Sorriso", "boca_sorriso.png"),
              ("canto", "Canto", "boca_canto.png"),
              ("dentes", "Dentes", "boca_dentes.png"),
              ("lingua", "Língua", "boca_lingua.png")],
    "hair": [("repicado", "Repicado", "cabelo_repicado.png"),
             ("chanel", "Chanel", "cabelo_chanel.png"),
             ("espetado", "Espetado", "cabelo_espetado.png"),
             ("coques", "Coques e cachos", "cabelo_coques_cachos.png"),
             ("liso", "Liso longo", "cabelo_liso_longo.png"),
             ("cacheado", "Cacheado", "cabelo_cacheado.png"),
             ("coquefranja", "Coques com franja", "cabelo_coques_franja.png"),
             ("cachosfofos", "Cachos fofos", "cabelo_cachos_fofos.png"),
             ("bagunca", "Bagunçado", "cabelo_bagunca.png"),
             ("cachostrancas", "Cachos e tranças", "cabelo_cachos_trancas.png"),
             ("desfiado", "Desfiado", "cabelo_desfiado.png"),
             ("cacheadocurto", "Cacheado curto", "cabelo_cacheado_curto.png"),
             ("trancasondas", "Tranças onduladas", "cabelo_trancas_ondas.png"),
             ("ondulongo", "Ondulado longo", "cabelo_ondulado_longo.png"),
             ("ondumedio", "Ondulado médio", "cabelo_ondulado_medio.png"),
             ("chiquinhas", "Maria-chiquinha", "cabelo_chiquinhas.png"),
             ("lisofranja", "Liso com franja", "cabelo_liso_franja.png"),
             ("bobfranja", "Bob com franja", "cabelo_bob_franja.png"),
             ("sofranja", "Só a franja", "cabelo_so_franja.png"),
             ("novo1", "Repicado volumoso", "cabelo_novo1.png"),
             ("novo2", "Cachos curtos", "cabelo_novo2.png"),
             ("novo3", "Lateral ondulado", "cabelo_novo3.png"),
             ("novo4", "Liso com mecha", "cabelo_novo4.png"),
             ("novo5", "Repicado com franja", "cabelo_novo5.png")],
    "clothes": [("regata", "Regata", "roupa_regata.png"),
               ("tubarao", "Moletom tubarão", "roupa_tubarao.png"),
               ("estrelas", "Blusa de estrelas", "roupa_estrelas.png"),
               ("esportiva", "Camiseta esportiva", "roupa_esportiva.png"),
               ("capuz", "Moletom com capuz", "roupa_capuz.png"),
               ("gravata", "Camisa e gravata", "roupa_gravata.png"),
               ("jaqueta", "Jaqueta de estrelas", "roupa_jaqueta.png"),
               ("cachecol", "Cachecol e casaco", "roupa_cachecol.png"),
               ("espartilho", "Top espartilho", "roupa_espartilho.png"),
               ("transparente", "Top mangas transparentes", "roupa_transparente.png"),
               ("jardineira", "Jardineira", "roupa_jardineira.png"),
               ("bolinhas", "Top de bolinhas", "roupa_bolinhas.png"),
               ("adesivos", "Adesivos em X", "roupa_adesivos.png"),
               ("xadrez", "Gola alta xadrez", "roupa_xadrez.png"),
               ("cruzado", "Tiras cruzadas", "roupa_cruzado.png"),
               ("suetergola", "Suéter caído com alças", "roupa_sueter_gola.png"),
               ("jaquetacoracao", "Jaqueta cinza com coração", "roupa_jaqueta_coracao.png"),
               ("redealcas", "Rede com top de alças", "roupa_rede_alcas.png"),
               ("casacoxadrez", "Casaco xadrez vermelho", "roupa_casaco_xadrez_vermelho.png"),
               ("sueterverde", "Suéter verde de folhas", "roupa_sueter_verde.png"),
               ("topmarrom", "Top marrom de amarrar", "roupa_top_marrom_amarrado.png")],
    # Estes 4 desenhos vêm com as DUAS mãos no mesmo PNG (maos_*.png): o build separa cada um
    # em mão esquerda + mão direita (ver MAOS_QUE_SE_DIVIDEM) e eles aparecem nas abas das mãos
    # separadas. Só "Dedos se tocando" fica de verdade como peça junta.
    "hands": [("dedo", "Dedo pra cima", "maos_dedo.png"),
              ("rock", "Rock", "maos_rock.png"),
              ("lata", "Latinha", "maos_lata.png"),
              ("pirulito", "Pirulito", "maos_pirulito.png"),
              ("tocando", "Dedos se tocando", "maos_dedos_tocando.png")],
    # Mãos separadas: escolhe a esquerda e a direita cada uma no seu canto.
    # "Esquerda/direita" = lado da TELA (esquerda = lado esquerdo da imagem). Seguem a cor da pele.
    "handL": [("dedomeio", "Dedo do meio", "mao_e_dedo_meio.png"),
              ("v", "Dedos em V", "mao_e_v.png"),
              ("palmas", "Palma aberta", "mao_e_palmas.png")],
    "handR": [("dedomeio", "Dedo do meio", "mao_d_dedo_meio.png"),
              ("v", "Dedos em V", "mao_d_v.png"),
              ("palmas", "Palma aberta", "mao_d_palmas.png")],
    # Chifres/orelhas: ficam com as cores ORIGINAIS do desenho (sem seletor)
    "extras": [("gato", "Orelhas de gato", "acessorio_orelhas_gato.png"),
            ("curvos", "Chifres curvos amarelos", "acessorio_curvos_amarelos.png"),
            ("barbatana", "Barbatanas verdes", "acessorio_barbatanas.png"),
            ("chifrinhos", "Chifrinhos vermelhos", "acessorio_chifrinhos.png"),
            ("chifres", "Chifres vermelhos", "acessorio_chifres.png")],
    # Acessórios de rosto: óculos (1 por vez) e piercings (pode usar vários juntos)
    "glasses": [("gatinho", "Gatinho", "oculos_gatinho.png"),
                ("redondo", "Redondo", "oculos_redondo.png")],
    "pierc": [("septo", "Septo", "piercing_septo.png"),
              ("bochecha", "Bochecha", "piercing_bochecha.png"),
              ("sobrancelha", "Sobrancelha", "piercing_sobrancelha.png"),
              ("labio", "Lábio", "piercing_labio.png")],
}
# Categorias que podem ficar vazias ("nenhuma") no site
OPCIONAL = {"ears": "Nenhuma", "brows": "Nenhuma", "hair": "Careca", "clothes": "Sem roupa",
            "hands": "Sem mãos juntas", "handL": "Sem mão", "handR": "Sem mão", "extras": "Nenhum",
            "glasses": "Sem óculos"}   # piercing é escolha múltipla: não tem "nenhum"   # boca, nariz, olhos e cabeça são obrigatórios

# ----------------------------------------------------------------------
# 2) CORES DE PINTURA  (cor usada no desenho -> papel no site)
#    papel "#ffffff" = cor fixa (não muda); os outros são tingidos.
#    "shade" = sombra da pele (calculada a partir da cor da pele).
# ----------------------------------------------------------------------
CORES_DE_PINTURA = {
    "head":  {"skin": (255, 203, 162), "shade": (188, 119, 76)},
    "eyes":  {"#ffffff": (255, 255, 255), "iris": (253, 20, 67)},
    "mouth": {"lip": (253, 20, 67)},
    "hair":  {"hair": (107, 117, 255)},
    "glasses": {"glass": (0, 85, 255)},          # armação azul -> cor da armação
    "pierc": {"#9f9f9f": (159, 159, 159)},       # brilho cinza do metal (fixo)
    "handL": {"skin": (255, 203, 162)},          # mãos separadas: pele (muda com a cor da pele); unhas/linhas = preto
    "handR": {"skin": (255, 203, 162)},
}
# Bocas com cores próprias (ficam FIXAS, não mudam com a cor dos lábios):
#   dentes = branco, língua = vermelho puro.  (categoria, peça) -> {papel: cor}
CORES_POR_PECA = {
    ("mouth", "dentes"): {"#ffffff": (255, 255, 255)},
    ("mouth", "lingua"): {"#ff0000": (255, 0, 0)},
    ("hands", "tocando"): {"skin": (255, 203, 162)},   # peça única "dedos se tocando": já vem pintada de pele
}
# Categorias que mantêm a imagem ORIGINAL colorida (sem separar linha/pintura, sem seletor)
COLORIDAS = {"extras"}
# Peças só de linha: o script pinta o interior sozinho com este papel
PINTURA_AUTO = {"ears": "skin", "brows": "hair"}

# Cabelos longos ganham um "cabelo de trás" (preenche o vão entre pescoço
# e mechas, e fica ATRÁS do corpo). Chave = cabelo.
CABELO_COM_FUNDO = {"repicado", "coques", "liso", "cachosfofos", "cachostrancas",
                    "trancasondas", "ondulongo", "lisofranja"}
# A partir de que linha (y, em 1080x1350) começa o cabelo de trás
FUNDO_A_PARTIR_DE_Y = 450

# Sobe (valor negativo) ou desce (positivo) uma peça, em pixels (escala 1080x1350).
# Chave = (categoria, peça).  Ex.: sobe o cabelo "Coques e cachos" 20px.
DESLOCAMENTO_Y = {("hair", "coques"): -20}

# As peças novas (cabelos, mãos, óculos, piercings) foram desenhadas centradas em x=540,
# mas o rosto/cabeça do projeto fica centrado em x=564. Estas peças são empurradas pra
# direita (em pixels, escala 1080x1350) DEPOIS de pintadas. Chave = (categoria, peça).
DX_PECAS_NOVAS = 25
DESLOCAMENTO_X = {("hair", k): DX_PECAS_NOVAS for k in
                  ("cacheadocurto", "trancasondas", "ondulongo", "ondumedio", "chiquinhas",
                   "lisofranja", "bobfranja", "sofranja", "novo1", "novo2", "novo3", "novo4", "novo5")}
DESLOCAMENTO_X.update({("hands", k): DX_PECAS_NOVAS for k in ("dedo", "rock", "lata", "pirulito")})
DESLOCAMENTO_X.update({("glasses", k): DX_PECAS_NOVAS for k in ("gatinho", "redondo")})
DESLOCAMENTO_X.update({("pierc", k): DX_PECAS_NOVAS for k in ("septo", "bochecha", "sobrancelha", "labio")})
# Roupas desenhadas centradas em x=540 (as roupas antigas e o pescoço ficam em x=562): empurra 23px
# pra direita pra alinhar. Se redesenhar uma delas já centrada em 562, apague a chave daqui.
DX_ROUPAS_NOVAS = 23
DESLOCAMENTO_X.update({("clothes", k): DX_ROUPAS_NOVAS for k in
                       ("suetergola", "jaquetacoracao", "redealcas", "casacoxadrez", "sueterverde", "topmarrom")})

# Cabelos em que os furinhos sem pintura (entre as mechas) são tapados
TAPAR_FUROS = {"liso", "cachosfofos", "cachostrancas", "trancasondas", "ondulongo", "lisofranja"}
# Furo maior que isso (px) é o rosto/abertura do cabelo, não é tapado
FURO_MAXIMO = 5000
# Cabelos com furinhos sem pintura DENTRO do cabelo (pontinhos colados no traço):
# são pintados com a cor do cabelo. Só furos menores que FURO_PEQUENO (px).
PREENCHER_FUROS_PINTURA = {"bagunca"}
FURO_PEQUENO = 600

# Peças pintadas com QUALQUER cor (o script descobre as cores sozinho):
#  - Cabelos novos: a cor única da peça vira o papel "hair" (muda com a cor do cabelo).
#  - Roupas: CADA cor diferente vira um papel próprio (k0, k1, k2...) e ganha
#    seu próprio seletor de cor no site.
CABELO_AUTO = {"coquefranja", "cachosfofos", "bagunca", "cachostrancas", "desfiado",
               "cacheadocurto", "trancasondas", "ondulongo", "ondumedio", "chiquinhas",
               "lisofranja", "bobfranja", "sofranja", "novo1", "novo2", "novo3", "novo4", "novo5"}
# Cabelos novos com uma 2ª cor (os elásticos roxos): a cor maior vira o cabelo e as
# outras ficam FIXAS (mantêm a cor do desenho). Os cabelos antigos não mudam.
CABELO_ACENTO_FIXO = {"trancasondas", "chiquinhas"}
# Mãos: objetos que não são pele (cor fixa). Os pontos (x, y) são um pixel DENTRO de cada
# parte do objeto, na mão ESQUERDA (a direita é espelhada sozinha).
OBJETOS_MAOS = {
    # cor fixa da lata (vermelho de refrigerante); os 2 últimos pontos são os "bolsinhos" entre os dedos,
    # por onde se vê a lata atrás dos dedos
    "lata": {"cor": "#e53935", "pontos": [(256, 912), (299, 1136), (304, 1192), (221, 1014), (235, 1065)]},
    # pirulito: bola rosa; o palito e a listra do meio da bola são brancos (cor fixa)
    "pirulito": {"cor": "#ff5c9d", "pontos": [(129, 873), (138, 938)],
                 "extras": [("#ffffff", [(143, 903), (163, 990)])]},
}
CATEGORIAS_MULTICOR = {"clothes"}
# Quantas cores diferentes uma roupa pode ter (o site tem seletores k0..k5)
MAX_CORES_ROUPA = 6
# Cores de roupa que ficam FIXAS (sem seletor, mantêm a cor original do desenho).
# chave da peça -> lista de cores exatas (hex) que não mudam.
# Ex.: no moletom tubarão os dentes (branco) e a boca (vermelho claro) não mudam.
# Sombras de roupa que ficam sem seletor: a cor da sombra vira a cor de base (sem sombreado).
# chave da peça -> {cor da sombra: cor de base}. Ex.: no casaco xadrez o vermelho escuro vira o vermelho.
FUNDIR_SOMBRA_ROUPA = {"casacoxadrez": {"#cb0000": "#ff0000"}}
CORES_FIXAS_ROUPA = {
    "tubarao": ["#ffffff", "#ffa1a1"],
}

# Ordem das camadas, de baixo pra cima (o site usa a mesma ordem)
ORDEM = ["hairBack", "ears", "hairMid", "head", "clothes", "hair", "extras", "handL", "handR", "hands", "eyes", "brows", "nose", "mouth", "glasses", "pierc"]

# Estado padrão usado para gerar as miniaturas
PADRAO = {"head": "oval", "eyes": "palpebra", "brows": "suave", "nose": "medio",
          "mouth": "labios", "hair": "repicado", "ears": None}
CORES_PADRAO = {"skin": (255, 203, 162), "iris": (253, 20, 67),
                "hair": (107, 117, 255), "lip": (253, 20, 67), "glass": (0, 85, 255)}
SOMBRA_PELE = (0.737, 0.586, 0.469)  # pele*isso = sombra (tirado da sua pintura)

# O que aparece junto na miniatura de cada categoria (só o necessário)
CONTEXTO_MINIATURA = {
    "head": {},
    "hair": {"head": "oval", "eyes": "palpebra"},
    "eyes": {"head": "oval"},
    "ears": {"head": "oval"},
    "brows": {"head": "oval", "eyes": "palpebra"},
    "mouth": {"head": "oval"},
    "nose": {"head": "oval"},
    "clothes": {"head": "oval"},
    "hands": {"head": "oval"},
    "glasses": {"head": "oval", "eyes": "palpebra", "brows": "suave"},
    "pierc": {"head": "oval", "eyes": "palpebra", "brows": "suave", "nose": "medio", "mouth": "labios"},
    "extras": {"head": "oval"},
    "handL": {}, "handR": {},
}

# Janela (x0,y0,x1,y1) recortada para a miniatura de cada categoria
RECORTE = {"head": (150, 60, 930, 900), "hair": (40, 0, 1040, 1300),
           "eyes": (300, 400, 830, 620), "ears": (60, 380, 1020, 680),
           "brows": (330, 290, 800, 480), "nose": (420, 520, 660, 700), "mouth": (440, 640, 640, 800),
           "clothes": (0, 700, 1080, 1560)}   # passa do fim da imagem de propósito: sobra espaço p/ a legenda
RECORTE.update({"hands": (0, 800, 1080, 1350), "glasses": (230, 330, 850, 640),
                "pierc": (320, 300, 760, 780),
                "extras": (60, 0, 1020, 420), "handL": (0, 790, 565, 1350), "handR": (565, 790, 1080, 1350)})
# Recorte próprio de cada piercing (são pecinhas pequenas: a miniatura chega mais perto)
RECORTE_PECA = {("pierc", "septo"): (400, 540, 680, 760), ("pierc", "bochecha"): (300, 470, 780, 680),
                ("pierc", "sobrancelha"): (320, 300, 760, 470), ("pierc", "labio"): (360, 640, 720, 820)}


# ----------------------------------------------------------------------
# 3) FUNÇÕES DE IMAGEM
# ----------------------------------------------------------------------
def abrir(arquivo):
    return Image.open(os.path.join(PASTA, arquivo)).convert("RGBA")


def deslocar(img, dy):
    """Move a peça na vertical (dy < 0 = sobe). O que sobra fica transparente."""
    if not dy:
        return img
    nova = Image.new("RGBA", img.size, (0, 0, 0, 0))
    nova.paste(img, (0, dy))
    return nova


def deslocar_x(m, dx, estica=False):
    """Move uma máscara (float) dx pixels pra direita. Se estica=True, a faixa que
    abre na esquerda repete a 1ª coluna (cabelo que encosta na borda continua encostando)."""
    if not dx:
        return m
    nova = np.zeros_like(m)
    nova[:, dx:] = m[:, :-dx]
    if estica:
        # só repete a borda onde o cabelo encosta nela por um trecho comprido (sem "pontinhas")
        from scipy.ndimage import binary_opening
        col = binary_opening(m[:, :3].min(1) > 0.5, structure=np.ones(160))
        nova[col, :dx] = m[col, :1]
    return nova


def separar(img, cores):
    """Separa linha e pinturas.
    Pixel de borda = pintura misturada com preto. Descobrimos "quanto de
    preto" (t) comparando com a cor da pintura -> a linha fica suave,
    sem halo escuro.  Retorna (alpha_linha, {papel: alpha_pintura})."""
    a = np.asarray(img).astype(np.float32)
    rgb, alfa = a[..., :3], a[..., 3] / 255.0
    mx = rgb.max(-1)
    papeis = list(cores.keys())
    linha = alfa.copy()                      # padrão: tudo é linha
    pint = {p: np.zeros_like(alfa) for p in papeis}
    if papeis:
        direc = rgb / np.maximum(mx, 1)[..., None]
        dist = []
        for p in papeis:
            c = np.array(cores[p], np.float32)
            dist.append(np.linalg.norm(direc - c / c.max(), axis=-1))
        dist = np.stack(dist)
        melhor = dist.argmin(0)
        eh_cor = mx >= 40                    # abaixo disso é preto = linha
        for i, p in enumerate(papeis):
            c = np.array(cores[p], np.float32)
            sel = eh_cor & (melhor == i)
            t = np.clip(1 - mx / c.max(), 0, 1)
            pint[p] = np.where(sel, alfa, 0)
            linha = np.where(sel, alfa * t, linha)
    return linha, pint


def binaria(m, lim=0.4):
    return (m > lim).astype(np.uint8)


def elipse(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def pintar_sozinho(linha, tipo):
    """Peça só de linha -> máscara do interior.
    orelha: casco convexo de cada orelha (a parte colada na cabeça fica
            escondida atrás da cabeça, então não precisa fechar certinho)
    sobrancelha: fecha as frestas do traço e preenche o miolo; se o traço
            for aberto demais, cai pro casco convexo."""
    b = binaria(linha)
    saida = np.zeros_like(b)
    # agrupa traços próximos (os 2 traços de uma mesma orelha/sobrancelha)
    junto = cv2.dilate(b, elipse(14 if tipo == "ears" else 10))
    n, rot = cv2.connectedComponents(junto)
    for k in range(1, n):
        parte = (b > 0) & (rot == k)
        if parte.sum() < 30:
            continue
        pts = cv2.findNonZero(parte.astype(np.uint8))
        miolo = np.zeros_like(b)
        if tipo == "brows":
            fechado = cv2.morphologyEx(parte.astype(np.uint8), cv2.MORPH_CLOSE, elipse(7))
            cont, _ = cv2.findContours(fechado, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(miolo, cont, -1, 1, cv2.FILLED)
            # se o miolo ficou só do tamanho do traço, usa o casco convexo
            if miolo.sum() < parte.sum() * 1.15:
                cv2.fillConvexPoly(miolo, cv2.convexHull(pts), 1)
        else:
            cv2.fillConvexPoly(miolo, cv2.convexHull(pts), 1)
        saida |= miolo
    # encolhe um pouco: a borda da tinta fica escondida embaixo da linha
    saida = cv2.erode(saida, elipse(2))
    return cv2.GaussianBlur(saida.astype(np.float32), (0, 0), 1.0)


def pintar_vazios_da_pele(linha, pint):
    """Olhos: a área entre o vinco da pálpebra e o olho é um "buraco"
    transparente (deixava o cabelo aparecer por trás). Acha todo espaço
    FECHADO por linha/pintura que ficou sem cor e pinta com a cor da pele."""
    from scipy.ndimage import binary_fill_holes
    uniao = binaria(linha, 0.3)
    for m in pint.values():
        uniao |= binaria(m, 0.3)
    uniao = cv2.morphologyEx(uniao, cv2.MORPH_CLOSE, elipse(3))
    buracos = (binary_fill_holes(uniao) & (uniao == 0)).astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(buracos)
    limpo = np.zeros_like(buracos)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] >= 150:       # ignora furinhos de antialias
            limpo[rot == k] = 1
    limpo = cv2.dilate(limpo, elipse(3))          # borda fica embaixo da linha
    return cv2.GaussianBlur(limpo.astype(np.float32), (0, 0), 0.8)


def fundo_do_cabelo(mascara):
    """Cabelo de trás: em cada linha (y >= FUNDO_A_PARTIR_DE_Y) preenche só o
    VÃO CENTRAL, da mecha esquerda mais interna até a direita mais interna.
    Fica atrás do corpo, então só aparece nos vãos entre pescoço e mechas.
    (Nunca passa da silhueta externa do cabelo, então não "enche" os
    recortes das pontas.)"""
    b = binaria(mascara, 0.5)
    # tira fiapos soltos de tinta (restos de antialias ao lado de traços finos)
    b = cv2.morphologyEx(b, cv2.MORPH_OPEN, elipse(4))
    saida = np.zeros_like(b)
    meio = W // 2
    for y in range(FUNDO_A_PARTIR_DE_Y, H):
        xs = np.flatnonzero(b[y])
        esq, dir_ = xs[xs < meio], xs[xs >= meio]
        if len(esq) and len(dir_):
            saida[y, esq.max():dir_.min() + 1] = 1
    # fecha entalhes pequenos e dá uma folguinha (a borda fica embaixo da linha)
    saida = cv2.morphologyEx(saida, cv2.MORPH_CLOSE, elipse(16))
    saida = cv2.dilate(saida, elipse(2))
    return saida.astype(np.float32)


def tapar_furos(linha, pintura, fundo):
    """Acha os espaços FECHADOS (cercados por linha/pintura) que ficaram sem
    cor, entre as mechas, e junta ao cabelo de trás (mesma cor do cabelo,
    fica atrás de tudo). A linha do desenho não muda.
    O espaço grande do rosto é ignorado (FURO_MAXIMO)."""
    from scipy.ndimage import binary_fill_holes
    coberto = ((linha > 0.3) | (pintura > 0.3) | (fundo > 0.3)).astype(np.uint8)
    furos = (binary_fill_holes(coberto) & (coberto == 0)).astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(furos)
    tapar = np.zeros_like(furos)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] <= FURO_MAXIMO:
            tapar[rot == k] = 1
    tapar = cv2.dilate(tapar, elipse(2))          # borda fica embaixo da linha
    return np.maximum(fundo, tapar.astype(np.float32)), int(tapar.sum())


def nome_da_cor(rgb):
    """Nome em português da cor ORIGINAL da peça (só pra identificar no site)."""
    import colorsys
    r, g, b = [v / 255.0 for v in rgb]
    h, sat, v = colorsys.rgb_to_hsv(r, g, b)
    if v < 0.22:
        return "preto"
    if sat < 0.14:
        return "branco" if v > 0.88 else ("cinza escuro" if v < 0.45 else "cinza")
    h *= 360
    if h < 15 or h >= 345:
        base = "vermelho"
    elif h < 40:
        base = "laranja"
    elif h < 70:
        base = "amarelo"
    elif h < 165:
        base = "verde"
    elif h < 195:
        base = "turquesa"
    elif h < 255:
        base = "azul"
    elif h < 290:
        base = "roxo"
    else:
        base = "rosa"
    if v < 0.6:
        return base + " escuro"
    if sat < 0.45 and v > 0.8:
        return base + " claro"
    return base


def separar_multi(img):
    """Separa uma peça pintada com VÁRIAS cores (roupas, cabelos novos).
    Retorna (linha, [(cor_rgb, mascara), ...]) com as cores da maior área
    pra menor.

    Como funciona:
      1. paleta = cores exatas (não pretas) com muitos pixels;
      2. pixel de borda (cor misturada com o preto da linha) recebe a cor do
         miolo mais próximo, e a parte \"preta\" dele vira linha;
      3. preto SEMITRANSPARENTE e grosso (manga transparente, gola alta,
         cabelo escuro) é uma pintura preta, não linha -> vira uma cor também;
      4. se uma cor foi pintada com opacidade ~80-95% (sem querer), vira
         100% opaca; opacidade baixa (<75%, ex.: manga transparente) é mantida."""
    from scipy.ndimage import distance_transform_edt
    a = np.asarray(img).astype(np.float32)
    rgb, alfa = a[..., :3], a[..., 3] / 255.0
    mx = rgb.max(-1)
    visivel = alfa > 0.02
    negro = (mx < 40) & visivel
    colorido = (mx >= 40) & visivel

    # 1) paleta
    sel = colorido & (alfa >= 0.5)
    px = rgb[sel].astype(np.int64)
    cod = (px[:, 0] << 16) | (px[:, 1] << 8) | px[:, 2]
    vals, cont = np.unique(cod, return_counts=True)
    paleta = []
    for k in np.argsort(-cont):
        if cont[k] < 400:
            break
        c = np.array([(vals[k] >> 16) & 255, (vals[k] >> 8) & 255, vals[k] & 255], np.float32)
        if all(np.linalg.norm(c - p) > 14 for p in paleta):
            paleta.append(c)

    # 2) rótulo de cada pixel colorido (núcleo exato + vizinho mais próximo)
    lab = np.full(alfa.shape, -1, np.int16)
    if paleta:
        dist = np.stack([np.linalg.norm(rgb - p, axis=-1) for p in paleta])
        melhor, dmin = dist.argmin(0), dist.min(0)
        nucleo = colorido & (dmin <= 14)
        lab[nucleo] = melhor[nucleo]
        resto = colorido & ~nucleo
        if resto.any() and nucleo.any():
            _, (iy, ix) = distance_transform_edt(~nucleo, return_indices=True)
            lab[resto] = lab[iy[resto], ix[resto]]

    # 3) preto semitransparente e grosso = pintura preta
    preto = None
    # só conta como pintura translucente se for MESMO translúcida (<95%);
    # traço grosso com 99% de opacidade continua sendo linha
    semi = negro & (alfa > 0.3) & (alfa < 0.95)
    if semi.sum() > 5000:
        nivel = np.bincount((alfa[semi] * 255).round().astype(int), minlength=256).argmax()
        m0 = (negro & (np.abs(alfa * 255 - nivel) <= 4)).astype(np.uint8)
        aberto = cv2.morphologyEx(m0, cv2.MORPH_OPEN, elipse(6))   # só áreas grossas
        if aberto.sum() >= 5000:
            anel = cv2.dilate(aberto, elipse(2)).astype(bool) & negro
            preto = (aberto.astype(bool), anel, nivel / 255.0)

    linha = np.zeros_like(alfa)
    linha[negro] = alfa[negro]
    fills = []
    for i, p in enumerate(paleta):
        m = lab == i
        interior = m & (np.abs(mx - p.max()) < 3)
        nivel = 1.0
        if interior.sum() > 200:
            nivel = np.bincount((alfa[interior] * 255).round().astype(int), minlength=256).argmax() / 255.0
        norm = nivel if 0.75 <= nivel < 0.985 else 1.0              # 4) opacidade
        a_eff = np.clip(alfa / norm, 0, 1)
        t = np.clip(1 - mx / p.max(), 0, 1)                         # \"quanto de preto\" no pixel
        linha = np.where(m, a_eff * t, linha)
        fills.append((tuple(int(v) for v in p), np.where(m, a_eff, 0).astype(np.float32)))
    if preto is not None:
        aberto, anel, nivel = preto
        norm = nivel if nivel >= 0.75 else 1.0
        linha = np.where(aberto, 0, linha)
        fills.append(((0, 0, 0), np.where(anel, np.clip(alfa / norm, 0, 1), 0).astype(np.float32)))
    # 5) cor "base escurecida pela camada translúcida" (ex.: o top azul visto por
    #    baixo da manga transparente, pintado como azul escuro): não é uma peça
    #    nova. Vira a cor base + a camada translúcida por cima, então a roupa
    #    fica com só 2 seletores (top e camada transparente).
    camada_por_cima = False
    if preto is not None and preto[2] < 0.75 and len(fills) > 1:
        nivel_p = preto[2]
        ip = len(fills) - 1                      # a camada preta é a última da lista
        for j in range(ip - 1, -1, -1):
            cj = np.array(fills[j][0], np.float32)
            for i in range(ip):
                if i == j or fills[i] is None:
                    continue
                ci = np.array(fills[i][0], np.float32)
                if np.abs(cj - ci * (1 - nivel_p)).max() <= 8:
                    fills[i] = (fills[i][0], np.maximum(fills[i][1], fills[j][1]))
                    fills[ip] = (fills[ip][0], np.maximum(fills[ip][1], fills[j][1] * nivel_p).astype(np.float32))
                    fills[j] = None
                    camada_por_cima = True
                    break
        fills = [f for f in fills if f is not None]
    if camada_por_cima:
        # desenha a camada translúcida por último (por cima do top)
        topo = fills[:-1]
        topo.sort(key=lambda f: -float((f[1] > 0.5).sum()))
        fills = topo + [fills[-1]]
    else:
        fills.sort(key=lambda f: -float((f[1] > 0.5).sum()))
    return linha.astype(np.float32), fills


def preencher_maos(img, chave):
    """Mãos (só linha) -> pele dentro do contorno; lata/pirulito ganham cor fixa.
    1) fecha o braço no pé da imagem (o desenho é cortado ali) e as frestinhas do traço;
    2) todo espaço FECHADO vira uma região;
    3) as regiões que contêm os pontos de OBJETOS_MAOS (e o espelho deles) são o objeto;
       as demais são a mão (cor da pele)."""
    from scipy.ndimage import binary_fill_holes
    alfa = np.asarray(img).astype(np.float32)[..., 3] / 255.0
    L = (alfa > 0.3).astype(np.uint8)
    n, rot = cv2.connectedComponents(cv2.dilate(L, elipse(15)))
    L2 = L.copy()
    for k in range(1, n):                       # cada mão: fecha o braço no pé da imagem
        xs = np.flatnonzero(((rot == k) & (L > 0)).any(0))
        if len(xs):
            L2[H - 2:, xs.min():xs.max() + 1] = 1
    C = cv2.morphologyEx(L2, cv2.MORPH_CLOSE, elipse(7))
    F = binary_fill_holes(C).astype(np.uint8)
    interior = ((F > 0) & (C == 0)).astype(np.uint8)
    n, lab = cv2.connectedComponents(interior, connectivity=4)
    obj_ids = set()
    obj = OBJETOS_MAOS.get(chave)
    extras = obj.get("extras", []) if obj else []          # [(cor, [pontos])]: partes do objeto com outra cor
    extra_ids = {cor: set() for cor, _ in extras}
    if obj:
        for (x, y) in obj["pontos"]:
            for xx in (x, W - 1 - x):           # mão esquerda e a direita (espelhada)
                if lab[y, xx] > 0:
                    obj_ids.add(int(lab[y, xx]))
        for cor, pts in extras:
            for (x, y) in pts:
                for xx in (x, W - 1 - x):
                    if lab[y, xx] > 0:
                        extra_ids[cor].add(int(lab[y, xx]))
    mao = np.zeros_like(interior)
    objm = np.zeros_like(interior)
    extm = {cor: np.zeros_like(interior) for cor, _ in extras}
    for k in range(1, n):
        alvo = mao
        if k in obj_ids:
            alvo = objm
        for cor in extra_ids:
            if k in extra_ids[cor]:
                alvo = extm[cor]
        alvo[lab == k] = 1
    # Frestinhas FINAS entre linhas (o "fechamento" de traço C as tapou, então não são região).
    # Cada fresta vira parte do que está mais PERTO dela:
    #  - fresta que contém um ponto de "extras" (palito, listra da bola) = cor daquela parte;
    #  - mais perto do objeto (lata/pirulito aparece por trás dos dedos) = cor do objeto;
    #  - senão, só os 3px colados na pele (pra não vazar cor pra fora do contorno).
    if obj and objm.any():
        fresta = ((C > 0) & (L2 == 0) & (F > 0)).astype(np.uint8)
        ng, glab = cv2.connectedComponents(fresta, connectivity=8)
        d_obj = cv2.distanceTransform((objm == 0).astype(np.uint8), cv2.DIST_L2, 3)
        d_mao = cv2.distanceTransform((mao == 0).astype(np.uint8), cv2.DIST_L2, 3)
        for g in range(1, ng):
            comp = glab == g
            feito = False
            for cor, pts in extras:
                for (x, y) in pts:
                    for xx in (x, W - 1 - x):
                        if comp[max(0, y - 6):y + 7, max(0, xx - 6):xx + 7].any():
                            extm[cor][comp] = 1
                            feito = True
                if feito:
                    break
            if feito:
                continue
            do, dm = float(d_obj[comp].min()), float(d_mao[comp].min())
            if do < dm and do <= 14:
                objm[comp] = 1
            else:
                mao[comp & (d_mao <= 3)] = 1
    # A pintura entra por baixo da linha preta vizinha (até 5px), mas só 1px por cima de falhas do
    # traço: assim não sobram frestinhas claras onde duas regiões se encontram, e a cor não "vaza"
    # pra fora do contorno nas quebras da linha (pontas dos dedos).
    linha_sob = L2 > 0

    # Cantinhos fora do contorno que o fechamento de traço (C) engoliu (ex.: junção do palito com a
    # bola) ficam sem pintura: a cor não pode aparecer do lado de fora da linha.
    quebra_fora = ((C > 0) & (L2 == 0) & (cv2.dilate((F == 0).astype(np.uint8), elipse(3)) > 0))

    def entrar(m):
        r = (cv2.dilate(m, elipse(1)) | (cv2.dilate(m, elipse(5)) & linha_sob.astype(np.uint8))) & F
        r[quebra_fora] = 0
        return r

    mao, objm = entrar(mao), entrar(objm)
    pint = {"skin": cv2.GaussianBlur(mao.astype(np.float32), (0, 0), 0.8)}
    if obj and objm.any():
        pint[obj["cor"]] = cv2.GaussianBlur(objm.astype(np.float32), (0, 0), 0.8)
    for cor, m in extm.items():
        if m.any():
            pint[cor] = cv2.GaussianBlur(entrar(m).astype(np.float32), (0, 0), 0.8)
    print(f"  mãos {chave:9s} regiões: {n - 1}  (objeto: {len(obj_ids)})")
    return alfa, pint


def preencher_furos_pequenos(linha, pintura):
    """Acha furinhos fechados (cercados por linha/pintura) SEM cor, dentro do
    cabelo, e pinta com a cor do cabelo. Só furos pequenos (FURO_PEQUENO)."""
    from scipy.ndimage import binary_fill_holes
    coberto = ((linha > 0.3) | (pintura > 0.3)).astype(np.uint8)
    furos = (binary_fill_holes(coberto) & (coberto == 0)).astype(np.uint8)
    n, rot, st, _ = cv2.connectedComponentsWithStats(furos)
    pequenos = np.zeros_like(furos)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] <= FURO_PEQUENO:
            pequenos[rot == k] = 1
    pequenos = cv2.dilate(pequenos, elipse(2))      # a borda fica embaixo da linha
    return np.maximum(pintura, pequenos.astype(np.float32)), int(pequenos.sum())


def fechar_bordas_abertas(linha, pintura):
    """Onde a pintura vai até a borda mas NÃO tem linha (corte reto, como
    o pedaço do cabelo que vaza perto do rosto), desenha uma linha fina
    pra o contorno ficar fechado."""
    f = binaria(pintura, 0.5)
    borda = f & cv2.dilate(1 - f, elipse(1))
    perto_de_linha = cv2.dilate(binaria(linha, 0.4), elipse(8))
    aberta = borda & (1 - perto_de_linha)
    n, rot, st, _ = cv2.connectedComponentsWithStats(aberta)
    limpa = np.zeros_like(aberta)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] >= 40:      # ignora pontinhos soltos
            limpa[rot == k] = 1
    nova = cv2.dilate(limpa, elipse(2)).astype(np.float32)
    nova = cv2.GaussianBlur(nova, (0, 0), 0.8)
    return np.maximum(linha, nova), int(limpa.sum())


def reduzir(m):
    """float 0..1 (1080x1350) -> PNG 'LA' pequeno (720x900), em data-URI.
    Linhas = preto com alfa; pinturas = branco com alfa (o site tinge)."""
    im = Image.fromarray((np.clip(m, 0, 1) * 255).astype(np.uint8), "L")
    im = im.resize((SW, SH), Image.LANCZOS)
    return im


def para_uri(alfa_img, preto):
    la = Image.merge("LA", (Image.new("L", alfa_img.size, 0 if preto else 255), alfa_img))
    buf = io.BytesIO()
    la.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# ----------------------------------------------------------------------
# 4) MONTA OS DADOS DE CADA PEÇA
# ----------------------------------------------------------------------
def processar():
    D = {}
    cru = {}                       # alfas em 1080x1350 (para as miniaturas)
    for cat, lista in PECAS.items():
        D[cat] = {}
        for chave, nome, arq in lista:
            img = deslocar(abrir(arq), DESLOCAMENTO_Y.get((cat, chave), 0))
            cores = CORES_POR_PECA.get((cat, chave), CORES_DE_PINTURA.get(cat, {}))
            defs = None
            if cat in COLORIDAS:
                # acessório: guarda a imagem colorida inteira, do jeito que foi desenhada
                cru[(cat, chave)] = (None, {}, {"rgba": img})
                D[cat][chave] = {"name": nome, "line": None, "fills": {}, "back": None}
                continue
            if cat in CATEGORIAS_MULTICOR:
                linha, fills = separar_multi(img)
                # sombras de roupa que NÃO viram seletor: a cor da sombra é fundida na cor de base
                # (a roupa fica sem sombra, igual em qualquer cor). chave da peça -> {sombra: base}
                for sombra, base in FUNDIR_SOMBRA_ROUPA.get(chave, {}).items():
                    cs = tuple(int(sombra[k:k + 2], 16) for k in (1, 3, 5))
                    cb = tuple(int(base[k:k + 2], 16) for k in (1, 3, 5))
                    ms = next((m for c, m in fills if c == cs), None)
                    if ms is not None:
                        fills = [(c, np.maximum(m, ms) if c == cb else m) for c, m in fills if c != cs]
                fills = fills[:MAX_CORES_ROUPA]
                fixas = [np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
                         for h in CORES_FIXAS_ROUPA.get(chave, [])]
                pint, defs, n_sel = {}, {}, 0
                for c, m in fills:
                    if any(np.linalg.norm(np.array(c, np.float32) - f) <= 14 for f in fixas):
                        pint["#%02x%02x%02x" % c] = m          # cor fixa: sem seletor
                    else:
                        pint[f"k{n_sel}"] = m
                        defs[f"k{n_sel}"] = c
                        n_sel += 1
                print(f"  {cat} {chave:12s} cores: " +
                      ", ".join(f"{nome_da_cor(c)} #%02x%02x%02x" % c for c, _ in fills) +
                      (f"  [seletores: {n_sel}; fixas: {len(fills) - n_sel}]" if fixas else "") if fills else
                      f"  {cat} {chave:12s} só linha")
            elif cat == "hair" and chave in CABELO_AUTO:
                linha, fills = separar_multi(img)
                tudo = np.zeros_like(linha)
                for _, m in fills:
                    tudo = np.maximum(tudo, m)
                pint = {"hair": tudo}
                if chave in CABELO_ACENTO_FIXO and len(fills) > 1:
                    # fills já vem da maior área p/ a menor: a 1ª é o cabelo, as outras ficam fixas
                    pint = {"hair": fills[0][1]}
                    for c, m in fills[1:]:
                        pint["#%02x%02x%02x" % c] = m
            elif cat == "hands" and chave != "tocando":
                linha, pint = preencher_maos(img, chave)
            else:
                linha, pint = separar(img, cores)
            if cat in ("hands", "handL", "handR"):
                pint, n_furo = tapar_furos_maos(linha, pint)
                if n_furo:
                    print(f"  mãos {cat}/{chave:9s} furos pintados: {n_furo}px")
            if cat in PINTURA_AUTO:
                pint = {PINTURA_AUTO[cat]: pintar_sozinho(linha, cat)}
            extra = {}
            if cat == "eyes":
                vazio = pintar_vazios_da_pele(linha, pint)
                if vazio.max() > 0.01:
                    pint = {"skin": vazio, **pint}      # pele fica por baixo
                    print(f"  olhos {chave:9s} pálpebra pintada com a pele")
            if cat == "hair":
                if chave in PREENCHER_FUROS_PINTURA:
                    pint["hair"], n_pf = preencher_furos_pequenos(linha, pint["hair"])
                    print(f"  cabelo {chave:9s} furinhos pintados: {n_pf}px")
                linha_original = linha
                linha, n_aberta = fechar_bordas_abertas(linha, pint["hair"])
                if chave in COLAR_AUTO:
                    extra["_antes"] = linha_original
                if chave in SEM_LINHA_EXTRA_NO_QUEIXO:
                    n_risco = 0
                    for ya, yb, xa, xb in SEM_LINHA_EXTRA_NO_QUEIXO[chave]:
                        n_risco += int(((linha - linha_original)[ya:yb + 1, xa:xb] > 0.1).sum())
                        linha[ya:yb + 1, xa:xb] = linha_original[ya:yb + 1, xa:xb]
                    print(f"  cabelo {chave:9s} risco do queixo (linha extra) removido: {n_risco}px")
                if chave in CABELO_COM_FUNDO:
                    extra["back"] = fundo_do_cabelo(pint["hair"])
                    if chave in TAPAR_FUROS:
                        extra["back"], n_furo = tapar_furos(linha, pint["hair"], extra["back"])
                        print(f"  cabelo {chave:9s} furos tapados: {n_furo}px")
                print(f"  cabelo {chave:9s} borda aberta fechada: {n_aberta:5d}px"
                      f"{'  + fundo' if extra else ''}")
            if defs:
                extra["defs"] = defs
            dx = DESLOCAMENTO_X.get((cat, chave), 0)
            if dx:                                   # alinha com o rosto do projeto
                linha = deslocar_x(linha, dx)
                pint = {p: deslocar_x(m, dx, True) for p, m in pint.items()}
                if extra.get("back") is not None:
                    extra["back"] = deslocar_x(extra["back"], dx, True)
            if cat == "hair" and chave in COLAR_NA_CABECA:
                ya, yb = COLAR_NA_CABECA[chave]
                cabecas = []
                for hk in D["head"]:
                    hl, hp, _ = cru[("head", hk)]
                    cabecas.append(np.maximum(hl, hp.get("skin", np.zeros_like(hl))))
                extra["mid"], linha = camada_do_meio(linha, pint["hair"], ya, yb, cabecas)
                print(f"  cabelo {chave:9s} fresta colada na cabeça (camada do meio): {int(extra['mid'].sum())}px")
            if cat == "hair" and chave in COLAR_AUTO:
                # Cada formato de rosto tem o seu contorno, então a correção é feita POR FORMATO e o site
                # escolhe a versão certa conforme o rosto escolhido (extra["porCabeca"]):
                #  - fresta fina (<= FRESTA_MAX px) entre o cabelo e o contorno desse rosto -> tapada com
                #    a cor do cabelo (camada do meio, por baixo da cabeça);
                #  - a linha extra do fechamento de bordas que ficaria colada no contorno desse rosto
                #    (o "risco" do queixo, a <= RISCO_DIST px) -> volta a linha original.
                # Num rosto mais estreito o cabelo fica mais longe, a linha extra passa a ser o contorno
                # da borda do cabelo e continua lá.
                antes = deslocar_x(extra.pop("_antes"), dx) if dx else extra.pop("_antes")
                por = {}
                relatorio = []
                for hk in D["head"]:
                    hl, hp, _ = cru[("head", hk)]
                    cab = np.maximum(hl, hp.get("skin", np.zeros_like(hl)))
                    mid_h = camada_do_meio_auto(linha, pint["hair"], [cab])
                    mid_h = cv2.GaussianBlur(np.maximum(mid_h, bolsos_de_fundo(linha, pint["hair"], cab)), (0, 0), 0.8)
                    perto = cv2.distanceTransform((cab <= 0.3).astype(np.uint8), cv2.DIST_L2, 3) <= RISCO_DIST
                    perto &= (cab <= 0.3)        # FORA do rosto: volta o traço original (até RISCO_DIST px)
                    # e na faixa de RISCO_DENTRO px DENTRO do contorno do rosto: a linha extra encostava no
                    # contorno e deixava o maxilar com traço duplo/grosso (o traço original do cabelo fica)
                    dentro_borda = cv2.distanceTransform((cab > 0.3).astype(np.uint8), cv2.DIST_L2, 3) <= RISCO_DENTRO
                    perto |= (cab > 0.3) & dentro_borda
                    perto[:RISCO_Y0, :] = False
                    perto[RISCO_Y1 + 1:, :] = False
                    n_risco = int(((linha - antes)[perto] > 0.1).sum())
                    por[hk] = (np.where(perto, antes, linha), mid_h)
                    relatorio.append(f"{hk}: risco {n_risco}px, fresta {int(mid_h.sum())}px")
                extra["porCabeca"] = por
                print(f"  cabelo {chave:9s} por formato de rosto -> " + " | ".join(relatorio))
            cru[(cat, chave)] = (linha, pint, extra)
            peca = {"name": nome, "line": linha, "fills": pint, "back": extra.get("back"), "mid": extra.get("mid")}
            D[cat][chave] = peca
    dividir_maos(D, cru)
    return D, cru


# A função fechar_bordas_abertas (mais abaixo) desenha uma linha fininha onde a pintura do cabelo
# termina sem contorno. Nestes cabelos ela desenhava um "risco" colado ao contorno do queixo, nas
# duas laterais (aparece na base da cabeça), ao lado da linha grossa da cabeça.
# Aqui a linha extra NÃO é desenhada nessa zona; o desenho original do cabelo não é alterado.
# chave do cabelo -> (y_inicial, y_final, x_inicial, x_final), em pixels 1080x1350 ANTES do deslocamento em x.
# A linha vertical do pescoço (abaixo de y_final) continua sendo desenhada.
# (o ondulado longo não tem o risco comprido: a linha extra só fazia uma pontinha no canto do queixo)
SEM_LINHA_EXTRA_NO_QUEIXO = {"trancasondas": [(680, 814, 300, 780)],
                             "lisofranja": [(680, 814, 300, 780)],
                             "ondulongo": [(796, 822, 415, 470), (796, 822, 610, 665)]}


# Cacheado curto: de um lado o cabelo não encostava na cabeça e aparecia a orelha (ou o fundo) na
# fresta. A "camada do meio" (entre a orelha e a cabeça) tampa a fresta com a cor do cabelo; como
# fica POR BAIXO da cabeça, não cobre o contorno de nenhum formato de rosto.
# chave -> (y_inicial, y_final) das linhas onde a fresta existe (coordenadas já alinhadas ao rosto)
COLAR_NA_CABECA = {"cacheadocurto": (474, 692)}


def camada_do_meio(linha, pintura, ya, yb, cabecas):
    """Devolve (mid, linha_sem_o_risco). cabecas: lista de máscaras (linha+pele) dos formatos de rosto."""
    H_, W_ = pintura.shape
    mid = np.zeros((H_, W_), np.float32)
    nova = linha.copy()
    ultimo = None
    for y in range(ya, yb + 1):
        fx = np.flatnonzero(pintura[y, W_ // 2:] > 0.5)
        if len(fx):
            ultimo = W_ // 2 + int(fx.min())
        if ultimo is None:
            continue
        xr = []
        for c in cabecas:
            hx = np.flatnonzero(c[y, W_ // 2:] > 0.5)
            if len(hx):
                xr.append(W_ // 2 + int(hx.max()))
        if not xr:
            continue
        if ultimo - min(xr) > 18:                # mais pra baixo a mecha já pende solta (sem tocar o rosto):
            break                                #   deixa como no desenho, sem corte reto
        xa = min(xr) - 8                         # entra por baixo da cabeça mais estreita
        xb = ultimo + 3
        if xb > xa:
            mid[y, xa:xb] = 1.0
            # o risquinho que fazia a borda do cabelo solto (agora a fresta está tampada); só nas
            # linhas em que o cabelo existe, pra não mexer no contorno da mecha que pende embaixo
            if len(fx) and ultimo - min(xr) > 2:
                nova[y, min(xr) + 1:ultimo + 8] = 0.0
    mid = cv2.GaussianBlur(mid, (0, 0), 0.8)
    return mid, nova


# Cabelos novos em que o cabelo não encosta direito no contorno do rosto (fresta fina por onde
# aparece o fundo/orelha): a camada do meio é calculada sozinha, nas duas laterais.
COLAR_AUTO = {"novo1", "novo2", "novo3", "novo4", "novo5"}
RISCO_DIST = 70      # (px) a linha extra só é removida a até esta distância do contorno do rosto (o rosto pontudo/quadrado deixa o contorno do rosto oval longe)
RISCO_DENTRO = 16    # (px) idem, mas pra dentro do rosto, colada no contorno do maxilar
RISCO_Y0, RISCO_Y1 = 560, 814   # e só do meio do rosto até o queixo (a linha vertical do pescoço, abaixo, fica)
FRESTA_MIN_AREA = 280   # (px) pedaços de fresta menores que isso são descartados
FRESTA_MAX = 7       # (px) até esta distância do cabelo e do rosto ao mesmo tempo = fresta; mais que isso é espaço de verdade


def camada_do_meio_auto(linha, pintura, cabecas):
    """Frestas finas (<= 2*FRESTA_MAX px) entre o cabelo e o contorno da cabeça, por onde aparece o
    fundo ou a orelha: pixels vazios que ficam perto (<= FRESTA_MAX px) do cabelo E da cabeça ao mesmo
    tempo. Vira uma camada com a cor do cabelo que fica POR BAIXO da cabeça (vale pra todo formato de
    rosto: a união das frestas de cada formato, e a cabeça cobre o que sobrar)."""
    H_, W_ = pintura.shape
    cob_cabelo = np.maximum(linha, pintura) > 0.3
    d_cabelo = cv2.distanceTransform((~cob_cabelo).astype(np.uint8), cv2.DIST_L2, 3)
    uniao = np.zeros((H_, W_), bool)
    for c in cabecas:
        cob_cab = c > 0.3
        d_cab = cv2.distanceTransform((~cob_cab).astype(np.uint8), cv2.DIST_L2, 3)
        fresta = (~cob_cabelo) & (~cob_cab) & (d_cab <= FRESTA_MAX) & (d_cabelo <= FRESTA_MAX)
        # a fresta tem cabeça de um lado e cabelo do outro NA MESMA LINHA (descarta pontinhos soltos
        # na ponta da mecha, perto do pescoço)
        k_h = np.ones((1, 2 * FRESTA_MAX + 3), np.uint8)
        fresta &= (cv2.dilate(cob_cab.astype(np.uint8), k_h) > 0) & (cv2.dilate(cob_cabelo.astype(np.uint8), k_h) > 0)
        fresta[:380, :] = False                  # só do rosto pra baixo (testa e franja ficam de fora)
        fresta[900:, :] = False
        uniao |= fresta
    mid = cv2.dilate(uniao.astype(np.uint8), elipse(3))
    # a fresta de verdade é comprida (acompanha o contorno); pedacinhos soltos (ex.: no vão entre a ponta
    # da mecha e o pescoço) apareceriam como pontinhos de cor pra fora do cabelo: descarta
    n, rot, st, _ = cv2.connectedComponentsWithStats(mid, connectivity=8)
    for k in range(1, n):
        if st[k, cv2.CC_STAT_AREA] < FRESTA_MIN_AREA:
            mid[rot == k] = 0
    return cv2.GaussianBlur(mid.astype(np.float32), (0, 0), 0.8)


def bolsos_de_fundo(linha, pintura, cab, area_max=15000):
    """Pedaços de fundo cercados por cabelo + rosto/pescoço (pontas entre o cabelo, a linha do queixo e o
    pescoço): espaço vazio que fica fechado quando se fecham frestas de até ~12px. Preenche com a cor do
    cabelo, por baixo da cabeça."""
    from scipy import ndimage as ndi
    cob = ((np.maximum(linha, pintura) > 0.3) | (cab > 0.3)).astype(np.uint8)
    fechado = cv2.morphologyEx(cob, cv2.MORPH_CLOSE, elipse(10))
    dentro = ndi.binary_fill_holes(fechado) & (cob == 0)
    dentro[:380, :] = False
    rot, n = ndi.label(dentro)
    bolsos = np.zeros(cob.shape, np.uint8)
    for k in range(1, n + 1):
        comp = rot == k
        if comp.sum() <= area_max:
            bolsos[comp] = 1
    return cv2.dilate(bolsos, elipse(3)).astype(np.float32)


def tapar_furos_maos(linha, pint, limite=6000):
    """Acha os buracos FECHADOS (cercados por linha/pintura, sem ligação com o fundo) onde não há
    nem linha nem pintura (por onde aparecia a roupa/cabelo por baixo) e pinta cada um com a cor
    da pintura vizinha (pele, lata, pirulito...). A pintura entra só por baixo da linha preta."""
    from scipy import ndimage as ndi
    cob = linha.copy()
    for m in pint.values():
        cob = np.maximum(cob, m)
    vazio = cob < 0.35
    rot, n = ndi.label(vazio)
    if n == 0:
        return pint, 0
    borda = set(np.unique(np.concatenate([rot[0], rot[-1], rot[:, 0], rot[:, -1]])))
    est8 = np.ones((3, 3), bool)
    novo = {p: m.copy() for p, m in pint.items()}
    total = 0
    for i in range(1, n + 1):
        if i in borda:
            continue
        buraco = rot == i
        area = int(buraco.sum())
        if area > limite:                       # grande demais: é espaço de verdade, não furo
            continue
        melhor, pontos = None, 0.0
        for raio in (4, 14):                    # buraco dentro de uma linha grossa: procura mais longe
            anel = ndi.binary_dilation(buraco, est8, iterations=raio) & ~buraco
            for p, m in pint.items():
                v = float(m[anel].sum())
                if v > pontos:
                    melhor, pontos = p, v
            if melhor is not None:
                break
        if melhor is None:
            continue
        area_pintar = buraco | (ndi.binary_dilation(buraco, est8, iterations=2) & (linha > 0.05))
        novo[melhor] = np.maximum(novo[melhor], area_pintar.astype(np.float32))
        total += area
    return novo, total


# Peças de mãos que vêm com as duas mãos num PNG só e são divididas em esquerda/direita.
# A linha de corte é a coluna x=565 (centro do rosto do projeto, já com o deslocamento aplicado);
# todas elas têm um vão vazio no meio, então o corte não pega em nenhum desenho.
MAOS_QUE_SE_DIVIDEM = ("dedo", "rock", "lata", "pirulito")
X_CORTE_MAOS = 565


def dividir_maos(D, cru):
    novos = {"handL": {}, "handR": {}}
    for chave in MAOS_QUE_SE_DIVIDEM:
        peca = D["hands"].pop(chave)
        linha, pint, extra = cru.pop(("hands", chave))
        for cat, esq in (("handL", True), ("handR", False)):
            def lado(m):
                m = m.copy()
                if esq:
                    m[:, X_CORTE_MAOS:] = 0
                else:
                    m[:, :X_CORTE_MAOS] = 0
                return m
            l2, p2 = lado(linha), {k: lado(m) for k, m in pint.items()}
            cru[(cat, chave)] = (l2, p2, {})
            novos[cat][chave] = {"name": peca["name"], "line": l2, "fills": p2, "back": None}
    for cat in novos:                              # as peças que já vieram da v13 ficam na frente da lista
        D[cat] = {**novos[cat], **D[cat]}


def compor(estado, cru, cores=CORES_PADRAO, fundo=None):
    """Mesma lógica de camadas do site, em Python (usada p/ miniaturas e testes)."""
    tela = np.zeros((H, W, 4), np.float32)
    if fundo is not None:
        tela[..., :3] = np.array(fundo) / 255.0
        tela[..., 3] = 1

    def pinta(m, rgb):
        nonlocal tela
        a = np.clip(m, 0, 1)[..., None]
        c = np.array(rgb, np.float32) / 255.0
        out_a = a + tela[..., 3:4] * (1 - a)
        out_rgb = (c * a + tela[..., :3] * tela[..., 3:4] * (1 - a)) / np.maximum(out_a, 1e-6)
        tela = np.concatenate([out_rgb, out_a], -1)

    def cor(papel):
        pele = np.array(cores["skin"], np.float32)
        if papel == "shade":
            return np.clip(pele * np.array(SOMBRA_PELE), 0, 255)
        if papel.startswith("#"):
            v = int(papel[1:], 16)
            return ((v >> 16) & 255, (v >> 8) & 255, v & 255)
        return cores[papel]

    for cam in ORDEM:
        if cam == "hairBack":
            ch = estado.get("hair")
            if ch and cru[("hair", ch)][2].get("back") is not None:
                pinta(cru[("hair", ch)][2]["back"], cores["hair"])
            continue
        if cam == "hairMid":
            ch = estado.get("hair")
            if ch and cru[("hair", ch)][2].get("mid") is not None:
                pinta(cru[("hair", ch)][2]["mid"], cores["hair"])
            elif ch and estado.get("head") in cru[("hair", ch)][2].get("porCabeca", {}):
                pinta(cru[("hair", ch)][2]["porCabeca"][estado["head"]][1], cores["hair"])
            continue
        ch = estado.get(cam)
        if not ch:
            continue
        linha, pint, ext = cru[(cam, ch)]
        if "porCabeca" in ext and estado.get("head") in ext["porCabeca"]:
            linha = ext["porCabeca"][estado["head"]][0]
        if "rgba" in ext:                       # acessório colorido: cola a imagem original
            arr = np.asarray(ext["rgba"]).astype(np.float32) / 255.0
            a = arr[..., 3:4]
            out_a = a + tela[..., 3:4] * (1 - a)
            tela = np.concatenate([(arr[..., :3] * a + tela[..., :3] * tela[..., 3:4] * (1 - a)) / np.maximum(out_a, 1e-6), out_a], -1)
            continue
        for papel, m in pint.items():
            pinta(m, ext["defs"][papel] if papel in ext.get("defs", {}) else cor(papel))
        pinta(linha, (0, 0, 0))
    return Image.fromarray((tela * 255).astype(np.uint8), "RGBA")


def miniatura(img, caixa, lado=160):
    rec = img.crop(caixa)
    w, h = rec.size
    s = lado * 0.92 / max(w, h)
    rec = rec.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    tela = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    tela.alpha_composite(rec, ((lado - rec.size[0]) // 2, (lado - rec.size[1]) // 2))
    buf = io.BytesIO()
    tela.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def exportar(D, cru):
    """Converte tudo pra data-URIs e devolve o JSON que o site lê."""
    saida = {}
    for cat, pecas in D.items():
        saida[cat] = {}
        if cat in OPCIONAL:
            saida[cat]["nenhuma"] = {"name": OPCIONAL[cat], "line": None, "fills": []}
        for chave, p in pecas.items():
            est = dict(CONTEXTO_MINIATURA[cat])
            est[cat] = chave
            thumb = miniatura(compor(est, cru), RECORTE_PECA.get((cat, chave), RECORTE[cat]))
            if cat in COLORIDAS:
                im = cru[(cat, chave)][2]["rgba"].convert("RGBa").resize((SW, SH), Image.LANCZOS).convert("RGBA")
                buf = io.BytesIO(); im.save(buf, "PNG", optimize=True)
                saida[cat][chave] = {"name": p["name"], "fills": [], "thumb": thumb,
                                     "line": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}
                continue
            item = {
                "name": p["name"],
                "line": para_uri(reduzir(p["line"]), True),
                "fills": [[para_uri(reduzir(m), False), papel]
                          for papel, m in p["fills"].items() if m.max() > 0.01],
                "thumb": thumb,
            }
            if p["back"] is not None:
                item["back"] = para_uri(reduzir(p["back"]), False)
            if p.get("mid") is not None:
                item["mid"] = para_uri(reduzir(p["mid"]), False)
            por = cru[(cat, chave)][2].get("porCabeca")
            if por:       # versões da linha e da camada do meio para cada formato de rosto
                item["porCabeca"] = {hk: {"line": para_uri(reduzir(l_), True), "mid": para_uri(reduzir(m_), False)}
                                     for hk, (l_, m_) in por.items()}
            defs = cru[(cat, chave)][2].get("defs")
            if defs:      # roupas: cor original de cada pintura (k0, k1...) e o nome dela
                item["fills"] = [f for f in item["fills"] if f[1] in defs or f[1][0] == "#"]
                sel = [f for f in item["fills"] if f[1] in defs]      # só as que têm seletor
                item["defs"] = ["#%02x%02x%02x" % defs[f[1]] for f in sel]
                item["cnames"] = [nome_da_cor(defs[f[1]]) for f in sel]
            saida[cat][chave] = item
    return saida


if __name__ == "__main__":
    print("Separando linha e pintura...")
    D, cru = processar()
    print("Gerando miniaturas e dados...")
    dados = exportar(D, cru)
    modelo = open(os.path.join(AQUI, "modelo.html"), encoding="utf8").read()
    html = modelo.replace("/*DADOS*/{}", json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
    # marca d'água: embute marca.png (se existir) como data URI
    import base64
    caminho_marca = os.path.join(AQUI, "marca.png")
    if os.path.exists(caminho_marca):
        b64 = base64.b64encode(open(caminho_marca, "rb").read()).decode()
        html = html.replace("/*MARCA*/", "data:image/png;base64," + b64)
    else:
        print("Aviso: marca.png não encontrado — o PNG baixado sairá sem marca d'água.")
    destino = os.path.join(AQUI, "criador.html")
    open(destino, "w", encoding="utf8").write(html)
    print(f"Pronto: {destino}  ({os.path.getsize(destino)/1024:.0f} KB)")
