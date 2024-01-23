<div align="center">
	<h1><strong>scrapper</strong></h1>
	<p>exports c++ functions with a c interface</p>
    <img alt="GitHub License" src="https://img.shields.io/github/license/thecomputekid/scrapper?style=for-the-badge&color=blue">
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/theComputeKid/scrapper/test.yml?style=for-the-badge">
	<img alt="Lines of Code" src="https://tokei.rs/b1/github/thecomputekid/scrapper?category=code&style=for-the-badge">
</div>

## Summary

This project pretends to export C++ functions with a C ABI:

1. It wraps C++ functions inside wrapper functions with a C signature.
2. It then exports those wrapper functions with a C ABI.
3. It then wraps those exported C functions inside C++ functions.

This means that the end user can benefit from a clean C++ interface to your library's functionality. The details of the function to be exported is supplied by a JSON file to the project script.

## Example
We wish to export the following functionality, where `T` can be `float` or `double`:
```
template <typename T>
T add(T left, T right){
    return left + right;
};
```

This script will create two wrappers:
1. A wrapper to be compiled by the library.
2. An exported interface to be used by the users of the code.

For the library, the following wrapper is generated:

```
// Forward declaration (to be implemented later).
template <typename T> T add(T left, T right);

float add_f32(float left, float right){
	return add(left, right);
}

double add_f64(double left, double right){
	return add(left, right);
}
```

This wrapper is included in the file that implements the C++ functionality (written by the library author):

```
#include "my_generated_wrapper.hpp"

template <typename T> // T can be float, double
T add(T left, T right){
    return left + right;
};
```

A pleasant side effect of generating the `add_f32` and `add_f64` functions is that it instantiates the original `add` C++ function for those types by virtue of calling it with those types.

The C interface (`add_f32` and `add_f64`) is then exported in a user-facing header, along with a convenience wrapper for calling via clean C++ code:

```
// Exported header interface of the library.

#ifdef __cplusplus
extern "C" {
#endif

float add_f32(float left, float right);
double add_f64(double left, double right);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus

template <typename T>
T add(T left, T right){
	if constexpr (std::is_same_v<T, float>){
		return add_f32(left, right);
	}
	else if constexpr (std::is_same_v<T, double>){
		return add_f64(left, right);
	} else {
        // Static assert to prevent fall-through.
    }
}

#endif
```

The script automatically adds the correct decorators (e.g. import/export/extern macros), but they are omitted here for display purposes. The user can then either call the C or C++ functions from the header files:

```
template <typename T>
T user_code(T left, T right){
	// Use C++ wrapper.
	return add(left, right);
}

float user_code2(float left, float right){
	// Use exported C function.
	return add_f32(left, right);
}
```

## Configuration

The JSON schema is provided as part of the project in `utils/schema.json` and can be seen used in the examples, which can be run as:

```
python3 ./scrapper.py examples/simple.json --output-header out/simple.h --output-impl out/simple.hpp
python3 ./scrapper.py examples/advanced.json -oh out/advanced.h -oi out/advanced.hpp -s
```

where:
- `--output-header`, `-oh`: The exported interface to be used by the user of your library
- `--output-implementation`, `-oi`: The implementation of the exported functions, to be compiled as part of the library.
- `--separate-header`, `-s`: Split the header into a cleaner interface (instead of having everything in one exported header).

The JSON is validated as part of the script. An example is:
```
{
    "$schema": "https://raw.githubusercontent.com/theComputeKid/scrapper/main/utils/schema.json",
    "includes": [
        "<stdint.h>"
    ],
    "linkage-macro": "MY_PROJECT",
    "suffix-mapping": {
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
                },
                {
                    "name": "p3",
                    "type": "void",
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
- `"includes"`: Any additional includes that the C exported ABI requires.
- `"linkage-macro"`: This is the base macro used to define the export/import linkage of the generated files. For example, if `"linkage-macro" : "PROJ"`, then the macro `"PROJ_EXPORT"` will be used to define OS-specific linkage decorations (e.g.: `__declspec(dllexport)`).
- `"functions"`: Array of C++ functions to be exported.
- `"suffix-mapping"`: Optional. This is the suffix added to the base C++ function name for each type to be exported. By default, the mapping is specified in `utils/suffix-mapping.json`, but this can be overridden. If a type is used that is not in the map, then it is used as-is as the suffix. For example, if `"float": "fp32"`, then the add function above would be exported as `float add_fp32(float left, float right)` for the `float` version.

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

The project can be built using cmake presets (for cmake >= 3.28):
```
cd test
cmake --workflow --preset default
cmake --workflow --preset split
```
For older versions of cmake, you will need to configure manually (you can use the presets.json as a guide).
