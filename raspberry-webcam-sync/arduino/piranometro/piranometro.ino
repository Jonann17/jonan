/*
 * ============================================================================
 *  piranometro.ino — Arduino UNO conectado al Pi A (cámara + servidor)
 * ============================================================================
 *
 *  BASADO EN: "Measuring Solar Radiation with Arduino" (Jeffrey, Hackster.io)
 *  https://www.hackster.io/jeffrey2/measuring-solar-radiation-with-arduino-f741ac
 *  — sin el Ethernet Shield: los datos van al Pi A por el cable serie
 *  (GPIO 14/15), y camara/camara.py los guarda junto con cada foto en
 *  mediciones.csv.
 *
 *  ¿QUÉ HACE ESTA PLACA?
 *  ---------------------
 *  Funciona como un PIRANÓMETRO CASERO: estima la radiación solar (W/m²)
 *  a partir de una celda solar chica.
 *
 *    1. Mide 5 veces por segundo, TODO el tiempo, la tensión de la celda.
 *    2. Con la idea del artículo calcula la potencia y la divide por el
 *       área de la celda:
 *              Potencia  P = V² / R
 *              Área      A = largo × ancho
 *              Radiación G = P / A
 *    3. Va acumulando estadísticas (promedio, mínimo, máximo, desvío).
 *    4. Cuando el Pi A le manda "GET", responde UNA línea JSON con
 *       el resumen desde la última foto y reinicia la ventana. Con "NOW"
 *       responde lo mismo SIN reiniciar (para el "en vivo" de la IHM).
 *
 *  ¿QUÉ CORREGIMOS DEL CÓDIGO ORIGINAL?
 *  ------------------------------------
 *  El código del artículo tiene errores que lo hacen dar resultados sin
 *  sentido (o colgar el Arduino). Acá están corregidos:
 *
 *    • Área: "60 * 20 / (100*100)" es una división ENTERA y da 0, así que
 *      después divide por cero. Además, de mm² a m² hay que dividir por
 *      1 000 000 (no por 10 000). Acá usamos números con coma (float).
 *    • Usaba analogRead() "crudo" (0 a 1023) como si fueran voltios. Acá
 *      lo convertimos a voltios reales con la tensión de referencia.
 *    • La resistencia estaba "en miles de ohms" (10) pero la fórmula la
 *      usaba como si fueran ohms. Acá va en ohms (10000).
 *    • "char *msg" sin memoria + sprintf("%f") (el Arduino UNO no imprime
 *      float con sprintf): cuelga o imprime basura. Acá usamos print().
 *
 *  ¡OJO CON LOS NÚMEROS!
 *  ---------------------
 *  Aun corregida, la fórmula P = V²/R no da la irradiancia "verdadera":
 *  la celda convierte solo ~15 % de la luz en electricidad y, con la
 *  resistencia en serie hacia A0, casi no circula corriente. El valor es
 *  un ÍNDICE que sube y baja con el sol. Para llevarlo a W/m² reales se
 *  usa CAL_K (ver Sección 1): se compara con una referencia (por ejemplo,
 *  la estación automática del INMET en Foz do Iguaçu) y se ajusta.
 *
 *  ALTERNATIVA (más lineal): MODO_SHUNT = 1. La celda queda casi en
 *  cortocircuito sobre una resistencia chica (~1 Ω) y se mide su
 *  corriente, que es PROPORCIONAL a la irradiancia: G = 1000·I/Isc.
 *
 *  EJEMPLO DE RESPUESTA (una sola línea):
 *  {"v_now":3.912,"adc_now":801,"v_avg":3.850,"v_min":3.701,"v_max":3.990,
 *   "v_std":0.0712,"p_avg_mw":1.483,"g_now":1.28,"g_avg":1.24,"g_min":1.14,
 *   "g_max":1.33,"g_std":0.05,"n_samples":2985,"window_s":600.2,"sat":0,
 *   "vcc":5.012}
 *
 *  Significado de cada campo:
 *    v_now / v_avg / v_min / v_max / v_std
 *              tensión medida en A0 [V]
 *    adc_now   valor "crudo" del conversor (0 a 1023)
 *    p_avg_mw  potencia promedio P = V²/R [mW]
 *    i_avg_ma  (solo MODO_SHUNT) corriente promedio de la celda [mA]
 *    g_now / g_avg / g_min / g_max / g_std
 *              radiación estimada [W/m²] (× CAL_K)
 *    n_samples cuántas mediciones entraron en la ventana
 *    window_s  cuántos segundos duró la ventana
 *    sat       muestras que llegaron al tope del ADC (1023). Si es > 0,
 *              la celda da más tensión de la que el Arduino puede medir.
 *    vcc       alimentación real del Arduino [V] (referencia del ADC)
 *
 *  CONEXIONES (ver arduino/esquematico_conexion.svg):
 *  ---------------------------------------------------------------
 *  Como en el artículo:
 *    Celda (+) ── R 10 kΩ ── A0      (¡la celda nunca más de 5 V!)
 *    Celda (−) ── GND
 *
 *    Pin 8 (RX)  <── conversor de nivel <── GPIO14 / TXD (pin 8)  de la Pi
 *    Pin 9 (TX)  ──> conversor de nivel ──> GPIO15 / RXD (pin 10) de la Pi
 *    GND         <─> GND de la Pi (imprescindible)
 *    5V          <── 5V de la Pi (pin 2)
 *
 *  CÓMO PROBARLO SOLO (sin el Pi):
 *  -----------------------------------
 *  Subir el sketch, abrir el Monitor Serie a 9600 baudios, escribir NOW
 *  o GET y dar Enter. Debe responder la línea JSON.
 * ============================================================================
 */

// SoftwareSerial crea un puerto serie "extra" en dos pines comunes. Así el
// puerto de fábrica (pines 0 y 1, el mismo del cable USB) queda libre
// para programar y depurar con el Monitor Serie mientras la Pi está
// conectada.
#include <SoftwareSerial.h>

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 1: CONFIGURACIÓN — los números que tenés que ajustar
// ════════════════════════════════════════════════════════════════════════

// 0 = método del artículo (P = V²/R, G = P/Área)   ← el que usamos
// 1 = método shunt (corriente de cortocircuito)     ← alternativa
#define MODO_SHUNT 0

const uint8_t PIN_PI_RX = 8;    // Pin 8: por acá RECIBIMOS lo que manda la Pi
const uint8_t PIN_PI_TX = 9;    // Pin 9: por acá le ENVIAMOS la respuesta
const uint8_t PIN_CELDA = A0;   // Entrada analógica (el ANALOG_PIN del artículo)

// ── Resistencia [Ω] ──
// Artículo: 10 kΩ en serie (el RESISTANCE = 10 "miles de ohms" del código).
// Medila con el multímetro y escribí el valor REAL.
// En MODO_SHUNT: la resistencia chica en paralelo con la celda (~1 Ω).
#if MODO_SHUNT
const float RESISTENCIA_OHM = 1.0;
#else
const float RESISTENCIA_OHM = 10000.0;
#endif

// ── Tamaño de la celda [mm] (PANEL_LENGTH y PANEL_WIDTH del artículo) ──
// Medí con una regla SOLO la parte que capta luz.
const float CELDA_LARGO_MM = 60.0;
const float CELDA_ANCHO_MM = 20.0;

// ── Solo para MODO_SHUNT: Isc de la etiqueta de la celda [A] ──
const float ISC_STC_A = 0.50;

// ── Factor de calibración ──
// Empezá con 1.0. Para pasar a W/m² reales, compará con una referencia
// (piranómetro de verdad o estación del INMET) en varios momentos:
//     CAL_K = G_referencia / G_que_mide_este_equipo
const float CAL_K = 1.0;

// ── Referencia del conversor analógico ──
// Método del artículo: la celda llega a ~5 V, así que usamos la
// referencia de 5 V (la alimentación). Como esa tensión puede no ser
// exactamente 5.00 V, el chip la mide él mismo (ver readVccMillivolts).
// MODO_SHUNT: tensiones chiquitas → referencia interna de 1.1 V (medí el
// pin AREF con el multímetro y escribí el valor exacto).
const float VREF_FALLBACK = 5.0;
const float VREF_INTERNAL = 1.1;

// Cada cuántos milisegundos tomamos una muestra (el artículo usaba
// delay(1000); nosotros 200 ms para promediar mejor entre fotos).
const unsigned long SAMPLE_INTERVAL_MS = 200;

// Puerto serie por software hacia el Pi A, a 9600 baudios.
SoftwareSerial piSerial(PIN_PI_RX, PIN_PI_TX);

// Área en m²: mm × mm = mm², y 1 m² = 1 000 000 mm²
const float AREA_M2 = (CELDA_LARGO_MM * CELDA_ANCHO_MM) / 1000000.0;

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 2: VARIABLES DE ESTADO — la "memoria" del programa
// ════════════════════════════════════════════════════════════════════════
//
//  La "ventana de medición" es el período entre dos fotos. En vez de
//  guardar las ~3000 mediciones (¡el UNO tiene solo 2 KB de RAM!),
//  guardamos acumuladores: suma, suma de cuadrados, mínimo y máximo.
//  Acumulamos la tensión Y la radiación por separado, porque G depende
//  de V² y el promedio de V² NO es el cuadrado del promedio de V.

struct Stats {
  double sum, sum2;   // suma y suma de cuadrados
  float  mn, mx;      // mínimo y máximo
};

unsigned long nSamples    = 0;    // contador de muestras de la ventana
unsigned long nSaturated  = 0;    // muestras que llegaron al tope del ADC
Stats         sV, sG;             // estadísticas de tensión y de radiación
unsigned long windowStart = 0;    // millis() cuando empezó la ventana

float lastV   = 0.0;              // última tensión medida (para "v_now")
float lastG   = 0.0;              // última radiación calculada (para "g_now")
int   lastAdc = 0;                // última lectura cruda

float vrefVolts = VREF_FALLBACK;  // referencia actual del ADC [V]
unsigned long lastVccMs = 0;
const unsigned long VCC_INTERVAL_MS = 5000;

unsigned long lastSampleMs = 0;   // cuándo tomamos la última muestra

// Buffers donde juntamos letra por letra lo que llega hasta el Enter
String cmdPi  = "";   // lo que llega del Pi A
String cmdUsb = "";   // lo que llega del Monitor Serie

// Resultado de leer un comando
enum Command { CMD_NONE, CMD_GET, CMD_NOW };

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 3: CONVERSIONES Y MEDICIÓN
// ════════════════════════════════════════════════════════════════════════

// Tensión en A0 [V] → radiación [W/m²]
float voltsToRadiation(float v) {
#if MODO_SHUNT
  // I = V / R ;  G = 1000 × I / Isc  (la corriente es proporcional al sol)
  float amps = v / RESISTENCIA_OHM;
  return 1000.0 * (amps / ISC_STC_A) * CAL_K;
#else
  // Fórmula del artículo, corregida:  P = V² / R ;  G = P / Área
  float power = (v * v) / RESISTENCIA_OHM;   // [W]
  return (power / AREA_M2) * CAL_K;          // [W/m²]
#endif
}

// ── Auto-calibración de VCC (el "truco" del ATmega328) ──────────────
// El chip tiene adentro una referencia fija de 1.1 V. Si la medimos
// usando VCC como escala, despejamos cuánto vale VCC de verdad:
//     lectura = 1.1 / VCC × 1023   →   VCC = 1.1 × 1023 / lectura
long readVccMillivolts() {
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2);                            // deja estabilizar el multiplexor
  ADCSRA |= _BV(ADSC);                 // dispara una conversión
  while (bit_is_set(ADCSRA, ADSC));    // espera a que termine
  long result = ADC;
  if (result == 0) return (long)(VREF_FALLBACK * 1000);
  return 1125300L / result;            // 1.1 V × 1023 × 1000
}

void refreshVref() {
#if MODO_SHUNT
  vrefVolts = VREF_INTERNAL;           // referencia fija, no hay que medir
#else
  float v = readVccMillivolts() / 1000.0;
  vrefVolts = (v > 3.0 && v < 5.6) ? v : VREF_FALLBACK;
#endif
}

void statsReset(Stats &s, float first) {
  s.sum = s.sum2 = 0.0;
  s.mn = s.mx = first;
}

void statsAdd(Stats &s, float x, bool first) {
  if (first) {
    s.mn = s.mx = x;
  } else {
    if (x < s.mn) s.mn = x;
    if (x > s.mx) s.mx = x;
  }
  s.sum  += x;
  s.sum2 += (double)x * x;
}

// Promedio y desvío estándar:  var = E[x²] − (E[x])²
void statsResult(const Stats &s, float &avg, float &std) {
  avg = std = 0.0;
  if (nSamples == 0) return;
  avg = s.sum / nSamples;
  double var = (s.sum2 / nSamples) - ((double)avg * avg);
  if (var < 0) var = 0;    // corrige el -0.0000001 de redondeo
  std = sqrt(var);
}

// Empieza una ventana de medición nueva (después de cada "GET").
void resetWindow() {
  nSamples   = 0;
  nSaturated = 0;
  statsReset(sV, lastV);
  statsReset(sG, lastG);
  windowStart = millis();
}

// Toma UNA muestra y actualiza todos los acumuladores.
void takeSample() {
  lastAdc = analogRead(PIN_CELDA);               // 0 (=0 V) a 1023 (=VREF)
  lastV   = lastAdc * (vrefVolts / 1023.0);      // regla de tres → voltios
  lastG   = voltsToRadiation(lastV);

  if (lastAdc >= 1023) nSaturated++;             // pasó del tope

  bool first = (nSamples == 0);
  statsAdd(sV, lastV, first);
  statsAdd(sG, lastG, first);
  nSamples++;
}

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 4: ARMADO Y ENVÍO DEL REPORTE JSON
// ════════════════════════════════════════════════════════════════════════

// Escribe el JSON en una línea por el puerto "out". Si "reset" es true
// (comando GET) arranca una ventana nueva; con NOW la ventana sigue.
void sendReport(Stream &out, bool reset) {
  float vAvg, vStd, gAvg, gStd;
  statsResult(sV, vAvg, vStd);
  statsResult(sG, gAvg, gStd);
  float windowS = (millis() - windowStart) / 1000.0;

  // F("...") guarda el texto en la flash y no gasta RAM.
  // El segundo argumento de print() es la cantidad de decimales.
  out.print(F("{\"v_now\":"));     out.print(lastV, 4);
  out.print(F(",\"adc_now\":"));   out.print(lastAdc);
  out.print(F(",\"v_avg\":"));     out.print(vAvg, 4);
  out.print(F(",\"v_min\":"));     out.print(sV.mn, 4);
  out.print(F(",\"v_max\":"));     out.print(sV.mx, 4);
  out.print(F(",\"v_std\":"));     out.print(vStd, 4);
#if MODO_SHUNT
  out.print(F(",\"i_avg_ma\":"));  out.print(vAvg / RESISTENCIA_OHM * 1000.0, 1);
#else
  // potencia promedio = radiación promedio × área  [mW]
  out.print(F(",\"p_avg_mw\":"));  out.print(gAvg / CAL_K * AREA_M2 * 1000.0, 4);
#endif
  out.print(F(",\"g_now\":"));     out.print(lastG, 2);
  out.print(F(",\"g_avg\":"));     out.print(gAvg, 2);
  out.print(F(",\"g_min\":"));     out.print(sG.mn, 2);
  out.print(F(",\"g_max\":"));     out.print(sG.mx, 2);
  out.print(F(",\"g_std\":"));     out.print(gStd, 2);
  out.print(F(",\"n_samples\":")); out.print(nSamples);
  out.print(F(",\"window_s\":"));  out.print(windowS, 1);
  out.print(F(",\"sat\":"));       out.print(nSaturated);
  out.print(F(",\"vcc\":"));       out.print(vrefVolts, 3);
  out.println(F("}"));   // el Enter final marca el fin del mensaje

  if (reset) resetWindow();
}

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 5: LECTURA DE COMANDOS
// ════════════════════════════════════════════════════════════════════════

// Junta los caracteres que llegan por "in" en "buf". Cuando llega un
// Enter, devuelve qué comando era. Nunca espera: procesa lo que hay y sale.
Command checkCommand(Stream &in, String &buf) {
  while (in.available()) {
    char c = in.read();
    if (c == '\n' || c == '\r') {
      buf.trim();
      buf.toUpperCase();
      Command cmd = CMD_NONE;
      if (buf == "GET") cmd = CMD_GET;
      else if (buf == "NOW") cmd = CMD_NOW;
      buf = "";
      if (cmd != CMD_NONE) return cmd;
    } else if (buf.length() < 16) {
      buf += c;
    } else {
      buf = "";   // basura larga (ruido eléctrico): descartar
    }
  }
  return CMD_NONE;
}

// Atiende un comando recibido por el puerto "port"
void handle(Stream &port, Command cmd) {
  if (cmd == CMD_GET) sendReport(port, true);
  else if (cmd == CMD_NOW) sendReport(port, false);
}

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 6: SETUP — se ejecuta UNA vez al encender
// ════════════════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(9600);       // Monitor Serie (USB)
  piSerial.begin(9600);     // Pi A
  pinMode(PIN_CELDA, INPUT);

#if MODO_SHUNT
  // Referencia interna de 1.1 V. Las primeras lecturas después del
  // cambio salen mal (AREF tarda en estabilizarse): las descartamos.
  analogReference(INTERNAL);
  for (int i = 0; i < 10; i++) {
    analogRead(PIN_CELDA);
    delay(10);
  }
#endif

  refreshVref();
  takeSample();
  resetWindow();
  Serial.println(F("[piranometro] listo. Comandos: GET (y reinicia) / NOW"));
}

// ════════════════════════════════════════════════════════════════════════
//  SECCIÓN 7: LOOP — se repite sin parar
// ════════════════════════════════════════════════════════════════════════
//
//  A diferencia del artículo, acá NO usamos delay(1000): congelaría al
//  Arduino y se podría perder el comando de la Pi. Usamos el patrón
//  millis(): miramos el reloj y actuamos solo cuando toca.

void loop() {
  unsigned long now = millis();
  if (now - lastSampleMs >= SAMPLE_INTERVAL_MS) {
    lastSampleMs = now;
    takeSample();
  }

  // Cada 5 s re-medimos la referencia (la alimentación "respira")
  if (now - lastVccMs >= VCC_INTERVAL_MS) {
    lastVccMs = now;
    refreshVref();
  }

  handle(piSerial, checkCommand(piSerial, cmdPi));   // ¿preguntó la Pi?
  handle(Serial,   checkCommand(Serial,   cmdUsb));  // ¿preguntaste vos?
}
