<div align="center">
	<h1><small>s</small><strong><large>crapper</strong></large></h1>
	<p>a script to generate c convenience wrappers for c++ functions</p>
    <img alt="GitHub License" src="https://img.shields.io/github/license/thecomputekid/scrapper?style=for-the-badge&color=blue">
    <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/theComputeKid/scrapper/test.yml?style=for-the-badge">
	<img alt="Lines of Code" src="https://tokei.rs/b1/github/thecomputekid/scrapper?category=code&style=for-the-badge">
</div>


## Motivation

C++ symbols are notoriously ABI-incompatible between different C++ compilers. Imagine you want to export the following functions from your C++ library:

```
template <typename T>
T add(T left, T right);
```

If this function is exported as a C++ symbol, it may not be ABI-compatible with the users of your library, who may not be able to link with this function as they may be using a different compiler vendor or even a different compiler version.

A solution to this problem is to wrap this C++ function in a series of C functions, which are then exported with C linkage:

```
// Exported header interface of the library.

#ifdef __cplusplus
extern "C" {
#endif

int add_int(int left, int right);
float add_float(float left, float right);
double add_double(double left, double right);

#ifdef __cplusplus
}
#endif
```

Internally, the library can use C++ functions:

```
// Internal implementation of the library.

// Function templates remain internal to the library.
// From this point on, we operate in the C++ domain.
template <typename T>
T add(T left, T right){
	return left + right;
}

int add_int(int left, int right){
	// Switch from C to C++.
	return add(left, right);
}

float add_float(float left, float right){
	return add(left, right);
}

double add_double(double left, double right){
	return add(left, right);
}
```

A pleasant side effect of doing this is that the C++ function `add` is automatically instantiated by way of being called inside the C function. The C++ function can then be defined in an another file that includes this file as a header.

This strategy is often used in linear algebra libraries (e.g. BLAS, LAPACK etc.), where each function is prefixed for each type  when it is exported. For example, the base `gemm` (general matrix-multiplication) name is decorated as `dgemm` for double precision matrix-multiplication and `sgemm` for the single-precision version.

However, the issue with exporting C functions is that it clutters the user's code when consuming the C functions. For example, if the user is writing C++ code, they may need to accomodate your library's API:

```
template <typename T>
T user_code(T left, T right){
	if constexpr (std::is_same_v<T, float>){
		return add_float(left, right);
	}
	if constexpr (std::is_same_v<T, double>){
		return add_double(left, right);
	}
	// All the other "overloads" ...
}
```

This problem would not exist if your library was exported with a C++ interface, and it adds noise to the user's code. A solution to this is to wrap the exported C interface in a C++ function that is compiled inline with the user's code. Applying this to our original exported header, it becomes:

```
// Exported header interface of the library.

#ifdef __cplusplus
extern "C" {
#endif

int add_int(int left, int right);
float add_float(float left, float right);
double add_double(double left, double right);

#ifdef __cplusplus
}

#ifdef __cplusplus

template <typename T>
add(T left, T right){
	if constexpr (std::is_same_v<T, float>){
		return add_float(left, right);
	}
	if constexpr (std::is_same_v<T, double>){
		return add_double(left, right);
	}
	// All the other "overloads" ...
}

#endif
```

This allows the user to call the library code conveniently:

```
template <typename T>
T user_code(T left, T right){
	return add(left, right);
}
```

Note that C functions cannot be overloaded so every "overload" must be exported with a unique function name. This can get very tedious if there are multiple templates, and there is a large range of types per template parameter that is exported. Consider mathematical libraries that need to export many, many data types (e.g.: different integer/floating point types, complex/real types, mixed-precision algorithms that take a combination of multiple types).

This package was created to make all of the above boiler-plate code more convenient. It originated as helper scripts for the convenience of my own mathematical projects, but I ended up using it enough to warrant it to become its own project.

## Description

Assuming you have a C++ functionality that you would like to export with C-linkage, this project will:
- wrap that C++ function in uniquely-named C functions, which are then exported.
- create inline C++ wrappers for the exported C functions, which are compiled along with the user code to maintain compatibility.

The script consumes a description of the C++ function as a JSON file. The schema is also provided and validated as part of the script.

As an example, if we wish to export the following functionality:

```
// T can be float, double
template <typename T>
T add(T left, T right);
```

The script will create an implementation file to be compiled with the library:

```
// Internal implementation of the library.

template <typename T>
T add(T left, T right);

float add_float(float left, float right){
	return add(left, right);
}

double add_double(double left, double right){
	return add(left, right);
}
```

For the user of your library, it will create the following header file with the exported interface, along with a C++ wrapper for convenience:

```
#ifdef __cplusplus
extern "C" {
#endif

float add_f32(float left, float right);
double add_f64(double left, double right);

#ifdef __cplusplus
}

#ifdef __cplusplus

template <typename T>
add(T left, T right);

template <typename T>
T add(T left, T right){
	if constexpr (std::is_same_v<T, float>){
		return add_f32(left, right);
	}
	if constexpr (std::is_same_v<T, double>){
		return add_f64(left, right);
	}
}

#endif
```

Note:
- The C++ wrapper function is declared before the inline implementation. This is to help the user have a clean interface to browse the header file, as the implementation of the wrapper should not be their concern.
- The script provides mapping from the types to the function suffixes (e.g. `float` -> `fp32`). These mapping are located in `utils/suffix_mappings.json` but can be overridden by supplying a `"suffix-mapping"` key in the config JSON (as seen in the `advanced` example).
- The C++ wrapper function arguments must be compatible with C (so no std::XXX).

The user of the library can then either directly call the C functions or the C++ wrapper function as desired:

```
template <typename T>
T user_code(T left, T right){
	// Use C++ wrapper.
	return add(left, right);
}

float user_code2(float left, float right){
	// Use C function.
	return add_fp32(left, right);
}
```

The generation of these files is defined by a JSON file supplied to the script:

```
{
    "$schema": "https://raw.githubusercontent.com/theComputeKid/scrapper/main/utils/schema.json",
    "linkage-macro": "MY_SIMPLE_PROJECT",
    "functions": [
        {
            "name": "add",
            "combination": "all",
            "templates": [
                {
                    "name": "T",
                    "types": [
                        "float",
                        "double"
                    ]
                }
            ],
            "parameters": [
                {
                    "name": "left",
                    "type": "T",
                    "const": false,
                    "pointer": false
                },
                {
                    "name": "right",
                    "type": "T",
                    "const": false,
                    "pointer": false
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

Other examples can be seen in the examples folder. The script can be called by providing the input JSON file.

```
python ./scrapper.py examples/simple.json --output-header out/simple.h --output-impl out/simple.hpp
python ./scrapper.py examples/advanced.json -oh out/advanced.h -oi out/advanced.hpp
```


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
```
For older versions of cmake, you will need to configure manually (you can use the presets.json as a guide).

## JSON schema

The schema is provided as part of the project in `utils/schema.json`, and can be seen used in the examples.
