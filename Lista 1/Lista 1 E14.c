#include <stdio.h>

int main(void) {
  float precioventa, preciocompra, ganancia;

  printf("Ingrese el precio de compra: ");
  scanf( "%f", &preciocompra);

  printf("Ingrese el precio de venta: ");
  scanf( "%f", &precioventa);

  ganancia = ((precioventa - preciocompra) / preciocompra) * 100;
  
  printf( "La ganancia es:  %f porciento", ganancia);
    
  
  return 0;
}