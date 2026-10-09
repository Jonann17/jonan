### Task 7: Tela "Automação LMR" (aba Upload)

**Files:**
- Create: `sigft/app_qt/views/lmr.py`
- Test: `tests/test_qt_tela_lmr.py`

**Interfaces:**
- Consumes: `ModuleFrame`, `pickers.FilePickerRow`, `blocos`, `dialogs.SelecaoComCaixasDialog`, `DialogosDeEspera.perguntar_sim_nao/pedir_texto/avisar/pausar_e_esperar/perguntar_retry_excel`, `sigft.app_qt.file_dialogs.ask_open_file`, `MSG_LOGIN_LMR`.
- Produces: `ModuloLMR(parent=None, controller=None, *, embutida=False, console_externo=None)` com `.btn_run`, `.picker_status`, `.caixa_linha_inicial: QCheckBox`, `.entry_linha_inicial: QLineEdit`, `.caminho_status_pmib`, `_linha_inicial_escolhida() -> int | None`, `escolher_aba(nome_arquivo, abas) -> str | None` (sobrescrevível em teste), `escolher_pmibs(pmibs) -> list[str]` (idem).

Comportamento a preservar (de `sigft/app/views/lmr.py`): título "Automação LMR"; quadro com "Preenchimento Automático de LMR (Aplicações)" (16 negrito `accent`), o texto de 4 linhas em cinza, "Marcar o resultado no _STATUS_PMIB (opcional):" (13 negrito `text_light`), seletor `chave="lmr.status_pmib"`, botão "Selecionar _STATUS_PMIB" (240), título "Selecione o _STATUS_PMIB", `filetypes=[("Excel", "*.xlsx *.xlsm")]`, vazio "Nenhum (o lote não será marcado na planilha)"; botão "Selecionar Excel e Iniciar" (300x50, primário, 14 negrito); caixa "Começar de um código específico" + campo de 70 px centrado (desabilitado e vazio enquanto a caixa está desmarcada); o texto explicativo (11, `gray70`) e "O script pedirá: ..." (12, `gray70`). Fluxo: escolher Excel (`chave="lmr.excel"`, título "Selecione o Excel LMR", `[("Excel", "*.xlsx")]`) → `listar_abas` (erro → "Não consegui ler as abas do arquivo:\n{e}"; nenhuma → "O arquivo não tem nenhuma aba.") → escolher aba (título "Escolha a aba", texto "{arquivo}\n\nQual aba contém as aplicações de LMR?") → log "Lendo {arquivo} (aba '{aba}')..." → pré-processamento numa tarefa (`carregar_dados_excel`; falha → erro "Falha ao ler Excel:\n{msg}"; sem PMIB → "Nenhum PMIB encontrado.") → seleção (título "Selecione as Fichas", "Selecione os PMIBs para processar:"; vazia → "Seleção cancelada.") → "{n} fichas selecionadas. Iniciando robô..." → worker: navegador, portal, `pausar_e_esperar(MSG_LOGIN_LMR)`, `processar_lista(selecionados, df, callback_log=self.log, callback_ask=self.perguntar_sim_nao, callback_input=self.pedir_texto, linha_inicio=...)`, "Automação LMR finalizada.", marcação do `_STATUS_PMIB` (mesmas mensagens de `_marcar_status_do_lote`), aviso "Sucesso"/"Processo concluído."; exceção → "Erro Fatal LMR: {e}"; `fechar_driver()` sempre. Linha inicial: desmarcada → `None`; vazia → `None`; não número → log "Linha inicial {texto!r} não é um número. Começando do 0." e `None`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_tela_lmr.py`:
```python
from types import SimpleNamespace

import pytest

from sigft.app import backends
from sigft.app_qt.views import lmr as tela_mod


class RoboFalso:
    def __init__(self):
        self.passos, self.callbacks = [], {}

    def carregar_dados_excel(self, caminho, aba):
        return True, "DF", ["111", "222"], f"lidas 2 fichas de {aba}"

    def iniciar_driver(self):
        self.passos.append("driver")

    def abrir_portal(self):
        self.passos.append("portal")

    def processar_lista(self, selecionados, df, *, callback_log, callback_ask, callback_input, linha_inicio):
        self.callbacks = dict(ask=callback_ask, input=callback_input, inicio=linha_inicio)
        self.passos.append(("lista", tuple(selecionados), df))
        return ["111"], []

    def fechar_driver(self):
        self.passos.append("fechou")


@pytest.fixture
def tela(qt_interface, qtbot, monkeypatch):
    robo = RoboFalso()
    marcadas = []
    modulo = SimpleNamespace(
        listar_abas=lambda caminho: ["Plan1", "LMR"],
        LMRAutomation=lambda: robo,
        marcar_status_pmib=lambda caminho, c, i, **k: marcadas.append((caminho, c, i)) or (1, "marcado"))
    monkeypatch.setattr(backends, "lmr_backend", modulo)
    monkeypatch.setattr(tela_mod.file_dialogs, "ask_open_file", lambda *a, **k: "/tmp/LMR.xlsx")
    t = tela_mod.ModuloLMR()
    qtbot.addWidget(t)
    t.robo, t.marcadas, t.avisos = robo, marcadas, []
    monkeypatch.setattr(t, "avisar", lambda ti, m, tipo="info": t.avisos.append((tipo, m)))
    monkeypatch.setattr(t, "pausar_e_esperar", lambda m, texto_botao=None: None)
    monkeypatch.setattr(t, "escolher_aba", lambda nome, abas: "LMR")
    monkeypatch.setattr(t, "escolher_pmibs", lambda pmibs: ["222"])
    return t


def test_textos_e_caixa_da_linha_inicial(tela):
    assert tela.label_titulo.text() == "Automação LMR"
    assert not tela.entry_linha_inicial.isEnabled()
    tela.caixa_linha_inicial.setChecked(True)
    assert tela.entry_linha_inicial.isEnabled()
    tela.entry_linha_inicial.setText("12")
    assert tela._linha_inicial_escolhida() == 12
    tela.caixa_linha_inicial.setChecked(False)
    assert tela.entry_linha_inicial.text() == "" and tela._linha_inicial_escolhida() is None


def test_linha_inicial_invalida_loga_e_comeca_do_zero(tela, qtbot):
    tela.caixa_linha_inicial.setChecked(True)
    tela.entry_linha_inicial.setText("abc")
    assert tela._linha_inicial_escolhida() is None
    qtbot.waitUntil(lambda: "não é um número" in tela.console.toPlainText(), timeout=2000)


def test_fluxo_completo(tela, qtbot):
    tela.caminho_status_pmib = "/tmp/STATUS.xlsx"
    tela.btn_run.click()
    qtbot.waitUntil(lambda: "fechou" in tela.robo.passos, timeout=3000)
    assert tela.robo.passos == ["driver", "portal", ("lista", ("222",), "DF"), "fechou"]
    assert tela.robo.callbacks["ask"] == tela.perguntar_sim_nao
    assert tela.robo.callbacks["input"] == tela.pedir_texto
    assert tela.marcadas == [("/tmp/STATUS.xlsx", ["111"], [])]
    texto = tela.console.toPlainText()
    assert "Lendo LMR.xlsx (aba 'LMR')..." in texto
    assert "1 fichas selecionadas. Iniciando robô..." in texto
    assert tela.avisos == [("info", "Processo concluído.")]


def test_selecao_vazia_cancela(tela, qtbot, monkeypatch):
    monkeypatch.setattr(tela, "escolher_pmibs", lambda pmibs: [])
    tela.btn_run.click()
    qtbot.waitUntil(lambda: "Seleção cancelada." in tela.console.toPlainText(), timeout=3000)
    assert tela.robo.passos == []
    qtbot.waitUntil(tela.btn_run.isEnabled, timeout=2000)


def test_arquivo_sem_abas(tela, monkeypatch):
    monkeypatch.setattr(backends.lmr_backend, "listar_abas", lambda c: [])
    erros = []
    monkeypatch.setattr(tela_mod.QMessageBox, "critical", staticmethod(lambda *a: erros.append(a[2])))
    tela.btn_run.click()
    assert erros == ["O arquivo não tem nenhuma aba."]
```

- [ ] **Step 2: Ver falhar** — `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

`sigft/app_qt/views/lmr.py`:
```python
"""Aba "Upload de Aplicações" (Automação LMR) na interface Qt.

Mesma tela de `sigft/app/views/lmr.py`. Lá, `callback_ask`/`callback_input`
chamavam `messagebox`/`simpledialog` de dentro do worker e o fim do lote
mexia no botão pela thread do robô; aqui as perguntas são `perguntar_sim_nao`
e `pedir_texto` (abrem na thread da interface) e o botão volta por
`iniciar_tarefa`.
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QInputDialog, QLineEdit, QMessageBox

from sigft.app import theme
from sigft.app.textos_dialogos import MSG_LOGIN_LMR
from sigft.app_qt import file_dialogs, interface
from sigft.app_qt.estilo import cinza_tk
from sigft.app_qt.widgets import blocos, pickers
from sigft.app_qt.widgets.dialogs import SelecaoComCaixasDialog
from sigft.app_qt.widgets.module_frame import ModuleFrame


class ModuloLMR(ModuleFrame):
    def __init__(self, parent=None, controller=None, *, embutida=False, console_externo=None) -> None:
        self.caminho_status_pmib = None
        super().__init__(parent, controller, titulo="Automação LMR",
                         embutida=embutida, console_externo=console_externo)

    def _build_ui(self) -> None:
        corpo = blocos.cartao(self.content_layout)
        corpo.addWidget(blocos.rotulo("Preenchimento Automático de LMR (Aplicações)", tamanho=16,
                                      negrito=True, cor=theme.COLORS["accent"]))
        corpo.addWidget(blocos.rotulo(
            "Este módulo lê uma aba de um arquivo Excel e cadastra as aplicações no Portal PMIB.\n"
            "Você escolhe a aba depois de selecionar o arquivo.\n"
            "Colunas esperadas: FICHA PMIB, CÓDIGO LMR e TAG LMR.\n"
            "Será solicitado login no navegador durante o processo.", cor="#BEBEBE"))
        corpo.addWidget(blocos.rotulo("Marcar o resultado no _STATUS_PMIB (opcional):",
                                      negrito=True, cor=theme.COLORS["text_light"]))
        self.picker_status = pickers.FilePickerRow(
            chave="lmr.status_pmib", categoria="excel", texto_botao="Selecionar _STATUS_PMIB",
            largura_botao=240, titulo="Selecione o _STATUS_PMIB",
            filetypes=[("Excel", "*.xlsx *.xlsm")],
            texto_vazio="Nenhum (o lote não será marcado na planilha)",
            ao_escolher=self._ao_escolher_status)
        corpo.addWidget(self.picker_status)
        self.btn_run = blocos.botao("Selecionar Excel e Iniciar", variante="primario", largura=300,
                                    altura=50, tamanho_fonte=14, negrito=True)
        self.btn_run.clicked.connect(self.iniciar_lmr)
        corpo.addWidget(self.btn_run)
        linha = QHBoxLayout()
        linha.addStretch()
        self.caixa_linha_inicial = QCheckBox("Começar de um código específico")
        self.entry_linha_inicial = QLineEdit()
        self.entry_linha_inicial.setFixedWidth(70)
        self.entry_linha_inicial.setPlaceholderText("0")
        self.entry_linha_inicial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.entry_linha_inicial.setEnabled(False)
        self.caixa_linha_inicial.toggled.connect(self._alternar_linha_inicial)
        linha.addWidget(self.caixa_linha_inicial)
        linha.addSpacing(10)
        linha.addWidget(self.entry_linha_inicial)
        linha.addStretch()
        corpo.addLayout(linha)
        corpo.addWidget(blocos.rotulo(
            "Desligado, processa a ficha inteira desde o começo.\n"
            "O número conta CÓDIGOS LMR (não linhas do Excel): o mesmo código\n"
            "espalhado pela planilha é uma aplicação só.", tamanho=11, cor=cinza_tk("gray70")))
        corpo.addWidget(blocos.rotulo(
            "O script pedirá:\n1. Arquivo Excel LMR\n2. Seleção das Fichas (Checkbox)",
            tamanho=12, cor=cinza_tk("gray70")))
        self.content_layout.addStretch()

    # -- linha inicial ---------------------------------------------------------
    def _alternar_linha_inicial(self, ligado: bool) -> None:
        self.entry_linha_inicial.setEnabled(ligado)
        if not ligado:
            self.entry_linha_inicial.clear()

    def _linha_inicial_escolhida(self):
        """`None` = "comece do começo, sem perguntar"; um número = "use este"."""
        if not self.caixa_linha_inicial.isChecked():
            return None
        texto = self.entry_linha_inicial.text().strip()
        if not texto:
            return None
        try:
            return int(texto)
        except ValueError:
            self.log(f"Linha inicial {texto!r} não é um número. Começando do 0.")
            return None

    # -- escolhas (sobrescrevíveis em teste) -----------------------------------
    def escolher_aba(self, nome_arquivo: str, abas: list[str]):
        aba, ok = QInputDialog.getItem(
            self, "Escolha a aba", f"{nome_arquivo}\n\nQual aba contém as aplicações de LMR?",
            abas, 0, False)
        return aba if ok else None

    def escolher_pmibs(self, pmibs: list[str]) -> list[str]:
        dialogo = SelecaoComCaixasDialog(self, titulo="Selecione as Fichas",
                                         mensagem="Selecione os PMIBs para processar:", itens=pmibs)
        return dialogo.selecionados() if dialogo.exec() else []

    # -- fluxo -----------------------------------------------------------------
    def _ao_escolher_status(self, caminho) -> None:
        self.caminho_status_pmib = caminho
        self.log(f"_STATUS_PMIB selecionado: {os.path.basename(caminho)}")

    def iniciar_lmr(self) -> None:
        excel_path = file_dialogs.ask_open_file("lmr.excel", "excel", titulo="Selecione o Excel LMR",
                                                filetypes=[("Excel", "*.xlsx")])
        if not excel_path:
            return
        modulo = self.backend("lmr_backend")
        if modulo is None:
            return
        try:
            abas = modulo.listar_abas(excel_path)
        except Exception as e:  # noqa: BLE001 -- vira aviso
            QMessageBox.critical(self, "Erro", f"Não consegui ler as abas do arquivo:\n{e}")
            return
        if not abas:
            QMessageBox.critical(self, "Erro", "O arquivo não tem nenhuma aba.")
            return
        aba = self.escolher_aba(os.path.basename(excel_path), abas)
        if aba is None:
            return
        self.log(f"Lendo {os.path.basename(excel_path)} (aba '{aba}')...")
        self.iniciar_tarefa(self._pre_processamento, modulo, excel_path, aba, botao=self.btn_run)

    def _pre_processamento(self, modulo, excel_path, aba) -> None:
        try:
            automator = modulo.LMRAutomation()
            ok, df_completo, pmibs_unicos, msg = automator.carregar_dados_excel(excel_path, aba)
            self.log(msg)
            if not ok:
                self.avisar("Erro", f"Falha ao ler Excel:\n{msg}", tipo="erro")
                return
            if not pmibs_unicos:
                self.log("Nenhum PMIB encontrado.")
                return
            interface.na_interface(self._selecionar_e_rodar, modulo, pmibs_unicos, df_completo)
        except Exception as e:  # noqa: BLE001 -- mesmo texto da tela antiga
            self.log(f"Erro Pré-processamento: {e}")

    def _selecionar_e_rodar(self, modulo, pmibs, df_completo) -> None:
        selecionados = self.escolher_pmibs(pmibs)
        if not selecionados:
            self.log("Seleção cancelada.")
            return
        self.log(f"{len(selecionados)} fichas selecionadas. Iniciando robô...")
        self.iniciar_tarefa(self._worker_lmr, modulo, selecionados, df_completo, botao=self.btn_run)

    def _marcar_status_do_lote(self, modulo, completas, incompletas) -> None:
        if not self.caminho_status_pmib:
            if completas or incompletas:
                self.log("[i] Nenhum _STATUS_PMIB selecionado. A planilha não foi marcada.")
            return
        self.log("Marcando o _STATUS_PMIB...")
        try:
            _marcadas, recado = modulo.marcar_status_pmib(
                self.caminho_status_pmib, completas, incompletas,
                retry_lock=self.perguntar_retry_excel, callback_log=self.log)
            self.log(recado)
        except Exception as erro:  # noqa: BLE001 -- o portal já foi feito
            self.log(f"[!] Não consegui marcar o _STATUS_PMIB: {type(erro).__name__}: {erro}")
            self.log("    O cadastro no portal FOI feito. Marque a planilha à mão.")

    def _worker_lmr(self, modulo, selecionados, df_completo) -> None:
        auto = modulo.LMRAutomation()
        try:
            self.log("Iniciando navegador...")
            auto.iniciar_driver()
            self.log("Carregando portal...")
            auto.abrir_portal()
            self.pausar_e_esperar(MSG_LOGIN_LMR)
            completas, incompletas = auto.processar_lista(
                selecionados, df_completo, callback_log=self.log,
                callback_ask=self.perguntar_sim_nao, callback_input=self.pedir_texto,
                linha_inicio=self._linha_inicial_escolhida())
            self.log("Automação LMR finalizada.")
            self._marcar_status_do_lote(modulo, completas, incompletas)
            self.avisar("Sucesso", "Processo concluído.")
        except Exception as e:  # noqa: BLE001 -- mesmo texto da tela antiga
            self.log(f"Erro Fatal LMR: {e}")
        finally:
            auto.fechar_driver()
```
`_linha_inicial_escolhida()` é lido DENTRO do worker: só lê texto e estado de caixa (sem alterar widget); o log, quando houver, passa pelo console thread-safe. Mantido assim para ficar igual à tela antiga.

- [ ] **Step 4: Ver passar (5x), suíte, commit**

```bash
for i in 1 2 3 4 5; do python -m pytest tests/test_qt_tela_lmr.py -q || break; done
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt/views/lmr.py tests/test_qt_tela_lmr.py
git commit -m "Qt6: aba de upload de aplicacoes LMR"
```

---

