#include <stdio.h>

int main(void) {
  int x, c, p=0;
  printf("• Ingrese un numero entero: ");
  scanf("%d", &x);
for (c=1; c<=x; c++){
  if (x%c==0){
    p++;
  }
} 
  if(x==1){
    printf("\n %d Es numero primo",x);
  }else{
  if(p==2){
    printf("\n %d Es numero primo",x);
  }else{
    printf("\n %d No es numero primo",x);
  }
  }
  return 0;
}