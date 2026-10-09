# Trabajo pendiente (pausado el 2026-10-09 a pedido de Jonathan)

Nada de esto está en `etapas3a6-en-curso/`: se guarda acá para no perderlo si el
contenedor de la sesión se recicla. **No aplicar en la rama de prueba** salvo el 0001.

| Archivo | Qué es | Estado |
|---|---|---|
| `0001-Qt6-uploads-com-erro-de-JSON...patch` | Correcciones de la revisión de Upload de Condições/Specs: JSON mal formado vuelve a avisar en la consola, Espacio/Enter ya no liberan la pausa del robot, un solo robot por vez, botón "Tentar Novamente" con el hover del CTk, sin código duplicado. | **Terminado** (check.sh OK y ruff limpio en el agente); falta integrarlo y que el revisor confirme las correcciones. Se aplica encima de `etapas3a6-en-curso/`. |
| `0002-WIP-tela-AutoSpec-AI.patch` + `0003-WIP-autospec-nao-commitado.diff` | Pantalla AutoSpec AI en Qt (frente de Rafael: solo la vista, ningún archivo de él). | **Sin terminar**: se cortó justo al correr la verificación final. Sin revisión. |
| `0004-WIP-home-paineis-testes.diff` | Home completa (barra de botones, paneles de claves/modelos/gastos de IA, mural, "Versões de teste"). | **Recién empezada**: solo hay pruebas escritas. |

Para retomar: aplicar `etapa1/`, `etapa2-en-curso/`, `etapas3a6-en-curso/` y después
`git am 0001-*.patch 0002-*.patch` y `git apply 0003-*.diff` (AutoSpec), o pedirle a
Claude "continua" en la sesión. Lo que falta está en `../../LOG.md`, sección
"Estado al pausar".
