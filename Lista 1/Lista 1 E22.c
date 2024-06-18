#include <stdio.h>

int main(void) {
  int num1, num2, num3;
  
  printf("Digite 1 numero: \n");
  scanf( "%d", &num1);

  printf( "Digite 2 numero: \n");
  scanf( "%d", &num2);

  printf( "Digite 3 numero: \n");
  scanf( "%d", &num3);

  if (num1 > num2 && num1 > num3)
    printf("El mayor numero es: %d", num1);
  else if (num2 > num1 && num2 > num3)
    printf("El mayor numero es: %d", num2);
  else
    printf( "El mayor numero es: %d", num3);
  
  return 0;
}