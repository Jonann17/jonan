"""Captura a JanelaAtualizacao Qt nos estados pedidos: inicial, baixando, falhou, uac."""
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from sigft.app_qt import atualizacao
from sigft.app_qt import main as qmain
from sigft.services import updater

saida = sys.argv[1]
NOTAS = ("## O que mudou na v1.2.0\n\n- **Upload:** agora salva `sozinho` quando a planilha "
         "fecha no meio do lote, sem perder o que ja foi enviado\n- Tradutor local, sem Google\n"
         "- Atualizacao pequena: so o que mudou\n\n---\n\n### Como instalar\n\nBaixe")


def info(**kw):
    base = dict(versao="1.2.0", notas=NOTAS, nome_arquivo="SIG-FT_Itaipu_Setup_1.2.0.exe",
                url_asset="x", tamanho=110_201_576, sha256="ab" * 32, url_pagina="x",
                publicado_em="2026-09-25")
    base.update(kw)
    return updater.Atualizacao(**base)


qmain._preparar_qt()
raiz = QMainWindow()
raiz.resize(200, 100)
raiz.move(900, 700)
raiz.show()

for estado in sys.argv[2:]:
    updater.precisa_elevacao = (lambda: True) if estado == "uac" else (lambda: False)
    j = atualizacao.JanelaAtualizacao(raiz, info=info(), versao_atual="1.1.0",
                                      disparar=lambda *a: None, fechar_app=lambda j: None)
    j.move(10, 10)
    j.show()
    if estado == "baixando":
        j.atualizar()
        j.barra.setValue(50)
    elif estado == "falhou":
        j.atualizar()
        j._falhou(RuntimeError("Nenhuma rota de rede funcionou. Direta: recusada (HTTP 403)."))
    for _ in range(30):
        QApplication.processEvents()
    j.grab().save(f"{saida}/qt_{estado}.png")
    print(estado, j.width(), j.height())
    for nome in ("rotulo_status", "botao_atualizar", "botao_agora_nao", "caixa_notas",
                 "rotulo_resumo", "barra", "rotulo_uac", "quadro_botoes", "rotulo_titulo"):
        w = getattr(j, nome, None)
        if w is not None and w.isVisible():
            p = w.mapTo(j, w.rect().topLeft())
            print("  ", nome, p.x(), p.y(), w.width(), w.height())
    j._baixando = False
    j.close()
