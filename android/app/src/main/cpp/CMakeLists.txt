cmake_minimum_required(VERSION 3.22)
project(tpc_demo CXX)
set(CMAKE_CXX_STANDARD 17)
set(CORE ${CMAKE_CURRENT_LIST_DIR}/../../../../../firmware/components/core)
add_library(tpc_demo SHARED tpc_jni.cpp
    ${CORE}/demo_device.cpp ${CORE}/logring.cpp ${CORE}/sdo.cpp ${CORE}/codec.cpp ${CORE}/point.cpp ${CORE}/points_table.cpp
    ${CORE}/access.cpp ${CORE}/sdo_queue.cpp ${CORE}/reads.cpp ${CORE}/reads_table.cpp ${CORE}/engine.cpp
    ${CORE}/entities.cpp ${CORE}/entities_table.cpp ${CORE}/alarms.cpp ${CORE}/alarm_names_table.cpp ${CORE}/json_parse.cpp ${CORE}/api.cpp)
target_include_directories(tpc_demo PRIVATE ${CORE})
target_compile_options(tpc_demo PRIVATE -Wall -O2 -fno-exceptions -fvisibility=hidden)
target_link_libraries(tpc_demo log)
