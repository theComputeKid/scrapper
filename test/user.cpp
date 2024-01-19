#include "out/exported-interface.h"
#include <iostream>
#include <stdint.h>

int main() {

  {
    uint32_t const left = 9;
    float const right = 1.0f;
    auto const result = add(left, right);
    std::cout << left << " (uint32_t) + " << right << " (float) = " << result
              << std::endl;
  }

  {
    int8_t const left = 20;
    float const right = 1.0f;
    auto const result = add(left, right);
    std::cout << left << " (int8_t) + " << right << " (float) = " << result
              << std::endl;
  }

  {
    uint32_t const left = 3;
    double const right = 1.0f;
    auto const result = add(left, right);
    std::cout << left << " (uint32_t) + " << right << " (double) = " << result
              << std::endl;
  }

  return 0;
}
