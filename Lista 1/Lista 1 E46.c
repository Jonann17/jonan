#include <stdio.h>

int main(void) {
  int c, x=0;
  printf("\n• Ingrese la tabla que desea visualizar [0-9]: ");
  scanf("%d", &x);
  while(x<0 || x>9){
    printf("\n- Error -\n");
    printf("\n• Ingrese la tabla que desea visualizar [0-9]: ");
    scanf("%d", &x);
  }

  for(c=0; c<=10; c++){
    printf("• %d x %d = %d\n", x, c, x*c);
  }

  return 0;
}