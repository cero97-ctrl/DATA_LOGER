import sys
import json
import re
import os

def verify_netlist(netlist_path):
    """
    Valida la presencia de componentes críticos en un archivo Netlist de KiCad.
    """
    if not os.path.exists(netlist_path):
        return {"status": "ERROR", "message": f"Archivo no encontrado: {netlist_path}"}

    try:
        with open(netlist_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Definición de componentes requeridos y sus patrones de búsqueda (Value o Footprint)
        requirements = {
            "MCU_ESP32-S3": {"pattern": r"ESP32-S3", "min_qty": 1},
            "RTC_DS3231": {"pattern": r"DS3231", "min_qty": 1},
            "RS485_Transceiver": {"pattern": r"SP3485|MAX485", "min_qty": 1},
            "MicroSD_Slot": {"pattern": r"MicroSD|SD_Card", "min_qty": 1},
            "Relays": {"pattern": r"Relay", "min_qty": 2},
            "Temp_Sensor_DS18B20": {"pattern": r"DS18B20", "min_qty": 1},
            "Buck_TPS5430": {"pattern": r"TPS5430", "min_qty": 1}
        }

        report = {}
        all_passed = True

        for comp_name, criteria in requirements.items():
            found_count = len(re.findall(criteria["pattern"], content, re.IGNORECASE))
            status = found_count >= criteria["min_qty"]
            
            report[comp_name] = {
                "found": found_count,
                "required": criteria["min_qty"],
                "status": "OK" if status else "MISSING"
            }
            
            if not status:
                all_passed = False

        return {
            "status": "SUCCESS" if all_passed else "FAILED",
            "check_results": report
        }

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ERROR", "message": "Uso: python verify_netlist.py <ruta_al_archivo.net>"}))
        sys.exit(1)

    net_path = sys.argv[1]
    result = verify_netlist(net_path)
    print(json.dumps(result, indent=4))
    
    if result["status"] == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)