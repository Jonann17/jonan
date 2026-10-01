/*
  Pasarela piezoeléctrica de 9 baldosas
  -------------------------------------
  - Cada baldosa tiene su propio detector (BC547) en D2..D10,
    leído con interrupciones de cambio de pin.
  - Cuenta pisadas totales y por baldosa.
  - Detecta cruces completos (baldosa 1 -> 9 o 9 -> 1): dirección y velocidad.
  - Mide la tensión del bus común (divisor 100k/10k en A0) y la energía
    guardada en el capacitor del bus: E = 1/2 * C * V^2.
  - LCD 16x2 I2C:
      línea 1: mapa en vivo de las baldosas  |#..#.....| >
      línea 2: rota entre pasos, velocidad, bus/energía y cruces

  Conexiones:
    Baldosa 1..9 : colector de su BC547 -> D2..D10 (pull-up interno)
    A0           : divisor 100k / 10k del bus común
    LCD I2C      : SDA -> A4, SCL -> A5, VCC -> 5V, GND -> GND

  Librería necesaria: "LiquidCrystal I2C" (Frank de Brabander)
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Si la pantalla no muestra nada, prueba 0x3F (o usa el sketch escaner_i2c).
LiquidCrystal_I2C lcd(0x27, 16, 2);

const byte NUM_BALDOSAS = 9;
const byte PINES_BALDOSA[NUM_BALDOSAS] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
const byte PIN_VOLTAJE = A0;

// Medidas de la pasarela
const float LARGO_BALDOSA_M = 0.30;  // largo de cada baldosa (metros)
// Distancia entre el centro de la baldosa 1 y el de la 9
const float DISTANCIA_CRUCE_M = (NUM_BALDOSAS - 1) * LARGO_BALDOSA_M;  // 2,4 m

// Medición del bus
const float R1 = 100000.0;
const float R2 = 10000.0;
const float FACTOR_DIVISOR = (R1 + R2) / R2;  // = 11 -> hasta 55 V
const float VREF = 5.0;
const float C_BUS_F = 220e-6;                 // capacitor del bus (220 uF)

// Tiempos
// Al pisar Y al levantar el pie el piezo da un pulso: el antirrebote
// debe cubrir los dos para contar una sola pisada.
const unsigned long ANTIRREBOTE_MS = 600;     // mínimo entre pisadas de una misma baldosa
const unsigned long TIEMPO_MAX_CRUCE_MS = 15000;
const unsigned long CAMBIO_PANTALLA_MS = 3000;
const unsigned long REFRESCO_LCD_MS = 200;

unsigned long pasosPorBaldosa[NUM_BALDOSAS];
unsigned long ultimoPasoMs[NUM_BALDOSAS];

// Bit i = la baldosa i+1 dio un pulso. Lo marcan las interrupciones
// de cambio de pin, así no se pierde ningún pulso corto.
volatile uint16_t pulsosPendientes = 0;
unsigned long pasosTotales = 0;

// Cruce en curso: 0 = ninguno, 1 = empezó en la baldosa 1, 9 = empezó en la 9
byte inicioCruce = 0;
unsigned long inicioCruceMs = 0;
unsigned long cruces = 0;
float ultimaVelocidad = 0;   // m/s
char ultimaDireccion = ' ';  // '>' de 1 a 9, '<' de 9 a 1

float vBus = 0;
byte pantalla = 0;
unsigned long ultimoCambioPantallaMs = 0;
unsigned long ultimoRefrescoMs = 0;

float leerVoltaje() {
  return analogRead(PIN_VOLTAJE) * (VREF / 1023.0) * FACTOR_DIVISOR;
}

void registrarCruce(byte baldosa, unsigned long ahora) {
  if (baldosa == 1 || baldosa == NUM_BALDOSAS) {
    byte otroExtremo = (baldosa == 1) ? NUM_BALDOSAS : 1;

    if (inicioCruce == otroExtremo && ahora - inicioCruceMs <= TIEMPO_MAX_CRUCE_MS) {
      // Cruce completo
      float segundos = (ahora - inicioCruceMs) / 1000.0;
      ultimaVelocidad = DISTANCIA_CRUCE_M / segundos;
      ultimaDireccion = (inicioCruce == 1) ? '>' : '<';
      cruces++;
      inicioCruce = 0;

      Serial.print("Cruce ");
      Serial.print(cruces);
      Serial.print(ultimaDireccion == '>' ? " (1->9)" : " (9->1)");
      Serial.print(" en ");
      Serial.print(segundos, 2);
      Serial.print(" s  velocidad=");
      Serial.print(ultimaVelocidad, 2);
      Serial.println(" m/s");
    } else {
      // Empieza (o reinicia) un cruce desde este extremo
      inicioCruce = baldosa;
      inicioCruceMs = ahora;
    }
  }
}

// D2..D7 = PIND bits 2..7  -> baldosas 1..6
ISR(PCINT2_vect) {
  byte bajos = ~PIND;
  for (byte i = 0; i < 6; i++) {
    if (bajos & (1 << (i + 2))) pulsosPendientes |= (1 << i);
  }
}

// D8..D10 = PINB bits 0..2 -> baldosas 7..9
ISR(PCINT0_vect) {
  byte bajos = ~PINB;
  for (byte i = 0; i < 3; i++) {
    if (bajos & (1 << i)) pulsosPendientes |= (1 << (i + 6));
  }
}

void revisarBaldosas() {
  noInterrupts();
  uint16_t pulsos = pulsosPendientes;
  pulsosPendientes = 0;
  interrupts();

  unsigned long ahora = millis();
  for (byte i = 0; i < NUM_BALDOSAS; i++) {
    if ((pulsos & (1 << i)) && ahora - ultimoPasoMs[i] > ANTIRREBOTE_MS) {
      ultimoPasoMs[i] = ahora;
      pasosPorBaldosa[i]++;
      pasosTotales++;
      registrarCruce(i + 1, ahora);

      Serial.print("Baldosa ");
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(pasosPorBaldosa[i]);
      Serial.print(" pasos  (total ");
      Serial.print(pasosTotales);
      Serial.println(")");
    }
  }

  // Cruce abandonado
  if (inicioCruce != 0 && ahora - inicioCruceMs > TIEMPO_MAX_CRUCE_MS) {
    inicioCruce = 0;
  }
}

void dibujarLCD() {
  unsigned long ahora = millis();

  // Línea 1: mapa en vivo. '#' = pisada hace menos de 500 ms.
  lcd.setCursor(0, 0);
  lcd.print('|');
  for (byte i = 0; i < NUM_BALDOSAS; i++) {
    bool activa = pasosPorBaldosa[i] > 0 && ahora - ultimoPasoMs[i] < 500;
    lcd.print(activa ? '#' : '.');
  }
  lcd.print("| ");
  lcd.print(ultimaDireccion);
  lcd.print("   ");

  // Línea 2: rota entre varias pantallas
  char linea[17];
  char num[10];
  switch (pantalla) {
    case 0:
      snprintf(linea, sizeof(linea), "Pasos: %lu", pasosTotales);
      break;
    case 1:
      dtostrf(ultimaVelocidad, 4, 2, num);
      snprintf(linea, sizeof(linea), "Vel: %s m/s", num);
      break;
    case 2: {
      float energia_mJ = 0.5 * C_BUS_F * vBus * vBus * 1000.0;
      char numE[10];
      dtostrf(vBus, 4, 1, num);
      dtostrf(energia_mJ, 4, 1, numE);
      snprintf(linea, sizeof(linea), "%sV %smJ", num, numE);
      break;
    }
    default:
      snprintf(linea, sizeof(linea), "Cruces: %lu", cruces);
      break;
  }
  lcd.setCursor(0, 1);
  lcd.print(linea);
  for (byte i = strlen(linea); i < 16; i++) lcd.print(' ');
}

void setup() {
  Serial.begin(9600);
  for (byte i = 0; i < NUM_BALDOSAS; i++) {
    pinMode(PINES_BALDOSA[i], INPUT_PULLUP);
    pasosPorBaldosa[i] = 0;
    ultimoPasoMs[i] = 0;
  }
  // Interrupciones de cambio de pin: D2..D7 (PCINT18..23) y D8..D10 (PCINT0..2)
  PCMSK2 |= 0b11111100;
  PCMSK0 |= 0b00000111;
  PCIFR  |= (1 << PCIF2) | (1 << PCIF0);
  PCICR  |= (1 << PCIE2) | (1 << PCIE0);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Pasarela Piezo");
  lcd.setCursor(0, 1);
  lcd.print("9 baldosas");
  delay(2000);
  lcd.clear();
}

void loop() {
  revisarBaldosas();
  vBus = leerVoltaje();

  unsigned long ahora = millis();
  if (ahora - ultimoCambioPantallaMs > CAMBIO_PANTALLA_MS) {
    ultimoCambioPantallaMs = ahora;
    pantalla = (pantalla + 1) % 4;
  }
  if (ahora - ultimoRefrescoMs > REFRESCO_LCD_MS) {
    ultimoRefrescoMs = ahora;
    dibujarLCD();
  }
}
