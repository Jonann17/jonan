#include <stdio.h>

int main(void) {
  float nota1, nota2, nota3, nota4, media;

  printf("Inserte 4 notas\n");
  scanf("%f %f %f %f", &nota1, &nota2, &nota3, &nota4);

  media = (nota1 + nota2 + nota3 + nota4) / 4;

  if (media >= 7)
    printf( "Aprobado\n");
  else
    printf("Desaprobado\n");

  return 0;
}