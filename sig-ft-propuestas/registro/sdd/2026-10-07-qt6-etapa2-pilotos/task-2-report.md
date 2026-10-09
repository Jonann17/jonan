# Task 2 - Estilo dos controles igual ao tema do CustomTkinter

## Implementacao
- `estilo.py`: constantes `AZUL_CTK`/`AZUL_CTK_HOVER`; QDialog separado (gray10); QPushButton padrao azul CTK + variante `primario`; checkbox (borda 3px #949A9F, marcado AZUL_CTK); regras novas QLineEdit, QComboBox, QTabWidget/QTabBar, QListWidget, `#cartao`.
- `views/home.py`: `modelos` e `gastos` com variante `"primario"`.
- `widgets/dialogs.py`: `PausaLoginDialog.botao` e `RetryLockDialog.botao_repetir` com `variante="primario"`.
- Teste: `tests/test_qt_estilo_controles.py` (5 testes).

## RED / GREEN
- RED: 5 failed (AZUL_CTK inexistente, BARRA com None).
- GREEN: `test_qt_estilo_controles + test_qt_estilo + test_qt_home` = 29 passed.

## Captura da Home (antes x depois)
- qt_home.png: 983 pixels diferentes, todos na caixa "Versoes de teste" (bbox 1056,167-1177,193): borda do checkbox mais grossa/clara (3px #949A9F), mudanca pedida pelo brief. Botoes da barra (modelos/gastos) identicos. Cards sem diferenca.
- qt_nao_migrada.png: 0 pixels diferentes.

## Verificacao
- `ruff check .`: All checks passed. `scripts/check.sh`: TUDO OK.

## Concerns
- Nenhum. Nota: o checkbox da Home mudou de aparencia (esperado pelo brief, alinhado ao CTk).
