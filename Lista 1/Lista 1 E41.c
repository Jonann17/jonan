#include <stdio.h>

int main(void) {
  int c=1, n=0, x, suma=0;
  for (c=1; c<=10; c++){
  printf("• Ingrese el valor nro %d: ", c);
  scanf("%d", &x);
    n++;
    suma=suma+x;
  }
  printf("• La cantidad de numeros informados: %d\n", n);
  printf("• La media es: %d\n", suma/n);
  return 0;
}