# Karta WWW (web/) jest pakowana (gzip) do tablicy C++ i osadzana w obrazie: jedna paczka = firmware + interfejs.
set(WEB_DIR ${CMAKE_CURRENT_LIST_DIR}/../../web)
set(WEB_GEN ${CMAKE_CURRENT_BINARY_DIR}/web_assets.cpp)
file(GLOB_RECURSE WEB_FILES ${WEB_DIR}/*.js ${WEB_DIR}/*.html ${WEB_DIR}/*.css ${WEB_DIR}/img/*)
execute_process(COMMAND ${PYTHON} ${CMAKE_CURRENT_LIST_DIR}/../../tools/pack_web.py ${WEB_DIR} ${WEB_GEN}
                RESULT_VARIABLE PACK_RC OUTPUT_VARIABLE PACK_OUT)
if(NOT PACK_RC EQUAL 0)
    message(FATAL_ERROR "pack_web.py nie powiodlo sie")
endif()
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${WEB_FILES} ${CMAKE_CURRENT_LIST_DIR}/../../tools/pack_web.py)

idf_component_register(
    SRCS main.cpp spi_idf.cpp firstboot.cpp logging.cpp store.cpp wifi_mgr.cpp http_srv.cpp mdns_srv.cpp ota_idf.cpp ${WEB_GEN}
    INCLUDE_DIRS "." 
    REQUIRES core driver esp_driver_gpio esp_timer esp_hw_support esp_system esp_wifi esp_netif esp_event nvs_flash esp_http_server
             app_update esp_partition lwip mbedtls)
