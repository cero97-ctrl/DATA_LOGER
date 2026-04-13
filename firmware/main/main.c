#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "pinout.h"

static const char *TAG = "DATA_LOGER";

void init_hw_relays(void)
{
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

void app_main(void)
{
    ESP_LOGI(TAG, "Initializing DATA_LOGER_IOT Firmware for ESP32-S3...");
    
    // Inicializar hardware básico
    init_hw_relays();
    
    while (1) {
        ESP_LOGD(TAG, "System alive...");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}