#include <stdio.h>

int main(void) {
  int a, b, x, y;

  printf("Coloca un valor para a: ");
  scanf("%d", &a);
  printf( "Coloca un valor para b: ");
  scanf("%d", &b);
  printf( "Coloca un valor para x: ");
  scanf( "%d", &x);

  y = a * x + b;

  printf( "El valor de y es: %d", y);
  return 0;
}