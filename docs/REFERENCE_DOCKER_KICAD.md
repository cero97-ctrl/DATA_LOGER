# Referencia: Sandbox KiCad en Docker

Este proyecto hereda la lógica de "Agente-IA-CIRCUITO-IMPRESO" para la automatización de hardware.

## Arquitectura del Sandbox
- **Imagen Base:** `ubuntu:22.04` (Para compatibilidad total con la API de KiCad y pcb2gcode).
- **Versión de KiCad:** `8.0.x` (Validado 8.0.9+).
- **Volúmenes:** Se monta el directorio `hardware/` del host en `/home/kicad/project` dentro del contenedor.
- **Comandos Headless:**
  - Generación de Netlist: `kicad-cli sch export netlist ...`
  - Verificación de Reglas (ERC/DRC): `kicad-cli pcb export report ...`
  - Generación de Gerbers: `kicad-cli pcb export gerber ...`

## Ventajas
- Ejecución determinista independiente del sistema operativo del host.
- Validación automática en pipelines de CI/CD o mediante la Capa de Orquestación.

## Checklist de Importación (Legacy: Agente-IA-CIRCUITO-IMPRESO)
Para integrar conocimiento previo, extraer de la carpeta del proyecto anterior:
1. **`Dockerfile`**: Basado en Ubuntu 22.04 con PPA de KiCad 8.0 oficial.
2. **`execution/kicad_auto_route.py`** (o similar): Lógica de ruteo programático.
3. **`directives/generate_gerbers.yaml`**: Flujo de pasos para producción.
4. **`requirements.txt`**: Debe incluir `pcb-tools-extension` y `pathfinding`.
5. **Logs de errores (Críticos para DATA_LOGER)**: 
    - **API KiCad 8**: Usar siempre `VECTOR2I` para coordenadas (adiós a `wxPoint`).
    - **Exportación**: No usar `SetExcludeEdgeLayer()`, genera errores en v8.
    - **Rendimiento**: Activar `ZRAM` con `zstd` si se ejecuta junto a Ollama.