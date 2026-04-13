# Guía de Montaje: DATA_LOGER_IOT

## 1. Herramientas Necesarias
- Estación de aire caliente (Recomendado para componentes con Pad Térmico).
- Soldador de punta fina (para retoques).
- Pasta de soldadura o flux de alta calidad.
- Multímetro para pruebas de continuidad.

## 2. Orden de Ensamblaje Sugerido
Se recomienda seguir la regla de "menor a mayor altura" y "SMD antes que Through-Hole".

### Paso 1: Regulador de Voltaje TPS5430 (U2)
- **Encapsulado:** SO-PowerPAD-8.
- **Atención Crítica:** Este componente tiene un pad metálico en la parte inferior. **DEBE** soldarse obligatoriamente a la zona de vías térmicas en la PCB. 
- **Técnica:** Aplicar una pequeña cantidad de pasta en el pad central. Usar aire caliente a 320°C. El componente se auto-alineará.
- **Función:** Sin esta conexión, el regulador se sobrecalentará en menos de un minuto y fallará.

### Paso 2: Microcontrolador ESP32-S3-WROOM-1 (U1)
- **Encapsulado:** SMD Castellation.
- **Técnica:** Soldar primero los pines de las esquinas para alinear. Luego, soldar los laterales. 
- **Pad Central:** El módulo tiene un pad de tierra central. Si bien se puede soldar con aire caliente, los pines laterales (castellation) son los que llevan la señal. Asegurar buena continuidad en el pin 1 (GND) y los pines de alimentación.

### Paso 3: Conector de Alimentación JST PH (J1)
- **Tipo:** Through-Hole (Agujero pasante).
- **Polaridad:** Verificar la muesca del conector JST. El Pin 1 es +12V.
- **Soldadura:** Usar soldador convencional por la cara inferior (B.Cu).

## 3. Verificación Post-Montaje (Checklist)

### Prueba de Continuidad (SIN ALIMENTACIÓN)
1. [ ] Verificar que no hay corto entre **+12V** y **GND** en el conector J1.
2. [ ] Verificar continuidad entre el pin 7 de U2 (TPS5430) y el positivo de J1.
3. [ ] Verificar que el Pad Térmico de U2 tiene continuidad con el plano de masa (GND).

### Prueba de Voltaje (CON ALIMENTACIÓN)
1. Aplicar 12V en J1.
2. Medir la salida del regulador (debería haber ruteo hacia el LDO o el siguiente riel).
3. Confirmar que el ESP32-S3 recibe el voltaje adecuado en sus pines VDD.

## 4. Notas de Seguridad
- **ESD:** El ESP32-S3 es sensible a descargas electrostáticas. Usar pulsera antiestática.
- **Inspección Visual:** Usar una lupa o microscopio para asegurar que no hay puentes de soldadura entre los pines del PowerPAD del TPS5430.