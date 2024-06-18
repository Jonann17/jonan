#include <stdio.h>

int main() {
    float tiempo, velocidad, distancia, litros;

    printf("Digite o tempo da viagem (em horas): ");
    scanf("%f", &tiempo);

    printf("Digite a velocidade média (Km/h): ");
    scanf("%f", &velocidad);

    distancia = tiempo * velocidad;

    litros = distancia / 12.5;

    printf("A quantidade de litros de combustível gasta é: %f litros\n", litros);

    return 0;
}