#include <stdio.h>

int main(void) {
  int c;
  float alt, mas=0, menos=0;
    for (c=1; c<=10; c++){
    printf("%d• Ingrese altura [m]: ", c);
    scanf("%f", &alt);
    if (alt>=1.70){
      mas++;
    }else{
      menos++;
    }
    }

  printf("\n• Cantidad de personas con altura mayor ( o igual) a 1.7m: %.0f", mas);
  printf("\n• Cantidad de personas con altura menor a 1.7m: %.0f", menos);
  return 0;
}