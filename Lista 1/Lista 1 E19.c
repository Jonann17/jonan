#include <stdio.h>

int main(void) {
  int numero1, numero2, division;
  printf("Digite o primeiro número: ");
  scanf( "%d", &numero1);

  printf("Digite o segundo número: ");
  scanf( "%d", &numero2);

  if (numero1 > numero2)
    division = numero1 / numero2;
  else
    division = numero2 / numero1;

  printf( "O resultado da divisão é: %d", division);
    
  return 0;
}