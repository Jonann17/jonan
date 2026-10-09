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

