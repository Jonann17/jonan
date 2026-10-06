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

Requisitos en el Pi:
    sudo apt install -y python3-pyqt6 python3-requests python3-matplotlib
    # (si no está el paquete apt:  pip3 install PyQt6 requests matplotlib)

Uso:
    python3 ihm/ihm.py
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
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QFrame, QGroupBox, QDialog,
    QMessageBox, QTabWidget, QDateTimeEdit,
)

# matplotlib es opcional: sin él, la pestaña Gráfico avisa cómo instalarlo.
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    HAY_MATPLOTLIB = True
except ImportError:
    HAY_MATPLOTLIB = False

# Cuántas miniaturas mostrar como máximo (para no saturar el Pi 3).
MAX_MINIATURAS = 60

# Opciones de intervalo entre fotos: (texto, segundos)
OPCIONES_INTERVALO = [
    ("1 minuto", 60),
    ("5 minutos", 300),
    ("10 minutos", 600),
    ("20 minutos", 1200),
    ("30 minutos", 1800),
    ("1 hora", 3600),
]

# Variables que se pueden graficar: (texto, columna de mediciones.csv)
VARIABLES_GRAFICO = [
    ("Radiación media entre fotos (W/m²)", "g_avg"),
    ("Radiación en el momento de la foto (W/m²)", "g_now"),
    ("Tensión media de la celda (V)", "v_avg"),
    ("Potencia media P = V²/R (mW)", "p_avg_mw"),
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
            self.setPixmap(pix.scaled(160, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation))
        self.setFixedSize(170, 130)
        self.setStyleSheet("border:1px solid #2a2f3a; background:#000;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(os.path.basename(ruta))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, _ev):
        self.ver_grande()

    def ver_grande(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(os.path.basename(self.ruta))
        lay = QVBoxLayout(dlg)
        lbl = QLabel()
        pix = QPixmap(self.ruta)
        if not pix.isNull():
            lbl.setPixmap(pix.scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation))
        lay.addWidget(lbl)
        dlg.exec()


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

        self.setWindowTitle("IHM Webcam — Raspberry Pi")
        self.resize(820, 620)
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

    # ---------- construcción de la interfaz ----------
    def _construir_ui(self):
        self.setStyleSheet("""
            QWidget { background:#0f1115; color:#e6e6e6; font-family:sans-serif; }
            QGroupBox { border:1px solid #2a2f3a; border-radius:10px; margin-top:1ex; padding:8px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; color:#9aa4b2; }
            QPushButton { background:#2563eb; color:#fff; border:none; padding:6px 12px; border-radius:8px; }
            QPushButton:hover { background:#1d4ed8; }
            QComboBox { background:#161a22; border:1px solid #2a2f3a; padding:4px 8px; border-radius:6px; color:#e6e6e6; min-width:120px; }
            QComboBox QAbstractItemView { background:#161a22; color:#e6e6e6; selection-background-color:#2563eb; }
        """)
        raiz = QVBoxLayout(self)

        titulo = QLabel("📷 Panel de control de la webcam")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        raiz.addWidget(titulo)

        pestanas = QTabWidget()
        pestanas.setStyleSheet("""
            QTabBar::tab { background:#161a22; color:#9aa4b2; padding:6px 14px;
                           border:1px solid #2a2f3a; border-bottom:none;
                           border-top-left-radius:8px; border-top-right-radius:8px; }
            QTabBar::tab:selected { background:#2563eb; color:#fff; }
            QTabWidget::pane { border:1px solid #2a2f3a; border-radius:8px; }
        """)
        pestanas.addTab(self._pestana_control(), "Control")
        pestanas.addTab(self._pestana_fotos(), "Fotos")
        pestanas.addTab(self._pestana_grafico(), "Gráfico")
        raiz.addWidget(pestanas, stretch=1)

    # ---------- pestaña Control ----------
    def _pestana_control(self):
        w = QWidget()
        raiz = QVBoxLayout(w)

        # --- Fila de estado (luces) ---
        caja_estado = QGroupBox("Estado del sistema")
        fila = QHBoxLayout(caja_estado)
        self.lbl_servidor = self._luz("Servidor")
        self.lbl_camara = self._luz("Cámara")
        self.lbl_desc = self._luz("Descargador")
        self.lbl_total = QLabel("🖼️ 0 fotos")
        for x in (self.lbl_servidor, self.lbl_camara, self.lbl_desc):
            fila.addWidget(x)
        fila.addStretch()
        fila.addWidget(self.lbl_total)
        raiz.addWidget(caja_estado)

        # --- Captura: iniciar / detener ---
        caja_cap = QGroupBox("Captura de fotos")
        cap = QHBoxLayout(caja_cap)
        self.lbl_captura = QLabel("⚪ —")
        self.lbl_captura.setStyleSheet("font-size:16px; font-weight:bold;")
        cap.addWidget(self.lbl_captura)
        cap.addStretch()
        self.btn_iniciar = QPushButton("▶  Iniciar captura")
        self.btn_iniciar.setStyleSheet("QPushButton { background:#16a34a; font-weight:bold; padding:8px 16px; }"
                                       "QPushButton:disabled { background:#2a2f3a; color:#6b7280; }")
        self.btn_iniciar.clicked.connect(self._al_iniciar)
        self.btn_detener = QPushButton("⏹  Detener")
        self.btn_detener.setStyleSheet("QPushButton { background:#dc2626; font-weight:bold; padding:8px 16px; }"
                                       "QPushButton:disabled { background:#2a2f3a; color:#6b7280; }")
        self.btn_detener.clicked.connect(lambda: self.sig_captura.emit("detener"))
        cap.addWidget(self.btn_iniciar)
        cap.addWidget(self.btn_detener)
        raiz.addWidget(caja_cap)

        # --- Configuración del intervalo ---
        caja_cfg = QGroupBox("Intervalo entre fotos")
        cfg = QHBoxLayout(caja_cfg)
        cfg.addWidget(QLabel("Sacar una foto cada"))
        self.combo = QComboBox()
        for texto, seg in OPCIONES_INTERVALO:
            self.combo.addItem(texto, seg)
        self.combo.setCurrentIndex(2)  # 10 minutos por defecto
        cfg.addWidget(self.combo)
        self.btn_aplicar = QPushButton("Aplicar")
        self.btn_aplicar.clicked.connect(self._al_aplicar)
        cfg.addWidget(self.btn_aplicar)
        cfg.addStretch()
        self.lbl_actual = QLabel("actual: —")
        self.lbl_actual.setStyleSheet("color:#9aa4b2;")
        cfg.addWidget(self.lbl_actual)
        raiz.addWidget(caja_cfg)

        # --- Fecha y hora del Pi de la cámara ---
        caja_hora = QGroupBox("Fecha y hora del Pi de la cámara (no tiene internet)")
        gh = QGridLayout(caja_hora)
        self.lbl_hora_pi = QLabel("—")
        self.lbl_hora_pi.setStyleSheet("font-size:16px; font-weight:bold;")
        self.lbl_hora_local = QLabel("—")
        self.lbl_hora_local.setStyleSheet("font-size:16px;")
        self.lbl_desfase = QLabel("—")
        gh.addWidget(QLabel("Pi de la cámara:"), 0, 0)
        gh.addWidget(self.lbl_hora_pi, 0, 1)
        gh.addWidget(self.lbl_desfase, 0, 2)
        gh.addWidget(QLabel("Este Pi:"), 1, 0)
        gh.addWidget(self.lbl_hora_local, 1, 1)
        self.edit_hora = QDateTimeEdit(QDateTime.currentDateTime())
        self.edit_hora.setDisplayFormat("dd/MM/yyyy  HH:mm:ss")
        self.edit_hora.setCalendarPopup(True)
        self.edit_hora.setStyleSheet("background:#161a22; border:1px solid #2a2f3a; padding:4px;")
        gh.addWidget(QLabel("Hora a enviar:"), 2, 0)
        gh.addWidget(self.edit_hora, 2, 1)
        btn_ahora = QPushButton("Usar la hora de este Pi")
        btn_ahora.clicked.connect(
            lambda: self.edit_hora.setDateTime(QDateTime.currentDateTime()))
        gh.addWidget(btn_ahora, 2, 2)
        btn_enviar = QPushButton("⏱  Enviar hora al Pi de la cámara")
        btn_enviar.clicked.connect(self._al_enviar_hora)
        gh.addWidget(btn_enviar, 3, 0, 1, 3)
        raiz.addWidget(caja_hora)

        # --- Piranómetro en vivo ---
        caja_sol = QGroupBox("Piranómetro (Arduino) — en vivo")
        hs = QHBoxLayout(caja_sol)
        self.lbl_sensor = QLabel("—")
        self.lbl_sensor.setStyleSheet("font-size:20px; font-weight:bold;")
        hs.addWidget(self.lbl_sensor)
        hs.addStretch()
        raiz.addWidget(caja_sol)

        raiz.addStretch()
        return w

    # ---------- pestaña Fotos ----------
    def _pestana_fotos(self):
        caja_gal = QWidget()
        vg = QVBoxLayout(caja_gal)
        barra = QHBoxLayout()
        btn_ref = QPushButton("↻ Refrescar galería")
        btn_ref.clicked.connect(self.refrescar_galeria)
        barra.addWidget(btn_ref)
        barra.addStretch()
        vg.addLayout(barra)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
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

        barra = QHBoxLayout()
        barra.addWidget(QLabel("Variable:"))
        self.combo_var = QComboBox()
        for texto, col in VARIABLES_GRAFICO:
            self.combo_var.addItem(texto, col)
        self.combo_var.currentIndexChanged.connect(self.redibujar_grafico)
        barra.addWidget(self.combo_var)
        barra.addWidget(QLabel("Día:"))
        self.combo_dia = QComboBox()
        self.combo_dia.currentIndexChanged.connect(self.redibujar_grafico)
        barra.addWidget(self.combo_dia)
        btn = QPushButton("↻ Actualizar datos")
        btn.clicked.connect(self.sig_mediciones.emit)
        barra.addWidget(btn)
        barra.addStretch()
        v.addLayout(barra)

        self.figura = Figure(figsize=(7, 4), tight_layout=True, facecolor="#0f1115")
        self.lienzo = FigureCanvasQTAgg(self.figura)
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

        col = self.combo_var.currentData()
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
        ax.tick_params(colors="#9aa4b2")
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
            ax.legend(loc="upper left", fontsize=8, facecolor="#161a22",
                      edgecolor="#2a2f3a", labelcolor="#e6e6e6")
            loc = mdates.AutoDateLocator()
            ax.xaxis.set_major_locator(loc)
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
            self.lbl_grafico.setText(f"{len(puntos)} mediciones  ·  "
                                     f"{xs[0]:%d/%m %H:%M} → {xs[-1]:%d/%m %H:%M}")
        else:
            ax.text(0.5, 0.5, "Sin mediciones todavía", ha="center", va="center",
                    transform=ax.transAxes, color="#6b7280")
            self.lbl_grafico.setText("Apretá “Actualizar datos” (o esperá al descargador).")
        ax.set_ylabel(self.combo_var.currentText(), color="#9aa4b2")
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

    def refrescar_galeria(self):
        fotos = self._listar_fotos_local()
        claves = tuple(a for _m, _r, a in fotos[:MAX_MINIATURAS])
        if claves == self._fotos_mostradas:
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

        columnas = 4
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
    v.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
