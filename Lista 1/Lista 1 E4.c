#include <stdio.h>

int main(void) {

  int numero1, numero2, numero3;
 float media;

  printf ("Digite un numero entero: \n ");
  scanf ("%d", &numero1);
  printf( "Digite otro numero entero: \n");
  scanf( "%d", &numero2);
  printf( "Digite un ultimo numero entero: \n");
  scanf( "%d", &numero3);
  media = (numero1 + numero2 + numero3)/3.0;

  printf("El resultado de la media aritmetica es: %f \n", media);

  return 0;
}