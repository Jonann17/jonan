#!/usr/bin/env python3
"""
ihm.py  —  Interfaz gráfica (IHM) para el Raspberry externo (Pi B), en PyQt6.

Permite:
  * Ver el ESTADO del sistema (servidor / cámara / descargador) con luces.
  * Ver la GALERÍA de fotos descargadas (agrupadas por día).
  * AJUSTAR el intervalo entre fotos de la cámara, de forma remota
    (se lo envía al servidor y la cámara lo toma sin reiniciar).

Requisitos en el Pi:
    sudo apt install -y python3-pyqt6 python3-requests
    # (si no está el paquete apt:  pip3 install PyQt6 requests)

Uso:
    python3 ihm/ihm.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comun import cargar_config, asegurar_carpeta

import requests
from PyQt6.QtCore import Qt, QThread, QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QSpinBox, QVBoxLayout,
    QHBoxLayout, QGridLayout, QScrollArea, QFrame, QGroupBox, QDialog,
    QMessageBox,
)

# Cuántas miniaturas mostrar como máximo (para no saturar el Pi 3).
MAX_MINIATURAS = 60


# ------------------------------------------------------------------
#  Worker de red: corre en otro hilo para no congelar la interfaz.
# ------------------------------------------------------------------
class Red(QObject):
    estado = pyqtSignal(object)     # dict con el estado, o None si falló
    aplicado = pyqtSignal(object)   # dict con el nuevo intervalo, o None

    def __init__(self, url_servidor):
        super().__init__()
        self.url = url_servidor.rstrip("/")

    @pyqtSlot()
    def consultar(self):
        try:
            r = requests.get(self.url + "/estado", timeout=5)
            self.estado.emit(r.json() if r.ok else None)
        except requests.RequestException:
            self.estado.emit(None)

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

    def __init__(self, config):
        super().__init__()
        self.carpeta = asegurar_carpeta(config["descargador"]["carpeta_local"])
        self.url = config["descargador"]["url_servidor"]
        self._fotos_mostradas = None  # para no reconstruir la galería sin cambios

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

    # ---------- construcción de la interfaz ----------
    def _construir_ui(self):
        self.setStyleSheet("""
            QWidget { background:#0f1115; color:#e6e6e6; font-family:sans-serif; }
            QGroupBox { border:1px solid #2a2f3a; border-radius:10px; margin-top:1ex; padding:8px; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; color:#9aa4b2; }
            QPushButton { background:#2563eb; color:#fff; border:none; padding:6px 12px; border-radius:8px; }
            QPushButton:hover { background:#1d4ed8; }
            QSpinBox { background:#161a22; border:1px solid #2a2f3a; padding:4px; border-radius:6px; color:#e6e6e6; }
        """)
        raiz = QVBoxLayout(self)

        titulo = QLabel("📷 Panel de control de la webcam")
        titulo.setStyleSheet("font-size:18px; font-weight:bold;")
        raiz.addWidget(titulo)

        # --- Fila de estado (luces) ---
        caja_estado = QGroupBox("Estado del sistema")
        fila = QHBoxLayout(caja_estado)
        self.lbl_servidor = self._luz("Servidor")
        self.lbl_camara = self._luz("Cámara")
        self.lbl_desc = self._luz("Descargador")
        self.lbl_total = QLabel("🖼️ 0 fotos")
        for w in (self.lbl_servidor, self.lbl_camara, self.lbl_desc):
            fila.addWidget(w)
        fila.addStretch()
        fila.addWidget(self.lbl_total)
        raiz.addWidget(caja_estado)

        # --- Configuración del intervalo ---
        caja_cfg = QGroupBox("Intervalo entre fotos")
        cfg = QHBoxLayout(caja_cfg)
        cfg.addWidget(QLabel("Sacar una foto cada"))
        self.spin = QSpinBox()
        self.spin.setRange(5, 86400)
        self.spin.setValue(600)
        self.spin.setSuffix(" seg")
        self.spin.valueChanged.connect(self._actualizar_equivalencia)
        cfg.addWidget(self.spin)
        self.lbl_equiv = QLabel("(= 10 min)")
        self.lbl_equiv.setStyleSheet("color:#9aa4b2;")
        cfg.addWidget(self.lbl_equiv)
        self.btn_aplicar = QPushButton("Aplicar")
        self.btn_aplicar.clicked.connect(self._al_aplicar)
        cfg.addWidget(self.btn_aplicar)
        cfg.addStretch()
        self.lbl_actual = QLabel("actual: —")
        self.lbl_actual.setStyleSheet("color:#9aa4b2;")
        cfg.addWidget(self.lbl_actual)
        raiz.addWidget(caja_cfg)

        # --- Galería ---
        caja_gal = QGroupBox("Fotos descargadas")
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
        raiz.addWidget(caja_gal, stretch=1)

        self._actualizar_equivalencia(self.spin.value())

    def _luz(self, texto):
        lbl = QLabel("⚪ " + texto)
        lbl.setStyleSheet("font-size:14px;")
        return lbl

    def _pintar_luz(self, lbl, texto, ok):
        color = "🟢" if ok else "🔴"
        lbl.setText(f"{color} {texto}")

    def _actualizar_equivalencia(self, seg):
        if seg < 60:
            txt = f"(= {seg} seg)"
        elif seg % 60 == 0:
            txt = f"(= {seg // 60} min)"
        else:
            txt = f"(= {seg // 60} min {seg % 60} s)"
        self.lbl_equiv.setText(txt)

    # ---------- red (hilo aparte) ----------
    def _arrancar_red(self):
        self.hilo = QThread()
        self.red = Red(self.url)
        self.red.moveToThread(self.hilo)
        self.sig_consultar.connect(self.red.consultar)
        self.sig_aplicar.connect(self.red.aplicar)
        self.red.estado.connect(self._al_estado)
        self.red.aplicado.connect(self._al_aplicado)
        self.hilo.start()

    def _al_estado(self, est):
        if est is None:
            self._pintar_luz(self.lbl_servidor, "Servidor", False)
            self._pintar_luz(self.lbl_camara, "Cámara", False)
            self._pintar_luz(self.lbl_desc, "Descargador", False)
            self.lbl_total.setText("🖼️ sin conexión")
            return
        self._pintar_luz(self.lbl_servidor, "Servidor", est.get("servidor_ok"))
        self._pintar_luz(self.lbl_camara,
                         "Cámara " + est.get("camara_txt", ""), est.get("camara_ok"))
        self._pintar_luz(self.lbl_desc, "Descargador", est.get("desc_ok"))
        self.lbl_total.setText(f"🖼️ {est.get('total_fotos', 0)} fotos")
        inter = est.get("intervalo_camara")
        if inter:
            self.lbl_actual.setText(f"actual: {inter} seg")

    def _al_aplicar(self):
        self.btn_aplicar.setEnabled(False)
        self.btn_aplicar.setText("Aplicando...")
        self.sig_aplicar.emit(self.spin.value())

    def _al_aplicado(self, resp):
        self.btn_aplicar.setEnabled(True)
        self.btn_aplicar.setText("Aplicar")
        if resp and resp.get("ok"):
            nuevo = resp.get("intervalo_camara")
            self.lbl_actual.setText(f"actual: {nuevo} seg")
            QMessageBox.information(self, "Listo",
                                    f"Nuevo intervalo: {nuevo} segundos.\n"
                                    "La cámara lo toma en el próximo ciclo.")
        else:
            QMessageBox.warning(self, "Error",
                                "No se pudo cambiar el intervalo.\n"
                                "¿El servidor está encendido y conectado?")

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
