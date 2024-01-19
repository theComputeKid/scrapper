def get_type_suffix(types: list[str]) -> str:
    mapping = {
        "int8_t": "i8",
        "int16_t": "i16",
        "int32_t": "i32",
        "int64_t": "i64",
        "uint8_t": "ui8",
        "uint16_t": "ui16",
        "uint32_t": "ui32",
        "uint64_t": "ui64",
        "half": "f16",
        "float": "f32",
        "double": "f64",
    }
    suffix = ""
    for t in types:
        if t in mapping:
            suffix += mapping[t]
        else:
            suffix += t
    return suffix
