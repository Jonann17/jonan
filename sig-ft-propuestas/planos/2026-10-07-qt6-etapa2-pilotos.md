# Migração para Qt6 — Etapa 2 (seletores + telas Tradutor e Aplicação LMR) — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** as primeiras telas reais funcionam na interface Qt — **Tradutor Técnico** e a seção **Aplicação LMR** (abas Upload e Exclusão) —, com os seletores de arquivo e os diálogos que elas usam, e com a mesma aparência da interface CustomTkinter.

**Architecture:** continua o pacote paralelo `sigft/app_qt/` da Etapa 1. As telas herdam de `ModuleFrame` (Qt), rodam o robô com `iniciar_tarefa` e falam com a pessoa SÓ por métodos de `DialogosDeEspera`, que sempre abrem a janela na thread da interface. Os seletores reaproveitam a memória de pastas de `sigft/app/file_dialogs.py` (que não importa tkinter no topo), trocando só o diálogo por `QFileDialog`.

**Tech Stack:** Python ≥ 3.10, PySide6 (≥ 6.9), pytest + pytest-qt (`QT_QPA_PLATFORM=offscreen`).

**Spec:** `docs/superpowers/specs/2026-10-07-migracao-qt6-design.md`. **Etapa anterior:** `planos/2026-10-07-qt6-etapa1-base.md` e o registro `planos/2026-10-07-qt6-etapa1-registro.md` (itens "Stage 2" da triagem final entram na Task 1).

## Global Constraints

- Biblioteca de UI: **PySide6**. Nada de tkinter/customtkinter em `sigft/app_qt/` (há teste: `tests/test_qt_sem_tkinter.py`).
- Nenhum widget é tocado fora da thread da interface: de outra thread, sempre `interface.na_interface(func, *args)` ou um método de `DialogosDeEspera`.
- Mesmos textos, títulos e fluxos das telas CustomTkinter (`sigft/app/views/translator.py`, `lmr.py`, `apagar_lmr.py`, `aplicacao_lmr.py`). Sem redesenho (decisão nº 3), exceto o que a Task 2 ajusta para ficar IGUAL ao tema `dark-blue` do CustomTkinter.
- Cores: de `sigft/app/theme.py`; as do tema `dark-blue` do CustomTkinter quando a tela antiga não define cor (botão padrão `#1F538D`/hover `#14375E`, campo `#343638`/borda `#565B5E`, caixa marcada `#1F538D`, janela `gray10`).
- Botões de diálogo do Qt em **português** (tradução `qtbase_pt_BR`).
- `sigft/core/` e `sigft/services/` **não mudam**. `sigft/app/` (CustomTkinter) só muda em `sigft/app/backends.py` (Task 1, aditivo).
- Código, comentários e mensagens em **português**; mensagens de commit **sem acento**, terminando com as duas linhas de atribuição da sessão.
- Verificação de cada task: `bash scripts/check.sh` verde **e** `python -m ruff check .` limpo (o CI roda os dois).
- Testes não dependem do diretório atual (um teste antigo vaza o `cwd`): caminhos a partir de `__file__`.

## Mapa de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `sigft/app_qt/interface.py` | `instalar()` recusa rodar fora da thread do `QApplication` |
| `sigft/app_qt/widgets/console.py` | `_agendado` volta a `False` se o agendamento falhar |
| `sigft/app_qt/widgets/module_frame.py` | botão destruído não vira traceback ao fim da tarefa |
| `sigft/app/backends.py` | `exigir()` recusa nome desconhecido e nomeia o módulo Python |
| `sigft/app_qt/main.py` | tradução pt_BR; tela que falha ao montar vira tela de erro; registro das telas novas |
| `sigft/app_qt/views/nao_migrada.py` | + `TelaComErro` |
| `sigft/app_qt/estilo.py` | botão padrão, `primario`, campos, abas, listas, caixa, cartão, fundo de diálogo |
| `sigft/app_qt/views/home.py`, `widgets/dialogs.py` | botões que eram `primary` passam a `variante="primario"` |
| `sigft/app_qt/widgets/espera.py` | + `perguntar_sim_nao`, `pedir_texto`, `avisar` |
| `sigft/app_qt/widgets/dialogs.py` | + `SelecaoComCaixasDialog` |
| `sigft/app_qt/widgets/blocos.py` | `cartao`, `rotulo`, `botao` (peças repetidas das telas) |
| `sigft/app_qt/file_dialogs.py` | os 4 `ask_*` com `QFileDialog` e a memória de pastas de sempre |
| `sigft/app_qt/widgets/pickers.py` | `FilePickerRow`, `MultiFilePickerRow`, `FolderPickerRow` |
| `sigft/app_qt/views/translator.py` | `ModuloTranslator` |
| `sigft/app_qt/views/apagar_lmr.py` | `ModuloApagarLMR` |
| `sigft/app_qt/views/lmr.py` | `ModuloLMR` |
| `sigft/app_qt/views/aplicacao_lmr.py` | `ModuloAplicacaoLMR` (abas + console compartilhado) |

---

### Task 1: Robustez que as telas reais vão exigir + botões em português

**Files:**
- Modify: `sigft/app_qt/interface.py` (função `instalar`)
- Modify: `sigft/app_qt/widgets/console.py` (método `log`)
- Modify: `sigft/app_qt/widgets/module_frame.py` (método `iniciar_tarefa`)
- Modify: `sigft/app/backends.py` (funções `exigir`, `motivo_da_falha`; nova `_modulo_de`)
- Modify: `sigft/app_qt/main.py` (`_preparar_qt`, `SIG_FT_App.show_frame`)
- Modify: `sigft/app_qt/views/nao_migrada.py` (+ `TelaComErro`)
- Test: `tests/test_qt_robustez.py`

**Interfaces:**
- Produces: `interface.instalar()` levanta `RuntimeError` se chamado fora da thread do `QApplication` (ou sem `QApplication`) e a ponte ainda não existe; `backends.exigir(nome)` levanta `KeyError` para nome que não é destino de `MODULOS` nem classe registrada; mensagem de `BackendIndisponivel` inclui `(módulo <nome_modulo>)`; `main._instalar_traducao(app) -> bool`; `TelaComErro(nome: str, erro: BaseException, parent=None)` com atributo `mensagem: QLabel`; `SIG_FT_App.show_frame` não guarda em cache a tela que falhou.

- [ ] **Step 1: Testes que falham**

`tests/test_qt_robustez.py`:
```python
import threading

import pytest
from PySide6.QtWidgets import QPushButton

from sigft.app import backends
from sigft.app_qt import interface


def test_instalar_fora_da_thread_da_interface_recusa(qt_interface, monkeypatch):
    monkeypatch.setattr(interface, "_ponte", None)
    erros = []

    def tentar():
        try:
            interface.instalar()
        except RuntimeError as erro:
            erros.append(str(erro))

    t = threading.Thread(target=tentar, daemon=True)
    t.start()
    t.join(3)
    assert erros and "thread da interface" in erros[0]


def test_console_volta_a_agendar_depois_de_falha(qt_interface, qtbot, monkeypatch):
    from sigft.app_qt.widgets.console import ConsoleFrame
    c = ConsoleFrame()
    qtbot.addWidget(c)
    original = interface.na_interface

    def falha_uma_vez(*a, **k):
        monkeypatch.setattr(interface, "na_interface", original)
        raise RuntimeError("canal fechado")

    monkeypatch.setattr(interface, "na_interface", falha_uma_vez)
    c.log("perdida")
    c.log("chega")
    qtbot.waitUntil(lambda: "chega" in c.toPlainText(), timeout=2000)


def test_botao_destruido_no_fim_da_tarefa_nao_vira_traceback(qt_interface, qtbot, capsys):
    from sigft.app_qt.widgets.module_frame import ModuleFrame

    class Tela(ModuleFrame):
        def _build_ui(self):
            pass

    tela = Tela(titulo="x")
    qtbot.addWidget(tela)
    botao = QPushButton("Rodar")
    liberar = threading.Event()
    thread = tela.iniciar_tarefa(liberar.wait, 5, botao=botao)
    botao.deleteLater()
    qtbot.wait(50)
    liberar.set()
    thread.join(3)
    qtbot.wait(100)
    assert "Traceback" not in capsys.readouterr().err


def test_exigir_nome_desconhecido_e_erro_de_programacao():
    with pytest.raises(KeyError, match="pdm_backnd"):
        backends.exigir("pdm_backnd")


def test_mensagem_nomeia_o_modulo(monkeypatch):
    monkeypatch.setattr(backends, "falhas", {"lmr_backend": TypeError("x")})
    monkeypatch.setattr(backends, "lmr_backend", None)
    with pytest.raises(backends.BackendIndisponivel, match=r"\(módulo lmr_backend\)"):
        backends.exigir("lmr_backend")


def test_traducao_pt_br_instalada(qt_interface):
    from PySide6.QtWidgets import QApplication

    from sigft.app_qt import main as qmain
    assert qmain._instalar_traducao(QApplication.instance()) is True
    assert QApplication.translate("QPlatformTheme", "Cancel") == "Cancelar"


def test_tela_que_falha_ao_montar_vira_tela_de_erro(qt_interface, qtbot, tmp_path, monkeypatch):
    from sigft.app_qt import main as qmain
    from sigft.app_qt.views.nao_migrada import TelaComErro
    monkeypatch.setattr(qmain, "_arquivo_de_chaves", lambda: str(tmp_path / "api_config.json"))

    def quebra(parent, controller):
        raise ValueError("faltou coluna")

    monkeypatch.setitem(qmain.TELAS, "Analyzer", quebra)
    janela = qmain.SIG_FT_App()
    qtbot.addWidget(janela)
    janela.show_frame("Analyzer")
    assert isinstance(janela.pilha.currentWidget(), TelaComErro)
    assert "faltou coluna" in janela.pilha.currentWidget().mensagem.text()
    assert "Analyzer" not in janela.telas  # a próxima visita tenta de novo
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_robustez.py -q`
Expected: 7 failed (sem guarda, sem `_instalar_traducao`, sem `TelaComErro`...).

- [ ] **Step 3: Implementar**

`sigft/app_qt/interface.py`, em `instalar()`, antes de criar a ponte:
```python
def instalar() -> None:
    """Cria a ponte na thread atual (a da interface). Chamar uma vez, cedo,
    DEPOIS do `QApplication` existir: a ponte vive na thread em que nasce, e
    é para lá que o Qt entrega as chamadas."""
    global _ponte, _thread_da_interface
    if _ponte is not None:
        return
    from PySide6.QtCore import QCoreApplication, QThread

    app = QCoreApplication.instance()
    if app is None or QThread.currentThread() is not app.thread():
        raise RuntimeError(
            "interface.instalar() precisa rodar na thread da interface, "
            "depois do QApplication existir.")
    _ponte = _Ponte()
    _thread_da_interface = threading.get_ident()
```

`sigft/app_qt/widgets/console.py`, em `log`, trocar o `except RuntimeError: pass` por:
```python
        except RuntimeError:
            # Canal fechado (app fechando) ou ainda não instalado: a linha fica
            # na fila e a PRÓXIMA chamada tenta agendar de novo -- sem isto o
            # `_agendado` ficaria preso em True e o console, mudo para sempre.
            with self._trava:
                self._agendado = False
```

`sigft/app_qt/widgets/module_frame.py`, em `iniciar_tarefa`, trocar `interface.na_interface(botao.setEnabled, True)` por `interface.na_interface(_reabilitar, botao)` e acrescentar no módulo:
```python
def _reabilitar(botao) -> None:
    """Devolve o botão. A tela pode ter sido fechada antes de a tarefa acabar."""
    try:
        botao.setEnabled(True)
    except RuntimeError:
        pass  # widget já destruído pelo Qt: nada a devolver
```

`sigft/app/backends.py`: acrescentar antes de `motivo_da_falha`:
```python
def _modulo_de(nome: str) -> str | None:
    """O módulo Python por trás de `nome` (destino ou classe), ou None."""
    for nome_modulo, destino, classes, _exibido in MODULOS:
        if nome == destino or nome in (classes or []):
            return nome_modulo
    return None
```
e em `exigir`, no começo:
```python
    nome_modulo = _modulo_de(nome)
    if nome_modulo is None:
        # Nome errado é defeito de programação, não do computador da pessoa:
        # sem isto, "pdm_backnd" respondia "espere a abertura terminar".
        raise KeyError(f"backend desconhecido: {nome!r}")
```
e na mensagem de falha: `f"Este módulo não carregou (módulo {nome_modulo}): {motivo}\n\n"` (o resto igual).

`sigft/app_qt/views/nao_migrada.py`, acrescentar:
```python
class TelaComErro(QWidget):
    """A tela existe mas não montou. Mostra o porquê em vez de sumir."""

    def __init__(self, nome: str, erro: BaseException, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("tela")
        layout = QVBoxLayout(self)
        self.mensagem = QLabel(
            f"A tela \"{nome}\" não conseguiu abrir.\n\n{type(erro).__name__}: {erro}\n\n"
            "O detalhe está em Documentos\\SIG-FT\\logs\\sigft.log.")
        self.mensagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mensagem.setWordWrap(True)
        self.mensagem.setStyleSheet("font-size: 15px; color: #E0E0E0;")
        layout.addWidget(self.mensagem)
```

`sigft/app_qt/main.py`:
```python
def _instalar_traducao(app) -> bool:
    """Botões dos diálogos do Qt em português ("Sim", "Não", "Cancelar").
    Sem isto o QMessageBox mostra "Yes"/"No"/"Cancel"."""
    from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator

    tradutor = QTranslator(app)
    pasta = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if tradutor.load(QLocale("pt_BR"), "qtbase", "_", pasta):
        app.installTranslator(tradutor)
        app._tradutor_qt = tradutor  # segura a referência
        return True
    return False
```
chamada em `_preparar_qt()` logo depois de criar/obter o `QApplication`; e em `show_frame`:
```python
        if tela is None:
            fabrica = TELAS.get(nome)
            if fabrica is None:
                tela = TelaNaoMigrada(nome)
            else:
                try:
                    tela = fabrica(self.pilha, self)
                except Exception as erro:  # noqa: BLE001 -- vira tela de erro
                    traceback.print_exc()
                    erro_tela = TelaComErro(nome, erro)
                    self.pilha.addWidget(erro_tela)
                    self.pilha.setCurrentWidget(erro_tela)
                    return  # sem cache: a próxima visita tenta montar de novo
            self.telas[nome] = tela
            self.pilha.addWidget(tela)
```
(importar `TelaComErro` junto de `TelaNaoMigrada`.)

- [ ] **Step 4: Ver passar, suíte, commit**

```bash
python -m pytest tests/test_qt_robustez.py tests/test_qt_interface.py tests/test_qt_main.py tests/test_backends_falhas.py -q
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt sigft/app/backends.py tests/test_qt_robustez.py
git commit -m "Qt6: robustez para as telas reais e dialogos do Qt em portugues"
```

---

### Task 2: Estilo dos controles igual ao tema do CustomTkinter

**Files:**
- Modify: `sigft/app_qt/estilo.py` (função `folha_de_estilo`)
- Modify: `sigft/app_qt/views/home.py` (`BARRA`: `modelos` e `gastos` com `"primario"`)
- Modify: `sigft/app_qt/widgets/dialogs.py` (`PausaLoginDialog.botao` e `RetryLockDialog.botao_repetir` com `variante="primario"`)
- Test: `tests/test_qt_estilo_controles.py`

**Interfaces:**
- Produces: variantes de `QPushButton`: `primario` (`COLORS["primary"]`), `acento`, `neutro`, `perigo`, `contorno`, e o botão SEM variante = azul padrão do CustomTkinter; `objectName` `cartao` para os quadros `#2B2B2B` das telas; constantes `AZUL_CTK = "#1F538D"`, `AZUL_CTK_HOVER = "#14375E"`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_estilo_controles.py`:
```python
from sigft.app import theme
from sigft.app_qt import estilo


def _qss():
    return estilo.folha_de_estilo()


def test_botao_padrao_e_o_azul_do_customtkinter():
    assert "QPushButton {" in _qss()
    assert estilo.AZUL_CTK == "#1F538D" and estilo.AZUL_CTK_HOVER == "#14375E"
    trecho = _qss().split("QPushButton {", 1)[1].split("}", 1)[0]
    assert estilo.AZUL_CTK in trecho


def test_variante_primario_usa_a_cor_da_marca():
    assert f'QPushButton[variante="primario"] {{ background: {theme.COLORS["primary"]}' in _qss()


def test_campos_abas_listas_e_cartao():
    qss = _qss()
    for trecho in ("QLineEdit", "#343638", "#565B5E", "QTabBar::tab:selected",
                   "QListWidget", "#1E1E1E", "#cartao", theme.COR_CARTAO, "QComboBox"):
        assert trecho in qss, trecho


def test_caixa_marcada_e_fundo_de_dialogo_como_no_ctk():
    qss = _qss()
    assert f"QCheckBox::indicator:checked {{ background: {estilo.AZUL_CTK}" in qss
    assert f"QDialog {{ background: {estilo.cinza_tk('gray10')}" in qss


def test_home_e_dialogos_usam_primario_onde_o_ctk_pintava_primary():
    from sigft.app_qt.views import home
    variantes = {chave: variante for chave, _t, variante in home.BARRA}
    assert variantes["modelos"] == "primario" and variantes["gastos"] == "primario"
```

- [ ] **Step 2: Ver falhar** — `python -m pytest tests/test_qt_estilo_controles.py -q` → falhas (`AZUL_CTK` não existe).

- [ ] **Step 3: Implementar**

Em `estilo.py`, acrescentar as constantes (com comentário: valores do `dark-blue.json` do CustomTkinter, o tema que `sigft/app/main.py` usa):
```python
# Tema "dark-blue" do CustomTkinter (customtkinter/assets/themes/dark-blue.json):
# é o que pinta tudo o que as telas antigas não coloriam à mão.
AZUL_CTK = "#1F538D"
AZUL_CTK_HOVER = "#14375E"
```
Na folha:
- trocar a regra `QMainWindow, QDialog, #conteudo, #tela { background: ... }` por duas: `QMainWindow, #conteudo, #tela {{ background: {c['background']}; }}` e `QDialog {{ background: {cinza_tk('gray10')}; }}` (o `CTkToplevel` é `gray10`);
- na regra `QPushButton {{ ... }}`: `background: {AZUL_CTK}` e `QPushButton:hover {{ background: {AZUL_CTK_HOVER}; }}`;
- acrescentar `QPushButton[variante="primario"] {{ background: {c['primary']}; }}` e `QPushButton[variante="primario"]:hover {{ background: {c['primary_hover']}; }}`;
- `QCheckBox::indicator` com `border: 3px solid #949A9F; border-radius: 6px` e `:checked {{ background: {AZUL_CTK}; border-color: {AZUL_CTK}; }}`;
- acrescentar:
```
QLineEdit {{ background: #343638; border: 2px solid #565B5E; border-radius: 6px;
             color: {cinza_tk('gray84')}; padding: 4px 8px; min-height: 22px; }}
QLineEdit:disabled {{ color: {cinza_tk('gray45')}; }}
QComboBox {{ background: {AZUL_CTK}; border-radius: 6px; padding: 4px 10px;
             color: #DCE4EE; min-height: 22px; }}
QTabWidget::pane {{ border: none; background: {cinza_tk('gray16')}; border-radius: 6px; }}
QTabBar::tab {{ background: {cinza_tk('gray29')}; color: #DCE4EE; padding: 6px 14px;
                margin: 0 1px; border-radius: 6px; }}
QTabBar::tab:selected {{ background: {AZUL_CTK}; }}
QTabBar::tab:hover:!selected {{ background: {cinza_tk('gray41')}; }}
QListWidget {{ background: #1E1E1E; color: {c['text_light']}; border: none; }}
QListWidget::item:selected {{ background: {c['primary']}; color: white; }}
#cartao {{ background: {theme.COR_CARTAO}; border-radius: 8px; }}
```
Em `views/home.py`, `BARRA`: `("modelos", "\U0001F916  Modelos de IA", "primario")` e `("gastos", "\U0001F4B0  Gastos de IA", "primario")`. Em `widgets/dialogs.py`, depois de criar `self.botao` (PausaLogin) e `self.botao_repetir` (RetryLock): `.setProperty("variante", "primario")`.

- [ ] **Step 4: Ver passar, conferir a Home, commit**

```bash
python -m pytest tests/test_qt_estilo_controles.py tests/test_qt_estilo.py tests/test_qt_home.py -q
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt tests/test_qt_estilo_controles.py
git commit -m "Qt6: controles com as cores do tema dark-blue do CustomTkinter"
```
Conferir a Home de novo (captura) — ela não pode mudar de cara: os dois botões passam a pedir `primario` explicitamente.

---

### Task 3: Perguntas, avisos e seleção sempre na thread da interface

**Files:**
- Modify: `sigft/app_qt/widgets/espera.py`
- Modify: `sigft/app_qt/widgets/dialogs.py` (+ `SelecaoComCaixasDialog`)
- Test: `tests/test_qt_perguntas.py`

**Interfaces:**
- Consumes: `interface.na_interface`, `interface.na_thread_da_interface`.
- Produces (em `DialogosDeEspera`, chamáveis de qualquer thread):
  - `perguntar_sim_nao(titulo: str, mensagem: str) -> bool` — `QMessageBox.question`, padrão "Não";
  - `pedir_texto(titulo: str, mensagem: str) -> str | None` — `QInputDialog.getText`; cancelar → `None`;
  - `avisar(titulo: str, mensagem: str, tipo: str = "info") -> None` — `tipo` em `{"info", "aviso", "erro"}`; NÃO bloqueia o worker.
- Produces (em `dialogs.py`): `SelecaoComCaixasDialog(parent, *, titulo: str, mensagem: str, itens: list[str])` com `.lista: QListWidget`, `.botao_todos`, `.botao_confirmar`, e `.selecionados() -> list[str]` (na ordem de `itens`); usar com `exec()` na thread da interface.

- [ ] **Step 1: Testes que falham**

`tests/test_qt_perguntas.py`:
```python
import threading

from PySide6.QtWidgets import QInputDialog, QMessageBox, QWidget

from sigft.app_qt.widgets import dialogs as qd
from sigft.app_qt.widgets.espera import DialogosDeEspera


class Tela(DialogosDeEspera, QWidget):
    pass


def _no_worker(qtbot, func):
    resultado, threads = [], []

    def rodar():
        threads.append(threading.get_ident())
        resultado.append(func())

    t = threading.Thread(target=rodar, daemon=True)
    t.start()
    qtbot.waitUntil(lambda: len(resultado) == 1, timeout=3000)
    return resultado[0]


def test_sim_nao_do_worker_pergunta_na_thread_da_interface(qt_interface, qtbot, monkeypatch):
    onde = []
    monkeypatch.setattr(QMessageBox, "question", staticmethod(
        lambda *a, **k: onde.append(threading.get_ident()) or QMessageBox.StandardButton.Yes))
    tela = Tela()
    qtbot.addWidget(tela)
    assert _no_worker(qtbot, lambda: tela.perguntar_sim_nao("T", "Continua?")) is True
    assert onde == [threading.main_thread().ident]


def test_sim_nao_responde_false_no_nao(qt_interface, qtbot, monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", staticmethod(
        lambda *a, **k: QMessageBox.StandardButton.No))
    tela = Tela()
    qtbot.addWidget(tela)
    assert tela.perguntar_sim_nao("T", "Continua?") is False  # da própria thread da interface


def test_pedir_texto_e_cancelar(qt_interface, qtbot, monkeypatch):
    respostas = iter([("PDM-1", True), ("", False)])
    monkeypatch.setattr(QInputDialog, "getText", staticmethod(lambda *a, **k: next(respostas)))
    tela = Tela()
    qtbot.addWidget(tela)
    assert _no_worker(qtbot, lambda: tela.pedir_texto("T", "Novo PDM?")) == "PDM-1"
    assert _no_worker(qtbot, lambda: tela.pedir_texto("T", "Novo PDM?")) is None


def test_avisar_nao_bloqueia_e_mostra_na_thread_da_interface(qt_interface, qtbot, monkeypatch):
    vistos = []
    for nome in ("information", "warning", "critical"):
        monkeypatch.setattr(QMessageBox, nome, staticmethod(
            lambda *a, _n=nome, **k: vistos.append((_n, threading.get_ident()))))
    tela = Tela()
    qtbot.addWidget(tela)
    _no_worker(qtbot, lambda: tela.avisar("T", "ok"))
    _no_worker(qtbot, lambda: tela.avisar("T", "cuidado", tipo="aviso"))
    _no_worker(qtbot, lambda: tela.avisar("T", "falhou", tipo="erro"))
    qtbot.waitUntil(lambda: len(vistos) == 3, timeout=2000)
    assert [v[0] for v in vistos] == ["information", "warning", "critical"]
    assert {v[1] for v in vistos} == {threading.main_thread().ident}


def test_selecao_com_caixas(qt_interface, qtbot):
    d = qd.SelecaoComCaixasDialog(None, titulo="Selecione as Fichas",
                                  mensagem="Selecione os PMIBs para processar:",
                                  itens=["A", "B", "C"])
    qtbot.addWidget(d)
    assert d.selecionados() == []
    d.lista.item(2).setCheckState(qd.Qt.CheckState.Checked)
    assert d.selecionados() == ["C"]
    d.botao_todos.click()
    assert d.selecionados() == ["A", "B", "C"]
```

- [ ] **Step 2: Ver falhar** — `python -m pytest tests/test_qt_perguntas.py -q` → falhas (`AttributeError`).

- [ ] **Step 3: Implementar**

Em `espera.py`, dentro de `DialogosDeEspera`:
```python
    # -- perguntas e avisos simples ------------------------------------------
    def _na_interface_e_esperar(self, func):
        """Roda `func()` na thread da interface e devolve o resultado.

        Da própria thread da interface, chama direto (os diálogos estáticos do
        Qt já bloqueiam sem parar o laço de eventos).
        """
        if interface.na_thread_da_interface():
            return func()
        evento = threading.Event()
        caixa: dict = {}

        def rodar() -> None:
            try:
                caixa["valor"] = func()
            except Exception:  # noqa: BLE001 -- o worker não pode ficar preso
                traceback.print_exc()
            finally:
                evento.set()

        interface.na_interface(rodar)
        evento.wait()
        return caixa.get("valor")

    def perguntar_sim_nao(self, titulo: str, mensagem: str) -> bool:
        def perguntar():
            resposta = QMessageBox.question(
                self, titulo, mensagem,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            return resposta == QMessageBox.StandardButton.Yes
        return bool(self._na_interface_e_esperar(perguntar))

    def pedir_texto(self, titulo: str, mensagem: str) -> str | None:
        def pedir():
            texto, ok = QInputDialog.getText(self, titulo, mensagem)
            return texto if ok else None
        return self._na_interface_e_esperar(pedir)

    def avisar(self, titulo: str, mensagem: str, tipo: str = "info") -> None:
        """Mostra e segue: o worker não espera a pessoa fechar o aviso."""
        funcao = {"info": QMessageBox.information, "aviso": QMessageBox.warning,
                  "erro": QMessageBox.critical}[tipo]
        if interface.na_thread_da_interface():
            funcao(self, titulo, mensagem)
        else:
            interface.na_interface(funcao, self, titulo, mensagem)
```
(imports: `from PySide6.QtWidgets import QInputDialog, QMessageBox`.)

Em `dialogs.py` (importar `Qt` já existe; acrescentar `QListWidget, QListWidgetItem`):
```python
class SelecaoComCaixasDialog(QDialog):
    """Lista com caixas de marcar + "Todos" + "CONFIRMAR".

    É a janela de seleção de fichas da Aplicação LMR (450x600). A lista é um
    QListWidget: desenha só as linhas visíveis, ao contrário de um widget por
    ficha -- com centenas de PMIBs a diferença aparece.
    """

    def __init__(self, parent, *, titulo: str, mensagem: str, itens: list[str]) -> None:
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.resize(450, 600)
        layout = QVBoxLayout(self)
        rotulo = QLabel(mensagem)
        rotulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        rotulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rotulo)
        self.lista = QListWidget()
        for texto in itens:
            item = QListWidgetItem(texto)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lista.addItem(item)
        layout.addWidget(self.lista, 1)
        linha = QHBoxLayout()
        self.botao_todos = QPushButton("Todos")
        self.botao_todos.setProperty("variante", "neutro")
        self.botao_todos.setFixedWidth(80)
        self.botao_todos.clicked.connect(self._marcar_todos)
        self.botao_confirmar = QPushButton("CONFIRMAR")
        self.botao_confirmar.setProperty("variante", "acento")
        self.botao_confirmar.setStyleSheet("color: #161616;")
        self.botao_confirmar.setFixedWidth(150)
        self.botao_confirmar.clicked.connect(self.accept)
        linha.addWidget(self.botao_todos)
        linha.addStretch()
        linha.addWidget(self.botao_confirmar)
        layout.addLayout(linha)

    def _marcar_todos(self) -> None:
        for i in range(self.lista.count()):
            self.lista.item(i).setCheckState(Qt.CheckState.Checked)

    def selecionados(self) -> list[str]:
        return [self.lista.item(i).text() for i in range(self.lista.count())
                if self.lista.item(i).checkState() == Qt.CheckState.Checked]
```

- [ ] **Step 4: Ver passar (5x), suíte, commit**

```bash
for i in 1 2 3 4 5; do python -m pytest tests/test_qt_perguntas.py -q || break; done
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt/widgets tests/test_qt_perguntas.py
git commit -m "Qt6: perguntas, avisos e selecao com caixas sempre na thread da interface"
```

---

### Task 4: Diálogos de arquivo, seletores e blocos de tela

**Files:**
- Create: `sigft/app_qt/file_dialogs.py`
- Create: `sigft/app_qt/widgets/pickers.py`
- Create: `sigft/app_qt/widgets/blocos.py`
- Test: `tests/test_qt_file_dialogs.py`, `tests/test_qt_pickers.py`

**Interfaces:**
- Consumes: `sigft.app.file_dialogs.ask_open_file/ask_open_files/ask_save_file/ask_directory` (mesma assinatura; recebem `dialog_fn`).
- Produces:
  - `sigft.app_qt.file_dialogs`: `filtro_qt(filetypes) -> str`; `ask_open_file`, `ask_open_files`, `ask_save_file`, `ask_directory` com a MESMA assinatura e retorno dos originais (`dialog_fn` opcional; padrão = `QFileDialog`).
  - `sigft.app_qt.widgets.pickers`: `FilePickerRow(parent=None, *, chave, categoria, texto_botao, titulo=None, filetypes=None, texto_vazio=TEXTO_SEM_ARQUIVO, ao_escolher=None, dialog_fn=None, largura_botao=240, pintar_botao=True)`; `MultiFilePickerRow` (mesmos parâmetros; valor = tupla); `FolderPickerRow(parent=None, *, chave, categoria="pasta", texto_botao, titulo=None, texto_vazio=TEXTO_SEM_PASTA, ...)`; todos com `.botao`, `.label_status`, `.valor`, `.limpar()`, `.definir(valor, rotulo)`; constantes `TEXTO_SEM_ARQUIVO`, `TEXTO_SEM_PASTA`, `COR_BOTAO_SELECAO = "#3A3A3A"`.
  - `sigft.app_qt.widgets.blocos`: `cartao(layout_pai) -> QVBoxLayout` (cria um `QFrame#cartao` e devolve o layout dele); `rotulo(texto, *, tamanho=13, negrito=False, cor=None, alinhar="centro") -> QLabel`; `botao(texto, *, variante=None, largura=None, altura=None, tamanho_fonte=None, negrito=False) -> QPushButton`.

- [ ] **Step 1: Testes que falham**

`tests/test_qt_file_dialogs.py`:
```python
import os

from PySide6.QtWidgets import QFileDialog

from sigft.app_qt import file_dialogs as fd


def test_filtro_tk_vira_filtro_qt():
    assert fd.filtro_qt([("Excel", "*.xlsx;*.xlsm")]) == "Excel (*.xlsx *.xlsm)"
    assert fd.filtro_qt([("Excel", "*.xlsx *.xlsm"), ("PDF", "*.pdf")]) == \
        "Excel (*.xlsx *.xlsm);;PDF (*.pdf)"
    assert fd.filtro_qt(None) == ""


def test_abrir_um_lembra_a_pasta(qt_interface, tmp_path, monkeypatch):
    escolhido = tmp_path / "a" / "ficha.xlsx"
    escolhido.parent.mkdir()
    escolhido.write_text("x")
    chamadas = []

    def falso(parent, titulo, pasta, filtro):
        chamadas.append((titulo, filtro))
        return str(escolhido), filtro

    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(falso))
    config = tmp_path / "prefs.json"
    caminho = fd.ask_open_file("lmr.excel", "excel", titulo="Selecione", filetypes=[("Excel", "*.xlsx")],
                               config_path=config)
    assert caminho == str(escolhido)
    assert chamadas == [("Selecione", "Excel (*.xlsx)")]
    # a memória de pastas é a de sempre (sigft.core.prefs)
    from sigft.core import prefs
    assert prefs.get_initial_dir("lmr.excel", "excel", config_path=config) == str(escolhido.parent)


def test_cancelar_devolve_vazio(qt_interface, monkeypatch, tmp_path):
    monkeypatch.setattr(QFileDialog, "getOpenFileNames", staticmethod(lambda *a: ([], "")))
    assert fd.ask_open_files("x", "excel", config_path=tmp_path / "p.json") == ()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", staticmethod(lambda *a: ""))
    assert fd.ask_directory("x", "pasta", config_path=tmp_path / "p.json") == ""


def test_salvar_acrescenta_extensao(qt_interface, monkeypatch, tmp_path):
    monkeypatch.setattr(QFileDialog, "getSaveFileName",
                        staticmethod(lambda *a: (os.path.join(str(tmp_path), "relatorio"), "")))
    assert fd.ask_save_file("x", "excel", defaultextension=".xlsx",
                            config_path=tmp_path / "p.json").endswith("relatorio.xlsx")
```

`tests/test_qt_pickers.py`:
```python
from sigft.app import theme
from sigft.app_qt.widgets import pickers


def test_arquivo_escolhido_fica_verde_e_avisa(qt_interface, qtbot):
    avisos = []
    linha = pickers.FilePickerRow(chave="k", categoria="excel", texto_botao="Selecionar",
                                  ao_escolher=avisos.append,
                                  dialog_fn=lambda **k: "/tmp/pasta/STATUS.xlsx")
    qtbot.addWidget(linha)
    assert linha.label_status.text() == pickers.TEXTO_SEM_ARQUIVO
    linha.botao.click()
    assert linha.valor == "/tmp/pasta/STATUS.xlsx"
    assert linha.label_status.text() == "STATUS.xlsx"
    assert theme.COLORS["accent"] in linha.label_status.styleSheet()
    assert avisos == ["/tmp/pasta/STATUS.xlsx"]


def test_cancelar_nao_apaga_o_que_ja_estava(qt_interface, qtbot):
    respostas = iter(["/tmp/a.xlsx", ""])
    linha = pickers.FilePickerRow(chave="k", categoria="excel", texto_botao="S",
                                  dialog_fn=lambda **k: next(respostas))
    qtbot.addWidget(linha)
    linha.botao.click()
    linha.botao.click()
    assert linha.valor == "/tmp/a.xlsx"


def test_varios_e_pasta(qt_interface, qtbot):
    varios = pickers.MultiFilePickerRow(chave="k", categoria="excel", texto_botao="S",
                                        dialog_fn=lambda **k: ("/a.xlsx", "/b.xlsx"))
    pasta = pickers.FolderPickerRow(chave="k", texto_botao="S", dialog_fn=lambda **k: "/x/y/")
    for w in (varios, pasta):
        qtbot.addWidget(w)
        w.botao.click()
    assert varios.label_status.text() == "2 arquivos selecionados"
    assert pasta.label_status.text() == "/x/y/"


def test_limpar_volta_ao_cinza(qt_interface, qtbot):
    linha = pickers.FilePickerRow(chave="k", categoria="excel", texto_botao="S",
                                  texto_vazio="Nenhum", dialog_fn=lambda **k: "/a.xlsx")
    qtbot.addWidget(linha)
    linha.botao.click()
    linha.limpar()
    assert linha.valor is None and linha.label_status.text() == "Nenhum"
```

- [ ] **Step 2: Ver falhar** — `python -m pytest tests/test_qt_file_dialogs.py tests/test_qt_pickers.py -q` → `ModuleNotFoundError`.

- [ ] **Step 3: Implementar `file_dialogs.py`**

```python
"""Diálogos de arquivo da interface Qt, com a MESMA memória de pastas de hoje.

Toda a lógica (pasta inicial por chave/categoria, lembrar a pasta escolhida,
cancelar devolvendo vazio) mora em `sigft/app/file_dialogs.py`, que não
depende de tkinter para isso: ela aceita um `dialog_fn`. Aqui só se troca o
diálogo do Tk pelo `QFileDialog`, com os mesmos nomes de parâmetro do Tk.
"""
from __future__ import annotations

import os

from PySide6.QtWidgets import QApplication, QFileDialog

from sigft.app import file_dialogs as _base


def filtro_qt(filetypes) -> str:
    """`[("Excel", "*.xlsx;*.xlsm")]` (Tk) -> `"Excel (*.xlsx *.xlsm)"` (Qt)."""
    if not filetypes:
        return ""
    return ";;".join(
        f"{nome} ({' '.join(padrao.replace(';', ' ').split())})" for nome, padrao in filetypes)


def _pai():
    return QApplication.activeWindow()


def _abrir_um(*, initialdir=None, title=None, filetypes=None, **_):
    caminho, _filtro = QFileDialog.getOpenFileName(_pai(), title or "", initialdir or "", filtro_qt(filetypes))
    return caminho


def _abrir_varios(*, initialdir=None, title=None, filetypes=None, **_):
    caminhos, _filtro = QFileDialog.getOpenFileNames(_pai(), title or "", initialdir or "", filtro_qt(filetypes))
    return tuple(caminhos)


def _salvar(*, initialdir=None, title=None, filetypes=None, defaultextension=None, **_):
    caminho, _filtro = QFileDialog.getSaveFileName(_pai(), title or "", initialdir or "", filtro_qt(filetypes))
    if caminho and defaultextension and not os.path.splitext(caminho)[1]:
        caminho += defaultextension
    return caminho


def _pasta(*, initialdir=None, title=None, **_):
    return QFileDialog.getExistingDirectory(_pai(), title or "", initialdir or "")


def ask_open_file(chave, categoria, *, dialog_fn=None, **kwargs) -> str:
    return _base.ask_open_file(chave, categoria, dialog_fn=dialog_fn or _abrir_um, **kwargs)


def ask_open_files(chave, categoria, *, dialog_fn=None, **kwargs):
    return _base.ask_open_files(chave, categoria, dialog_fn=dialog_fn or _abrir_varios, **kwargs)


def ask_save_file(chave, categoria, *, dialog_fn=None, **kwargs) -> str:
    return _base.ask_save_file(chave, categoria, dialog_fn=dialog_fn or _salvar, **kwargs)


def ask_directory(chave, categoria, *, dialog_fn=None, **kwargs) -> str:
    return _base.ask_directory(chave, categoria, dialog_fn=dialog_fn or _pasta, **kwargs)
```

- [ ] **Step 4: Implementar `widgets/blocos.py`**

```python
"""Peças que todas as telas repetem: o quadro cinza, o rótulo, o botão.

Nas telas CustomTkinter cada uma vinha com cor, fonte e tamanho escritos à
mão. Aqui a COR do quadro e dos botões vem da folha de estilo (objectName e
variante); fonte e tamanho continuam por chamada, porque variam de tela a tela.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

_ALINHAMENTO = {"centro": Qt.AlignmentFlag.AlignCenter, "esquerda": Qt.AlignmentFlag.AlignLeft}


def cartao(layout_pai) -> QVBoxLayout:
    quadro = QFrame(objectName="cartao")
    layout = QVBoxLayout(quadro)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(10)
    layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
    layout_pai.addWidget(quadro)
    return layout


def rotulo(texto: str, *, tamanho: int = 13, negrito: bool = False, cor: str | None = None,
           alinhar: str = "centro") -> QLabel:
    etiqueta = QLabel(texto)
    etiqueta.setAlignment(_ALINHAMENTO[alinhar])
    etiqueta.setWordWrap(True)
    estilo = f"font-size: {tamanho}px; background: transparent;"
    if negrito:
        estilo += " font-weight: bold;"
    if cor:
        estilo += f" color: {cor};"
    etiqueta.setStyleSheet(estilo)
    return etiqueta


def botao(texto: str, *, variante: str | None = None, largura: int | None = None,
          altura: int | None = None, tamanho_fonte: int | None = None,
          negrito: bool = False) -> QPushButton:
    b = QPushButton(texto)
    if variante:
        b.setProperty("variante", variante)
    if largura:
        b.setFixedWidth(largura)
    if altura:
        b.setFixedHeight(altura)
    estilo = ""
    if tamanho_fonte:
        estilo += f"font-size: {tamanho_fonte}px;"
    if negrito:
        estilo += " font-weight: bold;"
    if estilo:
        b.setStyleSheet(estilo)
    return b
```

- [ ] **Step 5: Implementar `widgets/pickers.py`**

```python
"""Seletores de arquivo/pasta da interface Qt — mesma API dos CustomTkinter.

A tela declara `chave`/`categoria` uma vez e nunca mais pensa em memória de
pastas (é o CP 7.2). Rótulo cinza "Nenhum arquivo selecionado" que vira o nome
em verde, botão cinza que vira `primary`: o comportamento de hoje.
"""
from __future__ import annotations

import os

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from sigft.app import theme
from sigft.app_qt import file_dialogs
from sigft.app_qt.estilo import cinza_tk

COR_BOTAO_SELECAO = "#3A3A3A"
COR_BOTAO_SELECAO_HOVER = "#454545"
TEXTO_SEM_ARQUIVO = "Nenhum arquivo selecionado"
TEXTO_SEM_PASTA = "Nenhuma pasta selecionada"


class _LinhaSeletora(QWidget):
    def __init__(self, parent=None, *, texto_botao: str, texto_vazio: str,
                 largura_botao: int = 240, pintar_botao: bool = True, ao_escolher=None) -> None:
        super().__init__(parent)
        self._texto_vazio = texto_vazio
        self._pintar_botao = pintar_botao
        self._ao_escolher = ao_escolher
        self._valor = None
        linha = QHBoxLayout(self)
        linha.setContentsMargins(0, 0, 0, 0)
        self.botao = QPushButton(texto_botao)
        self.botao.setFixedWidth(largura_botao)
        self.botao.clicked.connect(self._abrir_dialogo)
        self.label_status = QLabel()
        linha.addWidget(self.botao)
        linha.addSpacing(15)
        linha.addWidget(self.label_status)
        linha.addStretch()
        self.limpar()

    def _pintar(self, cor: str, cor_texto: str) -> None:
        if self._pintar_botao or cor == COR_BOTAO_SELECAO:
            hover = COR_BOTAO_SELECAO_HOVER if cor == COR_BOTAO_SELECAO else theme.COLORS["primary_hover"]
            self.botao.setStyleSheet(
                f"QPushButton {{ background: {cor}; font-size: 12px; }}"
                f" QPushButton:hover {{ background: {hover}; }}")
        self.label_status.setStyleSheet(f"color: {cor_texto}; background: transparent;")

    @property
    def valor(self):
        return self._valor

    def limpar(self) -> None:
        self._valor = None
        self.label_status.setText(self._texto_vazio)
        self._pintar(COR_BOTAO_SELECAO, cinza_tk(theme.COR_TEXTO_APOIO))

    def definir(self, valor, rotulo: str) -> None:
        self._valor = valor
        self.label_status.setText(rotulo)
        self._pintar(theme.COLORS["primary"], theme.COLORS["accent"])

    def _abrir_dialogo(self) -> None:
        raise NotImplementedError

    def _notificar(self) -> None:
        if self._ao_escolher is not None:
            self._ao_escolher(self._valor)


class FilePickerRow(_LinhaSeletora):
    def __init__(self, parent=None, *, chave: str, categoria: str, texto_botao: str,
                 titulo: str | None = None, filetypes=None, texto_vazio: str = TEXTO_SEM_ARQUIVO,
                 ao_escolher=None, dialog_fn=None, **kwargs) -> None:
        self._chave, self._categoria = chave, categoria
        self._titulo, self._filetypes, self._dialog_fn = titulo, filetypes, dialog_fn
        super().__init__(parent, texto_botao=texto_botao, texto_vazio=texto_vazio,
                         ao_escolher=ao_escolher, **kwargs)

    def _abrir_dialogo(self) -> None:
        caminho = file_dialogs.ask_open_file(self._chave, self._categoria, titulo=self._titulo,
                                             filetypes=self._filetypes, dialog_fn=self._dialog_fn)
        if not caminho:
            return  # cancelar não apaga o que já estava escolhido
        self.definir(caminho, os.path.basename(caminho))
        self._notificar()


class MultiFilePickerRow(_LinhaSeletora):
    def __init__(self, parent=None, *, chave: str, categoria: str, texto_botao: str,
                 titulo: str | None = None, filetypes=None, texto_vazio: str = TEXTO_SEM_ARQUIVO,
                 ao_escolher=None, dialog_fn=None, **kwargs) -> None:
        self._chave, self._categoria = chave, categoria
        self._titulo, self._filetypes, self._dialog_fn = titulo, filetypes, dialog_fn
        super().__init__(parent, texto_botao=texto_botao, texto_vazio=texto_vazio,
                         ao_escolher=ao_escolher, **kwargs)

    def _abrir_dialogo(self) -> None:
        caminhos = file_dialogs.ask_open_files(self._chave, self._categoria, titulo=self._titulo,
                                               filetypes=self._filetypes, dialog_fn=self._dialog_fn)
        if not caminhos:
            return
        self.definir(tuple(caminhos), f"{len(caminhos)} arquivos selecionados")
        self._notificar()


class FolderPickerRow(_LinhaSeletora):
    def __init__(self, parent=None, *, chave: str, categoria: str = "pasta", texto_botao: str,
                 titulo: str | None = None, texto_vazio: str = TEXTO_SEM_PASTA,
                 ao_escolher=None, dialog_fn=None, **kwargs) -> None:
        self._chave, self._categoria = chave, categoria
        self._titulo, self._dialog_fn = titulo, dialog_fn
        super().__init__(parent, texto_botao=texto_botao, texto_vazio=texto_vazio,
                         ao_escolher=ao_escolher, **kwargs)

    def _abrir_dialogo(self) -> None:
        pasta = file_dialogs.ask_directory(self._chave, self._categoria, titulo=self._titulo,
                                           dialog_fn=self._dialog_fn)
        if not pasta:
            return
        self.definir(pasta, os.path.basename(pasta) or pasta)
        self._notificar()
```
(`theme.COR_TEXTO_APOIO` é `"gray"`, por isso passa por `cinza_tk`.)

- [ ] **Step 6: Ver passar, suíte, commit**

```bash
python -m pytest tests/test_qt_file_dialogs.py tests/test_qt_pickers.py tests/test_qt_sem_tkinter.py -q
python -m ruff check . && bash scripts/check.sh
git add sigft/app_qt tests/test_qt_file_dialogs.py tests/test_qt_pickers.py
git commit -m "Qt6: dialogos de arquivo com a memoria de pastas, seletores e blocos de tela"
```
Acrescentar `sigft.app_qt.file_dialogs`, `sigft.app_qt.widgets.pickers` e `sigft.app_qt.widgets.blocos` à lista de módulos de `tests/test_qt_sem_tkinter.py`.

---

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

### Task 8: Seção "Aplicação LMR", registro das telas e conferência visual

**Files:**
- Create: `sigft/app_qt/views/aplicacao_lmr.py`
- Modify: `sigft/app_qt/main.py` (`TELAS`)
- Test: `tests/test_qt_tela_aplicacao_lmr.py`

**Interfaces:**
- Consumes: `ModuloLMR`, `ModuloApagarLMR`, `ModuloTranslator`.
- Produces: `ModuloAplicacaoLMR(parent=None, controller=None)` com `.abas: QTabWidget`, `.tela_upload`, `.tela_exclusao`; `TELAS["LMR"]` e `TELAS["Translator"]`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_tela_aplicacao_lmr.py`:
```python
from sigft.app_qt.views.aplicacao_lmr import ModuloAplicacaoLMR


def test_duas_abas_com_um_console(qt_interface, qtbot):
    secao = ModuloAplicacaoLMR()
    qtbot.addWidget(secao)
    assert secao.label_titulo.text() == "Aplicação LMR"
    assert [secao.abas.tabText(i) for i in range(secao.abas.count())] == \
        ["Upload de Aplicações", "Exclusão de Aplicações"]
    assert secao.abas.currentIndex() == 0  # nunca abre direto na aba que APAGA
    assert secao.tela_upload.console is secao.console
    assert secao.tela_exclusao.console is secao.console
    assert secao.tela_upload.header is None and secao.tela_exclusao.header is None


def test_telas_registradas_no_menu(qt_interface, qtbot, tmp_path, monkeypatch):
    from sigft.app_qt import main as qmain
    from sigft.app_qt.views.translator import ModuloTranslator
    monkeypatch.setattr(qmain, "_arquivo_de_chaves", lambda: str(tmp_path / "api_config.json"))
    janela = qmain.SIG_FT_App()
    qtbot.addWidget(janela)
    janela.show_frame("LMR")
    assert isinstance(janela.pilha.currentWidget(), ModuloAplicacaoLMR)
    janela.show_frame("Translator")
    assert isinstance(janela.pilha.currentWidget(), ModuloTranslator)
```

- [ ] **Step 2: Ver falhar** — `ModuleNotFoundError`.

- [ ] **Step 3: Implementar**

`sigft/app_qt/views/aplicacao_lmr.py`:
```python
"""Seção "Aplicação LMR": Upload e Exclusão em abas, com UM console.

Duas operações sobre a MESMA aba do portal e a MESMA coluna da planilha ficam
juntas, e o log fica num lugar só (decisão de 2026-08-28, ver a versão
CustomTkinter). Abre sempre na aba de Upload: a outra APAGA.
"""
from __future__ import annotations

from PySide6.QtWidgets import QTabWidget

from sigft.app_qt.views.apagar_lmr import ModuloApagarLMR
from sigft.app_qt.views.lmr import ModuloLMR
from sigft.app_qt.widgets.module_frame import ModuleFrame


class ModuloAplicacaoLMR(ModuleFrame):
    def __init__(self, parent=None, controller=None) -> None:
        super().__init__(parent, controller, titulo="Aplicação LMR", peso_conteudo=3)

    def _build_ui(self) -> None:
        self.abas = QTabWidget()
        self.content_layout.addWidget(self.abas)
        self.tela_upload = ModuloLMR(controller=self.controller, embutida=True,
                                     console_externo=self.console)
        self.tela_exclusao = ModuloApagarLMR(controller=self.controller, embutida=True,
                                             console_externo=self.console)
        self.abas.addTab(self.tela_upload, "Upload de Aplicações")
        self.abas.addTab(self.tela_exclusao, "Exclusão de Aplicações")
        self.abas.setCurrentIndex(0)
```
Em `sigft/app_qt/main.py`, no dicionário `TELAS`:
```python
    "LMR": lambda parent, controller: ModuloAplicacaoLMR(parent, controller),
    "Translator": lambda parent, controller: ModuloTranslator(parent, controller),
```
(com os imports correspondentes).

Atenção: o console da seção só existe depois que `ModuleFrame.__init__` montou o cabeçalho e o console — e `_build_ui` é chamado no fim do `__init__`, então `self.console` já existe em `_build_ui`. Confirme que, na `ModuleFrame` atual, o console é criado ANTES de `_build_ui()`; se não for, passe `construir=False` ao `super().__init__` e chame `self._build_ui()` depois.

- [ ] **Step 4: Ver passar, suíte, abrir de verdade, commit**

```bash
python -m pytest tests/test_qt_tela_aplicacao_lmr.py -q
python -m ruff check . && bash scripts/check.sh
```
Abrir de verdade (Python com tkinter + PySide6, Xvfb) e capturar, lado a lado com a versão CustomTkinter, em 1280x850: Tradutor; Aplicação LMR na aba Upload; Aplicação LMR na aba Exclusão. Diferença visível que não seja a das decisões já registradas (cards da Home, ícones) é defeito desta task.
```bash
git add sigft/app_qt tests/test_qt_tela_aplicacao_lmr.py
git commit -m "Qt6: secao Aplicacao LMR com abas e telas registradas no menu"
```

---

### Task 9: Entrega da etapa

- [ ] **Step 1:** `python -m ruff check .`, `bash scripts/check.sh`, e os dois smokes reais (`-m sigft.app_qt.main --smoke` e `frontend.py --smoke`) com exit 0.
- [ ] **Step 2:** Exportar os patches da etapa: `git format-patch <último commit da Etapa 1>..HEAD -o ../jonan/sig-ft-propuestas/patches/etapa2/`.
- [ ] **Step 3:** `LOG.md` — entrada "2. Qt6 — Etapa 2": o que muda, por quê, como foi testado, capturas lado a lado, como aplicar (`git am patches/etapa2/*.patch` DEPOIS da etapa 1), o que não foi testado (portal real: os robôs de LMR e o tradutor com Excel de verdade precisam de uma rodada na máquina da empresa).
- [ ] **Step 4:** commit e push no repo `jonan`.
