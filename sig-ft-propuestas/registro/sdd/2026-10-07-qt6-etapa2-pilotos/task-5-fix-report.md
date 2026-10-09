(Relatório do implementador da ronda de correção, commit 3a569fb)
Itens 1-7 corrigidos. check.sh: 5535 passed, 25 skipped (antes 5524); ruff limpo.
1. botao: min-height/max-height no stylesheet do próprio botão (vence o global); desconta a borda via estilo.BORDA_DA_VARIANTE (contorno=1px). Testes com a folha real: alturas 50/40/32/40/35.
2. cinza_tk("gray"/"grey") = #808080, com docstring; tela usa estilo.cinza_tk(theme.COR_TEXTO_APOIO).
3. #console: fundo gray20 #333333, sem borda, raio 6, texto gray84.
4. ModuleFrame: margens 20+PADDING_X/20+PADDING_Y, espaçamento 2*PADDING_Y. EXTRA: removeu header.setFixedHeight(ALTURA_HEADER) -- o header CTk mede 29px (winfo), não 50.
5. Cartão com spacing 0 e espaços explícitos (somas dos pady vizinhos: 10/30/20/10, margens 20, 20 acima/abaixo).
6. Nova variante "contorno_padrao" (borda #949A9F, texto text_light); "contorno" antiga mantida (usada pelo diálogo "Arquivo Bloqueado", que no CTk tem borda #555 e texto gray). Ambas com hover #14375E.
7. cartao sem alinhamento de layout; paliativo removido; teste de rótulo com quebra ocupando a largura.
Extras: texto de botão desabilitado gray60 (#999999, medido no CTk; antes gray45; menu lateral mantém gray45 por regra própria); parâmetro cor_texto em botao (run/stop com text_white); rótulos com altura mínima 28 (padrão CTkLabel); alinhar="esquerda" = esquerda + centro vertical.
Medidas 1280x850 (CTk vs Qt depois): título 317,30 vs 310,30; cartão y99 h311 vs y99 h308; botões 50/40/32 iguais; console y670 h150 igual; cores idênticas no pixel.
Diferenças restantes: barra lateral Qt 270px vs CTk 277 (etapa 1); descrição 3px mais baixa por espaçamento de linha da fonte.
