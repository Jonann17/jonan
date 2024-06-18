#include <stdio.h>

int main(void) {
 int dia, anho;

  printf("Ingrese el numeor de dias: ");
  scanf("%d", &dia);

  anho = dia / 365;

  printf("El numero de dias corresponde a %d año/s", anho);

  return 0;
}