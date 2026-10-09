# Paridade global Qt x CTk — negrito, texto dos botões, barra lateral (+ QLineEdit)

Commit local: `66b4cc5` — "Qt6: negrito sintetizado como no Tk, texto dos botoes #DCE4EE e barra lateral com a largura do CTk"
Branch `local/jonan-cambios`, sem push.

Arquivos: `sigft/app_qt/estilo.py`, `sigft/app_qt/main.py`, `sigft/app_qt/views/apagar_lmr.py`,
`tests/test_qt_estilo.py`, `tests/test_qt_estilo_controles.py`, `tests/test_qt_home.py`, `tests/test_qt_main.py`.
`pickers.py`, `frontend.py` e `sigft/app/` não foram tocados.

Capturas (antes/depois): `$CAP/paridade-global/{antes,depois,depois_sem_fontes_do_usuario}/`,
mais `lado_a_lado_apagar_lmr.png` e `lado_a_lado_home.png`
(`CAP=/tmp/claude-0/-home-user/111ccf73-6723-5e3b-a4c3-03916583ae47/scratchpad/capturas`).
`depois_sem_fontes_do_usuario` = Qt com HOME isolado. Neste contêiner o CustomTkinter copiou
Regular+Medium para `~/.fonts`, então o fontconfig entrega o Medium ao Qt mesmo sem registro.
No Windows o CTk registra com `AddFontResourceEx` privado ao processo, e o Qt não vê esse
Medium. Por isso o caso isolado é o que representa o Windows.

---

## 1. Negrito ~10% mais estreito

### Experimento (scripts `exp_negrito_qt.py`, `exp_negrito_tk.py`, `exp_negrito2.py`, `exp_negrito3.py` no scratchpad)

Larguras de tinta/avanço em px. Tk e Qt rodam sob Xvfb, com HOME isolado e as faces controladas.

| Texto (px) | Tk (Reg+Med, como o CTk no Linux) | Qt Reg+Med (antes) | Qt só Reg (hipótese) | Qt só Reg + hinting completo |
|---|---|---|---|---|
| Apagar Aplicações LMR (24) | 280 | 256 | 255 | 277 |
| ATENÇÃO: AÇÃO DESTRUTIVA (16) | 237 | 220 | 218 | 240 |
| Código PMIB: (14) | 94 | 86 | 85 | 96 |
| INICIAR LIMPEZA (14) | 123 | 111 | 110 | 125 |

**A hipótese "o Qt resolve o negrito para o Medium" está CERTA quanto à face**: `QFontInfo`
mostra `Roboto/Medium`. **Ela NÃO explica a largura no Linux**: só com o Regular, o negrito
sintetizado do Qt fica igualmente estreito, com acréscimo de 0,00 px por glifo. O Tk/Xft acrescenta
0,3 a 1,3 px por glifo.

Causa raiz, lida no código do Qt 6.11 (`qfontengine_ft.cpp`): o motor FreeType do Qt engrossa
(`FT_GlyphSlot_Embolden`), mas o hinting padrão no Linux usa a largura "de projeto"
(`linearHoriAdvance`), que não inclui o engrossamento. Com `PreferFullHinting` ele passa a usar o
avanço com hinting (`advance.x` depois do embolden, arredondado ao pixel), que é o modelo do Xft/GDI.

Windows (`qwindowsdirectwritefontdatabase.cpp` e `qwindowsfontenginedirectwrite.cpp`, Qt 6.11):
- o banco DirectWrite é o padrão desde o Qt 6.8. Ele registra o Medium sob o nome tipográfico
  "Roboto", peso 500. O negrito escolhe o Medium e, como 500 < DemiBold, aplica ainda
  `DWRITE_FONT_SIMULATIONS_BOLD`. Resultado: Medium + simulação, uma letra diferente da do Tk;
- o GDI do Tk lê o nome de família antigo (ID 1), que no Medium é "Roboto Medium": é outra
  família. "Roboto" negrito, para o Tk, é o Regular engrossado pelo GDI;
- a 100% de escala, o `determineHinting` do Qt já usa `PreferFullHinting` por padrão, com
  métricas `GetGdiCompatibleGlyphMetrics` e GDI_CLASSIC até 16 px. No Windows, portanto, o que
  difere do Tk é a FACE, e não o hinting.

### Correção (as duas partes)
1. `ARQUIVOS_DE_FONTE` sem o `Roboto-Medium.ttf`. O arquivo continua em `assets/fonts`, porque o
   teste de licença o exige, e nada pede peso 500 (verificado com grep: só `font-weight: bold`).
   No Windows, o negrito passa a ser Regular + simulação, o mesmo modelo do Tk.
2. `carregar_fontes()` põe `PreferFullHinting` na fonte do app. No Linux, isso corrige as
   larguras. No Windows a 100% não muda nada, porque já é o padrão. Com escala acima de 100%,
   força as métricas compatíveis com o GDI, que são as do Tk.

### Medidas no app real (apagar_lmr; ink em px; CTk = referência)

| Rótulo | CTk | Qt antes | Qt depois (HOME normal) | Qt depois (HOME isolado ≈ Windows) |
|---|---|---|---|---|
| título "Apagar Aplicações LMR" | 280 | 257 (−8%) | 278 | 276 (−1%) |
| "ATENÇÃO: AÇÃO DESTRUTIVA" | 237 | 221 (−7%) | 244 | 240 (+1%) |
| "Código PMIB:" | 92 | 84 (−9%) | 95 | 94 (+2%) |
| "INICIAR LIMPEZA" | 122 | 110 (−10%) | 124 | 123 (+1%) |

Translator: título 324 / 293 → 319; "Tradução Automática" 312 / 287 → 319; botão "Selecionar
Arquivos e Iniciar" 195 / 178 → 200 (ordem: CTk / Qt antes → Qt depois, caso isolado).

### Efeito colateral medido (preocupação)
Com hinting completo, a altura de linha do Qt fica inteira. A 12 px ela passa de 14,39 para
14 px por linha, enquanto o Tk usa 15. Rótulos multilinha de 12 px encolhem cerca de 1 px por
linha no Linux: "O robô irá…", com 5 linhas, foi de 75 para 70 px (CTk: 75), e o cartão do
Apagar LMR foi de 426 para 418 px (CTk: 428). Os testes de geometria medem espaços entre as
peças, não a altura dos rótulos, e continuam passando. A 13 px a altura de linha vai de 15,6 para
16 (Tk: 17). No Windows a 100% esse comportamento já era o padrão. A altura de linha
(ascent/descent do Tk ≠ do Qt) era uma diferença que já existia e continua aberta. Não foi
corrigida aqui.

## 2. Cor do texto dos botões

Medido nas capturas (cor mais clara do texto):

| Botão | CTk | Qt antes | Qt depois |
|---|---|---|---|
| Seletor "Selecionar _STATUS_PMIB" (sem text_color no CTk) | #DCE4EE | #E0E0E0 | #DCE4EE |
| Barra da Home "Chaves de API" (sem text_color no CTk) | #DCE4EE | **#FFFFFF** | #DCE4EE |
| Home da barra lateral (CTk escreve text_light) | #E0E0E0 | #E0E0E0 | #E0E0E0 |
| Menu lateral (CTk escreve text_light) | #E0E0E0 | #E0E0E0 | #E0E0E0 |
| Glossário (contorno_padrao; CTk escreve text_light) | #E0E0E0 | #E0E0E0 | #E0E0E0 |

- Regra global `QPushButton` → `TEXTO_BOTAO_CTK = "#DCE4EE"`. O `QComboBox` e o `QTabBar` passam
  a usar a mesma constante no lugar do literal.
- `#home` e `[menu="true"]` passam a declarar `text_light`, como o CTk fazia.
- A barra da Home perdeu o `color: text_white`, porque o CTk não define essa cor e mostra #DCE4EE
  (medido). Na Etapa 1, essa é a única mudança na Home, e o motivo é que o CTk faz diferente.
- Os overrides explícitos `cor_texto` (`blocos.botao`, botões vermelho e verde com text_white),
  `contorno` (COR_TEXTO_APOIO) e CONFIRMAR (#161616) ficaram como estavam.
- Corrigi o comentário do `contorno_padrao`: o CTk ESCREVE `text_color=text_light` no glossário.

## 3. Barra lateral

CTk (medido): canvas em 0–259, faixa da rolagem em 260–275 com o polegar cinza de 8 px em
264–271, 1 px de mistura em 276, e conteúdo a partir de x=277. No Qt o conteúdo começava em 270.

**Escolha: largura total de 277 SEM desenhar a barra cinza.** No CTk, a barra fica sempre visível
e só ocupa espaço quando tudo cabe. A margem direita do layout interno foi de 12 para 19, então
os botões mantêm os 246 px que tinham e a aparência da Etapa 1 não muda. Quando há o que rolar,
a rolagem do Qt aparece dentro dessa faixa. Depois: o conteúdo começa em x=277 na Home e nos
módulos, e o título vai de 310 para 317, como no CTk.

### Item extra necessário: largura dos botões da barra da Home
Com o negrito na largura certa e a barra 7 px mais larga, a linha da Home passou da área a
1280×850, e apareceu uma rolagem lateral sem estilo. Isso é regressão, e o teste pegou 25 px
de rolagem.

Causa: a folga do Qt era de 16 px e sem mínimo, enquanto o CTkButton usa 140 px ou texto + 7 de
cada lado (coluna de 6 = corner_radius, mais 1 do padx do Label do Tk, conferido em
`ctk_button.py`).

Regra nova: `min-width: 126px; padding: 0 7px`. Botões da barra:

| | Posições x / larguras (px) |
|---|---|
| CTk | 323/148, 481/140, 631/140, 781/140, 931/140 |
| Qt antes | 310/156, 476/140, 626/130, 766/139, 915/131 |
| Qt depois | 317/154, 481/140, 631/140, 781/140, 931/140 |

Não há mais rolagem lateral. O deslocamento de 6 px do primeiro botão vem da margem da Home
(323 contra 317) e já existia.

## 4. QLineEdit = CTkEntry (pedido extra do coordenador)

A regra global dava cerca de 34 px. Agora é: borda 2 #565B5E, fundo #343638, texto gray84, dica
gray62 (`placeholder-text-color` no QSS), fonte 13 e `padding: 0 3px 1px 3px` com min/max-height
de 23, o que soma 28 px. O CTkEntry põe o Entry do Tk com padx=6 e pady=(2, 3), e por isso a caixa
de texto tem 23 px. A folha própria do campo em `apagar_lmr.py` foi removida, junto com as
constantes `ALTURA_CAMPO`/`_BORDA_CAMPO`, que não tinham outro uso.

Medido no Apagar LMR (dica "Ex: 4500063671.1234" em relação à borda de fora):

| | x0 | y | largura da tinta |
|---|---|---|---|
| CTk | 8 | 9..17 | 121 |
| Qt antes | 9 | 10..18 | — |
| Qt depois | 8 | 9..17 | 119 |

O campo continua com 250×28, e o teste de geometria passa.

## Testes

Novos testes. Todos, menos o de guarda, falham no código antigo (conferido com `git stash` e,
no caso da Home, revertendo só a regra da barra):

- `test_qt_estilo.py::test_negrito_e_sintetizado_do_regular_como_no_tk`: sem Medium/Bold em
  `ARQUIVOS_DE_FONTE`.
- `test_qt_estilo.py::test_fonte_do_app_usa_hinting_completo_como_o_tk`
- `test_qt_estilo_controles.py::test_texto_do_botao_comum_e_o_do_tema_do_ctk`: comum e barra
  com #DCE4EE na paleta.
- `test_qt_estilo_controles.py::test_menu_home_e_glossario_mantem_o_text_light_que_o_ctk_escrevia`:
  teste de guarda, passa antes e depois.
- `test_qt_estilo_controles.py::test_campo_de_texto_e_o_ctkentry_do_tema`: QLineEdit simples sob
  a folha do app com 28 px, fonte 13 e dica/texto gray62/gray84.
- `test_qt_main.py::test_barra_lateral_tem_a_largura_total_da_do_customtkinter`: 277, conteúdo
  em x=277 e botões com 246.
- `test_qt_home.py::test_barra_com_a_largura_do_ctkbutton_e_sem_rolagem_lateral`

Os testes de medida que já existiam (`test_qt_tela_translator.py::test_medidas_iguais_as_do_customtkinter`
e `test_qt_tela_apagar_lmr.py::test_medidas_iguais_as_do_customtkinter`) passam sem mudar nenhum
número.

`bash scripts/check.sh`: **5561 passed, 25 skipped — TUDO OK**. `ruff check .`: **All checks passed!**

## Preocupações / próximos passos
1. **O efeito no Windows foi deduzido do código-fonte do Qt, não observado.** A troca de face
   (sem Medium) e o comportamento do hinting estão lidos no fonte do Qt 6.11. Não deu para
   capturar no Windows. Vale uma captura lado a lado no Windows, a 100% e a 125/150% de escala.
2. Se o Roboto (com Medium) estiver instalado no SISTEMA da máquina Windows, o Qt volta a achar
   o Medium sob "Roboto". O app não controla isso.
3. Altura de linha de rótulos multilinha no Linux: cerca de 1 px a menos por linha a 12 px
   (ver acima). É uma diferença de ascent/descent entre Tk e Qt que já existia e continua aberta.
4. No Linux, em 13–15 px, o negrito do Qt ficou de +2 a +5% mais largo que o do Tk/Xft, porque o
   Xft usa Medium + engrossamento fracionário. No caso que representa o Windows a diferença é de
   +1 a +3%.
5. Os ícones emoji da barra da Home são mais largos no Qt (Noto Emoji) que no CTk. Com o mínimo
   de 140 px isso só aparece no "Atividades do dia" (154 contra 148). É assunto da Etapa 1.
6. `assets/fonts/Roboto-Medium.ttf` ficou sem uso pelo app. Remover o arquivo (e ajustar
   `test_fontes_existem_com_licenca` e o spec de design) fica para uma decisão à parte.
