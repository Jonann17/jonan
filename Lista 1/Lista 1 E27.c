#include <stdio.h>

int main() {
    float peso, altura, imc;

    printf("Digite el peso (en kg): ");
    scanf("%f", &peso);

    printf("Digite la altura (en metros): ");
    scanf("%f", &altura);

    imc = peso / (altura * altura);

    printf("Índice de Masa Corporal (IMC): %f\n", imc);

    if (imc < 26) {
        printf("Grado de Obesidad: Normal\n");
    } else if (imc >= 26 && imc < 30) {
        printf("Grado de Obesidad: Obeso\n");
    } else {
        printf("Grado de Obesidad: Obesidad morbida\n");
    }

    return 0;
}