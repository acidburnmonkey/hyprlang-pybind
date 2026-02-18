cmake_minimum_required(VERSION 3.19)
project(hyprlang-python LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(pybind11 CONFIG REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(hyprlang REQUIRED IMPORTED_TARGET hyprlang)

pybind11_add_module(_core src/bindings.cpp)
target_link_libraries(_core PRIVATE PkgConfig::hyprlang)
install(TARGETS _core DESTINATION hyprlang_pybind)
