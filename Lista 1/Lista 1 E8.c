#include <stdio.h>

int main(void){
 float segundos, minutos, horas, otrosegundos;

  printf("Introduzca los segundos: ");
  scanf( "%f", &segundos);


  horas = segundos / 3600;
  minutos = segundos / 60;
  segundos = segundos / 60;


  printf("Corresponde a %f horas, %f minutos y %f segundos", horas, minutos, segundos);

    return 0;
  
}