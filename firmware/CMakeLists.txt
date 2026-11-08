cmake_minimum_required(VERSION 3.16)
# Budowa dla ESP-IDF:  idf.py set-target esp32c6 && idf.py build
# Testy na hoście:     cmake -S test -B build-host && cmake --build build-host && ctest --test-dir build-host
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
set(EXTRA_COMPONENT_DIRS ${CMAKE_CURRENT_LIST_DIR}/components)
set(PROJECT_VER "0.2.0")
project(teklapelletcan)
