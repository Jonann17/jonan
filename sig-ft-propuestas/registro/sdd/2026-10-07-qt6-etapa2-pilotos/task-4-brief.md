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

