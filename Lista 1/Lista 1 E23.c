#include <stdio.h>

int main(void) {
  int num1, num2, result;
  printf("Enter two numbers: ");
  scanf("%d %d", &num1, &num2);
  result = num1 / num2;
  if (num1 % num2 == 0)
    printf ("El primer numero es divisible entre el segundo\n");
  else
    printf ("El primer numero no es divisible entre el segundo\n");

  printf("Resultado: %d \n", result);
  return 0;
}