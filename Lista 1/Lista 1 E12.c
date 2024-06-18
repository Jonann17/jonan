#include <stdio.h>

int main(void) {
  float salarioactual, bono, comision, total, aumento, salariototal;
  printf("Ingrese su salario actual: ");
  scanf( "%f", &salarioactual);

  comision = 10000;

  bono = salarioactual * 0.20;

  aumento = bono + comision;

  total = aumento * 0.35;
  
  salariototal = total + salarioactual;

  printf("Su salario total es %f", salariototal);
  
  return 0;
}