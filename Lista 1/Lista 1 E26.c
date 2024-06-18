#include <stdio.h>

int main() {
    int numerodia;


    printf("Digite un número entre 1 al 7: ");
    scanf("%d", &numerodia);


    if (numerodia >= 1 && numerodia <= 7) {

        printf("Dia de la semana: ");
        if (numerodia == 1) {
            printf("Lunes");
        } else if (numerodia == 2) {
            printf("Martes");
        } else if (numerodia == 3) {
            printf("Miercoles");
        } else if (numerodia == 4) {
            printf("Jueves");
        } else if (numerodia == 5) {
            printf("Viernes");
        } else if (numerodia == 6) {
            printf("Sábado");
        } else {
            printf("Domingo");
        }
        printf("\n");
    } else {
        printf("Error no hay dia con ese numero.\n");
    }

    return 0;
}