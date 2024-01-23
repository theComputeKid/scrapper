#include "out/exported-interface.h"
#include <stdint.h>
#include <stdio.h>

int main() {

  {
    uint32_t const left = 9;
    float const right = 1.0f;
    float const result = add_ui32_f32(left, right);
    printf("%u (uint32) + %f (float) = %f", left, right, result);
  }

  return 0;
}
