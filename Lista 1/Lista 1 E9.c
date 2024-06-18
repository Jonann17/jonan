#include <stdio.h>
#define PI  3.1415
int main(void) {
  float radi, area;

  printf("Ingresa el valor del radio: ");
  scanf("%f", &radi);
  
  

  area = PI * radi * radi;

  printf("El area es: %f", area);
}