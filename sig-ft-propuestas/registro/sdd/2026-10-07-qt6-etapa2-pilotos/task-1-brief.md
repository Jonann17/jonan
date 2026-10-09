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

