cmake_minimum_required(VERSION 3.16)
project(teklapelletcan_host_tests CXX)
set(CMAKE_CXX_STANDARD 17)
set(CORE ${CMAKE_CURRENT_LIST_DIR}/../components/core)
add_executable(test_core test_core.cpp ${CORE}/sdo.cpp ${CORE}/codec.cpp ${CORE}/mcp2515.cpp ${CORE}/version.cpp ${CORE}/net_fsm.cpp
    ${CORE}/point.cpp ${CORE}/points_table.cpp ${CORE}/access.cpp ${CORE}/sdo_queue.cpp)
target_compile_options(test_core PRIVATE -Wall -Wextra)
enable_testing()
add_test(NAME core COMMAND test_core)
