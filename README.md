<div align="center">
	<h1><strong>scrapper</strong></h1>
	<p>pretends to export c++ functions with a c interface</p>
    <img alt="GitHub License" src="https://img.shields.io/github/license/thecomputekid/scrapper?style=for-the-badge&color=blue">
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/theComputeKid/scrapper/test.yml?style=for-the-badge">
	<img alt="Lines of Code" src="https://tokei.rs/b1/github/thecomputekid/scrapper?category=code&style=for-the-badge">
</div>

## Summary

This project pretends to export your library's C++ functions with a C ABI so that the end user can benefit from a clean C++ interface to your library's functionality, while also benefitting from a stable C ABI (e.g. with no name mangling etc).

For example, if our library contains the following functionality that is to be made available to the user:

```
template <typename T>
T add(T left, T right){
  return left + right;
};
```

The user of our library should be able to use this function with its native C++ interface without worrying about ABI compatiblity:

```
// Exported (native) signature.
template <typename T>
T add(T left, T right);

#include <iostream>

int main(){
  // C++ API used natively by the end user in their code.
  std::cout << "1 + 2 = " << add(1, 2) << std::endl;
}
```

## Methodology

The project performs 3 steps:
1. It wraps our library's C++ functions inside wrapper functions with a C-friendly signature (i.e.: `C++-to-C`).
2. It then exports those C-friendly wrapper functions with a C ABI.
3. It then wraps those exported C functions inside C++ functions with the same interface as the library's original C++ functions (i.e.: `C-to-C++`).

## Example
We wish to export the following function for `T=float` and `T=double`:

```
// library.cpp
template <typename T>
T add(T left, T right){
  return left + right;
};
```

### 1. Wrap C++ functions in a C wrapper (`C++-to-C`)

The project will first produce the following wrapper:

```
// wrapper.hpp
#pragma once

// Forward declaration.
template <typename T>
T add(T left, T right);

float add_f32(float left, float right){
  return add(left, right);
}

double add_f64(double left, double right){
  return add(left, right);
}
```

This generated file is meant to be included with the implementation of our C++ function:

```
// library.cpp

#include "wrapper.hpp"

template <typename T>
T add(T left, T right){
  return left + right;
};
```

### 2. Exporting with a C ABI

The project will then add C export specifiers to the C function signatures so that they are exported from the library with the C ABI:

```
// wrapper.hpp
#pragma once

#ifdef _WIN32
#  define SCRAPPER_EXPORT extern "C" __declspec(dllexport)
#else
#  define SCRAPPER_EXPORT extern "C" __attribute__((visibility("default")))
#endif

// Forward declaration.
template <typename T>
T add(T left, T right);

SCRAPPER_EXPORT float add_f32(float left, float right){
  return add(left, right);
}

SCRAPPER_EXPORT double add_f64(double left, double right){
  return add(left, right);
}
```

At this point, a limitation of the project becomes obvious; the C++ functions can only have C-friendly arguments, as otherwise they cannot be exported with the C ABI. This step happens at the same time as the previous one but is separated here for demonstration (i.e. the generated `wrapper.hpp` will already contain the C wrappers as well the export decorators).

An export header is generated (with the corresponding OS-specific symbol import macros) to allow the user to call these functions exported with the C ABI:

```
// export.h
#pragma once

#ifdef __cplusplus
#  define SCRAPPER_EXTERN_C extern "C"
#else
#  define SCRAPPER_EXTERN_C
#endif

#ifdef _WIN32
#  define SCRAPPER_IMPORT SCRAPPER_EXTERN_C __declspec(dllimport)
#else
#  define SCRAPPER_IMPORT SCRAPPER_EXTERN_C
#endif

SCRAPPER_IMPORT float add_f32(float left, float right);
SCRAPPER_IMPORT double add_f64(double left, double right);
```

At this point, we have two exported symbols with the C ABI: `add_f32` and `add_f64`.

### 3. Wrapping C functions in C++ wrappers (`C-to-C++`)

In order for the user to be able to use the original C++ API, the program then creates a C++ function inline with the exported header that is meant to be compiled with the user's code:

```
// export.h
#pragma once

#ifdef __cplusplus
#  define SCRAPPER_EXTERN_C extern "C"
#else
#  define SCRAPPER_EXTERN_C
#endif

#ifdef _WIN32
#  define SCRAPPER_IMPORT SCRAPPER_EXTERN_C __declspec(dllimport)
#else
#  define SCRAPPER_IMPORT SCRAPPER_EXTERN_C
#endif

SCRAPPER_IMPORT float add_f32(float left, float right);
SCRAPPER_IMPORT double add_f64(double left, double right);

#ifdef __cplusplus
template <typename T> T add(T left, T right);
#endif

#ifdef __cplusplus
#include <type_traits>
template <typename T> T add(T left, T right){
  if constexpr(std::is_same_v<T, float>){
    return add_f32(left, right);
  } else if constexpr (std::is_same_v<T, double>){
    return add_f64(left, right);
  } else {
    // Static assert to prevent unsupported type from being provided.
  }
}
#endif
```

The declaration of the C++ wrapper function is kept separate to the implementation so the user-facing interface is clean. Having the implementation at the bottom allows the user to not care about the bottom half of the exported interface. Because the implementation is `constexpr` (and inline), there is no user runtime cost for the switchyard contained within it.

The program can also provide an even cleaner interface, if requested. It can generate a separate implementation file that is automatically included in the main export header:

```
// export.h
#pragma once

#ifdef __cplusplus
#  define SCRAPPER_EXTERN_C extern "C"
#else
#  define SCRAPPER_EXTERN_C
#endif

#ifdef _WIN32
#  define SCRAPPER_IMPORT SCRAPPER_EXTERN_C __declspec(dllimport)
#else
#  define SCRAPPER_IMPORT SCRAPPER_EXTERN_C
#endif

SCRAPPER_IMPORT float add_f32(float left, float right);
SCRAPPER_IMPORT double add_f64(double left, double right);

#ifdef __cplusplus
template <typename T> T add(T left, T right);
#include "exportImpl.hpp"
#endif
```

This creates a clean interface with the minimum information needed by the user of the code. The implementation file is then generated as:

```
// exportImpl.hpp
#pragma once
#include "export.h"

#ifdef __cplusplus
#include <type_traits>
template <typename T> T add(T left, T right){
  if constexpr(std::is_same_v<T, float>){
    return add_f32(left, right);
  } else if constexpr (std::is_same_v<T, double>){
    return add_f64(left, right);
  } else {
    // Static assert to prevent unsupported type from being provided.
  }
}
```

The user will only need to include the main `export.h` header file. Note that the export header implementation file `exportImpl.hpp` includes `export.h`, but this is not strictly required and is only done to satisy code analysis tools which will want to index where the C functions used in the `if constexpr` switchyard are taken from.

### 4. User code

The user can then call the C++ API directly, as if calling the C++ interface of the original C++ function that was meant to be exported from the library:

```
// user.cpp
#include "export.h"
#include <iostream>

int main(){
  // C++ API used natively by the end user in their code.
  std::cout << "1 + 2 = " << add(1, 2) << std::endl;
}
```

They can also call the C ABI functions directly:

```
// user.c
#include "export.h"
#include <stdio.h>

int main(){
  float const left = 9.0f;
  float const right = 1.0f;
  float const result = add_f32(left, right);
  printf("%f + %f = %f", left, right, result);
}
```

## Usage

The configuration of the original C++ function(s) to be exported must be defined in a JSON file, provided to the program. Two examples are provided:

```
python3 ./scrapper.py examples/simple.json --output-header out/simple.h --output-impl out/simple.hpp
python3 ./scrapper.py examples/advanced.json -oh out/advanced.h -oi out/advanced.hpp -s
```

where:
- `--output-header`, `-oh`: The exported interface of your library. Equivalent to `export.h` in the example.
- `--output-implementation`, `-oi`: The implementation of the C functions, to be compiled as part of the library. Equivalent to `wrapper.h` in the example.
- `--separate-header`, `-s`: Split the export header into a cleaner interface as shown in the example with `exportImpl.hpp`. The program will automatically create this extra implementation file in the same directory as the `--output-header`.

Additional customization is welcome via pull requests.

## JSON schema

The JSON schema used for validation is provided as part of the project in `utils/schema.json`. The JSON is validated as part of the script. An example is:

```
{
    "$schema": "https://raw.githubusercontent.com/theComputeKid/scrapper/main/utils/schema.json",
    "includes": [
        "<stdint.h>"
    ],
    "macro": "MY_PROJECT",
    "mapping": {
        "float": "fp32"
    },
    "functions": [
        {
            "name": "myFunc",
            "combination": "fixed",
            "templates": [
                {
                    "name": "S",
                    "types": [
                        "float",
                        "int8_t"
                    ]
                },
                {
                    "name": "T",
                    "types": [
                        "double",
                        "int16_t"
                    ]
                }
            ],
            "parameters": [
                {
                    "name": "p1",
                    "type": "S",
                    "const": false,
                    "pointer": false
                },
                {
                    "name": "p2",
                    "type": "T",
                    "const": true,
                    "pointer": true
                }
            ],
            "return": {
                "type": "T",
                "const": false,
                "pointer": false
            }
        }
    ]
}

```

The supplied JSON must have:
- `"includes"`: Optional. Any additional includes that the C exported ABI requires.
- `"macro"`: Optional. This is the base macro used to define the export/import linkage of the generated files. For example, if `"macro" : "PROJ"`, then the macro `"PROJ_EXPORT"` will be used to define OS-specific linkage decorations (e.g.: `__declspec(dllexport)`). Default is `"SCRAPPER"`.
- `"functions"`: Array of C++ functions to be exported.
- `"mapping"`: Optional. This is the suffix added to the base C++ function name for each type to be exported. By default, the mapping is specified in `utils/mapping.json`, but this can be overridden. If a type is used that is not in the map, then it is used as-is as the suffix. For example, if `"float": "fp32"`, then the add function above would be exported as `float add_fp32(float left, float right)` for the `float` version.

The `"functions"` field is divided into:
- `"name"`: Name of the C++ function to be exported. This is also the base name that the generated functions will use.
- `"description"`: Optional. Generate doxygen comments (also per parameter).
- `"combination"`: Defines the combination of templates to create wrappers for.
  - `"all"`: All combinations of supplied types (cartesian product)
  - `"fixed"`: Linear combination of types. i.e. `template[0]type[0]` with `template[1]type[0]`, `template[0]type[1]` with `template[1]type[1]`.
- `"templates"`: An array of templates that the C++ function accepts.

The `"templates"` field is divided into:
- `"name"`: The placeholder type for the template (e.g. `T`) in the C++ function signature.
- `"types"`: Array of types that are accepted by the template. These must be C friendly (i.e. no std::XYZ).

## Test

A complete test case can be found in the `test` folder, demonstrating the intended usage of the script in a project. It involves the following steps:

- run this script to generate the wrappers.
- compile the library.
- compile the C user code.
- compile the C++ user code.
- run simple tests for the compiled executables.

The complete project can be built using cmake presets (for cmake >= 3.28):

```
cd test
cmake --workflow --preset default
cmake --workflow --preset split
```

For older versions of cmake, you will need to configure manually (you can use the presets.json as a guide). It requires the python package dependencies to be satisfied.

## Dependencies

Dependencies are listed in `requirements.txt`, and can be installed with:

```
pip install -r requirements.txt
```
