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

