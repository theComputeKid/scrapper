cmake_minimum_required(VERSION 3.16)

set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_VISIBILITY_INLINES_HIDDEN 1)

project(scrapper-demo C CXX)

# * Generate the headers.
if(CRAPPER_SPLIT)
	set(CRAPPER_SPLIT_FLAG -s)
endif()

if(NOT Python3_ROOT_DIR)
	set(Python3_ROOT_DIR "../*" CACHE STRING "" FORCE)
endif()

find_package(Python3 COMPONENTS Interpreter REQUIRED)

add_custom_target(
	run-scrapper ALL
	COMMAND ${Python3_EXECUTABLE} scrapper.py test/add.json -oh test/out/exported-interface.h -oi test/out/internal-impl.hpp ${CRAPPER_SPLIT_FLAG}
	COMMENT "Running scrapper."
	WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}/..
)

# * Compile the library.
add_library(scrapper-lib SHARED library.cpp)
add_dependencies(scrapper-lib run-scrapper)

# * Compile the user C++ code.
add_executable(scrapper-cpp-exe user.cpp)
target_link_libraries(scrapper-cpp-exe scrapper-lib)

# * Compile the user C code.
add_executable(scrapper-c-exe user.c)
target_link_libraries(scrapper-c-exe scrapper-lib)

# * Test
enable_testing()
add_test(NAME scrapper-cpp-test COMMAND $<TARGET_FILE:scrapper-cpp-exe>)
add_test(NAME scrapper-c-test COMMAND $<TARGET_FILE:scrapper-c-exe>)
