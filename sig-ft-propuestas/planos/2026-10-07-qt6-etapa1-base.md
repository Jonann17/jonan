# Migração para Qt6 — Etapa 1 (base) — Plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a interface Qt nova (`sigft/app_qt/`) abre com splash, barra lateral, Home com os 12 cards e as telas ainda não migradas mostrando um aviso — com a mesma aparência da atual, sem tocar na interface CustomTkinter, que continua sendo a oficial.

**Architecture:** pacote paralelo `sigft/app_qt/`. Toda chamada de thread para widget passa por `interface.na_interface()` (sinal Qt com fila). Telas são criadas na primeira visita. O registro de backends existente (`sigft/app/backends.py`, que não depende de tkinter) é reaproveitado e passa a guardar o motivo de cada falha.

**Tech Stack:** Python ≥ 3.10, PySide6 (Qt 6), pytest + pytest-qt (`QT_QPA_PLATFORM=offscreen`).

**Spec:** `sig-ft-propuestas/specs/2026-10-07-migracao-qt6-design.md` (no repo `Jonann17/jonan`).

## Global Constraints

- Biblioteca de UI: **PySide6** (LGPL). Nunca PyQt6.
- Python mínimo: **3.10**. Mensagem para versão menor: ver Task 2.
- Paleta, fontes e medidas vêm de `sigft/app/theme.py` — **não copiar valores de cor**.
- Fontes: `assets/fonts/Roboto-Regular.ttf`, `assets/fonts/Roboto-Medium.ttf`, `assets/fonts/NotoEmoji-Regular.ttf`, com as licenças ao lado.
- Ícones (emojis) em **preto e branco**: fonte Noto Emoji + seletor `U+FE0E` via `estilo.mono()`.
- Espaçamento igual ao atual: botão da barra lateral **35 px** de altura e **4 px** entre botões; rótulo de seção **20 px** acima / **5 px** abaixo; botões da barra da Home **40 px**.
- Cards da Home: descrição ocupa a largura do card (sem `wraplength`).
- Nenhum widget é tocado fora da thread da interface: de outra thread, sempre `interface.na_interface(func, *args)`.
- `sigft/core/` e `sigft/services/` **não mudam** (exceto o novo `sigft/core/python_minimo.py`).
- `sigft/app/` (interface CustomTkinter) **não muda**, exceto `sigft/app/backends.py` (Task 5).
- Código, comentários, docstrings e mensagens em **português**; mensagens de commit **sem acento**.
- Commits terminam com as duas linhas de atribuição da sessão.
- Verificação de cada task: `bash scripts/check.sh` verde.

## Desvios do spec (decididos ao planejar)

- **Sem `sigft/app_qt/backends.py`:** o registro `sigft/app/backends.py` não importa
  tkinter, então é reaproveitado e ganha `falhas`/`exigir` (Task 5). Duas cópias do
  registro seriam duas fontes de verdade.
- **Pickers e `file_dialogs` Qt vão para a Etapa 2**, junto com as telas piloto que os
  usam — assim cada um nasce testado contra uma tela de verdade.
- **Sem `requires-python` no `pyproject.toml`** (ver nota da Task 2).

## Mapa de arquivos

| Arquivo | Responsabilidade |
|---|---|
| `requirements.txt`, `requirements-dev.txt` | + `PySide6`, + `pytest-qt` |
| `.github/workflows/ci.yml` | bibliotecas do sistema para o Qt; Python 3.10 e 3.12 |
| `tests/conftest.py` | `QT_QPA_PLATFORM=offscreen`; fixture `qt_interface` |
| `sigft/core/python_minimo.py` | confere a versão do Python (só stdlib, sintaxe 3.6+) |
| `frontend.py` | chama `exigir_python_minimo()` antes de tudo |
| `assets/fonts/*` | Roboto (Apache 2.0) e Noto Emoji (OFL) + licenças |
| `sigft/app_qt/__init__.py` | pacote |
| `sigft/app_qt/estilo.py` | `cinza_tk`, `mono`, `carregar_fontes`, `folha_de_estilo` |
| `sigft/app_qt/interface.py` | `instalar`, `na_interface`, `na_thread_da_interface` |
| `sigft/app/backends.py` | + `falhas`, `motivo_da_falha`, `exigir`, `BackendIndisponivel` |
| `sigft/app_qt/widgets/__init__.py` | pacote |
| `sigft/app_qt/widgets/console.py` | `ConsoleFrame` (log em lote, thread-safe) |
| `sigft/app_qt/widgets/dialogs.py` | `PausaLoginDialog`, `RetryLockDialog` |
| `sigft/app_qt/widgets/espera.py` | `DialogosDeEspera` (`pausar_e_esperar`, `perguntar_retry_excel`) |
| `sigft/app_qt/widgets/module_frame.py` | `ModuleFrame` (cabeçalho, conteúdo, progresso, console) |
| `sigft/app_qt/catalogo.py` | MENU, MODULOS, TELAS_BLOQUEADAS, mensagens de fechar |
| `sigft/app_qt/views/__init__.py` | pacote |
| `sigft/app_qt/views/home.py` | `HomeView` |
| `sigft/app_qt/views/nao_migrada.py` | `TelaNaoMigrada` |
| `sigft/app_qt/main.py` | `SplashScreen`, `SIG_FT_App`, `main`, `executar_da_linha_de_comando` |
| `tests/test_qt_*.py` | um arquivo por unidade acima |

---

### Task 1: Dependências e ambiente de teste do Qt

**Files:**
- Modify: `requirements.txt` (depois da linha `customtkinter`)
- Modify: `requirements-dev.txt` (depois da linha `pytest`)
- Modify: `tests/conftest.py` (topo do arquivo, antes de qualquer import de projeto; e uma fixture nova no fim)
- Modify: `.github/workflows/ci.yml` (passos "setup-python" e "Instalar dependencias")
- Test: `tests/test_qt_ambiente.py`

**Interfaces:**
- Produces: fixture `qt_interface` (depende de `qapp` do pytest-qt; chama `sigft.app_qt.interface.instalar()` — criada na Task 4. Até lá a fixture só existe; nenhum teste a usa.)

- [ ] **Step 1: Escrever o teste que falha**

`tests/test_qt_ambiente.py`:
```python
"""O Qt roda na suíte sem display (QT_QPA_PLATFORM=offscreen)."""
import os

from PySide6.QtWidgets import QLabel


def test_plataforma_offscreen():
    assert os.environ.get("QT_QPA_PLATFORM") == "offscreen"


def test_widget_monta_sem_display(qtbot):
    rotulo = QLabel("SIG-FT")
    qtbot.addWidget(rotulo)
    rotulo.show()
    assert rotulo.text() == "SIG-FT"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_qt_ambiente.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'PySide6'` (ou fixture `qtbot` desconhecida).

- [ ] **Step 3: Dependências**

`requirements.txt`, logo abaixo de `customtkinter`:
```
# Interface Qt (migração em andamento: sigft/app_qt/). LGPL -- ver
# docs/superpowers/specs/2026-10-07-migracao-qt6-design.md, decisões.
PySide6
```

`requirements-dev.txt`, logo abaixo de `pytest`:
```
# Fixture `qtbot`: monta widgets Qt de verdade, sem display (offscreen).
pytest-qt
PySide6
```

Instalar: `pip install -r requirements-dev.txt`

- [ ] **Step 4: conftest**

No TOPO de `tests/conftest.py`, depois do docstring e antes do primeiro `import` de projeto:
```python
import os as _os_qt

# [Qt6] Sem display no CI e no contêiner: o Qt desenha em memória. Tem de vir
# antes de qualquer import do PySide6, e setdefault deixa quem quiser ver a
# janela (QT_QPA_PLATFORM=xcb) rodar com display de verdade.
_os_qt.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

No FIM de `tests/conftest.py`:
```python
@pytest.fixture
def qt_interface(qapp):
    """QApplication pronta e o canal thread -> interface instalado."""
    from sigft.app_qt import interface

    interface.instalar()
    return qapp
```
(Se `pytest` ainda não estiver importado no conftest, acrescentar `import pytest` junto aos imports.)

- [ ] **Step 5: Rodar e ver passar**

Run: `python -m pytest tests/test_qt_ambiente.py -q`
Expected: `2 passed`

- [ ] **Step 6: CI**

Em `.github/workflows/ci.yml`, trocar o passo `actions/setup-python@v5` por uma matriz e acrescentar as bibliotecas de sistema do Qt:
```yaml
    strategy:
      fail-fast: false
      matrix:
        # 3.10 e o minimo; 3.12 e o que a maioria instala hoje. O Qt e a
        # parte nova que mais depende de versao -- os dois ficam no portao.
        python: ["3.10", "3.12"]
```
(colocado em `jobs.testes`, no mesmo nível de `runs-on`), e no passo do setup:
```yaml
          python-version: ${{ matrix.python }}
```
Antes de "Instalar dependencias":
```yaml
      # O PySide6 precisa destas bibliotecas do sistema mesmo em modo
      # offscreen (sem elas: "libEGL.so.1: cannot open shared object file").
      - name: Bibliotecas do sistema para o Qt
        run: sudo apt-get update && sudo apt-get install -y libegl1 libxkbcommon0 libfontconfig1 libgl1
```

- [ ] **Step 7: Suíte inteira**

Run: `bash scripts/check.sh`
Expected: tudo verde (número de testes anterior + 2).

- [ ] **Step 8: Commit**

```bash
git add requirements.txt requirements-dev.txt tests/conftest.py tests/test_qt_ambiente.py .github/workflows/ci.yml
git commit -m "Qt6: PySide6 e pytest-qt no ambiente, CI em 3.10 e 3.12"
```

---

### Task 2: Conferência da versão mínima do Python

**Files:**
- Create: `sigft/core/python_minimo.py`
- Modify: `frontend.py` (logo depois do docstring e do `from __future__ import annotations`)
- Test: `tests/test_python_minimo.py`

**Interfaces:**
- Produces: `exigir_python_minimo(versao=None, sair=sys.exit, avisar=print) -> None`; constante `MINIMO = (3, 10)`; `MENSAGEM` (str com `{atual}`).

- [ ] **Step 1: Teste que falha**

`tests/test_python_minimo.py`:
```python
from sigft.core import python_minimo as pm


def test_versao_suficiente_nao_faz_nada():
    chamadas = []
    pm.exigir_python_minimo((3, 10, 0), sair=chamadas.append, avisar=chamadas.append)
    assert chamadas == []


def test_versao_antiga_avisa_e_sai_com_codigo_1():
    avisos, saidas = [], []
    pm.exigir_python_minimo((3, 9, 6), sair=saidas.append, avisar=avisos.append)
    assert saidas == [1]
    assert "3.9.6" in avisos[0] and "3.10" in avisos[0]


def test_arquivo_compila_em_sintaxe_antiga():
    # O modulo roda ANTES de saber se o Python serve: nada de `X | None`,
    # `match` ou walrus fora de string.
    import ast
    import inspect

    fonte = inspect.getsource(pm)
    ast.parse(fonte, feature_version=(3, 6))
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_python_minimo.py -q`
Expected: FAIL — `ImportError: cannot import name 'python_minimo'`

- [ ] **Step 3: Implementar**

`sigft/core/python_minimo.py`:
```python
"""Confere a versão do Python ANTES de qualquer import do SIG-FT.

Com Python 3.9 o app abria pela metade: três módulos falhavam na splash com
"unsupported operand type(s) for |" e a pessoa não tinha como saber que o
problema era a versão (aconteceu num Mac com o Python 3.9.6 que vem no sistema).

Este arquivo tem de compilar em Python antigo: sem `X | None`, sem `match`.
Há teste travando isso (`tests/test_python_minimo.py`).
"""
import sys

MINIMO = (3, 10)

MENSAGEM = (
    "O SIG-FT precisa do Python 3.10 ou mais novo, e este é o {atual}.\n"
    "Instale um Python novo em https://www.python.org/downloads/ "
    "(no Windows, marque \"Add python.exe to PATH\") e abra de novo."
)


def exigir_python_minimo(versao=None, sair=sys.exit, avisar=print):
    """Avisa e encerra com código 1 se o Python for menor que `MINIMO`."""
    if versao is None:
        versao = sys.version_info
    if tuple(versao[:2]) >= MINIMO:
        return
    atual = ".".join(str(parte) for parte in versao[:3])
    avisar(MENSAGEM.format(atual=atual))
    sair(1)
```

- [ ] **Step 4: Ligar no `frontend.py`**

Logo depois de `from __future__ import annotations` em `frontend.py`:
```python
# Antes de tudo: com Python antigo o app abria pela metade, com erro enigmático.
from sigft.core.python_minimo import exigir_python_minimo

exigir_python_minimo()
```

- [ ] **Step 5: Ver passar**

Run: `python -m pytest tests/test_python_minimo.py -q && bash scripts/check.sh`
Expected: `3 passed`; suíte verde.

- [ ] **Step 6: Commit**

```bash
git add sigft/core/python_minimo.py tests/test_python_minimo.py frontend.py
git commit -m "Conferir Python 3.10+ na abertura, com mensagem clara"
```

> Nota: o spec previa também `requires-python` no `pyproject.toml`. O arquivo não tem
> tabela `[project]` (só configura ruff/mypy), e criá-la exigiria `name` e `version`.
> Fica de fora; a conferência em tempo de execução é o que de fato protege.

---

### Task 3: Fontes e folha de estilo

**Files:**
- Create: `assets/fonts/Roboto-Regular.ttf`, `assets/fonts/Roboto-Medium.ttf`, `assets/fonts/LICENSE-Roboto.txt`
- Create: `assets/fonts/NotoEmoji-Regular.ttf`, `assets/fonts/OFL-NotoEmoji.txt`
- Create: `sigft/app_qt/__init__.py`, `sigft/app_qt/estilo.py`
- Test: `tests/test_qt_estilo.py`

**Interfaces:**
- Consumes: `sigft.app.theme` (`COLORS`, `COR_CARTAO`, `ALTURA_HEADER`, ...).
- Produces: `cinza_tk(nome: str) -> str`; `mono(texto: str) -> str`; `carregar_fontes() -> list[str]`; `folha_de_estilo() -> str`; `PASTA_FONTES: str`; constantes `ALTURA_BOTAO_MENU = 35`, `ESPACO_MENU = 4`, `ALTURA_BOTAO_BARRA = 40`.

- [ ] **Step 1: Copiar as fontes**

As Roboto são as MESMAS que o CustomTkinter usa hoje (vêm dentro do pacote dele):
```bash
mkdir -p assets/fonts
CTK=$(python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))")
cp "$CTK/assets/fonts/Roboto/Roboto-Regular.ttf" "$CTK/assets/fonts/Roboto/Roboto-Medium.ttf" assets/fonts/
curl -sSL -o assets/fonts/LICENSE-Roboto.txt https://www.apache.org/licenses/LICENSE-2.0.txt
```
Noto Emoji (monocromática) pelo Google Fonts — o CSS com user-agent antigo devolve o `.ttf`:
```bash
URL=$(curl -sS -A "Mozilla/4.0" "https://fonts.googleapis.com/css2?family=Noto+Emoji:wght@400" | grep -o 'https://[^)]*\.ttf')
curl -sSL -o assets/fonts/NotoEmoji-Regular.ttf "$URL"
curl -sSL -o assets/fonts/OFL-NotoEmoji.txt https://openfontlicense.org/documents/OFL.txt
file assets/fonts/*.ttf
```
Expected: os três `.ttf` reconhecidos como "TrueType Font data"; as duas licenças são texto (não HTML nem JSON — conferir com `head -3`).

- [ ] **Step 2: Teste que falha**

`tests/test_qt_estilo.py`:
```python
import os

from sigft.app import theme
from sigft.app_qt import estilo


def test_cinza_tk_converte_como_o_tk():
    assert estilo.cinza_tk("gray70") == "#B3B3B3"
    assert estilo.cinza_tk("gray30") == "#4D4D4D"
    assert estilo.cinza_tk("gray") == "#BEBEBE"
    assert estilo.cinza_tk("#123456") == "#123456"


def test_mono_pede_versao_texto_de_cada_emoji():
    assert estilo.mono("\U0001F4CB  Atividades") == "\U0001F4CB\ufe0e  Atividades"
    assert estilo.mono("Upload Condições – ok") == "Upload Condições – ok"


def test_fontes_existem_com_licenca():
    for nome in ("Roboto-Regular.ttf", "Roboto-Medium.ttf", "NotoEmoji-Regular.ttf",
                 "LICENSE-Roboto.txt", "OFL-NotoEmoji.txt"):
        assert os.path.isfile(os.path.join(estilo.PASTA_FONTES, nome)), nome


def test_carregar_fontes_registra_as_familias(qapp):
    familias = estilo.carregar_fontes()
    assert "Roboto" in familias and "Noto Emoji" in familias


def test_folha_usa_a_paleta_do_theme():
    qss = estilo.folha_de_estilo()
    for cor in (theme.COLORS["background"], theme.COLORS["sidebar"],
                theme.COLORS["accent"], theme.COR_CARTAO):
        assert cor in qss
    assert "gray" not in qss.replace("Roboto", "")  # nenhum cinza nomeado do Tk vazou
```

- [ ] **Step 3: Ver falhar**

Run: `python -m pytest tests/test_qt_estilo.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'sigft.app_qt'`

- [ ] **Step 4: Implementar**

`sigft/app_qt/__init__.py`:
```python
"""Interface Qt6 (PySide6) do SIG-FT — migração em andamento.

Convive com `sigft/app/` (CustomTkinter) até o corte. Desenho:
docs/superpowers/specs/2026-10-07-migracao-qt6-design.md.
"""
```

`sigft/app_qt/estilo.py`:
```python
"""A aparência do SIG-FT em Qt: a paleta de `theme.py` virando folha de estilo.

As CORES continuam morando em `sigft/app/theme.py` -- este módulo só as lê.
Duas paletas seria o jeito de as duas interfaces divergirem sem ninguém ver.
"""
from __future__ import annotations

import os
import re

from sigft.app import theme

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PASTA_FONTES = os.path.join(_RAIZ, "assets", "fonts")

ARQUIVOS_DE_FONTE = ("Roboto-Regular.ttf", "Roboto-Medium.ttf", "NotoEmoji-Regular.ttf")

# Medidas que o CustomTkinter aplica hoje (decisão: espaçamento igual ao atual).
ALTURA_BOTAO_MENU = 35
ESPACO_MENU = 4
ALTURA_BOTAO_BARRA = 40

_SELETOR_TEXTO = "\ufe0e"


def cinza_tk(nome: str) -> str:
    """`"grayNN"` do Tk em hexadecimal. O Qt não conhece esses nomes e pinta preto."""
    if nome in ("gray", "grey"):
        return "#BEBEBE"
    achado = re.fullmatch(r"gr[ae]y(\d{1,3})", nome)
    if not achado:
        return nome
    valor = round(255 * int(achado.group(1)) / 100)
    return f"#{valor:02X}{valor:02X}{valor:02X}"


def mono(texto: str) -> str:
    """Pede a versão PRETO E BRANCO de cada emoji (seletor U+FE0E).

    Só a fonte Noto Emoji não basta: sem o seletor, o Qt escolhe a fonte de
    emoji colorida do sistema (testado no protótipo de 2026-10-07).
    """
    saida = []
    for caractere in texto:
        saida.append(caractere)
        if ord(caractere) >= 0x1F000 or 0x2600 <= ord(caractere) <= 0x27BF:
            saida.append(_SELETOR_TEXTO)
    return "".join(saida)


def carregar_fontes() -> list[str]:
    """Registra Roboto e Noto Emoji no Qt. Chamar depois do QApplication.

    Devolve as famílias registradas. Fonte que falta não derruba o app: ele
    abre com a fonte padrão, que é feio, mas não é motivo para não abrir.
    """
    from PySide6.QtGui import QFont, QFontDatabase
    from PySide6.QtWidgets import QApplication

    familias: list[str] = []
    for nome in ARQUIVOS_DE_FONTE:
        indice = QFontDatabase.addApplicationFont(os.path.join(PASTA_FONTES, nome))
        if indice >= 0:
            familias.extend(QFontDatabase.applicationFontFamilies(indice))
    if "Noto Emoji" in familias:
        QFontDatabase.setApplicationEmojiFontFamilies(["Noto Emoji"])
    fonte = QFont()
    fonte.setFamilies(["Roboto", "Noto Emoji"])
    QApplication.setFont(fonte)
    return familias


def folha_de_estilo() -> str:
    """A folha QSS do app inteiro, montada a partir de `theme.py`."""
    c = theme.COLORS
    fam = '"Roboto", "Noto Emoji"'
    return f"""
QMainWindow, QDialog, #conteudo, #tela {{ background: {c['background']}; }}
QWidget {{ font-family: {fam}; color: {c['text_light']}; }}
#sidebar, #sidebar_interno {{ background: {c['sidebar']}; border: none; }}
#secao {{ color: {cinza_tk('gray50')}; font-size: 11px; font-weight: bold; padding-left: 10px; }}
#app_nome {{ color: {cinza_tk('gray60')}; font-size: 13px; }}
QPushButton {{ border-radius: 6px; color: {c['text_light']}; background: {c['primary']};
               border: none; padding: 0 14px; min-height: 28px; font-size: 13px; }}
QPushButton:hover {{ background: {c['primary_hover']}; }}
QPushButton:disabled {{ color: {cinza_tk('gray45')}; }}
QPushButton[menu="true"] {{ background: transparent; text-align: left; padding: 0 10px;
    min-height: {ALTURA_BOTAO_MENU}px; max-height: {ALTURA_BOTAO_MENU}px; font-size: 12px; }}
QPushButton[menu="true"]:hover {{ background: {c['primary']}; }}
#home {{ background: transparent; text-align: left; font-weight: bold;
         border: 1px solid {cinza_tk('gray30')}; }}
#home:hover {{ background: {c['primary']}; }}
QPushButton[barra="true"] {{ min-height: {ALTURA_BOTAO_BARRA}px; padding: 0 16px;
    font-weight: bold; color: {c['text_white']}; }}
QPushButton[variante="acento"] {{ background: {c['accent']}; }}
QPushButton[variante="acento"]:hover {{ background: {c['accent_hover']}; }}
QPushButton[variante="neutro"] {{ background: #3A3A3A; }}
QPushButton[variante="neutro"]:hover {{ background: #4A4A4A; }}
QPushButton[variante="perigo"] {{ background: {c['danger']}; }}
QPushButton[variante="contorno"] {{ background: transparent; border: 1px solid #555555;
    color: {cinza_tk('gray')}; }}
#titulo_home {{ font-size: 32px; font-weight: bold; }}
#subtitulo_home {{ font-size: 16px; color: {cinza_tk('gray70')}; }}
#texto_simples {{ font-size: 14px; }}
#titulo_modulo {{ font-size: 24px; font-weight: bold; color: {c['text_white']}; }}
#card {{ background: {theme.COR_CARTAO}; border: 1px solid #333333; border-radius: 8px; }}
#card:hover {{ border: 1px solid {c['accent']}; }}
#card_titulo {{ color: {c['accent']}; font-size: 15px; font-weight: bold; background: transparent; }}
#card_desc {{ color: {cinza_tk('gray70')}; font-size: 12px; background: transparent; }}
#console {{ background: #1D1E1E; border: 1px solid #333333; border-radius: 6px;
            font-family: "Consolas", "Menlo", monospace; font-size: 12px; }}
QCheckBox {{ font-size: 12px; }}
QCheckBox::indicator {{ width: 20px; height: 20px; border: 2px solid {cinza_tk('gray45')};
                        border-radius: 6px; background: transparent; }}
QCheckBox::indicator:checked {{ background: {c['primary']}; border-color: {c['primary']}; }}
QProgressBar {{ background: #333333; border: none; border-radius: 5px; max-height: 12px; }}
QProgressBar::chunk {{ background: {c['primary']}; border-radius: 5px; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 10px; }}
QScrollBar::handle:vertical {{ background: #4A4D50; border-radius: 5px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
"""
```

- [ ] **Step 5: Ver passar**

Run: `python -m pytest tests/test_qt_estilo.py -q`
Expected: `5 passed`

- [ ] **Step 6: Suíte e commit**

```bash
bash scripts/check.sh
git add assets/fonts sigft/app_qt/__init__.py sigft/app_qt/estilo.py tests/test_qt_estilo.py
git commit -m "Qt6: folha de estilo a partir do theme, fontes Roboto e Noto Emoji"
```

---

### Task 4: O canal thread -> interface

**Files:**
- Create: `sigft/app_qt/interface.py`
- Test: `tests/test_qt_interface.py`

**Interfaces:**
- Produces: `instalar() -> None` (idempotente; chamar na thread da interface depois do QApplication); `na_interface(func, *args) -> None` (qualquer thread; `RuntimeError` se `instalar()` não foi chamado); `na_thread_da_interface() -> bool`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_interface.py`:
```python
import threading

import pytest

from sigft.app_qt import interface


def test_funcao_roda_na_thread_da_interface(qt_interface, qtbot):
    vistas = []
    t = threading.Thread(target=lambda: interface.na_interface(
        lambda: vistas.append(threading.get_ident())))
    t.start()
    t.join()
    qtbot.waitUntil(lambda: len(vistas) == 1, timeout=2000)
    assert vistas == [threading.main_thread().ident]


def test_excecao_nao_derruba_o_canal(qt_interface, qtbot, capsys):
    ok = []
    interface.na_interface(lambda: 1 / 0)
    interface.na_interface(lambda: ok.append(True))
    qtbot.waitUntil(lambda: len(ok) == 1, timeout=2000)
    assert "ZeroDivisionError" in capsys.readouterr().err


def test_argumentos_sao_repassados(qt_interface, qtbot):
    recebido = []
    interface.na_interface(lambda a, b: recebido.append((a, b)), 1, "x")
    qtbot.waitUntil(lambda: len(recebido) == 1, timeout=2000)
    assert recebido == [(1, "x")]


def test_sabe_em_que_thread_esta(qt_interface):
    assert interface.na_thread_da_interface()
    fora = []
    t = threading.Thread(target=lambda: fora.append(interface.na_thread_da_interface()))
    t.start()
    t.join()
    assert fora == [False]


def test_sem_instalar_avisa(monkeypatch):
    monkeypatch.setattr(interface, "_ponte", None)
    with pytest.raises(RuntimeError, match="instalar"):
        interface.na_interface(print)
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_interface.py -q`
Expected: FAIL — `ImportError: cannot import name 'interface'`

- [ ] **Step 3: Implementar**

`sigft/app_qt/interface.py`:
```python
"""O ÚNICO caminho de uma thread até um widget.

No CustomTkinter isso era disciplina: `self.after(0, ...)` em cada lugar, e
onde alguém esqueceu, o widget era tocado fora da thread da interface -- no
macOS isso derruba o app (`cria_fichas.py` abria janela de dentro do robô).
Aqui é mecanismo: um sinal Qt com conexão em FILA entrega a função na thread
da interface, venha a chamada de onde vier.
"""
from __future__ import annotations

import threading
import traceback

from PySide6.QtCore import QObject, Qt, Signal, Slot


class _Ponte(QObject):
    executar = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.executar.connect(self._rodar, Qt.ConnectionType.QueuedConnection)

    @Slot(object)
    def _rodar(self, pacote) -> None:
        func, args = pacote
        try:
            func(*args)
        except Exception:  # noqa: BLE001 -- uma falha não pode matar o canal
            traceback.print_exc()


_ponte: _Ponte | None = None
_thread_da_interface: int | None = None


def instalar() -> None:
    """Cria a ponte na thread atual (a da interface). Chamar uma vez, cedo."""
    global _ponte, _thread_da_interface
    if _ponte is None:
        _ponte = _Ponte()
        _thread_da_interface = threading.get_ident()


def na_thread_da_interface() -> bool:
    return threading.get_ident() == _thread_da_interface


def na_interface(func, *args) -> None:
    """Agenda `func(*args)` na thread da interface. Chamável de qualquer thread."""
    if _ponte is None:
        raise RuntimeError("sigft.app_qt.interface.instalar() não foi chamado")
    _ponte.executar.emit((func, args))
```

- [ ] **Step 4: Ver passar e commit**

```bash
python -m pytest tests/test_qt_interface.py -q   # 5 passed
bash scripts/check.sh
git add sigft/app_qt/interface.py tests/test_qt_interface.py
git commit -m "Qt6: na_interface, o unico caminho de uma thread ate um widget"
```

---

### Task 5: Backend que não carregou deixa de ser silencioso

**Files:**
- Modify: `sigft/app/backends.py` (função `carregar_todos` e fim do arquivo)
- Test: `tests/test_backends_falhas.py`

**Interfaces:**
- Produces: `backends.falhas: dict[str, BaseException]` (chave = nome do módulo, ex. `"autospec_backend"`); `motivo_da_falha(nome: str) -> str | None`; `class BackendIndisponivel(RuntimeError)`; `exigir(nome: str)` -> devolve o objeto registrado ou levanta `BackendIndisponivel` com mensagem para a pessoa.

> Mudança num arquivo da interface atual, mas sem tkinter e só aditiva: a interface
> CustomTkinter continua funcionando igual. Vale para as duas.

- [ ] **Step 1: Teste que falha**

`tests/test_backends_falhas.py`:
```python
import pytest

from sigft.app import backends


@pytest.fixture(autouse=True)
def _limpa(monkeypatch):
    monkeypatch.setattr(backends, "falhas", {})


def test_falha_fica_registrada_com_o_motivo(monkeypatch):
    monkeypatch.setattr(backends, "MODULOS", [("modulo_que_nao_existe_x", "pdm_backend", None, "Teste")])
    monkeypatch.setattr(backends, "pdm_backend", None)
    backends.carregar_todos()
    assert "pdm_backend" in backends.falhas
    assert "modulo_que_nao_existe_x" in backends.motivo_da_falha("pdm_backend")


def test_exigir_explica_quando_nao_carregou(monkeypatch):
    monkeypatch.setattr(backends, "autospec_backend", None)
    backends.falhas["autospec_backend"] = TypeError("unsupported operand type(s) for |")
    with pytest.raises(backends.BackendIndisponivel) as erro:
        backends.exigir("autospec_backend")
    texto = str(erro.value)
    assert "não carregou" in texto and "unsupported operand" in texto and "sigft.log" in texto


def test_exigir_devolve_o_modulo_carregado(monkeypatch):
    sentinela = object()
    monkeypatch.setattr(backends, "lmr_backend", sentinela)
    assert backends.exigir("lmr_backend") is sentinela


def test_exigir_sem_falha_registrada_ainda_explica(monkeypatch):
    monkeypatch.setattr(backends, "lmr_backend", None)
    with pytest.raises(backends.BackendIndisponivel, match="ainda não foi carregado"):
        backends.exigir("lmr_backend")
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_backends_falhas.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'falhas'`

- [ ] **Step 3: Implementar**

Em `sigft/app/backends.py`, logo antes de `MODULOS = [`:
```python
# [Qt6] O motivo de cada backend que não carregou, por nome de destino
# ("pdm_backend", "mixed_classes"...). Antes a falha só ia para o console da
# splash, e a tela quebrava depois com `AttributeError: 'NoneType'`.
falhas: dict[str, BaseException] = {}


class BackendIndisponivel(RuntimeError):
    """O backend que a tela pediu não carregou. A mensagem é para a pessoa."""
```

Dentro de `carregar_todos`, no `except Exception as erro:` existente, ANTES de chamar `ao_falhar`:
```python
            falhas[destino] = erro
```

No fim do arquivo:
```python
def motivo_da_falha(nome: str) -> str | None:
    erro = falhas.get(nome)
    return None if erro is None else f"{type(erro).__name__}: {erro}"


def exigir(nome: str):
    """O backend `nome`, ou `BackendIndisponivel` com o motivo em português."""
    objeto = globals().get(nome)
    if objeto is not None:
        return objeto
    motivo = motivo_da_falha(nome)
    if motivo is None:
        raise BackendIndisponivel(
            f"O módulo '{nome}' ainda não foi carregado. Espere a abertura terminar.")
    raise BackendIndisponivel(
        f"Este módulo não carregou: {motivo}\n\n"
        "O detalhe está em Documentos\\SIG-FT\\logs\\sigft.log.")
```

- [ ] **Step 4: Ver passar e commit**

```bash
python -m pytest tests/test_backends_falhas.py tests/test_app_backends.py -q
bash scripts/check.sh
git add sigft/app/backends.py tests/test_backends_falhas.py
git commit -m "Backends: guardar o motivo da falha e exigir() com mensagem clara"
```

---

### Task 6: Console

**Files:**
- Create: `sigft/app_qt/widgets/__init__.py`, `sigft/app_qt/widgets/console.py`
- Test: `tests/test_qt_console.py`

**Interfaces:**
- Consumes: `interface.na_interface`.
- Produces: `ConsoleFrame(parent=None, *, altura: int | None = theme.ALTURA_CONSOLE)` com `.log(msg, nivel="info", contexto=None)`; `formatar_linha(msg) -> str` (sem `\n`); `PREFIXO_LINHA = "> "`; `INTERVALO_MS = 50`; `MAX_LINHAS = 20_000`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_console.py`:
```python
import ast
import threading

from sigft.app_qt.widgets import console as qconsole


def test_prefixo_igual_ao_da_interface_atual():
    arvore = ast.parse(open("sigft/app/widgets/console.py", encoding="utf-8").read())
    atual = next(n.value.value for n in arvore.body
                 if isinstance(n, ast.Assign) and n.targets[0].id == "PREFIXO_LINHA")
    assert qconsole.PREFIXO_LINHA == atual


def test_linhas_de_thread_chegam_em_ordem(qt_interface, qtbot):
    c = qconsole.ConsoleFrame()
    qtbot.addWidget(c)

    def worker():
        for i in range(500):
            c.log(f"linha {i}")

    t = threading.Thread(target=worker)
    t.start()
    t.join()
    qtbot.waitUntil(lambda: c.blockCount() >= 500, timeout=3000)
    linhas = c.toPlainText().splitlines()
    assert linhas[0] == "> linha 0" and linhas[-1] == "> linha 499" and len(linhas) == 500


def test_aceita_qualquer_objeto(qt_interface, qtbot):
    c = qconsole.ConsoleFrame()
    qtbot.addWidget(c)
    c.log(ValueError("x"))
    c.log(42)
    qtbot.waitUntil(lambda: c.blockCount() >= 2, timeout=2000)
    assert c.toPlainText().splitlines() == ["> x", "> 42"]


def test_somente_leitura_e_altura(qt_interface, qtbot):
    c = qconsole.ConsoleFrame(altura=120)
    qtbot.addWidget(c)
    assert c.isReadOnly() and c.height() == 120
    livre = qconsole.ConsoleFrame(altura=None)
    qtbot.addWidget(livre)
    assert livre.maximumHeight() > 120


def test_widget_destruido_nao_derruba_o_worker(qt_interface, qtbot):
    c = qconsole.ConsoleFrame()
    c.log("antes")
    c.deleteLater()
    qtbot.wait(100)
    c.log("depois")  # não pode levantar
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_console.py -q` → FAIL (`ModuleNotFoundError`)

- [ ] **Step 3: Implementar**

`sigft/app_qt/widgets/__init__.py`:
```python
"""Widgets reutilizáveis da interface Qt (um por responsabilidade)."""
```

`sigft/app_qt/widgets/console.py`:
```python
"""Console de log das telas, rápido e seguro para chamar de qualquer thread.

O `CTkTextbox` reescrevia e rolava a cada linha; num lote de milhares de linhas
isso pesava. Aqui as linhas que chegam são juntadas e escritas em LOTE a cada
`INTERVALO_MS` (medido no protótipo: 10.000 linhas em ~0,1 s), e o console
guarda no máximo `MAX_LINHAS` -- as mais antigas saem.
"""
from __future__ import annotations

import threading
from collections import deque

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPlainTextEdit

from sigft.app import theme
from sigft.app_qt import interface

PREFIXO_LINHA = "> "
INTERVALO_MS = 50
MAX_LINHAS = 20_000


def formatar_linha(msg: object) -> str:
    """A linha como as telas escrevem: ``"> {msg}"``. Aceita qualquer objeto."""
    return f"{PREFIXO_LINHA}{msg}"


class ConsoleFrame(QPlainTextEdit):
    def __init__(self, parent=None, *, altura: int | None = theme.ALTURA_CONSOLE) -> None:
        super().__init__(parent)
        self.setObjectName("console")
        self.setReadOnly(True)
        self.setMaximumBlockCount(MAX_LINHAS)
        if altura is not None:
            self.setFixedHeight(altura)
        self._pendentes: deque[str] = deque()
        self._trava = threading.Lock()
        self._agendado = False

    def log(self, msg: object, nivel: str = "info", contexto: object | None = None) -> None:
        """Assinatura do protocolo `core/callbacks.py`. Qualquer thread."""
        with self._trava:
            self._pendentes.append(formatar_linha(msg))
            if self._agendado:
                return
            self._agendado = True
        try:
            interface.na_interface(self._agendar)
        except RuntimeError:
            pass  # app fechando: perder a linha é o certo, derrubar o worker não

    def _agendar(self) -> None:
        try:
            QTimer.singleShot(INTERVALO_MS, self._descarregar)
        except RuntimeError:
            pass  # widget destruído

    def _descarregar(self) -> None:
        with self._trava:
            linhas = list(self._pendentes)
            self._pendentes.clear()
            self._agendado = False
        if not linhas:
            return
        try:
            self.appendPlainText("\n".join(linhas))
            barra = self.verticalScrollBar()
            barra.setValue(barra.maximum())
        except RuntimeError:
            pass  # widget destruído entre o agendamento e a escrita
```

- [ ] **Step 4: Ver passar e commit**

```bash
python -m pytest tests/test_qt_console.py -q   # 5 passed
bash scripts/check.sh
git add sigft/app_qt/widgets tests/test_qt_console.py
git commit -m "Qt6: console com escrita em lote e limite de linhas"
```

---

### Task 7: Diálogos de espera (login e Excel bloqueado)

**Files:**
- Create: `sigft/app_qt/widgets/dialogs.py`, `sigft/app_qt/widgets/espera.py`
- Test: `tests/test_qt_espera.py`

**Interfaces:**
- Consumes: `interface.na_interface`, `interface.na_thread_da_interface`; textos `MSG_EXCEL_BLOQUEADO`, `TEXTO_CONTINUAR`, `msg_excel_bloqueado` de `sigft.app.widgets.dialogs`.
- Produces: `PausaLoginDialog(parent, *, mensagem, evento_espera, texto_botao=TEXTO_CONTINUAR)` com `.botao` e `.liberar()`; `RetryLockDialog(parent, *, mensagem=MSG_EXCEL_BLOQUEADO, evento_espera, resultado: dict)` com `.botao_repetir`, `.botao_cancelar`, `.repetir()`, `.cancelar()`; mixin `DialogosDeEspera` com `pausar_e_esperar(mensagem, texto_botao=TEXTO_CONTINUAR) -> None` e `perguntar_retry_excel(caminho=None) -> bool`.

> Os TEXTOS continuam vindo de `sigft/app/widgets/dialogs.py` (são texto, não widget).
> Esse import puxa o `customtkinter`, que segue instalado até o corte; no corte os
> textos mudam para um módulo puro (plano da Etapa 6).

- [ ] **Step 1: Teste que falha**

`tests/test_qt_espera.py`:
```python
import threading

from PySide6.QtWidgets import QWidget

from sigft.app_qt.widgets import dialogs as qd
from sigft.app_qt.widgets.espera import DialogosDeEspera


class Tela(DialogosDeEspera, QWidget):
    pass


def _abertos(tipo):
    from PySide6.QtWidgets import QApplication
    return [w for w in QApplication.topLevelWidgets() if isinstance(w, tipo) and w.isVisible()]


def test_worker_espera_o_login_e_e_solto(qt_interface, qtbot):
    tela = Tela()
    qtbot.addWidget(tela)
    terminou = []
    t = threading.Thread(target=lambda: (tela.pausar_e_esperar("Faça login"), terminou.append(True)))
    t.start()
    qtbot.waitUntil(lambda: len(_abertos(qd.PausaLoginDialog)) == 1, timeout=2000)
    assert terminou == []
    _abertos(qd.PausaLoginDialog)[0].botao.click()
    t.join(3)
    assert terminou == [True]


def test_fechar_no_x_tambem_solta_o_worker(qt_interface, qtbot):
    tela = Tela()
    qtbot.addWidget(tela)
    terminou = []
    t = threading.Thread(target=lambda: (tela.pausar_e_esperar("x"), terminou.append(True)))
    t.start()
    qtbot.waitUntil(lambda: len(_abertos(qd.PausaLoginDialog)) == 1, timeout=2000)
    _abertos(qd.PausaLoginDialog)[0].close()
    t.join(3)
    assert terminou == [True]


def test_retry_excel_devolve_a_escolha(qt_interface, qtbot):
    tela = Tela()
    qtbot.addWidget(tela)
    respostas = []
    t = threading.Thread(target=lambda: respostas.append(tela.perguntar_retry_excel("C:/a.xlsx")))
    t.start()
    qtbot.waitUntil(lambda: len(_abertos(qd.RetryLockDialog)) == 1, timeout=2000)
    dialogo = _abertos(qd.RetryLockDialog)[0]
    assert "a.xlsx" in dialogo.rotulo.text()
    dialogo.botao_repetir.click()
    t.join(3)
    assert respostas == [True]


def test_retry_excel_fechar_no_x_e_cancelar(qt_interface, qtbot):
    tela = Tela()
    qtbot.addWidget(tela)
    respostas = []
    t = threading.Thread(target=lambda: respostas.append(tela.perguntar_retry_excel()))
    t.start()
    qtbot.waitUntil(lambda: len(_abertos(qd.RetryLockDialog)) == 1, timeout=2000)
    _abertos(qd.RetryLockDialog)[0].close()
    t.join(3)
    assert respostas == [False]


def test_janela_nasce_na_thread_da_interface(qt_interface, qtbot):
    tela = Tela()
    qtbot.addWidget(tela)
    t = threading.Thread(target=lambda: tela.pausar_e_esperar("x"))
    t.start()
    qtbot.waitUntil(lambda: len(_abertos(qd.PausaLoginDialog)) == 1, timeout=2000)
    dialogo = _abertos(qd.PausaLoginDialog)[0]
    assert dialogo.thread() is tela.thread()
    dialogo.botao.click()
    t.join(3)
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_espera.py -q` → FAIL (`ImportError`)

- [ ] **Step 3: Implementar os diálogos**

`sigft/app_qt/widgets/dialogs.py`:
```python
"""Janelas que param o robô à espera da pessoa. Mesmos textos de hoje.

Regra que não pode ser esquecida: fechar no "X" SEMPRE solta o worker, com a
resposta mais segura (continuar o login; não repetir a gravação). Sem isso, a
thread do robô fica presa em `Event.wait()` para sempre.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from sigft.app.widgets.dialogs import MSG_EXCEL_BLOQUEADO, TEXTO_CONTINUAR


class _DialogoDeAcaoManual(QDialog):
    def __init__(self, parent, *, titulo: str, mensagem: str, largura: int, altura: int) -> None:
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setFixedSize(largura, altura)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._decidido = False
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)
        self.rotulo = QLabel(mensagem)
        self.rotulo.setWordWrap(True)
        self.rotulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rotulo.setStyleSheet("font-size: 13px;")
        self.layout_principal.addWidget(self.rotulo, 1)

    def _ao_fechar_sem_decidir(self) -> None:
        raise NotImplementedError

    def closeEvent(self, evento) -> None:  # noqa: N802 -- nome do Qt
        if not self._decidido:
            self._ao_fechar_sem_decidir()
        super().closeEvent(evento)


class PausaLoginDialog(_DialogoDeAcaoManual):
    """"Ação Manual Necessária" com um botão: continuar a automação."""

    def __init__(self, parent, *, mensagem: str, evento_espera, texto_botao: str = TEXTO_CONTINUAR) -> None:
        super().__init__(parent, titulo="Ação Manual Necessária", mensagem=mensagem,
                         largura=450, altura=250)
        self._evento = evento_espera
        self.botao = QPushButton(texto_botao)
        self.botao.setMinimumHeight(45)
        self.botao.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.botao.clicked.connect(self.liberar)
        self.layout_principal.addWidget(self.botao, 0, Qt.AlignmentFlag.AlignHCenter)

    def liberar(self) -> None:
        self._decidido = True
        self._evento.set()
        self.accept()

    def _ao_fechar_sem_decidir(self) -> None:
        self._decidido = True
        self._evento.set()


class RetryLockDialog(_DialogoDeAcaoManual):
    """"Arquivo Bloqueado": Tentar Novamente × Ignorar e Continuar (chave "retry")."""

    def __init__(self, parent, *, mensagem: str = MSG_EXCEL_BLOQUEADO, evento_espera, resultado: dict) -> None:
        super().__init__(parent, titulo="Arquivo Bloqueado", mensagem=mensagem,
                         largura=450, altura=200)
        self._evento = evento_espera
        self._resultado = resultado
        linha = QHBoxLayout()
        self.botao_repetir = QPushButton("Tentar Novamente")
        self.botao_cancelar = QPushButton("Ignorar e Continuar")
        self.botao_cancelar.setProperty("variante", "contorno")
        for botao in (self.botao_repetir, self.botao_cancelar):
            botao.setFixedSize(150, 40)
            linha.addWidget(botao)
        self.botao_repetir.clicked.connect(self.repetir)
        self.botao_cancelar.clicked.connect(self.cancelar)
        self.layout_principal.addLayout(linha)

    def _responder(self, repetir: bool) -> None:
        self._decidido = True
        self._resultado["retry"] = repetir
        self._evento.set()

    def repetir(self) -> None:
        self._responder(True)
        self.accept()

    def cancelar(self) -> None:
        self._responder(False)
        self.reject()

    def _ao_fechar_sem_decidir(self) -> None:
        self._responder(False)
```

- [ ] **Step 4: Implementar o mixin**

`sigft/app_qt/widgets/espera.py`:
```python
"""`pausar_e_esperar` e `perguntar_retry_excel` para as telas Qt.

Mesma API e mesma regra da versão CustomTkinter:
* chamado de um worker: a janela nasce na thread da interface (`na_interface`)
  e o worker espera num `threading.Event`;
* chamado da própria thread da interface: `exec()`, que bloqueia SEM parar o
  laço de eventos -- `Event.wait()` ali congelaria o app.
"""
from __future__ import annotations

import threading

from sigft.app.widgets.dialogs import MSG_EXCEL_BLOQUEADO, TEXTO_CONTINUAR, msg_excel_bloqueado
from sigft.app_qt import interface
from sigft.app_qt.widgets import dialogs


class DialogosDeEspera:
    def _abrir_e_esperar(self, construir_dialogo) -> dict:
        evento = threading.Event()
        resultado: dict = {}
        if interface.na_thread_da_interface():
            dialogo = construir_dialogo(evento, resultado)
            dialogo.exec()
            return resultado

        def abrir() -> None:
            dialogo = construir_dialogo(evento, resultado)
            self._dialogo_aberto = dialogo  # segura a referência enquanto está aberto
            dialogo.show()

        interface.na_interface(abrir)
        evento.wait()
        return resultado

    def pausar_e_esperar(self, mensagem: str, texto_botao: str = TEXTO_CONTINUAR) -> None:
        self._abrir_e_esperar(lambda evento, _res: dialogs.PausaLoginDialog(
            self, mensagem=mensagem, evento_espera=evento, texto_botao=texto_botao))

    def perguntar_retry_excel(self, caminho: object = None) -> bool:
        mensagem = msg_excel_bloqueado(caminho) if caminho is not None else MSG_EXCEL_BLOQUEADO
        resultado = self._abrir_e_esperar(lambda evento, res: dialogs.RetryLockDialog(
            self, mensagem=mensagem, evento_espera=evento, resultado=res))
        return bool(resultado.get("retry", False))
```

- [ ] **Step 5: Ver passar e commit**

```bash
python -m pytest tests/test_qt_espera.py -q   # 5 passed
bash scripts/check.sh
git add sigft/app_qt/widgets/dialogs.py sigft/app_qt/widgets/espera.py tests/test_qt_espera.py
git commit -m "Qt6: dialogos de espera (login e Excel bloqueado) sempre na thread da interface"
```

> `perguntar_arquivos_travados` (Gestão PMIB) entra no plano da etapa que migra
> o PMIBManager, junto com o `ArquivosTravadosDialog` — é a única tela que o usa.

---

### Task 8: Esqueleto de tela (`ModuleFrame`)

**Files:**
- Create: `sigft/app_qt/widgets/module_frame.py`
- Test: `tests/test_qt_module_frame.py`

**Interfaces:**
- Consumes: `ConsoleFrame`, `DialogosDeEspera`, `backends.exigir`, `backends.BackendIndisponivel`.
- Produces: `ModuleFrame(parent=None, controller=None, *, titulo, cor_titulo=None, peso_conteudo=1, altura_console=theme.ALTURA_CONSOLE, com_progresso=False, construir=True, embutida=False, console_externo=None)`; atributos `.controller`, `.header`, `.label_titulo`, `.content` (QWidget com `QVBoxLayout` em `.content_layout`), `.progress_bar` (`QProgressBar` 0..1000 ou `None`), `.console`; métodos `_build_ui()` (abstrato), `log(msg, nivel="info", contexto=None)`, `backend(nome) -> objeto | None` (mostra o motivo no console e numa caixa quando falta), `iniciar_tarefa(alvo, *args, botao=None) -> threading.Thread`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_module_frame.py`:
```python
import threading

import pytest

from sigft.app import backends
from sigft.app_qt.widgets.module_frame import ModuleFrame


class Tela(ModuleFrame):
    def _build_ui(self):
        self.construida = True


def test_monta_cabecalho_conteudo_console(qt_interface, qtbot):
    t = Tela(titulo="Tradutor Técnico")
    qtbot.addWidget(t)
    assert t.construida and t.label_titulo.text() == "Tradutor Técnico"
    assert t.progress_bar is None and t.console is not None


def test_com_progresso(qt_interface, qtbot):
    t = Tela(titulo="x", com_progresso=True)
    qtbot.addWidget(t)
    assert t.progress_bar.maximum() == 1000


def test_embutida_usa_console_do_pai(qt_interface, qtbot):
    pai = Tela(titulo="pai")
    qtbot.addWidget(pai)
    filha = Tela(titulo="filha", embutida=True, console_externo=pai.console)
    qtbot.addWidget(filha)
    assert filha.header is None and filha.console is pai.console


def test_backend_que_falhou_vira_aviso_e_nao_excecao(qt_interface, qtbot, monkeypatch):
    monkeypatch.setattr(backends, "lmr_backend", None)
    monkeypatch.setattr(backends, "falhas", {"lmr_backend": ImportError("sem xlwings")})
    avisos = []
    monkeypatch.setattr("sigft.app_qt.widgets.module_frame.QMessageBox.warning",
                        lambda *a, **k: avisos.append(a[2]))
    t = Tela(titulo="x")
    qtbot.addWidget(t)
    assert t.backend("lmr_backend") is None
    assert "sem xlwings" in avisos[0]
    qtbot.waitUntil(lambda: "sem xlwings" in t.console.toPlainText(), timeout=2000)


def test_tarefa_desabilita_o_botao_no_clique_e_reabilita_no_fim(qt_interface, qtbot):
    from PySide6.QtWidgets import QPushButton
    t = Tela(titulo="x")
    qtbot.addWidget(t)
    botao = QPushButton("Rodar")
    qtbot.addWidget(botao)
    liberar = threading.Event()
    thread = t.iniciar_tarefa(liberar.wait, 5, botao=botao)
    assert not botao.isEnabled()          # desabilitado ANTES de a thread rodar
    assert not thread.daemon              # tarefa da pessoa: o "X" pergunta antes
    liberar.set()
    thread.join(3)
    qtbot.waitUntil(botao.isEnabled, timeout=2000)


def test_excecao_no_worker_vai_para_o_console_e_solta_o_botao(qt_interface, qtbot):
    from PySide6.QtWidgets import QPushButton
    t = Tela(titulo="x")
    qtbot.addWidget(t)
    botao = QPushButton("Rodar")
    qtbot.addWidget(botao)
    thread = t.iniciar_tarefa(lambda: 1 / 0, botao=botao)
    thread.join(3)
    qtbot.waitUntil(lambda: "ZeroDivisionError" in t.console.toPlainText(), timeout=2000)
    qtbot.waitUntil(botao.isEnabled, timeout=2000)
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_module_frame.py -q` → FAIL (`ModuleNotFoundError`)

- [ ] **Step 3: Implementar**

`sigft/app_qt/widgets/module_frame.py`:
```python
"""O esqueleto de uma tela: cabeçalho + conteúdo + (progresso) + console.

Mesma ideia e mesmos parâmetros do `ModuleFrame` CustomTkinter, mais duas
coisas que lá eram disciplina e aqui são mecanismo:

* `backend(nome)`: um backend que não carregou vira aviso com o motivo, nunca
  `AttributeError: 'NoneType'` (defeito 3 da revisão de 2026-10-07);
* `iniciar_tarefa(...)`: desabilita o botão NO CLIQUE (dois cliques não sobem
  dois robôs -- defeito 5), roda numa thread comum (o "X" pergunta antes de
  fechar) e, aconteça o que acontecer, devolve o botão e loga a exceção.
"""
from __future__ import annotations

import threading
import traceback

from PySide6.QtWidgets import (
    QLabel, QMessageBox, QProgressBar, QScrollArea, QVBoxLayout, QWidget,
)

from sigft.app import backends, theme
from sigft.app_qt import interface
from sigft.app_qt.widgets.console import ConsoleFrame
from sigft.app_qt.widgets.espera import DialogosDeEspera


class ModuleFrame(DialogosDeEspera, QWidget):
    def __init__(
        self,
        parent=None,
        controller=None,
        *,
        titulo: str,
        cor_titulo: str | None = None,
        peso_conteudo: int = 1,
        altura_console: int | None = theme.ALTURA_CONSOLE,
        com_progresso: bool = False,
        construir: bool = True,
        embutida: bool = False,
        console_externo=None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("tela")
        self.controller = controller
        self.embutida = embutida
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(theme.PADDING_X, theme.PADDING_Y, theme.PADDING_X, theme.PADDING_Y)
        raiz.setSpacing(theme.PADDING_Y)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        if embutida:
            # Dentro da aba de outra tela: sem cabeçalho nem console próprios, e
            # ROLÁVEL -- numa aba sobra menos altura, e o que não cabe sumiria.
            self.header = None
            self.label_titulo = None
            self.progress_bar = None
            self.console = console_externo
            rolagem = QScrollArea()
            rolagem.setWidgetResizable(True)
            rolagem.setWidget(self.content)
            raiz.setContentsMargins(0, 0, 0, 0)
            raiz.addWidget(rolagem)
        else:
            self.header = QWidget()
            linha_header = QVBoxLayout(self.header)
            linha_header.setContentsMargins(0, 0, 0, 0)
            self.label_titulo = QLabel(titulo, objectName="titulo_modulo")
            if cor_titulo:
                self.label_titulo.setStyleSheet(f"color: {cor_titulo};")
            linha_header.addWidget(self.label_titulo)
            self.header.setFixedHeight(theme.ALTURA_HEADER)
            raiz.addWidget(self.header)
            raiz.addWidget(self.content, peso_conteudo)
            self.progress_bar = None
            if com_progresso:
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 1000)
                self.progress_bar.setTextVisible(False)
                raiz.addWidget(self.progress_bar)
            self.console = ConsoleFrame(altura=altura_console)
            raiz.addWidget(self.console, 0 if altura_console is not None else 1)

        if construir:
            self._build_ui()

    def _build_ui(self) -> None:
        raise NotImplementedError(f"{type(self).__name__} precisa implementar _build_ui().")

    def log(self, msg: object, nivel: str = "info", contexto: object | None = None) -> None:
        if self.console is not None:
            self.console.log(msg, nivel, contexto)

    def backend(self, nome: str):
        """O backend `nome`, ou `None` depois de avisar a pessoa do porquê."""
        try:
            return backends.exigir(nome)
        except backends.BackendIndisponivel as erro:
            self.log(f"[ERRO] {erro}")
            QMessageBox.warning(self, "Módulo indisponível", str(erro))
            return None

    def iniciar_tarefa(self, alvo, *args, botao=None) -> threading.Thread:
        """Roda `alvo(*args)` numa thread comum. Chamar da thread da interface."""
        if botao is not None:
            botao.setEnabled(False)

        def rodar() -> None:
            try:
                alvo(*args)
            except Exception as erro:  # noqa: BLE001 -- vira log, e o botão volta
                self.log(f"[ERRO] {type(erro).__name__}: {erro}")
                traceback.print_exc()
            finally:
                if botao is not None:
                    interface.na_interface(botao.setEnabled, True)

        thread = threading.Thread(target=rodar, name=f"tarefa:{type(self).__name__}")
        thread.start()
        return thread
```

- [ ] **Step 4: Ver passar e commit**

```bash
python -m pytest tests/test_qt_module_frame.py -q   # 6 passed
bash scripts/check.sh
git add sigft/app_qt/widgets/module_frame.py tests/test_qt_module_frame.py
git commit -m "Qt6: ModuleFrame com backend() que avisa e iniciar_tarefa() que trava o botao no clique"
```

---

### Task 9: Catálogo (menu, módulos, telas bloqueadas)

**Files:**
- Create: `sigft/app_qt/catalogo.py`
- Test: `tests/test_qt_catalogo.py`

**Interfaces:**
- Produces: `MENU: list[tuple]` — itens `("secao", texto)` ou `("botao", texto, nome_da_tela)`, na ordem visual; `MODULOS: list[tuple[str, str, str]]` (alvo, título, descrição); `TELAS_BLOQUEADAS: frozenset[str]`; `MSG_TAREFA_EM_ANDAMENTO: str`; `MSG_ABERTURA_FALHOU: str` (com `{erro}`).

> Cópia dos dados que hoje moram em módulos que importam `customtkinter`. O teste
> lê os originais por AST e falha se divergirem — até o corte, quando os originais saem.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_catalogo.py`:
```python
import ast

from sigft.app_qt import catalogo


def _valor(caminho, nome):
    arvore = ast.parse(open(caminho, encoding="utf-8").read())
    for no in arvore.body:
        if isinstance(no, ast.Assign) and getattr(no.targets[0], "id", None) == nome:
            return ast.literal_eval(no.value)
    raise AssertionError(f"{nome} não achado em {caminho}")


def test_modulos_iguais_aos_da_home_atual():
    assert catalogo.MODULOS == _valor("sigft/app/views/home.py", "MODULOS")


def test_bloqueadas_iguais():
    assert catalogo.TELAS_BLOQUEADAS == frozenset(_valor("sigft/app/main.py", "TELAS_BLOQUEADAS"))


def test_mensagens_iguais():
    assert catalogo.MSG_TAREFA_EM_ANDAMENTO == _valor("sigft/app/main.py", "MSG_TAREFA_EM_ANDAMENTO")
    assert catalogo.MSG_ABERTURA_FALHOU == _valor("sigft/app/main.py", "MSG_ABERTURA_FALHOU")


def test_menu_tem_as_telas_dos_cards_e_na_ordem_da_barra():
    telas_menu = [item[2] for item in catalogo.MENU if item[0] == "botao"]
    assert telas_menu == ["CriaFichas", "PDM", "Analyzer", "UploadConditions", "Translator",
                          "UploadSpecs", "CorrecaoPDM", "CopiaFichas", "AutoSpec", "LMR",
                          "PMIBManager", "SearchPMIB"]
    assert {m[0] for m in catalogo.MODULOS} == set(telas_menu)
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_catalogo.py -q` → FAIL

- [ ] **Step 3: Implementar**

`sigft/app_qt/catalogo.py` (o menu segue a ordem de `SIG_FT_App.__init__` em `sigft/app/main.py`; o resto é cópia literal dos originais):
```python
"""Os dados da navegação, sem widget nenhum.

Até o corte, cópia do que mora em `sigft/app/views/home.py` e
`sigft/app/main.py` (módulos que importam o customtkinter). O teste
`tests/test_qt_catalogo.py` compara por AST e falha se alguém mudar um lado só.
"""
from __future__ import annotations

MENU = [
    ("secao", "Início da Ficha"),
    ("botao", "1. Cria Fichas PMIB", "CriaFichas"),
    ("botao", "2. Planilhas PMIB", "PDM"),
    ("botao", "3. Analyzer (IA)", "Analyzer"),
    ("secao", "Dados Técnicos & Upload"),
    ("botao", "4.1. Upload Condições", "UploadConditions"),
    ("botao", "4.2. Tradutor", "Translator"),
    ("botao", "4.3. Upload Specs", "UploadSpecs"),
    ("botao", "4.4. Correção de PDM", "CorrecaoPDM"),
    ("botao", "5. Upload duplicadas", "CopiaFichas"),
    ("botao", "6. AutoSpec AI (RAG)", "AutoSpec"),
    ("botao", "7. Aplicação LMR", "LMR"),
    ("secao", "Gestão"),
    ("botao", "8. PMIB Manager", "PMIBManager"),
    ("botao", "9. Search", "SearchPMIB"),
]

MODULOS = [
    ("CriaFichas", "Cria Fichas PMIB",
     "Lê a lista de materiais, escolhe o PDM de cada item com IA e cria as "
     "fichas no portal. Tem também a edição do código de projeto em massa."),
    ("PDM", "Planilhas PMIB",
     "Fatia a lista geral de PDMs da Itaipu por sistema, aplica o template das "
     "fichas e organiza as pastas de trabalho."),
    ("Analyzer", "Analyzer (IA)",
     "Dá nota às fichas preenchidas e separa as que passam das que voltam para "
     "correção. Gera o relatório de pendências para mandar ao fornecedor."),
    ("UploadConditions", "Upload de Condições",
     "Preenche no portal as condições de armazenamento, transporte, manutenção "
     "e descarte, a partir da ficha, com a tradução para o espanhol."),
    ("UploadSpecs", "Upload de Características",
     "Preenche as características técnicas da ficha no portal, uma linha por "
     "especificação."),
    ("CorrecaoPDM", "Correção de PDM",
     "Troca ou atualiza o PDM das fichas no portal sem perder as "
     "características: fotografa antes, repõe o que o PDM novo também tem, e "
     "lista o que não voltou."),
    ("Translator", "Tradutor Técnico",
     "Traduz as características das fichas de português para espanhol, no "
     "próprio computador, e grava numa aba nova da própria planilha."),
    ("CopiaFichas", "Fichas Duplicadas",
     "Copia uma ficha existente do portal para outra: campos, condições, "
     "características, PDM, documentos e imagens."),
    ("AutoSpec", "AutoSpec AI (RAG)",
     "Preenche ficha vazia lendo manuais em PDF e buscando datasheets na web, "
     "com conferência dos documentos duvidosos."),
    ("LMR", "Aplicação LMR",
     "Cadastra as aplicações (TAGs) das fichas no portal, e apaga quando "
     "preciso. As duas coisas ficam em abas da mesma seção."),
    ("PMIBManager", "PMIB Manager",
     "Atualiza o mapeamento a partir do Aconex: renomeia arquivos pelo RDS-PP, "
     "calcula o avanço, e mantém as abas de lista de preços e de atividades."),
    ("SearchPMIB", "Busca PMIB",
     "Procura um código ou descrição nas planilhas de uma pasta inteira, sem "
     "abrir arquivo por arquivo."),
]

TELAS_BLOQUEADAS = frozenset({"CorrecaoPDM"})

MSG_TAREFA_EM_ANDAMENTO = (
    "Há uma tarefa em andamento (um robô, uma tradução ou uma consulta à IA).\n\n"
    "Se fechar agora, ela é interrompida no ponto em que está, e uma planilha "
    "que estava sendo gravada pode ficar pela metade.\n\n"
    "Fechar o SIG-FT mesmo assim?"
)

MSG_ABERTURA_FALHOU = (
    "O SIG-FT não conseguiu abrir a janela principal.\n\n{erro}\n\n"
    "O detalhe completo está em Documentos\\SIG-FT\\logs\\sigft.log. "
    "Mande esse arquivo para quem cuida do SIG-FT."
)
```

- [ ] **Step 4: Ver passar e commit**

```bash
python -m pytest tests/test_qt_catalogo.py -q   # 4 passed
git add sigft/app_qt/catalogo.py tests/test_qt_catalogo.py
git commit -m "Qt6: catalogo de navegacao, travado contra a interface atual"
```

---

### Task 10: Home e tela "ainda não migrada"

**Files:**
- Create: `sigft/app_qt/views/__init__.py`, `sigft/app_qt/views/home.py`, `sigft/app_qt/views/nao_migrada.py`
- Test: `tests/test_qt_home.py`

**Interfaces:**
- Consumes: `catalogo.MODULOS`, `estilo.mono`, `sigft.services.updater.canal_testes_ligado/ligar_canal_testes`.
- Produces: `HomeView(parent=None, controller=None)` com `.cards: dict[str, QFrame]`, `.botoes_barra: dict[str, QPushButton]` (chaves `"atividades"`, `"modelos"`, `"gastos"`, `"chaves"`, `"atualizacoes"`), `.caixa_canal_testes: QCheckBox`; `TelaNaoMigrada(nome: str, parent=None)`. O controller precisa de `show_frame(nome)`.

- [ ] **Step 1: Teste que falha**

`tests/test_qt_home.py`:
```python
from PySide6.QtCore import QPoint, Qt

from sigft.app_qt import catalogo
from sigft.app_qt.views.home import HomeView
from sigft.app_qt.views.nao_migrada import TelaNaoMigrada


class Controller:
    def __init__(self):
        self.visitas = []

    def show_frame(self, nome):
        self.visitas.append(nome)


def test_um_card_por_modulo_com_os_textos(qt_interface, qtbot):
    home = HomeView(controller=Controller())
    qtbot.addWidget(home)
    assert list(home.cards) == [m[0] for m in catalogo.MODULOS]


def test_clique_no_card_inteiro_navega(qt_interface, qtbot):
    ctrl = Controller()
    home = HomeView(controller=ctrl)
    qtbot.addWidget(home)
    home.show()
    qtbot.mouseClick(home.cards["Analyzer"], Qt.MouseButton.LeftButton, pos=QPoint(5, 5))
    assert ctrl.visitas == ["Analyzer"]


def test_icones_da_barra_em_preto_e_branco(qt_interface, qtbot):
    home = HomeView(controller=Controller())
    qtbot.addWidget(home)
    assert "\ufe0e" in home.botoes_barra["atividades"].text()


def test_canal_de_testes_lembra_a_escolha(qt_interface, qtbot, monkeypatch):
    from sigft.services import updater
    gravado = []
    monkeypatch.setattr(updater, "canal_testes_ligado", lambda: False)
    monkeypatch.setattr(updater, "ligar_canal_testes", gravado.append)
    home = HomeView(controller=Controller())
    qtbot.addWidget(home)
    home.caixa_canal_testes.setChecked(True)
    assert gravado == [True]


def test_tela_nao_migrada_diz_o_nome(qt_interface, qtbot):
    t = TelaNaoMigrada("AutoSpec")
    qtbot.addWidget(t)
    assert "AutoSpec" in t.mensagem.text()
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_home.py -q` → FAIL

- [ ] **Step 3: Implementar**

`sigft/app_qt/views/__init__.py`:
```python
"""Telas da interface Qt: uma por arquivo, mesmos nomes da interface atual."""
```

`sigft/app_qt/views/nao_migrada.py`:
```python
"""Lugar-tenente das telas que ainda não foram migradas para Qt."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TelaNaoMigrada(QWidget):
    def __init__(self, nome: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("tela")
        layout = QVBoxLayout(self)
        self.mensagem = QLabel(
            f"A tela \"{nome}\" ainda não foi migrada para a interface nova.\n"
            "Use a versão atual (python frontend.py) para ela.")
        self.mensagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mensagem.setStyleSheet("font-size: 16px; color: #B3B3B3;")
        layout.addWidget(self.mensagem)
```

`sigft/app_qt/views/home.py`:
```python
"""A Home em Qt: cabeçalho, barra de botões e um card clicável por módulo.

Aparência aprovada no protótipo de 2026-10-07: cards compactos (a descrição
ocupa a largura do card), ícones em preto e branco, espaçamento de hoje.
Os painéis da barra (Atividades, Modelos de IA, Gastos, Chaves, Atualizações)
migram no plano da Etapa 6; até lá cada botão avisa isso.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from sigft.app_qt import catalogo
from sigft.app_qt.estilo import mono

BARRA = [
    ("atividades", "\U0001F4CB  Atividades do dia", "acento"),
    ("modelos", "\U0001F916  Modelos de IA", None),
    ("gastos", "\U0001F4B0  Gastos de IA", None),
    ("chaves", "\U0001F511  Chaves de API", "neutro"),
    ("atualizacoes", "\U0001F504  Atualizações", "neutro"),
]
TEXTO_CANAL_TESTES = "Versões de teste"


class _Card(QFrame):
    def __init__(self, alvo, titulo, descricao, ao_clicar) -> None:
        super().__init__(objectName="card")
        self._alvo = alvo
        self._ao_clicar = ao_clicar
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.addWidget(QLabel(titulo, objectName="card_titulo"))
        desc = QLabel(descricao, objectName="card_desc")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        for rotulo in self.findChildren(QLabel):
            rotulo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def mousePressEvent(self, evento) -> None:  # noqa: N802 -- nome do Qt
        if evento.button() == Qt.MouseButton.LeftButton:
            self._ao_clicar(self._alvo)
        super().mousePressEvent(evento)


class HomeView(QScrollArea):
    def __init__(self, parent=None, controller=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self.setWidgetResizable(True)
        self.setObjectName("conteudo")
        corpo = QWidget(objectName="conteudo")
        layout = QVBoxLayout(corpo)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(6)
        layout.addWidget(QLabel("SIG-FT", objectName="titulo_home"))
        layout.addWidget(QLabel("Sistema Integrado de Gestão de Fichas Técnicas - GE Vernova",
                                objectName="subtitulo_home"))
        layout.addSpacing(30)
        layout.addWidget(QLabel("Clique num módulo abaixo para abri-lo. Os botões desta barra "
                                "abrem painéis em janela, para a Home ficar limpa.",
                                objectName="texto_simples"))
        layout.addSpacing(6)
        layout.addLayout(self._barra())
        layout.addSpacing(10)
        layout.addLayout(self._cards())
        layout.addStretch()
        self.setWidget(corpo)

    def _barra(self) -> QHBoxLayout:
        linha = QHBoxLayout()
        linha.setSpacing(10)
        self.botoes_barra: dict[str, QPushButton] = {}
        for chave, texto, variante in BARRA:
            botao = QPushButton(mono(texto))
            botao.setProperty("barra", True)
            if variante:
                botao.setProperty("variante", variante)
            botao.clicked.connect(lambda _=False, t=texto: self._painel_em_migracao(t))
            self.botoes_barra[chave] = botao
            linha.addWidget(botao)
        self.caixa_canal_testes = QCheckBox(TEXTO_CANAL_TESTES)
        try:
            from sigft.services import updater
            self.caixa_canal_testes.setChecked(bool(updater.canal_testes_ligado()))
        except Exception:  # noqa: BLE001 -- preferência é conveniência
            pass
        self.caixa_canal_testes.toggled.connect(self._lembrar_canal_testes)
        linha.addWidget(self.caixa_canal_testes)
        linha.addStretch()
        return linha

    def _cards(self) -> QGridLayout:
        grade = QGridLayout()
        grade.setSpacing(12)
        self.cards: dict[str, _Card] = {}
        for indice, (alvo, titulo, descricao) in enumerate(catalogo.MODULOS):
            card = _Card(alvo, titulo, descricao, self._ir)
            self.cards[alvo] = card
            grade.addWidget(card, indice // 2, indice % 2)
        return grade

    def _ir(self, alvo: str) -> None:
        if self.controller is not None:
            self.controller.show_frame(alvo)

    def _lembrar_canal_testes(self, ligado: bool) -> None:
        try:
            from sigft.services import updater
            updater.ligar_canal_testes(bool(ligado))
        except Exception:  # noqa: BLE001 -- lembrar não pode atrapalhar o clique
            pass

    def _painel_em_migracao(self, texto: str) -> None:
        QMessageBox.information(self, "SIG-FT", f"O painel \"{texto.split('  ')[-1]}\" "
                                "ainda não foi migrado. Use a versão atual (python frontend.py).")
```

- [ ] **Step 4: Ver passar e commit**

```bash
python -m pytest tests/test_qt_home.py -q   # 5 passed
bash scripts/check.sh
git add sigft/app_qt/views tests/test_qt_home.py
git commit -m "Qt6: Home com cards clicaveis e tela de aviso para o que falta migrar"
```

---

### Task 11: Janela principal, splash e ponto de entrada

**Files:**
- Create: `sigft/app_qt/main.py`
- Test: `tests/test_qt_main.py`

**Interfaces:**
- Consumes: tudo acima; `sigft.config.carregar_chaves`, `sigft.config.caminho_config`; `sigft.core.instancia` (`preparar`, `tarefas_em_andamento`, `encerrar`); `backends.carregar_todos`.
- Produces: `TELAS: dict[str, Callable[[QWidget, "SIG_FT_App"], QWidget]]` (registro que os planos seguintes preenchem; nesta etapa só `"Home"`); `SIG_FT_App(QMainWindow)` com `show_frame(nome)`, `show_home()`, `show_modulo(nome)`, `get_key(id) -> str`, `save_keys(dict) -> None`, `api_keys: dict`, `botoes_menu: dict[str, QPushButton]`, `telas: dict[str, QWidget]`; `SplashScreen(QWidget)` com sinal `pronta`; `main() -> None`; `executar_da_linha_de_comando() -> None` (trata `--smoke`).

- [ ] **Step 1: Teste que falha**

`tests/test_qt_main.py`:
```python
import json

import pytest

from sigft.app_qt import main as qmain


@pytest.fixture
def app_qt(qt_interface, qtbot, tmp_path, monkeypatch):
    monkeypatch.setattr(qmain, "_arquivo_de_chaves", lambda: str(tmp_path / "api_config.json"))
    janela = qmain.SIG_FT_App()
    qtbot.addWidget(janela)
    return janela


def test_abre_na_home_e_cria_telas_so_na_visita(app_qt):
    assert list(app_qt.telas) == ["Home"]
    app_qt.show_frame("Analyzer")
    assert "Analyzer" in app_qt.telas
    assert app_qt.pilha.currentWidget() is app_qt.telas["Analyzer"]


def test_tela_nao_registrada_mostra_aviso(app_qt):
    from sigft.app_qt.views.nao_migrada import TelaNaoMigrada
    app_qt.show_frame("AutoSpec")
    assert isinstance(app_qt.telas["AutoSpec"], TelaNaoMigrada)


def test_tela_bloqueada_nao_abre_e_botao_desabilitado(app_qt):
    app_qt.show_frame("CorrecaoPDM")
    assert "CorrecaoPDM" not in app_qt.telas
    assert not app_qt.botoes_menu["CorrecaoPDM"].isEnabled()


def test_titulo_com_versao(app_qt):
    from sigft import _build_info
    assert f"v{_build_info.VERSAO}" in app_qt.windowTitle()


def test_salvar_chaves_preserva_o_resto_do_arquivo(app_qt, tmp_path):
    arquivo = tmp_path / "api_config.json"
    arquivo.write_text(json.dumps({"_modelos_ia": {"global": "x"}, "GEMINI": "velha"}), encoding="utf-8")
    app_qt.save_keys({"GEMINI": "nova"})
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert dados == {"_modelos_ia": {"global": "x"}, "GEMINI": "nova"}
    assert app_qt.get_key("GEMINI") == "nova"


def test_fechar_com_tarefa_pergunta_antes(app_qt, monkeypatch):
    from sigft.core import instancia
    perguntas = []
    monkeypatch.setattr(instancia, "tarefas_em_andamento", lambda: ["tarefa:x"])
    monkeypatch.setattr(qmain.QMessageBox, "question",
                        lambda *a, **k: perguntas.append(a[2]) or qmain.QMessageBox.StandardButton.No)
    app_qt.show()
    app_qt.close()
    assert perguntas and app_qt.isVisible()


def test_smoke_monta_e_sai_com_zero(qt_interface, monkeypatch, tmp_path):
    monkeypatch.setattr(qmain, "_arquivo_de_chaves", lambda: str(tmp_path / "api_config.json"))
    monkeypatch.setattr(qmain.backends, "carregar_todos", lambda **k: None)
    assert qmain._smoke() == 0
```

- [ ] **Step 2: Ver falhar**

Run: `python -m pytest tests/test_qt_main.py -q` → FAIL

- [ ] **Step 3: Implementar**

`sigft/app_qt/main.py`:
```python
"""Ponto de entrada da interface Qt:  python -m sigft.app_qt.main

Mesma janela de hoje (barra lateral + conteúdo, splash enquanto os backends
carregam), com três diferenças deliberadas, todas do desenho de 2026-10-07:
* as telas são criadas na PRIMEIRA visita, não as 13 na abertura;
* a splash não tem pausas artificiais (eram ~2 s por abertura);
* tela ainda não migrada mostra um aviso em vez de não existir.
"""
from __future__ import annotations

if __name__ == "__main__":
    from sigft.core.python_minimo import exigir_python_minimo

    exigir_python_minimo()

import json
import os
import sys
import threading
import time
import traceback

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget,
)

from sigft import _build_info
from sigft.app import backends, theme
from sigft.app_qt import catalogo, estilo, interface
from sigft.app_qt.views.home import HomeView
from sigft.app_qt.views.nao_migrada import TelaNaoMigrada
from sigft.core import instancia

_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Registro das telas migradas: nome -> fábrica(parent, controller). Cada plano
# de etapa acrescenta as suas aqui.
TELAS = {
    "Home": lambda parent, controller: HomeView(parent, controller),
}


def resource_path(relativo: str) -> str:
    base = getattr(sys, "_MEIPASS", _RAIZ)
    return os.path.join(base, relativo)


def _arquivo_de_chaves() -> str:
    from sigft.config import caminho_config

    return caminho_config()


class SIG_FT_App(QMainWindow):  # noqa: N801 -- mesmo nome da interface atual
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"SIG-FT v{_build_info.VERSAO} - GE Vernova")
        self.resize(1280, 850)
        icone = resource_path(os.path.join("assets", "icone-sig-ft.png"))
        if os.path.exists(icone):
            self.setWindowIcon(QIcon(icone))

        self.api_keys: dict = {}
        self.load_keys()

        central = QWidget()
        linha = QHBoxLayout(central)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(0)
        linha.addWidget(self._montar_sidebar())
        self.pilha = QStackedWidget(objectName="conteudo")
        linha.addWidget(self.pilha, 1)
        self.setCentralWidget(central)

        self.telas: dict[str, QWidget] = {}
        self.show_frame("Home")

    # -- barra lateral --------------------------------------------------------
    def _montar_sidebar(self) -> QScrollArea:
        area = QScrollArea(objectName="sidebar")
        area.setFixedWidth(270)
        area.setWidgetResizable(True)
        area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        interno = QWidget(objectName="sidebar_interno")
        lay = QVBoxLayout(interno)
        lay.setContentsMargins(12, 26, 12, 12)
        lay.setSpacing(estilo.ESPACO_MENU)

        logo = QLabel()
        caminho_logo = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(caminho_logo):
            logo.setPixmap(QPixmap(caminho_logo).scaledToWidth(
                180, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo)
        nome = QLabel("SIG-FT System", objectName="app_nome")
        nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(nome)
        lay.addSpacing(22)
        home = QPushButton(estilo.mono("  🏠  Home"), objectName="home")
        home.clicked.connect(self.show_home)
        lay.addWidget(home)
        lay.addSpacing(6)

        self.botoes_menu: dict[str, QPushButton] = {}
        for item in catalogo.MENU:
            if item[0] == "secao":
                lay.addSpacing(20)
                lay.addWidget(QLabel(item[1].upper(), objectName="secao"))
                lay.addSpacing(5)
                continue
            _tipo, texto, alvo = item
            botao = QPushButton(f"  {texto}")
            botao.setProperty("menu", True)
            botao.setEnabled(alvo not in catalogo.TELAS_BLOQUEADAS)
            botao.clicked.connect(lambda _=False, a=alvo: self.show_frame(a))
            self.botoes_menu[alvo] = botao
            lay.addWidget(botao)
        lay.addStretch()
        area.setWidget(interno)
        return area

    # -- navegação ------------------------------------------------------------
    def show_frame(self, nome: str) -> None:
        """Funil único de navegação: barra lateral e cards passam por aqui."""
        if nome in catalogo.TELAS_BLOQUEADAS:
            return
        tela = self.telas.get(nome)
        if tela is None:
            fabrica = TELAS.get(nome)
            tela = fabrica(self.pilha, self) if fabrica else TelaNaoMigrada(nome)
            self.telas[nome] = tela
            self.pilha.addWidget(tela)
        self.pilha.setCurrentWidget(tela)

    def show_modulo(self, nome: str) -> None:
        self.show_frame(nome)

    def show_home(self) -> None:
        self.show_frame("Home")

    # -- chaves de API ----------------------------------------------------------
    def load_keys(self) -> None:
        from sigft.config import carregar_chaves

        self.api_keys = carregar_chaves(_arquivo_de_chaves())

    def save_keys(self, novas: dict) -> None:
        """Lê o JSON inteiro, troca só as chaves de API e grava de forma atômica.

        Atômica (arquivo temporário + `os.replace`): um corte no meio da
        gravação não pode deixar o `api_config.json` pela metade, que faria as
        chaves "sumirem" na próxima abertura.
        """
        arquivo = _arquivo_de_chaves()
        dados: dict = {}
        try:
            with open(arquivo, encoding="utf-8") as f:
                carregado = json.load(f)
            if isinstance(carregado, dict):
                dados = carregado
        except (OSError, ValueError):
            dados = {}
        dados.update(novas)
        temporario = arquivo + ".tmp"
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4)
        os.replace(temporario, arquivo)
        self.api_keys = {**self.api_keys, **novas}

    def get_key(self, key_id: str) -> str:
        return self.api_keys.get(key_id) or ""

    # -- fechar -------------------------------------------------------------------
    def closeEvent(self, evento) -> None:  # noqa: N802 -- nome do Qt
        if instancia.tarefas_em_andamento():
            resposta = QMessageBox.question(
                self, "Fechar o SIG-FT", catalogo.MSG_TAREFA_EM_ANDAMENTO,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if resposta != QMessageBox.StandardButton.Yes:
                evento.ignore()
                return
        evento.accept()


class SplashScreen(QWidget):
    """A splash de hoje, sem as pausas artificiais: o progresso é o real."""

    pronta = Signal()

    def __init__(self) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.SplashScreen)
        self.setFixedSize(500, 350)
        self.setObjectName("conteudo")
        self.setStyleSheet(f"background: {theme.COLORS['background']};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(50, 50, 50, 20)
        logo = QLabel()
        caminho = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(caminho):
            logo.setPixmap(QPixmap(caminho).scaledToWidth(
                300, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(logo)
        titulo = QLabel("SIG-FT System")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: gray; font-size: 16px;")
        lay.addWidget(titulo)
        lay.addStretch()
        self.status = QLabel("Iniciando...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(f"color: {theme.COLORS['accent']}; font-size: 12px;")
        lay.addWidget(self.status)
        self.barra = QProgressBar()
        self.barra.setRange(0, 1000)
        self.barra.setTextVisible(False)
        self.barra.setStyleSheet(f"QProgressBar::chunk {{ background: {theme.COLORS['accent']}; }}")
        lay.addWidget(self.barra)

    def carregar(self) -> None:
        threading.Thread(target=self._carregar, name="splash", daemon=True).start()

    def _carregar(self) -> None:
        inicio = time.time()

        def progredir(exibido, fracao):
            interface.na_interface(self.status.setText, f"Carregando: {exibido}...")
            interface.na_interface(self.barra.setValue, int(fracao * 1000))

        def falhar(exibido, erro):
            print(f"Erro ao carregar {exibido}: {erro}")
            interface.na_interface(self.status.setText, f"Erro em {exibido}")

        backends.carregar_todos(ao_progredir=progredir, ao_falhar=falhar)
        interface.na_interface(self.status.setText, f"Concluído em {time.time() - inicio:.1f}s")
        interface.na_interface(self.pronta.emit)


def _preparar_qt() -> QApplication:
    app = QApplication.instance() or QApplication(sys.argv)
    interface.instalar()
    estilo.carregar_fontes()
    app.setStyleSheet(estilo.folha_de_estilo())
    return app


def main() -> None:
    instancia.preparar()
    app = _preparar_qt()
    splash = SplashScreen()
    janela: list[SIG_FT_App] = []

    def abrir_principal() -> None:
        try:
            principal = SIG_FT_App()
        except Exception as erro:  # noqa: BLE001 -- vira aviso, e não fantasma
            traceback.print_exception(erro)
            QMessageBox.critical(None, "SIG-FT", catalogo.MSG_ABERTURA_FALHOU.format(
                erro=f"{type(erro).__name__}: {erro}"))
            instancia.encerrar(1)
            return
        janela.append(principal)
        principal.show()
        splash.close()

    splash.pronta.connect(abrir_principal)
    splash.show()
    splash.carregar()
    app.exec()
    instancia.encerrar(0)


def _smoke() -> int:
    """Monta a janela principal e sai, sem laço de eventos (para o CI)."""
    try:
        _preparar_qt()
        backends.carregar_todos()
        janela = SIG_FT_App()
        janela.close()
    except Exception as erro:  # noqa: BLE001 -- é o que se quer relatar
        print(f"[smoke] FALHOU: {type(erro).__name__}: {erro}")
        traceback.print_exc()
        return 1
    print("[smoke] a janela principal Qt montou e fechou sem erro.")
    return 0


def executar_da_linha_de_comando() -> None:
    if "--smoke" in sys.argv:
        sys.exit(_smoke())
    main()


if __name__ == "__main__":
    executar_da_linha_de_comando()
```

- [ ] **Step 4: Ver passar**

Run: `python -m pytest tests/test_qt_main.py -q`
Expected: `7 passed`

- [ ] **Step 5: Abrir de verdade (exigência do CLAUDE.md)**

Com display (Windows/macOS, ou `xvfb-run` no Linux):
```bash
python -m sigft.app_qt.main
```
Conferir: splash com progresso, janela com o título `SIG-FT vX.Y.Z - GE Vernova`, barra lateral com "4.4. Correção de PDM" em cinza, Home com os 12 cards, clique num card abre o aviso "ainda não foi migrada", fechar encerra o processo.

Captura lado a lado com `python frontend.py` (mesmo tamanho de janela, 1280x850) e comparar com `sig-ft-propuestas/specs/prototipo/comparacion_home_v2.png`.

- [ ] **Step 6: Suíte e commit**

```bash
bash scripts/check.sh
git add sigft/app_qt/main.py tests/test_qt_main.py
git commit -m "Qt6: janela principal com telas sob demanda, splash sem pausas e --smoke"
```

---

### Task 12: Entregar a etapa (patches + log)

**Files:**
- Modify: `Jonann17/jonan:sig-ft-propuestas/LOG.md`
- Create: `Jonann17/jonan:sig-ft-propuestas/patches/etapa1/*.patch`

- [ ] **Step 1: Medir a abertura (antes x depois)**

```bash
# CustomTkinter (atual) -- tempo até a janela principal montar
python - <<'PY'
import time, subprocess, sys
t = time.time(); subprocess.run([sys.executable, "frontend.py", "--smoke"]); print("ctk:", round(time.time() - t, 2), "s")
t = time.time(); subprocess.run([sys.executable, "-m", "sigft.app_qt.main", "--smoke"]); print("qt:", round(time.time() - t, 2), "s")
PY
```
Anotar os dois números no LOG. (O `--smoke` não inclui a splash; a economia das pausas, ~2 s, soma-se a isso na abertura normal.)

- [ ] **Step 2: Exportar os patches**

```bash
BASE=$(git merge-base HEAD origin/claude/checkpoint-01-refactor-executor-5lawtu)
git format-patch "$BASE"..HEAD -o ../jonan/sig-ft-propuestas/patches/etapa1/
```

- [ ] **Step 3: LOG.md**

Acrescentar em `sig-ft-propuestas/LOG.md`, seção "Cambios":
```markdown
### 1. Qt6 — Etapa 1 (base)
- Archivos: sigft/app_qt/ (nuevo), sigft/core/python_minimo.py, sigft/app/backends.py,
  frontend.py, requirements*.txt, tests/conftest.py, ci.yml, assets/fonts/
- Qué cambia: la interfaz Qt abre con splash, barra lateral y Home; las pantallas
  todavía no migradas muestran un aviso. La interfaz actual no cambia.
- Por qué: migración autorizada por Luan (spec 2026-10-07-migracao-qt6-design.md).
- Cómo se probó: bash scripts/check.sh verde; app abierta en <Windows/macOS>; capturas.
- Medición: abertura ctk = <x> s, qt = <y> s.
- Parches: patches/etapa1/ (aplicar con `git am patches/etapa1/*.patch`)
```

- [ ] **Step 4: Commit e push no repo `jonan`**

```bash
cd ../jonan
git add sig-ft-propuestas
git commit -m "SIG-FT Qt6: parches de la etapa 1 (base)"
git push -u origin claude/youthful-newton-94cb81
```

---

## Próximos planos (um por etapa, escritos quando a anterior fechar)

- **Etapa 2:** pickers (`FilePickerRow`, `MultiFilePickerRow`, `FolderPickerRow`, `FileQueueList`) + `file_dialogs` Qt (adaptador `dialog_fn` sobre `QFileDialog`, reaproveitando `sigft/app/file_dialogs.py`) + telas piloto **ApagarLMR** e **Translator**.
- **Etapa 3:** LMR (aba única), BuscaPMIB, PMIBManager (+ `ArquivosTravadosDialog`), Analyzer, PDM (+ `TabelaSelecaoDialog`, `SelecaoMultiplaDialog`).
- **Etapa 4:** UploadConditions, UploadTechSpecs, CopiaFichas, CorrecaoPDM (bloqueada).
- **Etapa 5:** CriaFichas (`JanelaAcaoRobo` via `DialogosDeEspera`) e AutoSpec, com nota para o Rafael.
- **Etapa 6:** painéis da Home, mural, atualização automática, textos dos diálogos para módulo puro, medições finais, `SIG-FT.spec`/`conferencia.py`/CI de Release, corte do `frontend.py` e remoção do CustomTkinter.
