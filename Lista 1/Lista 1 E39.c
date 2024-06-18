#include <stdio.h>

int main() {
    int valor, suma = 0, cantidadValores = 0;

    printf("Digite valores. O programa continuará lendo enquanto a soma for menor que 30.\n");

    while (suma < 30) {
        printf("Digite um valor: ");
        scanf("%d", &valor);

        suma += valor;
        cantidadValores++;
    }

    printf("\nSoma total: %d\n", suma);
    printf("Quantidade de valores lidos: %d\n", cantidadValores);

    return 0;
}