#include "out/internal-impl.hpp"

// The C++ function we want to export with C wrappers.
template <typename S, typename T> T add(S const left, T const right) {
  return static_cast<T>(left) + right;
}
