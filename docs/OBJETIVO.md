#### **1. Objetivo del Proyecto**
Se llevará a cabo el diseño de un **Data Logger IoT de alto rendimiento** basado en el microcontrolador **ESP32-S3**. Este dispositivo estará destinado al monitoreo industrial y contará con una entrada de **12V DC**. El sistema integrará las siguientes capacidades técnicas:
*   Sincronización temporal mediante un **RTC (DS3231)** con respaldo de batería.
*   Almacenamiento masivo en **tarjeta microSD** vía protocolo SPI.
*   Monitoreo ambiental con un sensor de temperatura **DS18B20**.
*   Control de actuadores mediante **dos relés** con botones de activación manual.
*   Comunicación industrial a través de un puerto **RS485** y conectividad **USB-C** para programación.

#### **2. Integración de Gemini Code Assistant a la Capa de Orquestación de la Fase Inicial**
Para la concepción del sistema, se utilizará **Gemini** con el fin de generar el **diagrama de bloques** y realizar la selección preliminar de componentes. Se espera que la IA proponga una arquitectura de potencia que convierta los 12V de entrada en rieles de 5V y 3.3V para el microcontrolador y periféricos.
*   **Criterio de ingeniería:** El diseñador supervisará las propuestas de la IA, optando por **relés compactos** y conectores **JST** en lugar de cabezales de pines tradicionales para optimizar el espacio y la practicidad del montaje.

#### **3. Validación y Revisión del Esquemático con Gemini**
Una vez finalizado el esquema en KiCad, se exportará para que **Gemini realice una validación técnica exhaustiva**. El objetivo es identificar posibles errores u omisiones antes de la fabricación, tales como:
*   Verificación de **condensadores de desacoplo** en el ESP32-S3.
*   Confirmación de componentes críticos, como la **resistencia de base** para el transistor del buzzer y condensadores para el LED RGB.
*   Se mantendrá un enfoque de "humano en el bucle", donde el ingeniero validará cada alerta de la IA utilizando su propio conocimiento técnico.

#### **4. Directrices para el Diseño de la PCB (Layout)**
El trazado de la placa seguirá reglas de diseño asistidas por las recomendaciones técnicas de Gemini para asegurar la integridad de la señal:
*   **Gestión de pistas:** Se planean anchos de **0.3 mm** para señales, **0.5 mm** para alimentación y **2 mm** para las líneas de AC y USB.
*   **Seguridad y Térmica:** Se implementará un aislamiento (**creepage**) de al menos **4 mm** entre las líneas de alto y bajo voltaje. Además, se colocarán **vías térmicas** bajo el pad del TPS5430 para la disipación de calor.
*   **Señales Críticas:** Se aplicará **length matching** (emparejamiento de longitud) en las rutas de datos de USB, SD y RS485 para prevenir fallos de comunicación.

#### **5. Finalización y Estética Profesional**
El proyecto concluirá con un enfoque en la calidad de fabricación y la estética. Se planea integrar **gráficos personalizados en la serigrafía** para darle un acabado profesional a la placa. Finalmente, se empleará el **visor 3D de KiCad** para realizar una inspección visual de la disposición de los componentes y las áreas de aislamiento antes de enviar el diseño a producción.