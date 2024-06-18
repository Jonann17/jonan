#include <stdio.h>

int main(void) {
float farenheit, celsius;

  printf("Ingresa la temperatura en Farenheit: ");
  scanf("%f", &farenheit);


  celsius = (farenheit - 32) * 5 / 9;

    printf("La temperatura en Celsius es: %f", celsius);
  return 0;
  
}