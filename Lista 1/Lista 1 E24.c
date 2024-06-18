#include <stdio.h>

int main() {
    float valorcompra, valordescuento, valortotal;


    printf("Digite el valor de la compra: ");
    scanf("%f", &valorcompra);

    if (valorcompra <= 100.00) {
        valordescuento = valorcompra * 0.05;  
    } else if (valorcompra > 100.00 && valorcompra < 200.00) {
        valordescuento = valorcompra * 0.10;  
    } else {
        valordescuento = valorcompra * 0.20; 
    }


    valortotal = valorcompra - valordescuento;


    printf("Valor total con descuento: %f\n", valortotal);

    return 0;
}