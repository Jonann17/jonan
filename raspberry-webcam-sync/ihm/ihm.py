#!/usr/bin/env python3
"""
ihm.py  —  Interfaz gráfica (IHM) para el Raspberry externo (Pi B), en PyQt6.

Permite:
  * Ver el ESTADO del sistema (servidor / cámara / descargador) con luces.
  * INICIAR / DETENER la captura de fotos (la cámara arranca en espera).
  * AJUSTAR el intervalo entre fotos de la cámara, de forma remota
    (se lo envía al servidor y la cámara lo toma sin reiniciar).
  * AJUSTAR LA FECHA Y HORA del Pi de la cámara (no tiene internet).
  * Ver la radiación del piranómetro EN VIVO y un GRÁFICO de la medición
    de cada foto (mediciones.csv).
  * Ver la GALERÍA de fotos descargadas (agrupadas por día).

Es "responsive": se adapta a la pantallita de 5" (800x480) y a pantallas
grandes. En pantallas chicas arranca en pantalla completa (botón ⛶ o F11
para salir/volver), el contenido se apila si no entra a lo ancho y los
botones son grandes para usarla con el dedo. Ver [ihm] en config.ini.

Requisitos en el Pi:
    sudo apt install -y python3-pyqt6 python3-requests python3-matplotlib
    # (si no está el paquete apt:  pip3 install PyQt6 requests matplotlib)

Uso:
    python3 ihm/ihm.py
    python3 ihm/ihm.py --ventana        # forzar ventana (sin pantalla completa)
"""

import os
import csv
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, asegurar_carpeta

import requests
from PyQt6.QtCore import (
    Qt, QThread, QObject, QTimer, QDateTime, pyqtSignal, pyqtSlot,
)
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QGroupBox, QDialog,
    QMessageBox, QTabWidget, QDateTimeEdit, QBoxLayout, QFrame,
)

# matplotlib es opcional: sin él, la pestaña Gráfico avisa cómo instalarlo.
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    HAY_MATPLOTLIB = True
except ImportError:
    HAY_MATPLOTLIB = False

# Cuántas miniaturas mostrar como máximo (para que la galería cargue rápido).
MAX_MINIATURAS = 60

# Tamaño de cada miniatura de la galería (las columnas se calculan con el ancho).
MINI_ANCHO, MINI_ALTO = 168, 126

# Por debajo de este ancho la interfaz "se apila" (modo angosto).
ANCHO_ANGOSTO = 640
# Por debajo de este alto se oculta el título para ganar espacio.
ALTO_BAJO = 560
# Pantallas de este tamaño o menores arrancan en pantalla completa ("auto").
PANTALLA_CHICA = (1024, 600)

# Opciones de intervalo entre fotos: (texto, segundos)
OPCIONES_INTERVALO = [
    ("1 minuto", 60),
    ("5 minutos", 300),
    ("10 minutos", 600),
    ("20 minutos", 1200),
    ("30 minutos", 1800),
    ("1 hora", 3600),
]

# Variables que se pueden graficar: (texto, columna de mediciones.csv, unidad)
VARIABLES_GRAFICO = [
    ("Radiación media entre fotos", "g_avg", "W/m²"),
    ("Radiación al sacar la foto", "g_now", "W/m²"),
    ("Tensión media de la celda", "v_avg", "V"),
    ("Potencia media P = V²/R", "p_avg_mw", "mW"),
]


# ------------------------------------------------------------------
#  Worker de red: corre en otro hilo para no congelar la interfaz.
# ------------------------------------------------------------------
class Red(QObject):
    estado = pyqtSignal(object)     # dict con el estado, o None si falló
    aplicado = pyqtSignal(object)   # dict con el nuevo intervalo, o None
    captura_hecha = pyqtSignal(object)   # dict de /captura, o None
    hora_hecha = pyqtSignal(object)      # dict de /hora, o None
    mediciones_bajadas = pyqtSignal(bool)

    def __init__(self, url_servidor, carpeta_local):
        super().__init__()
        self.url = url_servidor.rstrip("/")
        self.carpeta = carpeta_local

    @pyqtSlot()
    def consultar(self):
        try:
            enviado = time.time()
            r = requests.get(self.url + "/estado", timeout=5)
            datos = r.json() if r.ok else None
            if datos and "hora_pi" in datos:
                # Diferencia entre el reloj del Pi A y el de este Pi,
                # corrigiendo la mitad de lo que tardó la consulta.
                datos["desfase"] = datos["hora_pi"] - (enviado + time.time()) / 2
            self.estado.emit(datos)
        except requests.RequestException:
            self.estado.emit(None)

    @pyqtSlot(str)
    def captura(self, accion):
        try:
            r = requests.post(self.url + "/captura", data={"accion": accion}, timeout=5)
            self.captura_hecha.emit(r.json() if r.ok else None)
        except requests.RequestException:
            self.captura_hecha.emit(None)

    @pyqtSlot(float)
    def hora(self, epoch):
        try:
            r = requests.post(self.url + "/hora", data={"epoch": epoch}, timeout=10)
            try:
                datos = r.json()
            except ValueError:
                datos = {"ok": False, "error": f"respuesta {r.status_code}"}
            self.hora_hecha.emit(datos)
        except requests.RequestException as e:
            self.hora_hecha.emit({"ok": False, "error": str(e)})

    @pyqtSlot()
    def bajar_mediciones(self):
        """Baja mediciones.csv a la carpeta local (lo mismo que el descargador)."""
        try:
            r = requests.get(self.url + "/mediciones.csv", timeout=15)
            if r.ok:
                destino = os.path.join(self.carpeta, "mediciones.csv")
                with open(destino + ".parcial", "wb") as f:
                    f.write(r.content)
                os.replace(destino + ".parcial", destino)
            self.mediciones_bajadas.emit(r.ok)
        except (requests.RequestException, OSError):
            self.mediciones_bajadas.emit(False)

    @pyqtSlot(int)
    def aplicar(self, segundos):
        try:
            r = requests.post(self.url + "/config",
                              data={"intervalo_camara": segundos}, timeout=5)
            self.aplicado.emit(r.json() if r.ok else None)
        except requests.RequestException:
            self.aplicado.emit(None)


# ------------------------------------------------------------------
#  Miniatura clickeable (abre la foto en grande).
# ------------------------------------------------------------------
class Miniatura(QLabel):
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
        pix = QPixmap(ruta)
        if not pix.isNull():
            self.setPixmap(pix.scaled(MINI_ANCHO - 8, MINI_ALTO - 8,
                                      Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation))
        self.setFixedSize(MINI_ANCHO, MINI_ALTO)
        self.setStyleSheet("border:1px solid #2a2f3a; background:#000;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(os.path.basename(ruta))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, _ev):
        self.ver_grande()

    def ver_grande(self):
        VisorFoto(self.ruta, self.window()).exec()


class VisorFoto(QDialog):
    """Muestra una foto lo más grande posible. En pantallas chicas ocupa
    toda la pantalla; se cierra tocando la foto o el botón Cerrar."""

    def __init__(self, ruta, padre):
        super().__init__(padre)
        self.setWindowTitle(os.path.basename(ruta))
        self.pix = QPixmap(ruta)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setMinimumSize(1, 1)   # deja que la foto se achique
        self.lbl.mousePressEvent = lambda _ev: self.accept()
        lay.addWidget(self.lbl, stretch=1)
        pie = QHBoxLayout()
        nombre = QLabel(os.path.basename(ruta))
        nombre.setStyleSheet("color:#9aa4b2;")
        pie.addWidget(nombre, stretch=1)
        cerrar = QPushButton("✕  Cerrar")
        cerrar.clicked.connect(self.accept)
        pie.addWidget(cerrar)
        lay.addLayout(pie)

        disp = self.screen().availableGeometry()
        if disp.width() <= PANTALLA_CHICA[0] or disp.height() <= PANTALLA_CHICA[1]:
            self.setWindowState(Qt.WindowState.WindowFullScreen)
        else:
            self.resize(int(disp.width() * 0.8), int(disp.height() * 0.85))

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if not self.pix.isNull():
            self.lbl.setPixmap(self.pix.scaled(
                self.lbl.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))


# ------------------------------------------------------------------
#  Ventana principal
# ------------------------------------------------------------------
class Ventana(QWidget):
    sig_consultar = pyqtSignal()
    sig_aplicar = pyqtSignal(int)
    sig_captura = pyqtSignal(str)
    sig_hora = pyqtSignal(float)
    sig_mediciones = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.carpeta = asegurar_carpeta(config["descargador"]["carpeta_local"])
        self.url = config["descargador"]["url_servidor"]
        self._fotos_mostradas = None  # para no reconstruir la galería sin cambios
        self._estado = None           # último /estado recibido
        self._desfase = None          # hora Pi A − hora de este Pi (segundos)
        self._iniciar_despues_de_hora = False
        self._angosto = None          # modo actual (se calcula al redimensionar)
        self._columnas = 0            # columnas de la galería

        self.setWindowTitle("IHM Webcam — Raspberry Pi")
        self.setMinimumSize(320, 240)
        # La galería se rearma (con otra cantidad de columnas) un ratito
        # después de que cambia el tamaño, no en cada píxel.
        self._timer_galeria = QTimer(self)
        self._timer_galeria.setSingleShot(True)
        self._timer_galeria.timeout.connect(self._ajustar_galeria)
        self._construir_ui()
        self._arrancar_red()

        # Refresco automático cada 5 segundos.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sig_consultar.emit)
        self.timer.start(5000)
        self.sig_consultar.emit()   # primer refresco inmediato
        self.refrescar_galeria()

        # Relojes de la pestaña Control: se actualizan cada segundo.
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self._tic_reloj)
        self.timer_reloj.start(1000)
        self.redibujar_grafico()

        # Pantalla completa: F11 alterna, Esc sale.
        QShortcut(QKeySequence("F11"), self, activated=self.alternar_pantalla_completa)
        QShortcut(QKeySequence("Esc"), self, activated=self._salir_pantalla_completa)
        self._acomodar(self.width(), self.height())

    # ---------- construcción de la interfaz ----------
    def _construir_ui(self):
        # Botones, menús y pestañas altos: se usan con el dedo en la pantallita.
        self.setStyleSheet("""
            QWidget { background:#0f1115; color:#e6e6e6; font-family:sans-serif; font-size:14px; }
            QGroupBox { border:1px solid #2a2f3a; border-radius:10px; margin-top:1ex; padding:6px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; color:#9aa4b2; }
            QPushButton { background:#2563eb; color:#fff; border:none; padding:6px 12px;
                          border-radius:8px; min-height:30px; }
            QPushButton:hover { background:#1d4ed8; }
            QComboBox { background:#161a22; border:1px solid #2a2f3a; padding:4px 8px;
                        border-radius:6px; color:#e6e6e6; min-height:30px; }
            QComboBox QAbstractItemView { background:#161a22; color:#e6e6e6;
                                          selection-background-color:#2563eb; }
            QComboBox QAbstractItemView::item { min-height:34px; }
            QScrollArea { border:none; }
            QScrollBar:vertical { background:#161a22; width:16px; border-radius:8px; }
            QScrollBar::handle:vertical { background:#3b4252; min-height:40px; border-radius:8px; }
            QScrollBar::add-line, QScrollBar::sub-line { height:0px; }
        """)
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(6, 6, 6, 6)
        raiz.setSpacing(4)

        self.titulo = QLabel("📷 Panel de control de la webcam")
        self.titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        raiz.addWidget(self.titulo)

        self.pestanas = QTabWidget()
        self.pestanas.setStyleSheet("""
            QTabBar::tab { background:#161a22; color:#9aa4b2; padding:8px 16px; min-height:24px;
                           border:1px solid #2a2f3a; border-bottom:none;
                           border-top-left-radius:8px; border-top-right-radius:8px; }
            QTabBar::tab:selected { background:#2563eb; color:#fff; }
            QTabWidget::pane { border:1px solid #2a2f3a; border-radius:8px; }
        """)
        self.pestanas.addTab(self._pestana_control(), "Control")
        self.pestanas.addTab(self._pestana_fotos(), "Fotos")
        self.pestanas.addTab(self._pestana_grafico(), "Gráfico")
        self.pestanas.currentChanged.connect(lambda _i: self._timer_galeria.start(50))

        # Botón de pantalla completa, a la derecha de las pestañas.
        self.btn_pantalla = QPushButton("⛶")
        self.btn_pantalla.setToolTip("Pantalla completa (F11)")
        self.btn_pantalla.setStyleSheet("QPushButton { background:#161a22; border:1px solid #2a2f3a;"
                                        " min-width:40px; font-size:18px; padding:2px 8px; }")
        self.btn_pantalla.clicked.connect(self.alternar_pantalla_completa)
        self.pestanas.setCornerWidget(self.btn_pantalla, Qt.Corner.TopRightCorner)
        raiz.addWidget(self.pestanas, stretch=1)

    @staticmethod
    def _con_scroll(contenido):
        """Pone una pestaña dentro de un área con scroll vertical: si no entra
        en la pantalla, se desplaza con el dedo en vez de quedar cortada."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(contenido)
        return scroll

    # ---------- pestaña Control ----------
    def _pestana_control(self):
        w = QWidget()
        raiz = QVBoxLayout(w)
        raiz.setContentsMargins(6, 6, 6, 6)
        raiz.setSpacing(6)

        # --- Estado (luces) + captura, en una sola caja ---
        caja_estado = QGroupBox("Estado y captura")
        ve = QVBoxLayout(caja_estado)
        self.grid_luces = QGridLayout()
        self.lbl_servidor = self._luz("Servidor")
        self.lbl_camara = self._luz("Cámara")
        self.lbl_desc = self._luz("Descargador")
        self.lbl_total = QLabel("🖼️ 0 fotos")
        self._luces = (self.lbl_servidor, self.lbl_camara, self.lbl_desc, self.lbl_total)
        ve.addLayout(self.grid_luces)

        self.lay_cap = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        self.lbl_captura = QLabel("⚪ —")
        self.lbl_captura.setWordWrap(True)
        self.lbl_captura.setStyleSheet("font-size:16px; font-weight:bold;")
        self.lay_cap.addWidget(self.lbl_captura, stretch=1)
        botones = QHBoxLayout()
        self.btn_iniciar = QPushButton("▶  Iniciar captura")
        self.btn_iniciar.setStyleSheet("QPushButton { background:#16a34a; font-weight:bold; padding:8px 16px; min-height:34px; }"
                                       "QPushButton:disabled { background:#2a2f3a; color:#6b7280; }")
        self.btn_iniciar.clicked.connect(self._al_iniciar)
        self.btn_detener = QPushButton("⏹  Detener")
        self.btn_detener.setStyleSheet("QPushButton { background:#dc2626; font-weight:bold; padding:8px 16px; min-height:34px; }"
                                       "QPushButton:disabled { background:#2a2f3a; color:#6b7280; }")
        self.btn_detener.clicked.connect(lambda: self.sig_captura.emit("detener"))
        botones.addWidget(self.btn_iniciar)
        botones.addWidget(self.btn_detener)
        self.lay_cap.addLayout(botones)
        ve.addLayout(self.lay_cap)
        raiz.addWidget(caja_estado)

        # --- Piranómetro en vivo (arriba: es lo que más se mira) ---
        caja_sol = QGroupBox("Piranómetro (Arduino) — en vivo")
        hs = QHBoxLayout(caja_sol)
        self.lbl_sensor = QLabel("—")
        self.lbl_sensor.setWordWrap(True)
        self.lbl_sensor.setStyleSheet("font-size:20px; font-weight:bold;")
        hs.addWidget(self.lbl_sensor)
        raiz.addWidget(caja_sol)

        # --- Configuración del intervalo ---
        caja_cfg = QGroupBox("Intervalo entre fotos")
        self.lay_cfg = QBoxLayout(QBoxLayout.Direction.LeftToRight, caja_cfg)
        fila_cfg = QHBoxLayout()
        fila_cfg.addWidget(QLabel("Una foto cada"))
        self.combo = QComboBox()
        for texto, seg in OPCIONES_INTERVALO:
            self.combo.addItem(texto, seg)
        self.combo.setCurrentIndex(2)  # 10 minutos por defecto
        fila_cfg.addWidget(self.combo, stretch=1)
        self.btn_aplicar = QPushButton("Aplicar")
        self.btn_aplicar.clicked.connect(self._al_aplicar)
        fila_cfg.addWidget(self.btn_aplicar)
        self.lay_cfg.addLayout(fila_cfg, stretch=1)
        self.lbl_actual = QLabel("actual: —")
        self.lbl_actual.setStyleSheet("color:#9aa4b2;")
        self.lay_cfg.addWidget(self.lbl_actual)
        raiz.addWidget(caja_cfg)

        # --- Fecha y hora del Pi de la cámara ---
        caja_hora = QGroupBox("Fecha y hora del Pi de la cámara (no tiene internet)")
        self.grid_hora = QGridLayout(caja_hora)
        self.lbl_hora_pi = QLabel("—")
        self.lbl_hora_pi.setStyleSheet("font-size:16px; font-weight:bold;")
        self.lbl_hora_local = QLabel("—")
        self.lbl_hora_local.setStyleSheet("font-size:16px;")
        self.lbl_desfase = QLabel("—")
        self.lbl_desfase.setWordWrap(True)
        self._et_hora_pi = QLabel("Pi de la cámara:")
        self._et_hora_local = QLabel("Este Pi:")
        self._et_hora_enviar = QLabel("Hora a enviar:")
        self.edit_hora = QDateTimeEdit(QDateTime.currentDateTime())
        self.edit_hora.setDisplayFormat("dd/MM/yyyy  HH:mm:ss")
        self.edit_hora.setCalendarPopup(True)
        self.edit_hora.setStyleSheet("background:#161a22; border:1px solid #2a2f3a; padding:4px; min-height:30px;")
        self.btn_ahora = QPushButton("Usar la hora de este Pi")
        self.btn_ahora.clicked.connect(
            lambda: self.edit_hora.setDateTime(QDateTime.currentDateTime()))
        self.btn_enviar = QPushButton("⏱  Enviar hora al Pi de la cámara")
        self.btn_enviar.clicked.connect(self._al_enviar_hora)
        raiz.addWidget(caja_hora)

        raiz.addStretch()
        return self._con_scroll(w)

    # ---------- modo ancho / angosto ----------
    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._acomodar(self.width(), self.height())
        self._timer_galeria.start(150)

    def _acomodar(self, ancho, alto):
        """Reacomoda la interfaz según el tamaño de la ventana."""
        self.titulo.setVisible(alto >= ALTO_BAJO)
        angosto = ancho < ANCHO_ANGOSTO
        if angosto == self._angosto:
            return
        self._angosto = angosto
        vertical = QBoxLayout.Direction.TopToBottom
        horizontal = QBoxLayout.Direction.LeftToRight

        # Luces de estado: en fila (ancho) o de a dos (angosto).
        for x in self._luces:
            self.grid_luces.removeWidget(x)
        por_fila = 2 if angosto else 4
        for i, x in enumerate(self._luces):
            self.grid_luces.addWidget(x, i // por_fila, i % por_fila)

        self.lay_cap.setDirection(vertical if angosto else horizontal)
        self.lay_cfg.setDirection(vertical if angosto else horizontal)
        if hasattr(self, "lay_barra_graf"):
            self.lay_barra_graf.setDirection(vertical if angosto else horizontal)

        # Fecha y hora: 3 columnas (ancho) o 2 columnas apiladas (angosto).
        g = self.grid_hora
        for x in (self._et_hora_pi, self.lbl_hora_pi, self.lbl_desfase,
                  self._et_hora_local, self.lbl_hora_local,
                  self._et_hora_enviar, self.edit_hora, self.btn_ahora, self.btn_enviar):
            g.removeWidget(x)
        if angosto:
            filas = [(self._et_hora_pi, 0, 0, 1, 1), (self.lbl_hora_pi, 0, 1, 1, 1),
                     (self.lbl_desfase, 1, 0, 1, 2),
                     (self._et_hora_local, 2, 0, 1, 1), (self.lbl_hora_local, 2, 1, 1, 1),
                     (self._et_hora_enviar, 3, 0, 1, 1), (self.edit_hora, 3, 1, 1, 1),
                     (self.btn_ahora, 4, 0, 1, 2), (self.btn_enviar, 5, 0, 1, 2)]
        else:
            filas = [(self._et_hora_pi, 0, 0, 1, 1), (self.lbl_hora_pi, 0, 1, 1, 1),
                     (self.lbl_desfase, 0, 2, 1, 1),
                     (self._et_hora_local, 1, 0, 1, 1), (self.lbl_hora_local, 1, 1, 1, 1),
                     (self._et_hora_enviar, 2, 0, 1, 1), (self.edit_hora, 2, 1, 1, 1),
                     (self.btn_ahora, 2, 2, 1, 1), (self.btn_enviar, 3, 0, 1, 3)]
        for x, f, c, fs, cs in filas:
            g.addWidget(x, f, c, fs, cs)

    # ---------- pantalla completa ----------
    def alternar_pantalla_completa(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _salir_pantalla_completa(self):
        if self.isFullScreen():
            self.showNormal()

    # ---------- pestaña Fotos ----------
    def _pestana_fotos(self):
        caja_gal = QWidget()
        vg = QVBoxLayout(caja_gal)
        barra = QHBoxLayout()
        btn_ref = QPushButton("↻ Refrescar galería")
        btn_ref.clicked.connect(lambda: self.refrescar_galeria(forzar=True))
        barra.addWidget(btn_ref)
        barra.addStretch()
        vg.addLayout(barra)

        vg.setContentsMargins(6, 6, 6, 6)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.cont_galeria = QWidget()
        self.grid = QGridLayout(self.cont_galeria)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.cont_galeria)
        vg.addWidget(self.scroll)
        return caja_gal

    # ---------- pestaña Gráfico ----------
    def _pestana_grafico(self):
        w = QWidget()
        v = QVBoxLayout(w)
        if not HAY_MATPLOTLIB:
            v.addWidget(QLabel("Para ver el gráfico instalá matplotlib:\n"
                               "    sudo apt install python3-matplotlib"))
            return w

        v.setContentsMargins(6, 6, 6, 6)
        # Barra de opciones: en una fila (ancho) o en dos (angosto).
        self.lay_barra_graf = QBoxLayout(QBoxLayout.Direction.LeftToRight)
        fila_var = QHBoxLayout()
        self.combo_var = QComboBox()
        for texto, col, unidad in VARIABLES_GRAFICO:
            self.combo_var.addItem(f"{texto} ({unidad})", (col, unidad))
        self.combo_var.currentIndexChanged.connect(self.redibujar_grafico)
        fila_var.addWidget(self.combo_var, stretch=1)
        fila_dia = QHBoxLayout()
        fila_dia.addWidget(QLabel("Día:"))
        self.combo_dia = QComboBox()
        self.combo_dia.currentIndexChanged.connect(self.redibujar_grafico)
        fila_dia.addWidget(self.combo_dia, stretch=1)
        btn = QPushButton("↻ Actualizar")
        btn.clicked.connect(self.sig_mediciones.emit)
        fila_dia.addWidget(btn)
        self.lay_barra_graf.addLayout(fila_var, stretch=3)
        self.lay_barra_graf.addLayout(fila_dia, stretch=2)
        v.addLayout(self.lay_barra_graf)

        self.figura = Figure(figsize=(5, 3), tight_layout=True, facecolor="#0f1115")
        self.lienzo = FigureCanvasQTAgg(self.figura)
        self.lienzo.setMinimumSize(200, 150)
        v.addWidget(self.lienzo, stretch=1)
        self.lbl_grafico = QLabel("")
        self.lbl_grafico.setStyleSheet("color:#9aa4b2;")
        v.addWidget(self.lbl_grafico)
        return w

    def _luz(self, texto):
        lbl = QLabel("⚪ " + texto)
        lbl.setStyleSheet("font-size:14px;")
        return lbl

    def _pintar_luz(self, lbl, texto, ok):
        color = "🟢" if ok else "🔴"
        lbl.setText(f"{color} {texto}")

    def _texto_intervalo(self, seg):
        """Texto legible de un intervalo en segundos (para el 'actual: ...')."""
        for texto, s in OPCIONES_INTERVALO:
            if s == seg:
                return texto
        if seg % 60 == 0:
            return f"{seg // 60} min"
        return f"{seg} seg"

    # ---------- red (hilo aparte) ----------
    def _arrancar_red(self):
        self.hilo = QThread()
        self.red = Red(self.url, self.carpeta)
        self.red.moveToThread(self.hilo)
        self.sig_consultar.connect(self.red.consultar)
        self.sig_aplicar.connect(self.red.aplicar)
        self.sig_captura.connect(self.red.captura)
        self.sig_hora.connect(self.red.hora)
        self.sig_mediciones.connect(self.red.bajar_mediciones)
        self.red.estado.connect(self._al_estado)
        self.red.aplicado.connect(self._al_aplicado)
        self.red.captura_hecha.connect(self._al_captura)
        self.red.hora_hecha.connect(self._al_hora)
        self.red.mediciones_bajadas.connect(self._al_mediciones)
        self.hilo.start()

    def _al_estado(self, est):
        self._estado = est
        if est is None:
            self._pintar_luz(self.lbl_servidor, "Servidor", False)
            self._pintar_luz(self.lbl_camara, "Cámara", False)
            self._pintar_luz(self.lbl_desc, "Descargador", False)
            self.lbl_total.setText("🖼️ sin conexión")
            self.lbl_captura.setText("⚪ Sin conexión con el Pi de la cámara")
            self.lbl_sensor.setText("—")
            self._desfase = None
            self.btn_iniciar.setEnabled(False)
            self.btn_detener.setEnabled(False)
            return

        # Captura
        capt = est.get("capturando", False)
        if capt:
            self.lbl_captura.setText("🟢 CAPTURANDO")
        elif est.get("camara_viva"):
            self.lbl_captura.setText("🟡 En espera (apretá Iniciar)")
        else:
            self.lbl_captura.setText("🔴 El programa de la cámara no responde")
        self.btn_iniciar.setEnabled(not capt)
        self.btn_detener.setEnabled(capt)

        # Hora y piranómetro
        self._desfase = est.get("desfase")
        sensor = est.get("sensor")
        if sensor:
            sat = "  ⚠ saturó" if sensor.get("sat") else ""
            self.lbl_sensor.setText(f"☀️ {sensor.get('g_now', '?')} W/m²   ·   "
                                    f"{sensor.get('v_now', '?')} V{sat}")
        else:
            self.lbl_sensor.setText("☁️ Sin datos del Arduino")
        self._pintar_luz(self.lbl_servidor, "Servidor", est.get("servidor_ok"))
        self._pintar_luz(self.lbl_camara,
                         "Cámara " + est.get("camara_txt", ""), est.get("camara_ok"))
        self._pintar_luz(self.lbl_desc, "Descargador", est.get("desc_ok"))
        self.lbl_total.setText(f"🖼️ {est.get('total_fotos', 0)} fotos")
        inter = est.get("intervalo_camara")
        if inter:
            self.lbl_actual.setText(f"actual: {self._texto_intervalo(inter)}")
            # Si el intervalo actual coincide con una opción, la deja seleccionada.
            idx = self.combo.findData(inter)
            if idx >= 0 and not self.combo.hasFocus():
                self.combo.setCurrentIndex(idx)

    def _al_aplicar(self):
        self.btn_aplicar.setEnabled(False)
        self.btn_aplicar.setText("Aplicando...")
        self.sig_aplicar.emit(int(self.combo.currentData()))

    def _al_aplicado(self, resp):
        self.btn_aplicar.setEnabled(True)
        self.btn_aplicar.setText("Aplicar")
        if resp and resp.get("ok"):
            nuevo = resp.get("intervalo_camara")
            self.lbl_actual.setText(f"actual: {self._texto_intervalo(nuevo)}")
            QMessageBox.information(self, "Listo",
                                    f"Nuevo intervalo: {self._texto_intervalo(nuevo)}.\n"
                                    "La cámara lo toma en el próximo ciclo.")
        else:
            QMessageBox.warning(self, "Error",
                                "No se pudo cambiar el intervalo.\n"
                                "¿El servidor está encendido y conectado?")

    # ---------- captura ----------
    def _al_iniciar(self):
        """Antes de iniciar, verifica que la hora del Pi de la cámara esté bien."""
        if self._estado and not self._estado.get("hora_ajustada"):
            caja = QMessageBox(self)
            caja.setIcon(QMessageBox.Icon.Warning)
            caja.setWindowTitle("Hora sin ajustar")
            caja.setText("La hora del Pi de la cámara no se ajustó desde que se "
                         "prendió.\nLas fotos van a tener fecha y hora incorrectas.\n\n"
                         "¿Enviar la hora de este Pi antes de iniciar?")
            enviar = caja.addButton("Enviar hora e iniciar",
                                    QMessageBox.ButtonRole.AcceptRole)
            igual = caja.addButton("Iniciar igual", QMessageBox.ButtonRole.DestructiveRole)
            caja.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
            caja.exec()
            if caja.clickedButton() is enviar:
                self._iniciar_despues_de_hora = True
                self.sig_hora.emit(time.time())
            elif caja.clickedButton() is igual:
                self.sig_captura.emit("iniciar")
            return
        self.sig_captura.emit("iniciar")

    def _al_captura(self, resp):
        if not resp or not resp.get("ok"):
            QMessageBox.warning(self, "Error",
                                "No se pudo cambiar la captura.\n"
                                "¿El Pi de la cámara está encendido y conectado?")
        self.sig_consultar.emit()

    # ---------- fecha y hora ----------
    def _tic_reloj(self):
        ahora = time.time()
        self.lbl_hora_local.setText(datetime.fromtimestamp(ahora).strftime("%d/%m/%Y  %H:%M:%S"))
        if self._desfase is None:
            self.lbl_hora_pi.setText("— (sin conexión)")
            self.lbl_desfase.setText("")
            return
        self.lbl_hora_pi.setText(
            datetime.fromtimestamp(ahora + self._desfase).strftime("%d/%m/%Y  %H:%M:%S"))
        ajustada = self._estado and self._estado.get("hora_ajustada")
        d = self._desfase
        if abs(d) < 5:
            txt, color = "✔ igual a este Pi", "#22c55e"
        else:
            txt, color = f"diferencia {d:+.0f} s", "#ef4444"
        if not ajustada:
            txt += " · sin ajustar desde que prendió"
            color = "#f59e0b" if abs(d) < 5 else color
        self.lbl_desfase.setText(txt)
        self.lbl_desfase.setStyleSheet(f"color:{color};")

    def _al_enviar_hora(self):
        epoch = float(self.edit_hora.dateTime().toSecsSinceEpoch())
        self.sig_hora.emit(epoch)

    def _al_hora(self, resp):
        iniciar = self._iniciar_despues_de_hora
        self._iniciar_despues_de_hora = False
        if resp and resp.get("ok"):
            if iniciar:
                self.sig_captura.emit("iniciar")
            else:
                QMessageBox.information(self, "Listo",
                                        f"Hora del Pi de la cámara: {resp.get('hora_pi_txt')}")
        else:
            QMessageBox.warning(self, "Error",
                                "No se pudo ajustar la hora.\n"
                                + (resp or {}).get("error", "Sin conexión."))
        self.sig_consultar.emit()

    # ---------- gráfico ----------
    def _al_mediciones(self, ok):
        if not ok:
            QMessageBox.warning(self, "Error", "No se pudieron bajar las mediciones "
                                "(¿todavía no hay fotos con medición?).")
        self.redibujar_grafico()

    def _leer_mediciones(self):
        ruta = os.path.join(self.carpeta, "mediciones.csv")
        filas = []
        try:
            with open(ruta, "r", encoding="utf-8", newline="") as f:
                for fila in csv.DictReader(f):
                    try:
                        fila["_t"] = datetime.strptime(fila["fecha_hora"], "%Y-%m-%d %H:%M:%S")
                    except (KeyError, TypeError, ValueError):
                        continue
                    filas.append(fila)
        except OSError:
            pass
        return filas

    def redibujar_grafico(self):
        if not HAY_MATPLOTLIB:
            return
        filas = self._leer_mediciones()

        # Lista de días (sin disparar redibujos mientras se rellena)
        dias = sorted({f["_t"].date() for f in filas}, reverse=True)
        elegido = self.combo_dia.currentData()
        self.combo_dia.blockSignals(True)
        self.combo_dia.clear()
        self.combo_dia.addItem("Todos", None)
        for d in dias:
            self.combo_dia.addItem(d.strftime("%d/%m/%Y"), d)
        idx = self.combo_dia.findData(elegido) if elegido else (1 if dias else 0)
        self.combo_dia.setCurrentIndex(max(0, idx))
        self.combo_dia.blockSignals(False)

        col, unidad = self.combo_var.currentData()
        dia = self.combo_dia.currentData()

        def num(f, c):
            try:
                return float(f[c])
            except (KeyError, TypeError, ValueError):
                return None

        puntos = [(f["_t"], num(f, col), f) for f in filas
                  if (dia is None or f["_t"].date() == dia) and num(f, col) is not None]

        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.set_facecolor("#161a22")
        for borde in ax.spines.values():
            borde.set_color("#2a2f3a")
        ax.tick_params(colors="#9aa4b2", labelsize=8)
        if puntos:
            xs = [p[0] for p in puntos]
            ys = [p[1] for p in puntos]
            if col == "g_avg":
                banda = [(p[0], num(p[2], "g_min"), num(p[2], "g_max")) for p in puntos]
                banda = [b for b in banda if b[1] is not None and b[2] is not None]
                if banda:
                    ax.fill_between([b[0] for b in banda], [b[1] for b in banda],
                                    [b[2] for b in banda], color="#f59e0b", alpha=0.2,
                                    label="mín–máx entre fotos")
            ax.plot(xs, ys, "-o", color="#f59e0b", markersize=3, linewidth=1.2,
                    label="una medición por foto")
            ax.legend(loc="upper left", fontsize=7, facecolor="#161a22",
                      edgecolor="#2a2f3a", labelcolor="#e6e6e6")
            loc = mdates.AutoDateLocator(maxticks=6)
            ax.xaxis.set_major_locator(loc)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
            self.lbl_grafico.setText(f"{len(puntos)} mediciones  ·  "
                                     f"{xs[0]:%d/%m %H:%M} → {xs[-1]:%d/%m %H:%M}")
        else:
            ax.text(0.5, 0.5, "Sin mediciones todavía", ha="center", va="center",
                    transform=ax.transAxes, color="#6b7280")
            self.lbl_grafico.setText("Apretá “Actualizar datos” (o esperá al descargador).")
        ax.set_ylabel(unidad, color="#9aa4b2", fontsize=9)
        ax.grid(True, color="#2a2f3a")
        self.lienzo.draw_idle()

    # ---------- galería ----------
    def _listar_fotos_local(self):
        fotos = []
        for raiz, _dirs, archivos in os.walk(self.carpeta):
            for a in archivos:
                if a.lower().endswith(".jpg"):
                    ruta = os.path.join(raiz, a)
                    fotos.append((os.path.getmtime(ruta), ruta, a))
        fotos.sort(reverse=True)  # más nuevas primero
        return fotos

    def _columnas_galeria(self):
        """Cuántas miniaturas entran a lo ancho (mínimo 1)."""
        ancho = self.scroll.viewport().width() - 12
        return max(1, ancho // (MINI_ANCHO + self.grid.horizontalSpacing() + 2))

    def _ajustar_galeria(self):
        """Tras un cambio de tamaño, rearma la galería si cambian las columnas."""
        if self.pestanas.currentIndex() == 1 and self._columnas_galeria() != self._columnas:
            self.refrescar_galeria(forzar=True)

    def refrescar_galeria(self, forzar=False):
        fotos = self._listar_fotos_local()
        claves = tuple(a for _m, _r, a in fotos[:MAX_MINIATURAS])
        if claves == self._fotos_mostradas and not forzar:
            return  # nada cambió, evitamos reconstruir
        self._fotos_mostradas = claves

        # Vaciar la grilla
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not fotos:
            self.grid.addWidget(QLabel("Todavía no hay fotos descargadas."), 0, 0)
            return

        columnas = self._columnas = self._columnas_galeria()
        fila = col = 0
        dia_actual = None
        for _m, ruta, nombre in fotos[:MAX_MINIATURAS]:
            dia = self._dia_de(nombre)
            if dia != dia_actual:
                dia_actual = dia
                if col != 0:
                    fila += 1
                    col = 0
                cab = QLabel(f"📅 {dia}")
                cab.setStyleSheet("font-weight:bold; color:#cbd5e1; margin-top:6px;")
                self.grid.addWidget(cab, fila, 0, 1, columnas)
                fila += 1
            self.grid.addWidget(Miniatura(ruta), fila, col)
            col += 1
            if col >= columnas:
                col = 0
                fila += 1

    def _dia_de(self, nombre):
        import re
        m = re.search(r"_(\d{2})(\d{2})(\d{4})_", nombre)
        return f"{m.group(1)}/{m.group(2)}/{m.group(3)}" if m else "sin fecha"

    def closeEvent(self, ev):
        self.hilo.quit()
        self.hilo.wait(1000)
        ev.accept()


def main():
    config = cargar_config()
    app = QApplication(sys.argv)
    v = Ventana(config)

    # Pantalla completa: "si", "no" o "auto" (solo en pantallas chicas,
    # como la de 5"). Con --ventana se fuerza ventana normal.
    modo = config.get("ihm", "pantalla_completa", fallback="auto").strip().lower()
    disp = app.primaryScreen().availableGeometry()
    chica = disp.width() <= PANTALLA_CHICA[0] or disp.height() <= PANTALLA_CHICA[1]
    if "--ventana" not in sys.argv and (modo == "si" or (modo == "auto" and chica)):
        v.showFullScreen()
    else:
        v.resize(min(900, disp.width()), min(680, disp.height()))
        v.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
