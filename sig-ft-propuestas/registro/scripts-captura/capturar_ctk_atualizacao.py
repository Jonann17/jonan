"""Captura a JanelaAtualizacao do CTk nos estados pedidos: inicial, baixando, falhou, uac."""
import sys
import time

import customtkinter as ctk
from PIL import ImageGrab

from sigft.app import atualizacao
from sigft.services import updater

saida = sys.argv[1]
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
NOTAS = ("## O que mudou na v1.2.0\n\n- **Upload:** agora salva `sozinho` quando a planilha "
         "fecha no meio do lote, sem perder o que ja foi enviado\n- Tradutor local, sem Google\n"
         "- Atualizacao pequena: so o que mudou\n\n---\n\n### Como instalar\n\nBaixe")


def info(**kw):
    base = dict(versao="1.2.0", notas=NOTAS, nome_arquivo="SIG-FT_Itaipu_Setup_1.2.0.exe",
                url_asset="x", tamanho=110_201_576, sha256="ab" * 32, url_pagina="x",
                publicado_em="2026-09-25")
    base.update(kw)
    return updater.Atualizacao(**base)


raiz = ctk.CTk()
raiz.geometry("200x100+900+700")


def capturar(janela, nome):
    for _ in range(25):
        raiz.update()
        time.sleep(0.04)
    x, y = janela.winfo_rootx(), janela.winfo_rooty()
    w, h = janela.winfo_width(), janela.winfo_height()
    ImageGrab.grab(bbox=(x, y, x + w, y + h)).save(f"{saida}/ctk_{nome}.png")
    print(nome, x, y, w, h)
    for nome_w in ("rotulo_status", "botao_atualizar", "botao_agora_nao", "caixa_notas",
                   "rotulo_resumo", "barra", "rotulo_uac", "quadro_botoes"):
        w_ = getattr(janela, nome_w, None)
        if w_ is not None and w_.winfo_ismapped():
            print("  ", nome_w, w_.winfo_rootx() - x, w_.winfo_rooty() - y,
                  w_.winfo_width(), w_.winfo_height())


for estado in sys.argv[2:]:
    updater.precisa_elevacao = (lambda: True) if estado == "uac" else (lambda: False)
    j = atualizacao.JanelaAtualizacao(raiz, info=info(), versao_atual="1.1.0",
                                      disparar=lambda *a: None, fechar_app=lambda j: None)
    j.geometry("580x560+10+10")
    if estado == "baixando":
        j.atualizar()
        j.barra.set(0.5)
    elif estado == "falhou":
        j.atualizar()
        j._falhou(RuntimeError("Nenhuma rota de rede funcionou. Direta: recusada (HTTP 403)."))
    capturar(j, estado)
    j.destroy()
raiz.destroy()
