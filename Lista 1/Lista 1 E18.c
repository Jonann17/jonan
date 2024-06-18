#include <stdio.h>

int main(void) {
  int numero;
  printf("Digite um número: ");
  scanf( "%d", &numero);

  if (numero % 2 == 0)
    printf("El numero es par");
  else
    printf("El numero es impar");

  return 0;
}