#include <stdio.h>

int main(void) {
  float multa, taxa, total;
  

  printf("Introduzca el valor de la multa: ");
  scanf("%f", &multa);

  printf("Introduzca el valor de la taxa: ");
  scanf("%f", &taxa);


  total = multa + (multa * taxa / 100);

  printf("El total a pagar es: %f", total);
  
  
  return 0;
}