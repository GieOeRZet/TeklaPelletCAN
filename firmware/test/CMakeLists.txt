cmake_minimum_required(VERSION 3.16)
project(teklapelletcan_host_tests CXX)
set(CMAKE_CXX_STANDARD 17)
set(CORE ${CMAKE_CURRENT_LIST_DIR}/../components/core)
add_executable(test_core test_core.cpp ${CORE}/sdo.cpp ${CORE}/codec.cpp ${CORE}/mcp2515.cpp ${CORE}/version.cpp ${CORE}/net_fsm.cpp
    ${CORE}/point.cpp ${CORE}/points_table.cpp ${CORE}/access.cpp ${CORE}/sdo_queue.cpp ${CORE}/license.cpp ${CORE}/license_pubkey.cpp
    ${CORE}/reads.cpp ${CORE}/reads_table.cpp ${CORE}/engine.cpp)
target_link_libraries(test_core mbedcrypto)
target_compile_options(test_core PRIVATE -Wall -Wextra)
enable_testing()
add_test(NAME core COMMAND test_core)

add_executable(test_engine test_engine.cpp ${CORE}/sdo.cpp ${CORE}/codec.cpp ${CORE}/point.cpp ${CORE}/points_table.cpp
    ${CORE}/access.cpp ${CORE}/sdo_queue.cpp ${CORE}/reads.cpp ${CORE}/reads_table.cpp ${CORE}/engine.cpp
    ${CORE}/license.cpp ${CORE}/license_pubkey.cpp)
target_link_libraries(test_engine mbedcrypto)
target_compile_options(test_engine PRIVATE -Wall -Wextra)
add_test(NAME engine COMMAND test_engine)
