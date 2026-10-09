### Task 6: Tela "Apagar Aplicações LMR" (aba Exclusão)

**Files:**
- Create: `sigft/app_qt/views/apagar_lmr.py`
- Test: `tests/test_qt_tela_apagar_lmr.py`

**Interfaces:**
- Consumes: `ModuleFrame` (inclui `embutida`/`console_externo`), `pickers.FilePickerRow`, `blocos`, textos `MSG_LOGIN_APAGAR_LMR`, `TEXTO_COMECAR_EXCLUSAO` de `sigft.app.textos_dialogos`.
- Produces: `ModuloApagarLMR(parent=None, controller=None, *, embutida=False, console_externo=None)` com `.entry_pmib: QLineEdit`, `.picker_status`, `.btn_run`, `.caminho_status`.

Comportamento a preservar (de `sigft/app/views/apagar_lmr.py`): título "Apagar Aplicações LMR" em `danger`; "ATENÇÃO: AÇÃO DESTRUTIVA" (16, negrito, `danger`); texto do irreversível em cinza; linha "Código PMIB:" (14 negrito) + campo 250 px com placeholder "Ex: 4500063671.1234"; texto do `_STATUS_PMIB` opcional (12, `gray70`); seletor com `chave="apagar_lmr.status_pmib"`, `categoria="excel"`, botão "Selecionar _STATUS_PMIB" (220 px), título "Selecione o _STATUS_PMIB (opcional)", `filetypes=[("Excel", "*.xlsx;*.xlsm")]`, vazio "Nenhum (a planilha não será alterada)"; botão "INICIAR LIMPEZA" (350x50, perigo, 14 negrito); texto "O robô irá: ..." (12, `gray70`). Clique: PMIB vazio → aviso "Digite o código PMIB."; confirmação "Tem certeza que deseja APAGAR todas as aplicações do PMIB {pmib}?" (Sim/Não); depois "Preparando limpeza para: {pmib}..." e o worker. Worker: "Iniciando navegador...", `iniciar_driver`, "Carregando portal...", `abrir_portal`, `pausar_e_esperar(MSG_LOGIN_APAGAR_LMR, texto_botao=TEXTO_COMECAR_EXCLUSAO)`, "Iniciando varredura...", `limpou = executar_limpeza(pmib, callback_log=self.log)`, "Processo Finalizado.", limpeza do `_STATUS_PMIB` (mesmas mensagens e regras de `_limpar_status_do_lote`), aviso "Sucesso"/"Limpeza concluída."; exceção → "Erro Fatal: {e}"; `fechar_driver()` sempre.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_tela_apagar_lmr.py`:
```python
from types import SimpleNamespace

import pytest

from sigft.app import backends
from sigft.app_qt.views import apagar_lmr as tela_mod


class RoboFalso:
    def __init__(self, limpou=True):
        self.limpou, self.passos = limpou, []

    def iniciar_driver(self):
        self.passos.append("driver")

    def abrir_portal(self):
        self.passos.append("portal")

    def executar_limpeza(self, pmib, callback_log=None):
        callback_log("apagando...")
        self.passos.append(("limpeza", pmib))
        return self.limpou

    def fechar_driver(self):
        self.passos.append("fechou")


@pytest.fixture
def tela(qt_interface, qtbot, monkeypatch):
    t = tela_mod.ModuloApagarLMR()
    qtbot.addWidget(t)
    t.avisos, t.pausas = [], []
    monkeypatch.setattr(t, "avisar", lambda ti, m, tipo="info": t.avisos.append((tipo, m)))
    monkeypatch.setattr(t, "pausar_e_esperar", lambda m, texto_botao=None: t.pausas.append(texto_botao))
    monkeypatch.setattr(t, "perguntar_sim_nao", lambda ti, m: True)
    return t


def _robo(monkeypatch, limpou=True):
    robo = RoboFalso(limpou)
    limpezas = []
    modulo = SimpleNamespace(
        ApagarLMRAutomation=lambda: robo,
        limpar_status_pmib=lambda caminho, pmibs, **k: limpezas.append((caminho, pmibs)) or (1, "ok"))
    monkeypatch.setattr(backends, "apagar_lmr_backend", modulo)
    return robo, limpezas


def test_titulo_vermelho_e_textos(tela):
    from sigft.app import theme
    assert tela.label_titulo.text() == "Apagar Aplicações LMR"
    assert theme.COLORS["danger"] in tela.label_titulo.styleSheet()
    assert tela.entry_pmib.placeholderText() == "Ex: 4500063671.1234"


def test_pmib_vazio_avisa_e_nao_roda(tela, monkeypatch):
    avisos = []
    monkeypatch.setattr(tela_mod.QMessageBox, "warning", staticmethod(lambda *a: avisos.append(a[2])))
    tela.btn_run.click()
    assert avisos == ["Digite o código PMIB."]


def test_fluxo_completo_com_status(tela, qtbot, monkeypatch):
    robo, limpezas = _robo(monkeypatch, limpou=True)
    tela.caminho_status = "/tmp/STATUS.xlsx"
    tela.entry_pmib.setText(" 4500063671.1234 ")
    tela.btn_run.click()
    qtbot.waitUntil(lambda: "fechou" in robo.passos, timeout=3000)
    assert robo.passos == ["driver", "portal", ("limpeza", "4500063671.1234"), "fechou"]
    assert tela.pausas == ["COMEÇAR A EXCLUSÃO"]
    assert limpezas == [("/tmp/STATUS.xlsx", ["4500063671.1234"])]
    assert tela.avisos == [("info", "Limpeza concluída.")]
    qtbot.waitUntil(tela.btn_run.isEnabled, timeout=2000)


def test_limpeza_incompleta_nao_mexe_no_status(tela, qtbot, monkeypatch):
    robo, limpezas = _robo(monkeypatch, limpou=False)
    tela.caminho_status = "/tmp/STATUS.xlsx"
    tela.entry_pmib.setText("1")
    tela.btn_run.click()
    qtbot.waitUntil(lambda: "fechou" in robo.passos, timeout=3000)
    assert limpezas == []
    assert "NÃO foi alterado" in tela.console.toPlainText()


def test_embutida_escreve_no_console_do_pai(qt_interface, qtbot):
    from sigft.app_qt.widgets.console import ConsoleFrame
    console = ConsoleFrame()
    qtbot.addWidget(console)
    t = tela_mod.ModuloApagarLMR(embutida=True, console_externo=console)
    qtbot.addWidget(t)
    t.log("oi")
    qtbot.waitUntil(lambda: "oi" in console.toPlainText(), timeout=2000)
```

- [ ] **Step 2: Ver falhar** — `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

`sigft/app_qt/views/apagar_lmr.py`:
```python
"""Aba "Exclusão de Aplicações" (Apagar Aplicações LMR) na interface Qt.

Ação destrutiva: título em vermelho, confirmação antes de começar. Mesma tela
de `sigft/app/views/apagar_lmr.py`, com os avisos do worker passando pela
thread da interface.
"""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QMessageBox

from sigft.app import theme
from sigft.app.textos_dialogos import MSG_LOGIN_APAGAR_LMR, TEXTO_COMECAR_EXCLUSAO
from sigft.app_qt.estilo import cinza_tk
from sigft.app_qt.widgets import blocos, pickers
from sigft.app_qt.widgets.module_frame import ModuleFrame


class ModuloApagarLMR(ModuleFrame):
    def __init__(self, parent=None, controller=None, *, embutida=False, console_externo=None) -> None:
        self.caminho_status = None
        super().__init__(parent, controller, titulo="Apagar Aplicações LMR",
                         cor_titulo=theme.COLORS["danger"],
                         embutida=embutida, console_externo=console_externo)

    def _build_ui(self) -> None:
        corpo = blocos.cartao(self.content_layout)
        corpo.addWidget(blocos.rotulo("ATENÇÃO: AÇÃO DESTRUTIVA", tamanho=16, negrito=True,
                                      cor=theme.COLORS["danger"]))
        corpo.addWidget(blocos.rotulo(
            "Esta ferramenta apaga TODAS as aplicações LMR de uma ficha.\nO processo é irreversível.",
            cor="#BEBEBE"))
        linha = QHBoxLayout()
        linha.addStretch()
        linha.addWidget(blocos.rotulo("Código PMIB:", tamanho=14, negrito=True))
        self.entry_pmib = QLineEdit()
        self.entry_pmib.setFixedWidth(250)
        self.entry_pmib.setPlaceholderText("Ex: 4500063671.1234")
        linha.addWidget(self.entry_pmib)
        linha.addStretch()
        corpo.addLayout(linha)
        corpo.addWidget(blocos.rotulo(
            "Opcional: informe o _STATUS_PMIB para LIMPAR a marcação da coluna\n"
            "\"APLICAÇÃO - LMR\" das fichas que forem apagadas com sucesso.",
            tamanho=12, cor=cinza_tk("gray70")))
        self.picker_status = pickers.FilePickerRow(
            chave="apagar_lmr.status_pmib", categoria="excel",
            texto_botao="Selecionar _STATUS_PMIB", largura_botao=220,
            titulo="Selecione o _STATUS_PMIB (opcional)",
            filetypes=[("Excel", "*.xlsx;*.xlsm")],
            texto_vazio="Nenhum (a planilha não será alterada)",
            ao_escolher=self._ao_escolher_status)
        corpo.addWidget(self.picker_status)
        self.btn_run = blocos.botao("INICIAR LIMPEZA", variante="perigo", largura=350, altura=50,
                                    tamanho_fonte=14, negrito=True)
        self.btn_run.clicked.connect(self.iniciar_limpeza)
        corpo.addWidget(self.btn_run)
        corpo.addWidget(blocos.rotulo(
            "O robô irá:\n1. Abrir o navegador\n2. Solicitar login manual\n3. Acessar a ficha\n"
            "4. Clicar em todas as lixeiras até esvaziar a lista.",
            tamanho=12, cor=cinza_tk("gray70")))
        self.content_layout.addStretch()

    def _ao_escolher_status(self, caminho) -> None:
        self.caminho_status = caminho
        self.log(f"_STATUS_PMIB selecionado: {caminho}")

    def _limpar_status_do_lote(self, modulo, pmib, limpou) -> None:
        """Só limpa a coluna quando a planilha foi informada E a exclusão terminou bem."""
        if not self.caminho_status:
            return
        if not limpou:
            self.log("   [i] A exclusão não terminou limpa. O _STATUS_PMIB NÃO foi "
                     "alterado. A marcação continua como estava, o que é o certo "
                     "enquanto houver aplicação na ficha.")
            return
        try:
            _n, recado = modulo.limpar_status_pmib(
                self.caminho_status, [pmib], retry_lock=self.perguntar_retry_excel,
                callback_log=self.log)
            self.log(f"   {recado}")
        except Exception as erro:  # noqa: BLE001 -- o portal já foi feito
            self.log(f"   [!] Não consegui atualizar o _STATUS_PMIB: {erro}")

    def iniciar_limpeza(self) -> None:
        pmib = self.entry_pmib.text().strip()
        if not pmib:
            QMessageBox.warning(self, "Aviso", "Digite o código PMIB.")
            return
        if not self.perguntar_sim_nao(
                "Confirmar", f"Tem certeza que deseja APAGAR todas as aplicações do PMIB {pmib}?"):
            return
        self.log(f"Preparando limpeza para: {pmib}...")
        self.iniciar_tarefa(self._worker, pmib, botao=self.btn_run)

    def _worker(self, pmib) -> None:
        modulo = self.backend("apagar_lmr_backend")
        if modulo is None:
            return
        auto = modulo.ApagarLMRAutomation()
        try:
            self.log("Iniciando navegador...")
            auto.iniciar_driver()
            self.log("Carregando portal...")
            auto.abrir_portal()
            self.pausar_e_esperar(MSG_LOGIN_APAGAR_LMR, texto_botao=TEXTO_COMECAR_EXCLUSAO)
            self.log("Iniciando varredura...")
            limpou = auto.executar_limpeza(pmib, callback_log=self.log)
            self.log("Processo Finalizado.")
            self._limpar_status_do_lote(modulo, pmib, limpou)
            self.avisar("Sucesso", "Limpeza concluída.")
        except Exception as e:  # noqa: BLE001 -- mesmo texto da tela antiga
            self.log(f"Erro Fatal: {e}")
        finally:
            auto.fechar_driver()
```
(`self.label_titulo.styleSheet()` contém a cor porque `ModuleFrame` aplica `cor_titulo` com `setStyleSheet`.)

- [ ] **Step 4: Ver passar (5x), suíte, commit**

```bash
for i in 1 2 3 4 5; do python -m pytest tests/test_qt_tela_apagar_lmr.py -q || break; done
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt/views/apagar_lmr.py tests/test_qt_tela_apagar_lmr.py
git commit -m "Qt6: aba de exclusao de aplicacoes LMR"
```

---

