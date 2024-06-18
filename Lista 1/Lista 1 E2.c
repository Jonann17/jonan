#include <stdio.h>

int main(void) {
 int numero1,  numero2;

  printf( "Introduzca el primer numero: \n" );
  scanf( "%d", &numero1 );
  printf( "Introduzca el segundo numero: \n" );
  scanf( "%d", &numero2 );

  printf( "La suma de los dos numeros es: %d\n", numero1 + numero2 );
  printf( "La multiplicacion de los dos numeros es: %d\n", numero1 * numero2 );
  
  return 0;
}