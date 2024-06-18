#include <stdio.h>

int main(void) {
  int x=0; 
  float media=0, suma=0, positivo=0, negativo=0, mayor=0, impar=0;

  while(x>=0){
    printf("• Ingrese un valor entero: ");
    scanf("%d", &x);
if(x>=0){
    suma=suma+x;
    positivo++;
    if(x%2==1){
      impar++;
    }
    if(x>mayor){
      mayor=x;
    }
}
  }
  media=suma/positivo;

  printf("\n--------------\n");
  printf("\n • Cantidad de positivos: %.0f", positivo);
  printf("\n • Media de positivos: %.2f", media);
  printf("\n • Mayor positivo informado: %.0f", mayor);
  printf("\n • Cantidad de impares: %.0f", impar);
  return 0;
}