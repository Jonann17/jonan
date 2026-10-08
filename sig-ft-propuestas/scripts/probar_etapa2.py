"""Abre la interfaz Qt con las pantallas de la etapa 2 que ya están listas.

Uso (desde la carpeta del SIG-FT, con el .venv activado):
    python /ruta/a/sig-ft-propuestas/scripts/probar_etapa2.py

Mientras la etapa 2 no termine, el menú todavía no conoce estas pantallas
(el registro es la tarea 8). Este script las registra solo para probar:
  - "4.2. Tradutor"      -> pantalla del Traductor
  - "7. Aplicação LMR"   -> por ahora, la pestaña de Exclusión sola
"""
import os
import sys

sys.path.insert(0, os.getcwd())

from sigft.app_qt import main as qmain  # noqa: E402
from sigft.app_qt.views.apagar_lmr import ModuloApagarLMR  # noqa: E402
from sigft.app_qt.views.translator import ModuloTranslator  # noqa: E402

qmain.TELAS["Translator"] = lambda p, c: ModuloTranslator(p, c)
qmain.TELAS.setdefault("LMR", lambda p, c: ModuloApagarLMR(p, c))
qmain.main()
