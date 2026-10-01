/*
  Generador piezoeléctrico de pisadas
  ------------------------------------
  - Cuenta cada pisada (detector con transistor BC547 en D2).
  - Mide la tensión pico generada por los piezos (divisor en A0).
  - Estima la energía generada por pisada: E = 1/2 * C * V^2.
  - Muestra todo en un LCD 16x2 I2C.

  Conexiones:
    LCD I2C : SDA -> A4, SCL -> A5, VCC -> 5V, GND -> GND
    A0      : punto medio del divisor 100k / 10k (ver README)
    D2      : colector del BC547 (usa pull-up interno)

  Librería necesaria: "LiquidCrystal I2C" (Frank de Brabander)
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Si la pantalla no muestra nada, prueba 0x3F (o usa el sketch escaner_i2c).
LiquidCrystal_I2C lcd(0x27, 16, 2);

const byte PIN_PASO    = 2;   // salida del BC547 (activo en LOW)
const byte PIN_VOLTAJE = A0;  // divisor de tensión

// Divisor: R1 = 100k (arriba), R2 = 10k (abajo)  ->  factor = (R1 + R2) / R2
const float R1 = 100000.0;
const float R2 = 10000.0;
const float FACTOR_DIVISOR = (R1 + R2) / R2;   // = 11  -> hasta 55 V
const float VREF = 5.0;                         // tensión de referencia del ADC
const float C_FARADIOS = 10e-6;                 // condensador de 10 uF

const unsigned long ANTIRREBOTE_MS = 250;       // tiempo mínimo entre pisadas

volatile unsigned long pasos = 0;
volatile unsigned long ultimoPasoMs = 0;

float vPicoActual = 0;       // pico de la pisada en curso
float vUltimaPisada = 0;     // pico de la última pisada terminada
float energiaTotal_uJ = 0;   // energía acumulada estimada (microjoules)
unsigned long pasosMostrados = 0;
unsigned long ultimoRefrescoMs = 0;

void contarPaso() {
  unsigned long ahora = millis();
  if (ahora - ultimoPasoMs > ANTIRREBOTE_MS) {
    pasos++;
    ultimoPasoMs = ahora;
  }
}

float leerVoltaje() {
  int lectura = analogRead(PIN_VOLTAJE);
  return lectura * (VREF / 1023.0) * FACTOR_DIVISOR;
}

void setup() {
  Serial.begin(9600);
  pinMode(PIN_PASO, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_PASO), contarPaso, FALLING);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Generador Piezo");
  lcd.setCursor(0, 1);
  lcd.print("Pise la placa!");
  delay(2000);
  lcd.clear();
}

void loop() {
  // Seguimos el pico de tensión mientras dura la pisada.
  float v = leerVoltaje();
  if (v > vPicoActual) vPicoActual = v;

  noInterrupts();
  unsigned long pasosAhora = pasos;
  unsigned long msDesdePaso = millis() - ultimoPasoMs;
  interrupts();

  // Cuando la pisada terminó (pasaron 200 ms), cerramos su medición.
  if (pasosAhora != pasosMostrados && msDesdePaso > 200) {
    vUltimaPisada = vPicoActual;
    energiaTotal_uJ += 0.5 * C_FARADIOS * vUltimaPisada * vUltimaPisada * 1e6;
    vPicoActual = 0;
    pasosMostrados = pasosAhora;

    Serial.print("Paso ");
    Serial.print(pasosAhora);
    Serial.print("  Vpico=");
    Serial.print(vUltimaPisada, 2);
    Serial.print(" V  Etotal=");
    Serial.print(energiaTotal_uJ, 1);
    Serial.println(" uJ");
  }

  // Refrescamos la pantalla 4 veces por segundo.
  if (millis() - ultimoRefrescoMs > 250) {
    ultimoRefrescoMs = millis();

    lcd.setCursor(0, 0);
    lcd.print("Pasos:");
    lcd.print(pasosMostrados);
    lcd.print("          ");

    lcd.setCursor(0, 1);
    lcd.print(vUltimaPisada, 1);
    lcd.print("V ");
    if (energiaTotal_uJ < 10000) {
      lcd.print(energiaTotal_uJ, 0);
      lcd.print("uJ");
    } else {
      lcd.print(energiaTotal_uJ / 1000.0, 1);
      lcd.print("mJ");
    }
    lcd.print("        ");
  }
}
