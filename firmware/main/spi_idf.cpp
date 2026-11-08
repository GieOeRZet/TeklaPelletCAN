#include "spi_idf.h"
#include <cstring>

bool IdfSpi::init(int sck, int miso, int mosi, int cs, int clock_hz) {
    spi_bus_config_t bus = {};
    bus.mosi_io_num = mosi;
    bus.miso_io_num = miso;
    bus.sclk_io_num = sck;
    bus.quadwp_io_num = -1;
    bus.quadhd_io_num = -1;
    bus.max_transfer_sz = 32;
    if (spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO) != ESP_OK) return false;

    spi_device_interface_config_t dev = {};
    dev.clock_speed_hz = clock_hz;
    dev.mode = 0;
    dev.spics_io_num = cs;
    dev.queue_size = 2;
    return spi_bus_add_device(SPI2_HOST, &dev, &dev_) == ESP_OK;
}

bool IdfSpi::transfer(const uint8_t* tx, uint8_t* rx, size_t len) {
    if (!dev_ || len == 0 || len > 32) return false;
    spi_transaction_t t = {};
    t.length = len * 8;
    t.tx_buffer = tx;
    t.rx_buffer = rx;
    return spi_device_polling_transmit(dev_, &t) == ESP_OK;
}
