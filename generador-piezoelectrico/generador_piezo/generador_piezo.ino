/*
  Generador piezoeléctrico de pisadas (maqueta, como el del video)
  ----------------------------------------------------------------
  - Lee la tensión de los piezos (rectificada) por A0, con un divisor 100k / 10k.
  - Cuenta una pisada cada vez que la tensión SUBE de golpe (el capacitor
    tarda en descargarse, por eso se mide la subida y no el nivel).
  - Enciende un LED (a través del BC547, desde D8) con cada pisada.
  - Muestra pasos y tensión pico en un LCD 16x2 I2C.

  Conexiones:
    A0  : punto medio del divisor 100k / 10k (sobre el capacitor de 10 uF)
    D8  : resistencia 10k -> base del BC547 (el BC547 enciende el LED)
    LCD : SDA -> A4, SCL -> A5, VCC -> 5V, GND -> GND

  Librería necesaria: "LiquidCrystal I2C" (Frank de Brabander)
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Si la pantalla no muestra nada, prueba 0x3F (o usa el sketch escaner_i2c).
LiquidCrystal_I2C lcd(0x27, 16, 2);

const byte PIN_VOLTAJE = A0;
const byte PIN_LED = 8;

// Divisor: R1 = 100k (arriba), R2 = 10k (abajo)  ->  factor = (R1 + R2) / R2
const float R1 = 100000.0;
const float R2 = 10000.0;
const float FACTOR_DIVISOR = (R1 + R2) / R2;  // = 11  -> hasta 55 V
const float VREF = 5.0;

// Subida mínima de tensión (voltios) que cuenta como pisada.
// Súbela si cuenta pasos solo; bájala si no detecta las pisadas.
const float UMBRAL_SUBIDA_V = 0.8;
// Al pisar Y al levantar el pie hay un pulso: cubre los dos.
const unsigned long ANTIRREBOTE_MS = 600;
const unsigned long MEDIR_PICO_MS = 150;  // tiempo para capturar el pico
const unsigned long LED_MS = 200;    // cuánto queda encendido el LED

unsigned long pasos = 0;
bool midiendoPico = false;
float vBase = 0;        // nivel de reposo (sigue la descarga del capacitor)
float vPico = 0;
float vUltimaPisada = 0;
unsigned long inicioPisadaMs = 0;
unsigned long ledEncendidoMs = 0;
bool hayQueRefrescar = true;

float leerVoltaje() {
  return analogRead(PIN_VOLTAJE) * (VREF / 1023.0) * FACTOR_DIVISOR;
}

void setup() {
  Serial.begin(9600);
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Footstep Energy");
  lcd.setCursor(3, 1);
  lcd.print("Generator");
  delay(1500);
  lcd.clear();
}

void loop() {
  unsigned long ahora = millis();
  float v = leerVoltaje();

  // La base baja junto con la descarga del capacitor.
  if (v < vBase) vBase = v;

  if (!midiendoPico && v > vBase + UMBRAL_SUBIDA_V && ahora - inicioPisadaMs > ANTIRREBOTE_MS) {
    // Empieza una pisada
    midiendoPico = true;
    inicioPisadaMs = ahora;
    vPico = v;
    pasos++;
    digitalWrite(PIN_LED, HIGH);
    ledEncendidoMs = ahora;
  }

  if (midiendoPico) {
    if (v > vPico) vPico = v;
    if (ahora - inicioPisadaMs > MEDIR_PICO_MS) {
      midiendoPico = false;
      vUltimaPisada = vPico;
      vBase = vPico;   // la próxima pisada tiene que subir desde aquí
      hayQueRefrescar = true;

      Serial.print("Paso ");
      Serial.print(pasos);
      Serial.print("  Vpico=");
      Serial.print(vUltimaPisada, 2);
      Serial.println(" V");
    }
  }

  if (digitalRead(PIN_LED) == HIGH && ahora - ledEncendidoMs > LED_MS) {
    digitalWrite(PIN_LED, LOW);
  }

  if (hayQueRefrescar) {
    hayQueRefrescar = false;
    lcd.setCursor(0, 0);
    lcd.print("Pasos: ");
    lcd.print(pasos);
    lcd.print("        ");
    lcd.setCursor(0, 1);
    lcd.print("Voltaje: ");
    lcd.print(vUltimaPisada, 1);
    lcd.print("V    ");
  }
}
