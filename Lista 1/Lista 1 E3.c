#include <stdio.h>

int main(void) {
  float numero;
  printf("Digite un número real: \n");
  scanf("%f", &numero);

  printf("La tercera parte del numero real es: %f", numero/3);

  return 0;
}