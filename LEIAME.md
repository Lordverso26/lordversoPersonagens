# Lordverso · Criador de personagens (v2)

Abra **criador.html** no navegador (arquivo único, não precisa de internet).

## O que tem na pasta
| Arquivo | Para quê |
|---|---|
| `criador.html` | O criador pronto (gerado pelo build.py) |
| `modelo.html` | O código do site (visual, abas, botões) — é aqui que você mexe no layout |
| `build.py` | Lê as peças, separa linha/pintura, pinta o que falta e gera o criador.html |
| `pecas/` | Suas peças (renomeadas), PNG 1080x1350 |

Depois de mexer em qualquer coisa: `python3 build.py` (precisa de `pip install pillow numpy scipy opencv-python-headless`).

## Como o desenho vira "peça que muda de cor"
Cada peça é separada em **linha** (o contorno preto, sempre preto) e **pinturas** (manchas de cor que o site tinge).
O script reconhece a pintura pela **cor exata** que você usou:

| Cor no seu desenho | Vira |
|---|---|
| `#ffcba2` (pele) | cor da pele |
| `#bc774c` (sombra do pescoço) | sombra da pele (calculada: pele × 0.74/0.59/0.47) |
| `#ffffff` no olho | branco do olho (fixo) |
| `#fd1443` no olho | cor dos olhos |
| `#fd1443` na boca | cor dos lábios (mantém a transparência que você usou) |
| `#6b75ff` no cabelo | cor do cabelo |

Pintou uma peça nova com essas mesmas cores? Só colocar em `pecas/`, listar em `PECAS` no build.py e rodar.

## O que o script resolveu sozinho
- **Orelhas** (só linha) → preenche o interior com a cor da pele.
- **Sobrancelhas** (só linha) → preenche com a cor do cabelo.
- **Cabelo de trás** (repicado, coques e liso longo) → tampa o vão que ficava entre o pescoço e as mechas.
- **Cortes retos na pintura do cabelo** (onde a tinta ia além do traço, perto do rosto) → desenha um traço fino fechando o contorno.
- **Ordem das camadas:** orelhas → cabeça → cabelo → olhos → sobrancelhas → boca (olhos e sobrancelhas ficam por cima da franja, senão o cabelo esconde).

## Novidades no criador
Botão de recomeçar (⟲), cores iniciais = as da sua pintura, cada aba só mostra cor se a peça tem pintura daquele tipo, salvamento automático do último personagem.

## Faltando (me manda que eu encaixo)
- **Nariz** — não veio nenhuma peça no zip (o protótipo antigo tinha 3, mas eram do outro desenho).
- **Sorriso aberto com língua** do protótipo antigo também não veio.
- Os nomes dos cabelos (Repicado, Chanel, Espetado, Coques e cachos, Liso longo, Cacheado) fui eu que dei — troque em `PECAS` no build.py.
- O cabelo "Coques e cachos" deixa um pedacinho do topo da cabeça aparecendo entre os coques; se quiser, desenhe uma peça de "topo" pra cobrir.

## Narizes
Vieram do protótipo antigo (fino, pequeno, médio): reescalei pra proporção das peças novas, posicionei entre os olhos e a boca. Estão em `pecas/nariz_*.png` — se redesenhar, é só substituir os arquivos.

## Pálpebra dos olhos
O espaço entre o vinco da pálpebra e o olho era transparente (aparecia o cabelo por trás). O build.py agora acha esses espaços fechados e pinta com a cor da pele.

## Roupas (aba "Roupa") e cabelos novos
**Cabelos novos:** Coques com franja, Cachos fofos, Bagunçado, Cachos e tranças, Desfiado. Mudam com a "Cor do cabelo".
O Cachos fofos veio em preto semitransparente: o script trata como pintura e deixa 100% opaco.

**Roupas (15 peças, `pecas/roupa_*.png`):** cada COR diferente da pintura vira um seletor próprio ("Cor 1 · azul",
"Cor 2 · vermelho"...). Partes que tinham a mesma cor mudam juntas (ex.: estrelas e lapelas vermelhas da jaqueta).
O script descobre as cores sozinho: pegue qualquer cor exata (não preta) com bastante área e ela vira um seletor.
- Ao escolher uma roupa, as cores voltam às da sua pintura original (a 1ª bolinha de cada seletor).
- **Preto semitransparente e grosso** (manga transparente, gola alta, cabelo escuro) é tratado como pintura: dá pra recolorir.
  Se a opacidade é baixa (menos de 75%, como a manga transparente) ela é mantida translúcida; se é alta (80-95%), vira opaca.
- **Adesivos em X** só tem linha preta, então não tem cor pra mudar.
- Ordem das camadas: cabelo de trás → orelhas → cabeça → **roupa** → cabelo → olhos → sobrancelhas → nariz → boca
  (o cabelo comprido fica por cima da roupa).
- Botão 🎲: sempre sorteia uma roupa (cores originais ou sorteadas); "Sem roupa" só escolhendo à mão.
- Nomes das roupas/cabelos fui eu que dei: troque em `PECAS` no build.py.

## Furinhos sem pintura (Bagunçado)
O cabelo Bagunçado tinha pontinhos sem pintura colados no traço (nos bicos da franja e no emaranhado da ponta esquerda).
O build.py agora pinta com a cor do cabelo os furos pequenos (menos de 600 px) dos cabelos listados em `PREENCHER_FUROS_PINTURA`.

## Marca d'água (Lordverso no canto inferior direito)
Todo PNG baixado sai com a logo no canto inferior direito, pequena e com opacidade baixa.
- `marca.png` = a logo com fundo transparente (versão leve, 360 px). O `build.py` embute ela dentro do criador.html.
- `marca_lordverso_grande.png` = a mesma logo em tamanho grande, só pra você guardar/usar em outros lugares.
- Pra ajustar tamanho, opacidade e margem: abra `modelo.html`, procure `MARCA_LARGURA`, `MARCA_OPACIDADE` e `MARCA_MARGEM`, mude os números e rode `python3 build.py`.
- Pra trocar a logo: substitua `marca.png` (PNG com fundo transparente) e rode `python3 build.py`.
- A marca só aparece no arquivo baixado, não na pré-visualização do criador.

## Top mangas transparentes: 2 seletores
Essa roupa tem 2 peças: o **top** (Cor 1) e a **camada transparente** por cima (Cor 2, translúcida).
O azul escuro que o desenho tinha onde as duas se sobrepõem não é uma cor nova: é o top visto por baixo da camada transparente.
O build.py reconhece isso sozinho (cor = base escurecida pela camada translúcida) e junta com o top, então a parte sobreposta
muda junto com as duas cores. Vale pra qualquer roupa futura pintada do mesmo jeito.

## Cores fixas em roupas (moletom tubarão)
No moletom tubarão só a **blusa** (Cor 1) e a **gola** (Cor 2) têm seletor. Os dentes (branco) e a boca (vermelho claro) ficam sempre com a cor original.
Pra deixar outra cor de qualquer roupa fixa: em `build.py`, adicione a peça e a cor exata em `CORES_FIXAS_ROUPA` (ex.: `"jaqueta": ["#ffba42"]`) e rode `python3 build.py`.

## Carta do personagem (para postar no story)
O botão **🃏 Montar minha carta** (embaixo do boneco) abre uma janela onde a pessoa digita o **nome do personagem** e, se quiser, o **@ do Instagram**.
A carta sai em 1080×1920 (tamanho de story): retrato, nome, @ da pessoa, logo do Lordverso e **@lordverso_oficial** no rodapé.
Embaixo há o pedido para marcar você e um link para o seu Instagram. No celular, aparece também o botão **Compartilhar**.
O botão **⬇ PNG** continua baixando só o personagem, com a marca d'água.
- Para mudar textos e cores da carta: em `modelo.html`, procure `CARTA_PERFIL`, `CARTA_TITULO`, `CARTA_CHAMADA`, `CARTA_FUNDO`, `CARTA_DESTAQUE` e rode `python3 build.py`.
- Para mudar o link do botão de seguir: procure `id="seg"` no `modelo.html`.
- A pessoa só vê o nome e o @ que ela mesma digitou; nada é enviado para servidor, tudo fica no navegador dela.

## Novidades da v13: cabelos, acessórios de rosto, roupa e mãos
**Cabelos novos (8):** Cacheado curto, Tranças onduladas, Ondulado longo, Ondulado médio, Maria-chiquinha, Liso com franja, Bob com franja e Só a franja.
Todos mudam com a "Cor do cabelo". Os **elásticos roxos** (Tranças onduladas e Maria-chiquinha) ficam sempre roxos: é a lista `CABELO_ACENTO_FIXO` no `build.py`
(tire a peça da lista e o elástico passa a seguir a cor do cabelo). A Maria-chiquinha e os cabelos curtos não têm "cabelo de trás".

**Aba Acessórios (nova):**
- **Óculos** (Gatinho e Redondo): escolhe um por vez, com seletor de **Cor da armação** (começa no azul do seu desenho). "Sem óculos" tira.
- **Piercings** (Septo, Bochecha, Sobrancelha, Lábio): botões de liga/desliga, dá para usar **vários ao mesmo tempo**. O metal é sempre cinza (o brilho `#9f9f9f` do seu desenho).
- Ordem das camadas: óculos e piercings ficam por cima de tudo no rosto (inclusive da franja).

**Roupa nova:** "Suéter caído com alças" (Cor 1 roxo = suéter, Cor 2 azul = alças da blusa por baixo). Renomeie em `PECAS` se quiser.

**Aba Mãos (nova):** Dedo pra cima, Rock, Latinha e Pirulito. Cada peça junta a mão esquerda + a direita (`pecas/maos_*.png`).
- Seu desenho das mãos era só linha: o `build.py` pinta o interior com a **cor da pele** (muda junto com a pele do personagem).
- A **latinha** (branca) e o **pirulito** (rosa) têm cor fixa. Para trocar: `OBJETOS_MAOS` no `build.py`.
- As mãos ficam por cima da roupa e do cabelo.
- Botão 🎲: sorteia mãos, óculos (às vezes sem) e piercings (cada um com 25% de chance).

**Detalhe a observar:** no Ondulado longo e no Liso com franja a pintura passa um pouquinho do traço perto do rosto (cortes retos).
O script fecha com um traço fino, mas se quiser perfeito, retoque nesses 2 PNGs e rode `python3 build.py`.

## Alinhamento das peças novas (v13.1)
As peças novas (cabelos, mãos, óculos e piercings) foram desenhadas centradas em x=540, mas o rosto do projeto é centrado em x=564.
O `build.py` agora empurra essas peças 25 px pra direita depois de pintar (`DESLOCAMENTO_X` / `DX_PECAS_NOVAS`).
Os PNGs em `pecas/` continuam originais. Se redesenhar uma peça já centrada no rosto, apague a linha dela em `DESLOCAMENTO_X`.
Se ainda sobrar um pouco de diferença, ajuste `DX_PECAS_NOVAS` (ou o valor de uma peça só) e rode `python3 build.py`.

## Novidades da v14: mãos separadas, chifres/orelhas e 2 bocas (juntado em cima da v13)
**Aba "Chifres e orelhas"** (categoria `extras`, `pecas/acessorio_*.png`): Orelhas de gato, Chifres curvos amarelos, Barbatanas verdes, Chifrinhos vermelhos, Chifres vermelhos.
Sem seletor de cor: entram com as cores originais do desenho (lista `COLORIDAS` no build.py). Ficam por cima do cabelo. A aba "Acessórios" (óculos e piercings) continua separada.

**Mãos: 3 abas.**
- **Mão esquerda** e **Mão direita**: cada lado escolhido separado, então dá pra combinar à vontade (ex.: rock de um lado e latinha do outro, ou a mesma peça nos dois). Opções: Dedo pra cima, Rock, Latinha, Pirulito (seus desenhos da v13, que o build agora **divide ao meio** em esquerda/direita) + Dedo do meio, Dedos em V e Palma aberta (`pecas/mao_e_*.png`, `pecas/mao_d_*.png`). "Esquerda/direita" = lado da TELA.
- **Mãos juntas:** só **Dedos se tocando**, que é uma peça única com as duas mãos.
- A divisão dos 4 desenhos da v13 é a lista `MAOS_QUE_SE_DIVIDEM` e a coluna de corte `X_CORTE_MAOS` no build.py (todos têm um vão vazio no meio, o corte não pega em nada). Os arquivos `pecas/maos_dedo/rock/lata/pirulito.png` continuam sendo os originais com as duas mãos.
- Escolher "Dedos se tocando" apaga as mãos separadas, e escolher uma mão separada apaga as "juntas", para não sobrepor.
- As três abas têm o seletor "Cor da pele"; as mãos seguem a pele do personagem. Latinha (branca) e pirulito (rosa) mantêm cor fixa (`OBJETOS_MAOS`).

**Bocas novas:** Dentes (branco fixo) e Língua (vermelho `#ff0000` fixo). Não mudam com a "Cor dos lábios". Para a língua seguir a cor dos lábios, tire `("mouth", "lingua")` de `CORES_POR_PECA` no build.py e pinte a língua com `#fd1443`.

No 🎲: chifres/orelhas têm 50% de chance de vir vazios; as mãos saem "juntas" (25%), separadas (cada lado pode vir vazio) ou sem mãos.
Nomes das peças novas fui eu que dei: troque em `PECAS`.

### Correção de pintura das mãos
Algumas mãos tinham buracos fechados sem pintura (na latinha, no pirulito, no dedo pra cima e no rock) e por eles aparecia a roupa/cabelo por baixo. O `build.py` agora acha esses buracos (`tapar_furos_maos`) e pinta cada um com a cor da pintura vizinha (pele, lata branca, pirulito rosa), só por baixo da linha preta, então o desenho não muda. Espaços abertos de verdade (entre os dedos, por exemplo) continuam transparentes. Se ainda sobrar algum ponto, o limite de tamanho do furo é o parâmetro `limite` da função.

### Risco no queixo (Tranças onduladas, Ondulado longo, Liso com franja)
Nesses 3 cabelos aparecia uma linha extra na base da cabeça, nas laterais do queixo. Ela **não está no desenho original**: era criada pelo próprio build, na função `fechar_bordas_abertas` (que fecha com uma linha fina onde a pintura do cabelo fica sem contorno). Agora o build não desenha essa linha extra nessas zonas (`SEM_LINHA_EXTRA_NO_QUEIXO` no build.py: cabelo -> caixas y/x onde a linha extra é ignorada). O desenho original do cabelo, as mechas e a linha vertical do pescoço não foram alterados. Para aplicar em outro cabelo, é só adicionar uma caixa nessa lista.

### Ajustes: cacheado curto, lata e fundos de bandeiras
**Cacheado curto:** de um lado o cabelo não encostava na cabeça e aparecia a orelha (ou o fundo) na fresta. O build agora cria uma "camada do meio" (`COLAR_NA_CABECA` / `camada_do_meio` no build.py; no site é a camada `hairMid`, entre a orelha e a cabeça) que tampa a fresta com a cor do cabelo. Como fica POR BAIXO da cabeça, funciona nos 3 formatos de rosto e com todas as orelhas. O risquinho de borda que sobrava ali foi removido; a mecha que pende embaixo continua como no desenho.

**Latinha:** agora tem cor fixa, vermelho `#e53935` (`OBJETOS_MAOS["lata"]["cor"]` no build.py). Revisei entre os dedos: as frestinhas finas por onde se vê a lata atrás dos dedos agora ficam com a cor da lata (antes mudavam de cor num corte seco) e sumiram as linhazinhas claras onde duas regiões se encontravam. Isso vale também pro pirulito.

**Fundos de bandeiras (aba "Fundo" → seção "Bandeiras"):** 23 bandeiras desenhadas por código (lista `FLAGS` no modelo.html: `s` = listras [cor, peso], `o` = detalhe extra), então servem no site, no PNG e na carta: Orgulho LGBT, Progresso, Filadélfia, Gay (7 listras), Lésbica, Bissexual, Pansexual, Polissexual, Onissexual, Assexual, Demissexual, Cinzassexual, Aromântica, Transgênero, Não-binário, Gênero fluido, Genderqueer, Agênero, Bigênero, Demigarota, Demigaroto, Intersexo, Poliamor. Para adicionar outra: uma linha nova em `FLAGS`. As cores de Bissexual, Pansexual, Gay, Lésbica, Trans, Assexual e arco-íris foram conferidas em mais de uma fonte; as de Polissexual, Onissexual, Genderqueer, Cinzassexual e Poliamor vêm de referências comuns, então vale uma olhada se quiser tom oficial. No 🎲 o fundo tem 25% de chance de ser uma bandeira.

### Título da carta e mão do pirulito
**Carta:** o texto pequeno no topo agora é "MEMBRO OFICIAL DO LORDVERSO" (`CARTA_TITULO` no modelo.html). O tamanho da letra diminui sozinho se o texto não couber na largura.

**Mão do pirulito (e ajustes que valem pra todas as mãos):**
- O palito e a listra do meio da bola agora são **brancos** (cor fixa). A bola continua rosa `#ff5c9d`. Em `OBJETOS_MAOS` cada objeto pode ter `extras`: partes com outra cor, marcadas por um ponto dentro delas (as frestas finas também entram, é o caso do palito e da listra).
- Vazamento de cor: a pintura entrava por cima das quebras do traço e aparecia pra fora do contorno nas pontas dos dedos e na junção do palito com a bola. Agora ela só entra por baixo da linha preta (até 5px) e quase nada por cima de falhas do traço (1px); cantinhos fora do contorno ficam sem cor. As frestas entre os dedos ficam com a cor da coisa mais próxima (pele, lata ou pirulito) em vez de sempre pele.

### 5 cabelos novos (pasta Picrew do zip de 09/11)
`pecas/cabelo_novo1..5.png` entram como cabelos automáticos (a cor única vira a "cor do cabelo"; o deslocamento em x é o mesmo das outras peças novas): **Repicado volumoso** (novo1), **Cachos curtos** (novo2), **Lateral ondulado** (novo3), **Liso com mecha** (novo4), **Repicado com franja** (novo5). Os nomes fui eu que dei, é só trocar em `PECAS["hair"]`.
Esses cabelos tinham frestas finas entre o cabelo e o contorno do rosto (aparecia o fundo). O build acha essas frestas sozinho (`COLAR_AUTO` / `camada_do_meio_auto`: espaço vazio a até `FRESTA_MAX` px do cabelo e da cabeça ao mesmo tempo) e tampa com a cor do cabelo numa camada por baixo da cabeça, então funciona nos 3 formatos de rosto. Para usar em outro cabelo, adicione a chave em `COLAR_AUTO`.

### Risco do queixo nos cabelos novos (novo1, novo3, novo4)
Eles tinham a mesma linha extra fininha colada no contorno do queixo (criada pelo fechamento de bordas do build, não é do desenho). Para os cabelos em `COLAR_AUTO` o build agora devolve a linha original nessa zona: a até `RISCO_DIST` px do contorno da cabeça, entre `RISCO_Y0` e `RISCO_Y1` (do meio do rosto até o queixo; a linha vertical do pescoço, abaixo disso, continua). A fresta que sobrava é tampada pela camada do meio. Também ajustei essa camada pra não deixar pontinhos de cor perto do pescoço: só fica fresta comprida e com cabeça de um lado e cabelo do outro (`FRESTA_MIN_AREA`).

### Vazamento nos cabelos novos (correção por formato de rosto)
O ajuste do risco/fresta dos cabelos novos tinha sido feito só pensando no rosto oval, e nos outros rostos aparecia cor do cabelo por cima da face (sem contorno) e cunhas coloridas. Agora, para cada cabelo em `COLAR_AUTO`, o build gera **uma versão da linha e da camada do meio para cada formato de rosto** (`extra["porCabeca"]`), e o site escolhe a versão certa conforme o rosto selecionado (`porCabeca` no JSON; `layers()` no modelo.html):
- a linha extra do queixo só é removida **fora** do rosto e a até `RISCO_DIST` px do contorno **daquele** rosto; por cima da face a linha do cabelo sempre fica;
- fresta fina (até `FRESTA_MAX` px) entre cabelo e contorno daquele rosto é tapada; em rosto mais estreito (pontudo) o cabelo fica mais longe e o vão aparece normal, com o contorno do cabelo.
O arquivo cresceu uns 1 MB por causa dessas versões.

### Pedaços de fundo aparecendo nos cabelos novos
Sobravam bolsinhos de fundo entre o cabelo, a linha do queixo e o pescoço. Agora, em cada versão por formato de rosto (`porCabeca`), o build acha todo espaço vazio que fica **cercado** por cabelo + rosto/pescoço (`bolsos_de_fundo`: fecha vãos de até ~20px e preenche o que ficou fechado, até `area_max` px) e pinta com a cor do cabelo na camada do meio, por baixo da cabeça.

## Novidades da v14.1: 5 roupas novas + correções de revisão
**Roupas novas (aba Roupa, `pecas/roupa_*.png`):** Jaqueta cinza com coração, Rede com top de alças, Casaco xadrez vermelho, Suéter verde de folhas e Top marrom de amarrar.
- Jaqueta cinza com coração: 3 seletores (cinza, azul da gola, rosa do coração).
- Rede com top de alças: só linha preta, sem cor pra mudar.
- Casaco xadrez vermelho: 2 seletores (vermelho e cinza do top). O vermelho escuro do desenho (sombreado do xadrez) não tem seletor: o build junta ele ao vermelho (`FUNDIR_SOMBRA_ROUPA` no build.py), então o casaco fica sem sombra em qualquer cor.
- Suéter verde de folhas: 2 seletores (verde e verde claro das folhas).
- Top marrom de amarrar: 1 seletor.
- Nomes que dei: troque em `PECAS` no build.py.

**Correções da revisão:**
- Essas 5 roupas e o **Suéter caído com alças** foram desenhados centrados em x=540, mas o pescoço e as roupas antigas ficam em x=562. O build agora empurra essas 6 roupas 23 px pra direita (`DX_ROUPAS_NOVAS` / `DESLOCAMENTO_X`). Os PNGs em `pecas/` continuam originais.
- O build usa `scipy`, que não estava na lista de instalação. Agora o comando é `pip install pillow numpy scipy opencv-python-headless`.
- **Linha estranha no maxilar (Repicado volumoso, Lateral ondulado, Liso com mecha):** a linha não era do seu desenho, era a linha fina que o build desenha para fechar a borda da pintura do cabelo. Ela era calculada para o rosto oval, então no rosto pontudo ou quadrado ficava boiando dentro do cabelo, e no oval deixava o contorno do maxilar duplo/grosso. Agora, perto do rosto, o build volta ao seu traço original: até 70 px fora do contorno (`RISCO_DIST`) e até 16 px dentro dele (`RISCO_DENTRO`). Se sobrar algum traço, aumente esses números e rode `python3 build.py`.
