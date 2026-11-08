cmake_minimum_required(VERSION 3.16)
# Budowa dla ESP-IDF:  idf.py set-target esp32c6 && idf.py build
# Testy na hoście:     cmake -S test -B build-host && cmake --build build-host && ctest --test-dir build-host
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
set(EXTRA_COMPONENT_DIRS ${CMAKE_CURRENT_LIST_DIR}/components)
# Wersja: plik VERSION w korzeniu repo; CI dopisuje numer budowy (TPC_VERSION="0.3.0+17"), co pozwala porównywać wydania.
file(READ ${CMAKE_CURRENT_LIST_DIR}/../VERSION TPC_BASE_VERSION)
string(STRIP "${TPC_BASE_VERSION}" TPC_BASE_VERSION)
if(DEFINED ENV{TPC_VERSION} AND NOT "$ENV{TPC_VERSION}" STREQUAL "")
    set(PROJECT_VER "$ENV{TPC_VERSION}")
else()
    set(PROJECT_VER "${TPC_BASE_VERSION}+0")
endif()
project(teklapelletcan)
