#include <stdio.h>

int main() {
    int valor1, valor2, resultado;

    printf("Digite un numero: ");
    scanf("%d", &valor1);

    printf("Digite otro numero: ");
    scanf("%d", &valor2);

    resultado = valor1 + valor2;


    if (resultado >= 10) {
        resultado += 5;  
    } else {
        resultado -= 5;  
    }


    printf("El valor final es: %d\n", resultado);

    return 0;
}