#include "driver/gpio.h"
#include "driver/i2c.h"
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
 * @brief Estructura para almacenar fecha y hora del RTC
 */
typedef struct {
  uint8_t sec;
  uint8_t min;
  uint8_t hour;
  uint8_t day;
  uint8_t date;
  uint8_t month;
  uint16_t year;
} ds3231_time_t;

// Conversión BCD a Decimal
static uint8_t bcd2dec(uint8_t val) { return ((val / 16 * 10) + (val % 16)); }
// Conversión Decimal a BCD
static uint8_t dec2bcd(uint8_t val) { return ((val / 10 * 16) + (val % 10)); }

/**
 * @brief Lee la hora actual del DS3231
 */
esp_err_t ds3231_get_time(ds3231_time_t *time) {
  uint8_t data[7];
  uint8_t reg = 0x00;

  esp_err_t ret = i2c_master_write_read_device(
      I2C_MASTER_NUM, DS3231_ADDR, &reg, 1, data, 7, pdMS_TO_TICKS(1000));
  if (ret != ESP_OK)
    return ret;

  time->sec = bcd2dec(data[0]);
  time->min = bcd2dec(data[1]);
  time->hour = bcd2dec(data[2] & 0x3F); // Modo 24h
  time->day = bcd2dec(data[3]);
  time->date = bcd2dec(data[4]);
  time->month = bcd2dec(data[5] & 0x1F);
  time->year = bcd2dec(data[6]) + 2000;

  return ESP_OK;
}

/**
 * @brief Establece la hora en el DS3231
 */
esp_err_t ds3231_set_time(const ds3231_time_t *time) {
  uint8_t data[8];
  data[0] = 0x00; // Registro inicial
  data[1] = dec2bcd(time->sec);
  data[2] = dec2bcd(time->min);
  data[3] = dec2bcd(time->hour);
  data[4] = dec2bcd(time->day);
  data[5] = dec2bcd(time->date);
  data[6] = dec2bcd(time->month);
  data[7] = dec2bcd(time->year % 100);

  return i2c_master_write_to_device(I2C_MASTER_NUM, DS3231_ADDR, data, 8,
                                    pdMS_TO_TICKS(1000));
}

/**
 * @brief Lee la temperatura interna del DS3231
 */
esp_err_t ds3231_get_temp(float *temp) {
  uint8_t data[2];
  uint8_t reg = 0x11;

  esp_err_t ret = i2c_master_write_read_device(
      I2C_MASTER_NUM, DS3231_ADDR, &reg, 1, data, 2, pdMS_TO_TICKS(1000));
  if (ret != ESP_OK)
    return ret;

  int8_t integer = (int8_t)data[0];
  uint8_t fraction = data[1] >> 6;
  *temp = integer + (fraction * 0.25f);

  return ESP_OK;
}

/**
 * @brief Inicializa el bus I2C para el RTC DS3231
 */
void init_i2c_bus(void) {
  i2c_config_t conf = {
      .mode = I2C_MODE_MASTER,
      .sda_io_num = I2C_MASTER_SDA_IO,
      .sda_pullup_en = GPIO_PULLUP_ENABLE,
      .scl_io_num = I2C_MASTER_SCL_IO,
      .scl_pullup_en = GPIO_PULLUP_ENABLE,
      .master.clk_speed = 100000, // 100kHz standard mode
  };

  esp_err_t err = i2c_param_config(I2C_MASTER_NUM, &conf);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "I2C config failed");
    return;
  }
  ESP_ERROR_CHECK(i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0));
  ESP_LOGI(TAG, "I2C bus initialized (SDA: %d, SCL: %d)", I2C_MASTER_SDA_IO,
           I2C_MASTER_SCL_IO);
}

/**
 * @brief Escanea el bus I2C en busca de dispositivos conectados.
 */
void i2c_master_scan(void) {
  ESP_LOGI(TAG, "Scanning I2C bus...");
  for (uint8_t i = 1; i < 127; i++) {
    int ret = i2c_master_probe(I2C_MASTER_NUM, i, 100 / portTICK_PERIOD_MS);
    if (ret == ESP_OK) {
      ESP_LOGI(TAG, "Found device at I2C address 0x%02X", i);
    }
  }
  ESP_LOGI(TAG, "I2C scan complete.");
}

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
  init_i2c_bus();
  init_sd_card();

  i2c_master_scan();

  ds3231_time_t now;
  float temp;

  while (1) {
    if (ds3231_get_time(&now) == ESP_OK) {
      if (ds3231_get_temp(&temp) == ESP_OK) {
        ESP_LOGI(TAG, "RTC Time: %04d-%02d-%02d %02d:%02d:%02d | Temp: %.2f C",
                 now.year, now.month, now.date, now.hour, now.min, now.sec,
                 temp);
      }
    } else {
      ESP_LOGE(TAG, "Could not read RTC. Check connections.");
    }
    vTaskDelay(pdMS_TO_TICKS(5000));
  }
}