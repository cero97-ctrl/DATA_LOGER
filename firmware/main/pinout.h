#ifndef PINOUT_H
#define PINOUT_H

// RS485 Configuration (UART1)
#define RS485_UART_PORT     UART_NUM_1
#define RS485_TX_IO         (17)
#define RS485_RX_IO         (18)
#define RS485_RTS_IO        (16) // Control DE/RE pin

// SD Card SPI Configuration
#define SD_CS_IO            (10)
#define SD_MOSI_IO          (11)
#define SD_MISO_IO          (13)
#define SD_SCLK_IO          (12)

// Relay Control GPIOs
#define RELAY_1_IO          (4)
#define RELAY_2_IO          (5)

#endif // PINOUT_H