# Qt6 — Etapas 3 a 6: la app Qt completa y ejecutable

Pedido de Jonathan (2026-10-08): "haz todo lo que tengas que hacer hasta que tengamos una
aplicación funcional y ejecutable sin un script". Objetivo: todas las pantallas de la
interfaz CustomTkinter funcionando en Qt, iguales en comportamiento y apariencia, y la app
abriendo por el camino normal (`python frontend.py`, `SIG-FT.bat`, el `.exe`), sin script
de prueba.

Base: fin de la etapa 2 (Traductor + Aplicação LMR con sus dos pestañas, registradas).
Convenciones de cada tarea (hilos, paridad visual, capturas, verificación, informe):
`sigft/.superpowers/sdd/qt-convencoes.md` (copia en este directorio: `qt-convencoes.md`).

Proceso por tarea: implementador → revisión independiente (spec + calidad) → correcciones →
registro. Tareas sin archivos en común corren en paralelo, cada una en su worktree; se
integran con cherry-pick en `local/jonan-cambios` y se corre `check.sh` + `ruff` después de
cada integración.

## Etapa 3 — piezas compartidas
- **E3.1 Widgets genéricos que faltan** (`sigft/app_qt/widgets/`): `SelecaoMultiplaDialog`,
  `TabelaSelecaoDialog` (con `de_dataframe`), `ArquivosTravadosDialog` (+ el método de
  `DialogosDeEspera` que lo usa, igual a `sigft/app/widgets/espera.py`), `FileQueueList`,
  `JanelaPainel`; estilos globales que imiten CTkRadioButton, CTkSwitch, CTkSlider,
  CTkTabview (botones segmentados arriba, centrados), CTkScrollableFrame, ttk.Treeview,
  CTkProgressBar. Cada uno con captura CTk×Qt.
- **E3.2 Ventanas auxiliares** (`sigft/app_qt/views/janelas.py` = `sigft/app/views/janelas.py`):
  JanelaSelecao, JanelaResumo, JanelaEscolherPDM, JanelaRevisaoPDM, JanelaAcaoRobo,
  JanelaSelecaoDuplicadas, JanelaRevisaoEdicao. Depende de E3.1.

## Etapa 4 — pantallas (en tandas paralelas, después de E3.1)
| Tarea | Pantalla CTk | Usa |
|---|---|---|
| E4.1 | `busca_pmib.py` (SearchPMIB) | radio, option menu |
| E4.2 | `pmib_manager.py` (PMIBManager) | progreso |
| E4.3 | `analyzer.py` (Analyzer) | pickers, slider |
| E4.4 | `upload_conditions.py` (UploadConditions) | tabview, switch, FileQueueList, diálogos |
| E4.5 | `upload_tech_specs.py` (UploadSpecs) | ídem |
| E4.6 | `pdm.py` (PDM) | tabview, radios, SelecaoMultipla |
| E4.7 | `copia_fichas.py` (CopiaFichas) | janelas (E3.2) |
| E4.8 | `correcao_pdm.py` (CorrecaoPDM, bloqueada en el menú) | treeview, JanelaEscolherPDM |
| E4.9 | `cria_fichas.py` (CriaFichas) | janelas (E3.2), tabview |
| E4.10 | `autospec.py` (AutoSpec — frente de Rafael; nota aparte) | conferência |

## Etapa 5 — Home completa y actualización
- **E5.1 Paneles de la Home**: barra de botones (Chaves de API, Modelos de IA, Gastos de IA,
  Mural, Procurar atualizações), caja "Versões de teste", cards de instrucciones; ventanas
  `JanelaPainel` con el área de claves, el panel de modelos de IA y el de gastos
  (`sigft/app/views/home.py`), mural (`sigft/app/widgets/mural.py`).
- **E5.2 Actualización automática**: `sigft/app/atualizacao.py` en Qt (aviso al abrir,
  "procurar agora", `JanelaAtualizacao`), mismos servicios (`updater`).

## Etapa 6 — corte (la app Qt pasa a ser la oficial)
- **E6.1 Registro y arranque**: todas las pantallas en `TELAS`; `frontend.py` abre la
  interfaz Qt (con `--ctk` para abrir la vieja mientras dure la transición); `SIG-FT.bat`
  y lanzador para macOS; `requirements.txt` con PySide6; conferencia del `.exe`
  (`sigft/app/conferencia.py`) cubriendo Qt.
- **E6.2 Empaquetado**: `SIG-FT.spec` incluye Qt (y deja de excluirlo), `release.yml`;
  medir tamaño y tiempo de apertura del `.exe`.
- **E6.3 Entrega**: parches por etapa en `patches/`, entrada en `LOG.md`, nota para Rafael
  sobre AutoSpec, revisión final de toda la rama.

## Lo que no se puede probar acá
Portal (RPA) y `.exe` en Windows: se prueban con el contenedor sin acceso al portal solo
contra dobles. El LOG lo dice explícitamente; Luan/Jonathan validan en máquina real.
