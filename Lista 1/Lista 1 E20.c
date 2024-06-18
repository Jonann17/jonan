#include <stdio.h>

int main(void) {
  int edad;
  
  printf("Ingrese su edad: ");
  scanf("%d", &edad);

  if (edad >= 18 && edad < 65)
    printf( "Mayor de edad\n" );
  else if (edad >= 65)
    printf( "Jubilado\n" );
  else
    printf( "Menor de edad\n" );
  return 0;
}