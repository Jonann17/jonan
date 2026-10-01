/*
  Escáner I2C: muestra en el Monitor Serie (9600 baudios)
  la dirección de tu pantalla LCD (normalmente 0x27 o 0x3F).
*/

#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(9600);
  while (!Serial) {}
  Serial.println("Buscando dispositivos I2C...");

  byte encontrados = 0;
  for (byte dir = 1; dir < 127; dir++) {
    Wire.beginTransmission(dir);
    if (Wire.endTransmission() == 0) {
      Serial.print("Dispositivo encontrado en 0x");
      if (dir < 16) Serial.print("0");
      Serial.println(dir, HEX);
      encontrados++;
    }
  }
  if (encontrados == 0) Serial.println("Nada encontrado. Revisa SDA->A4 y SCL->A5.");
}

void loop() {}
