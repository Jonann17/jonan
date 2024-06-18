#include <stdio.h>

int main(void) {
  int c=1, N, x, max=0, min=0;
  printf("• Ingrese cantidad de numeros a ingresar: ");
  scanf("%d", &N);

  for(c=1; c<=N; c++){
    printf("• Ingrese el valor nro %d: ", c);
    scanf("%d", &x);

    if (c==1){
      max=x;
      min=x;
    }

    if(x>max){
      max=x;
    }
    if (x<min){
      min=x;
    }
  }
  printf("\n• El mayor es: %d: ", max);
  printf("\n• El menor es: %d: ", min);
  return 0;
}