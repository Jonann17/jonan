#include<stdio.h>
int main(){
    int x, y;

    printf("INICIO DE LA TABLA\n");
    printf("-----------------------------\n");

    for(y=1; y<=10; y++){
        for(x=1; x<=10; x++){
            printf("%d x %d = %d\n",y,  x, y*x);
        }
        printf("-----------------\n");
    }
    printf("FIN DE LA TABLA\n");

  return 0;

  }