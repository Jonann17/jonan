#include <stdio.h>

int main(void) {
 int numero;

  printf("Introduzca un numero entero:  ");
   scanf("%d", &numero);

  if (numero  < 0)
    printf ( "El numero es menor que 0");
  else if (numero == 0)
    printf ( "El numero es igual a 0");
  else
    printf( "El numero es mayor que 0");
  
  return 0;
}