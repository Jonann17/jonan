#include <stdio.h>
#include <strings.h>

char sn;
int sw=0;

char son(){
  printf("--> s o n: ");
   scanf("%c",&sn);
   getchar();
 while (sn!='s' && sn!='n'){
   printf("--> s o n: ");
   scanf("%c",&sn);
   getchar();
 }
  if (sn=='s'){
    sw=1;
  }
  if (sn=='n'){
    sw=0;
  }
  return 0;
}

int main(void) {

  printf(" Responda las preguntas con s o n  \n\n");

  printf("-> ¿Tu animal es un mamifero?\n");
  son(sn);
    if (sw==1){
      printf("---> ¿Tu animal es un cuadrupedo?\n");
      son(sn);
        if (sw==1){
                  printf("----> ¿Tu animal es carnivoro?\n");
                  son(sn);
                if (sw==1){
                    printf("------> Tu animal es un leon :p");
                }else{
                    printf("----> ¿Tu animal es hervivoro?\n");
                    son(sn);
                        if (sw==1){
                          printf("------> Tu animal es un caballo");
                          }else{
                          printf("------> Tu animal no existe");
                  }
                        }
        }else{
                  printf("---> ¿Tu animal es un bipedo?\n");
                  son(sn);
                    if (sw==1){
                              printf("----> ¿Tu animal es omnivoro?\n");
                              son(sn);
                            if (sw==1){
                                printf("------> Tu animal es un humano");
                            }else{
                                printf("----> ¿Tu animal come frutas?\n");
                                son(sn);
                                    if (sw==1){
                                      printf("------> Tu animal es un mono");
                                      }else{
                                      printf("------> Tu animal no esta aca");
                              }
                                    }
                    }else{
                      printf("----> ¿Tu animal es volador?\n");
                      son(sn);
                        if (sw==1){
                        printf("------> Tu animal es un murcielago");
                        }else{
                          printf("----> ¿Tu animal es acuatico?\n");
                          son(sn);
                            if (sw==1){
                            printf("------> Tu animal es una ballena");
                            }else{
                              printf("------> Tu animal no esta");
                            }
                        }
                    }
        } 
      }else{
      printf("-> ¿Tu animal es un ave?\n");
      son(sn);
        if (sw==1){
          printf("---> ¿Tu animal no vuela?\n");
          son(sn);
            if (sw==1){
                      printf("----> ¿Tu animal es tropical?\n");
                      son(sn);
                    if (sw==1){
                        printf("------> Tu animal es un avestruz");
                    }else{
                        printf("----> ¿Tu animal es polar?\n");
                        son(sn);
                            if (sw==1){
                              printf("------> Tu animal es un pinguino");
                              }else{
                              printf("------> Tu animal no esta aqui");
                      }
                            }
            }else{
                      printf("---> ¿Tu animal es nadador?\n");
                      son(sn);
                        if (sw==1){

                                    printf("------> Tu animal es un pato");
                        }else{
                          printf("----> ¿Tu animal es un ave rapaz?\n");
                          son(sn);
                            if (sw==1){
                            printf("------> Tu animal es un aguila");
                            }else{

                                  printf("------> Tu animal no existe");

                            }
                        }
            } 
          }else{

          printf("-> ¿Tu animal es un REPTIL?\n");
          son(sn);
            if (sw==1){
              printf("---> ¿Tu animal tiene caparazon?\n");
              son(sn);
                if (sw==1){

                            printf("------> Tu animal es una tortuga");

                }else{
                          printf("---> ¿Tu animal es carnivoro?\n");
                          son(sn);
                            if (sw==1){
                                        printf("------> Tu animal es un cocodrilo");
                            }else{
                              printf("----> ¿Tu animal no tiene patas?\n");
                              son(sn);
                                if (sw==1){
                                printf("------> Tu animal es una cobra");
                                }else{

                                      printf("------> Tu animal no existe");

                                }
                            }
                } 
              }else{
              printf("------> Tu animal no esta aqui");
              }

          }
      }




  if (sn=='n'){



  }
  return 0;
}