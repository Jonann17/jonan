#include <stdio.h>

int main() {
    int N, valor, cantidadImpares = 0, suma = 0;

    // Solicitar al usuario ingresar el valor de N
    printf("Digite o valor de N: ");
    scanf("%d", &N);

    // Leer N números enteros
    printf("Digite os %d números inteiros:\n", N);

    for (int i = 0; i < N; i++) {
        printf("Número %d: ", i + 1);
        scanf("%d", &valor);

        suma += valor;

        // Verificar si el número es impar
        if (valor % 2 != 0) {
            cantidadImpares++;
        }
    }

    // Calcular la media de todos los números
    double media = (double)suma / N;

    // Imprimir los resultados
    printf("\nQuantidade de números ímpares: %d\n", cantidadImpares);
    printf("Média de todos os números: %.2f\n", media);

    return 0;
}