#include <stdio.h>

int main() {
  // Declaração de variáveis
  float salario, valorCasa, prestacao;
  int meses;

  printf("Informe o valor do seu salário: ");
  scanf("%f", &salario);

  valorCasa = 35000;
  prestacao = salario * 0.35;

  meses = valorCasa / prestacao;

  printf("A quantidade de meses necessária para comprar e pagar uma casa popular é de %d.\n", meses);

  return 0;
}