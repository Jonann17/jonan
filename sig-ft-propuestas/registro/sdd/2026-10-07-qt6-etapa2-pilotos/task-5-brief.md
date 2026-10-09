### Task 5: Tela "Tradutor Técnico"

**Files:**
- Create: `sigft/app_qt/views/translator.py`
- Test: `tests/test_qt_tela_translator.py`

**Interfaces:**
- Consumes: `ModuleFrame` (`backend`, `iniciar_tarefa`, `log`, `perguntar_retry_excel`, `avisar`), `blocos`, `sigft.app_qt.file_dialogs.ask_open_files`, `sigft.core.plataforma.abrir_no_sistema`.
- Produces: `ModuloTranslator(parent=None, controller=None)` com `.btn_run`, `.btn_stop`, `.btn_glossario`, `.tradutor` (instância de `TechnicalTranslator` criada no primeiro uso).

Comportamento a preservar (de `sigft/app/views/translator.py`): título "Tradutor Técnico (PT -> ES)"; quadro com "Tradução Automática de Características" (16, negrito, `accent`), o texto de 3 linhas em cinza, botão "Selecionar Arquivos e Iniciar" (300x50, primário, 14 negrito), "PARAR AGORA" (200x40, perigo, desabilitado), "Abrir glossário (correções de termos)" (300x32, contorno); o backend nasce no primeiro clique; `processar_arquivos(files, retry_lock=self.perguntar_retry_excel)` é um gerador: "PARADO" → loga "Processo interrompido pelo usuário." e sai; "ABORTADO" → loga "Tradução não iniciada." e avisa erro com a última linha `[ERRO]` (ou "A tradução não pôde começar."); palavras de `STATUS` não vão ao log; fim → "Tradução em lote finalizada." e aviso "Sucesso"/"Processo concluído."; exceção → log "Erro Fatal: {e}"; no fim, "PARAR AGORA" volta a desabilitado e o botão principal volta.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_tela_translator.py`:
```python
from types import SimpleNamespace

import pytest

from sigft.app import backends
from sigft.app_qt.views import translator as tela_mod


class TradutorFalso:
    def __init__(self, mensagens):
        self.mensagens = mensagens
        self.parou = False

    def processar_arquivos(self, files, retry_lock=None):
        yield from self.mensagens

    def request_stop(self):
        self.parou = True

    def caminho_do_glossario(self):
        return "/tmp/glossario.csv"


@pytest.fixture
def tela(qt_interface, qtbot, monkeypatch):
    avisos = []
    monkeypatch.setattr(tela_mod.ModuloTranslator, "avisar",
                        lambda self, t, m, tipo="info": avisos.append((tipo, m)))
    t = tela_mod.ModuloTranslator()
    qtbot.addWidget(t)
    t.avisos = avisos
    return t


def _com_backend(monkeypatch, mensagens):
    falso = TradutorFalso(mensagens)
    modulo = SimpleNamespace(TechnicalTranslator=lambda: falso,
                             STATUS=frozenset({"SUCESSO", "ERRO", "PARADO", "ABORTADO", "ERRO_MOVER"}))
    monkeypatch.setattr(backends, "translator_backend", modulo)
    monkeypatch.setattr(tela_mod.file_dialogs, "ask_open_files", lambda *a, **k: ("/a.xlsx",))
    return falso


def test_monta_com_os_textos(tela):
    assert tela.label_titulo.text() == "Tradutor Técnico (PT -> ES)"
    assert tela.btn_run.text() == "Selecionar Arquivos e Iniciar"
    assert not tela.btn_stop.isEnabled()


def test_lote_completo(tela, qtbot, monkeypatch):
    _com_backend(monkeypatch, ["Traduzindo a.xlsx", "SUCESSO"])
    tela.btn_run.click()
    qtbot.waitUntil(lambda: "Tradução em lote finalizada." in tela.console.toPlainText(), timeout=3000)
    texto = tela.console.toPlainText()
    assert "Iniciando tradução de 1 arquivos..." in texto and "SUCESSO" not in texto
    qtbot.waitUntil(tela.btn_run.isEnabled, timeout=2000)
    assert not tela.btn_stop.isEnabled()
    assert tela.avisos == [("info", "Processo concluído.")]


def test_abortado_avisa_o_ultimo_erro(tela, qtbot, monkeypatch):
    _com_backend(monkeypatch, ["[ERRO] Excel não abriu", "ABORTADO"])
    tela.btn_run.click()
    qtbot.waitUntil(lambda: "Tradução não iniciada." in tela.console.toPlainText(), timeout=3000)
    assert tela.avisos == [("erro", "[ERRO] Excel não abriu")]


def test_parar(tela, monkeypatch):
    falso = _com_backend(monkeypatch, [])
    assert tela._tradutor() is falso
    tela.btn_stop.setEnabled(True)
    tela.btn_stop.click()
    assert falso.parou


def test_backend_que_nao_carregou_nao_abre_dialogo(tela, monkeypatch):
    monkeypatch.setattr(backends, "translator_backend", None)
    monkeypatch.setattr(backends, "falhas", {"translator_backend": ImportError("sem xlwings")})
    monkeypatch.setattr(tela_mod.QMessageBox, "warning", staticmethod(lambda *a: None))
    chamou = []
    monkeypatch.setattr(tela_mod.file_dialogs, "ask_open_files", lambda *a, **k: chamou.append(1))
    tela.btn_run.click()
    assert chamou == []
```

- [ ] **Step 2: Ver falhar** — `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

`sigft/app_qt/views/translator.py`:
```python
"""Tela "Tradutor Técnico (PT -> ES)" na interface Qt.

Mesma tela de `sigft/app/views/translator.py`. O que muda é só COMO ela fala
com a pessoa a partir do worker: lá eram `messagebox` e `btn.configure`
chamados de dentro da thread (proibido no Tk, fatal no macOS); aqui é
`self.avisar(...)` e `iniciar_tarefa`, que sempre passam pela thread da
interface.
"""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from sigft.app import backends, theme
from sigft.app_qt import file_dialogs, interface
from sigft.app_qt.widgets import blocos
from sigft.app_qt.widgets.module_frame import ModuleFrame
from sigft.core import plataforma


class ModuloTranslator(ModuleFrame):
    def __init__(self, parent=None, controller=None) -> None:
        self.tradutor = None  # nasce no primeiro clique, não aqui
        super().__init__(parent, controller, titulo="Tradutor Técnico (PT -> ES)")

    def _build_ui(self) -> None:
        corpo = blocos.cartao(self.content_layout)
        corpo.addWidget(blocos.rotulo("Tradução Automática de Características", tamanho=16,
                                      negrito=True, cor=theme.COLORS["accent"]))
        corpo.addWidget(blocos.rotulo(
            "Selecione as planilhas para traduzir do Português para Espanhol.\n"
            "O sistema cria uma nova aba traduzida.\n"
            "A tradução roda neste computador: nenhuma resposta sai daqui.",
            cor="#BEBEBE"))
        self.btn_run = blocos.botao("Selecionar Arquivos e Iniciar", variante="primario",
                                    largura=300, altura=50, tamanho_fonte=14, negrito=True)
        self.btn_run.clicked.connect(self.iniciar_traducao)
        self.btn_stop = blocos.botao("PARAR AGORA", variante="perigo", largura=200, altura=40)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.parar_traducao)
        self.btn_glossario = blocos.botao("Abrir glossário (correções de termos)",
                                          variante="contorno", largura=300, altura=32)
        self.btn_glossario.clicked.connect(self.abrir_glossario)
        for b in (self.btn_run, self.btn_stop, self.btn_glossario):
            corpo.addWidget(b)
        self.content_layout.addStretch()

    def _tradutor(self):
        if self.tradutor is None:
            modulo = self.backend("translator_backend")
            if modulo is None:
                return None
            self.tradutor = modulo.TechnicalTranslator()
        return self.tradutor

    def iniciar_traducao(self) -> None:
        if self._tradutor() is None:
            return
        files = file_dialogs.ask_open_files("translator.fichas", "excel",
                                            titulo="Selecione as Fichas (.xlsx)",
                                            filetypes=[("Excel", "*.xlsx")])
        if not files:
            return
        self.log(f"Iniciando tradução de {len(files)} arquivos...")
        self.btn_stop.setEnabled(True)
        self.iniciar_tarefa(self._worker, files, botao=self.btn_run)

    def parar_traducao(self) -> None:
        if self.tradutor is not None:
            self.tradutor.request_stop()
        self.log("[COMANDO] Parada solicitada...")

    def abrir_glossario(self) -> None:
        tradutor = self._tradutor()
        if tradutor is None:
            return
        try:
            caminho = tradutor.caminho_do_glossario()
            self.log(f"Abrindo o glossário: {caminho}")
            plataforma.abrir_no_sistema(caminho)
        except Exception as e:  # noqa: BLE001 -- vira aviso
            QMessageBox.critical(self, "Glossário", f"Não consegui abrir o glossário: {e}")

    def _worker(self, files) -> None:
        status = backends.exigir("translator_backend").STATUS
        ultimo_erro = ""
        try:
            for msg in self.tradutor.processar_arquivos(files, retry_lock=self.perguntar_retry_excel):
                if msg == "PARADO":
                    self.log("Processo interrompido pelo usuário.")
                    return
                if msg == "ABORTADO":
                    self.log("Tradução não iniciada.")
                    self.avisar("Tradutor", ultimo_erro or "A tradução não pôde começar.", tipo="erro")
                    return
                if msg in status:
                    continue
                if msg.startswith("[ERRO]"):
                    ultimo_erro = msg
                self.log(msg)
            self.log("Tradução em lote finalizada.")
            self.avisar("Sucesso", "Processo concluído.")
        except Exception as e:  # noqa: BLE001 -- mesmo texto da tela antiga
            self.log(f"Erro Fatal: {e}")
        finally:
            interface.na_interface(self.btn_stop.setEnabled, False)
```

- [ ] **Step 4: Ver passar (5x), suíte, commit**

```bash
for i in 1 2 3 4 5; do python -m pytest tests/test_qt_tela_translator.py -q || break; done
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt/views/translator.py tests/test_qt_tela_translator.py
git commit -m "Qt6: tela do Tradutor Tecnico"
```

---

