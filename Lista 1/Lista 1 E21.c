#include <stdio.h>

int main() {
    int num1, num2, num3;

    printf("Ingrese el primer número entero: ");
    scanf("%d", &num1);

    printf("Ingrese el segundo número entero (distinto al primero): ");
    scanf("%d", &num2);

    printf("Ingrese el tercer número entero (distinto al primero y al segundo): ");
    scanf("%d", &num3);

    if ((num1 < num2 && num2 < num3) || (num3 < num2 && num2 < num1)) {
        printf("El valor del medio es: %d\n", num2);
    } else if ((num2 < num1 && num1 < num3) || (num3 < num1 && num1 < num2)) {
        printf("El valor del medio es: %d\n", num1);
    } else {
        printf("El valor del medio es: %d\n", num3);
    }

    return 0;
}