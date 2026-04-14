#include "driver/gpio.h"
#include "driver/sdspi_host.h"
#include "driver/uart.h"
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "pinout.h"
#include "sdmmc_cmd.h"
#include <stdio.h>

static const char *TAG = "DATA_LOGER";

/**
 * @brief Inicializa el driver UART para comunicación RS485
 */
void init_rs485(void) {
  const uart_config_t uart_config = {
      .baud_rate = 115200,
      .data_bits = UART_DATA_8_BITS,
      .parity = UART_PARITY_DISABLE,
      .stop_bits = UART_STOP_BITS_1,
      .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
      .source_clk = UART_SCLK_DEFAULT,
  };

  // Instalar el driver (Buffers de 1024 bytes)
  ESP_ERROR_CHECK(
      uart_driver_install(RS485_UART_PORT, 1024 * 2, 0, 0, NULL, 0));

  // Configurar parámetros
  ESP_ERROR_CHECK(uart_param_config(RS485_UART_PORT, &uart_config));

  // Configurar pines (TX, RX, RTS, CTS)
  ESP_ERROR_CHECK(uart_set_pin(RS485_UART_PORT, RS485_TX_IO, RS485_RX_IO,
                               RS485_RTS_IO, UART_PIN_NO_CHANGE));

  // Establecer modo RS485 Half-Duplex (Control automático de RTS/DE)
  ESP_ERROR_CHECK(uart_set_mode(RS485_UART_PORT, UART_MODE_RS485_HALF_DUPLEX));

  ESP_LOGI(TAG, "RS485 initialized on UART%d (TX:%d, RX:%d, RTS:%d)",
           RS485_UART_PORT, RS485_TX_IO, RS485_RX_IO, RS485_RTS_IO);
}

void init_hw_relays(void) {
  // Configuración de los pines de los relés como salida
  gpio_config_t io_conf = {
      .pin_bit_mask = (1ULL << RELAY_1_IO) | (1ULL << RELAY_2_IO),
      .mode = GPIO_MODE_OUTPUT,
      .pull_up_en = GPIO_PULLUP_DISABLE,
      .pull_down_en = GPIO_PULLDOWN_DISABLE,
      .intr_type = GPIO_INTR_DISABLE,
  };
  gpio_config(&io_conf);
  ESP_LOGI(TAG, "Relays initialized on GPIO %d and %d", RELAY_1_IO, RELAY_2_IO);
}

/**
 * @brief Inicializa la tarjeta SD vía bus SPI
 */
void init_sd_card(void) {
  esp_vfs_fat_sdmmc_mount_config_t mount_config = {
      .format_if_mount_failed = true,
      .max_files = 5,
      .allocation_unit_size = 16 * 1024};
  sdmmc_card_t *card;
  const char mount_point[] = "/sdcard";

  sdmmc_host_t host = SDSPI_HOST_DEFAULT();
  spi_bus_config_t bus_cfg = {
      .mosi_io_num = SD_MOSI_IO,
      .miso_io_num = SD_MISO_IO,
      .sclk_io_num = SD_SCLK_IO,
      .quadwp_io_num = -1,
      .quadhd_io_num = -1,
      .max_transfer_sz = 4000,
  };

  esp_err_t ret = spi_bus_initialize(host.slot, &bus_cfg, SPI_DMA_CH_AUTO);
  if (ret != ESP_OK) {
    ESP_LOGE(TAG, "Failed to initialize SPI bus for SD.");
    return;
  }

  sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
  slot_config.gpio_cs = SD_CS_IO;
  slot_config.host_id = host.slot;

  ESP_LOGI(TAG, "Mounting SD card...");
  ret = esp_vfs_fat_sdspi_mount(mount_point, &host, &slot_config, &mount_config,
                                &card);

  if (ret != ESP_OK) {
    ESP_LOGE(TAG, "Failed to mount SD card (%s)", esp_err_to_name(ret));
    return;
  }
  ESP_LOGI(TAG, "SD Card mounted successfully.");
  sdmmc_card_print_info(stdout, card);
}

void app_main(void) {
  ESP_LOGI(TAG, "Initializing DATA_LOGER_IOT Firmware for ESP32-S3...");

  // Inicializar hardware básico
  init_hw_relays();
  init_rs485();
  init_sd_card();

  while (1) {
    ESP_LOGD(TAG, "System alive...");
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}