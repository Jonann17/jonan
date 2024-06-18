#include <stdio.h>

int main(void) {
  float consumo, kilometros, consumido;

  printf("Ingrese la cantidad de kilometros recorridos: ");
  scanf( "%f", &kilometros);

  consumo = 17;

    consumido = kilometros / consumo;

  printf("El consumo de combustible es: %f", consumido);

    
  return 0;
}