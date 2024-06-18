#include <stdio.h>

int main(void) {
  int x; 
  float media=0, suma=0, cant=0,  mayor=0;

  while(x!=0){
    printf("• Ingrese un valor entero: ");
    scanf("%d", &x);
if(x!=0){
    suma=suma+x;
    cant++;
    if(x>mayor){
      mayor=x;
    }
}
  }
  media=suma/cant;

  printf("\n--------------\n");
  printf("\n • Cantidad de valores informados: %.0f", cant);
  printf("\n • Media de valores: %.2f", media);
  printf("\n • Mayor valor informado: %.0f", mayor);
  return 0;
}