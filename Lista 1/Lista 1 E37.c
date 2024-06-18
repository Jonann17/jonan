#include <stdio.h>

int main() {
    int X;

    printf("Digite uN número: ");
    scanf("%d", &X);


    if (X > 0) {
        printf("Números impares entre 1 y %d:\n", X);

        for (int i = 1; i < X; i += 2) {
            printf("%d\n", i);
        }
    } else {
        printf("Por favor, coloca un numero mayor a 0.\n");
    }

    return 0;
}