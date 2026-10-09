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

