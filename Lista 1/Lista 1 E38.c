#include <stdio.h>

int main(void) {
  int num1, num2, num3, num4, num5, num6, num7, num8, num9, num10;
  float suma, media;

  printf( "Enter ten numbers: " );
  scanf( "%d" "%d" "%d" "%d" "%d" "%d" "%d" "%d" "%d" "%d", &num1, &num2, &num3, &num4, &num5, &num6, &num7, &num8, &num9, &num10);

  suma = num1 + num2 + num3 + num4 + num5 + num6 + num7 + num8 + num9 + num10;

  media = suma / 10;

  printf( "The sum is %f\n", suma );

  printf( "The average is %f\n", media );

  return 0;
}