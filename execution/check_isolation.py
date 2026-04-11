import sys
import os
import re
import json

def check_pcb_isolation_rule(pcb_file_path, min_clearance=4.0):
    """
    Verifica si existe una regla de clearance de al menos min_clearance en el archivo .kicad_pcb.
    """
    if not os.path.exists(pcb_file_path):
        return {"status": "ERROR", "message": f"Archivo no encontrado: {pcb_file_path}"}

    try:
        with open(pcb_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Busca la definición de clearance en reglas personalizadas o netclasses
        # Patrón simple para encontrar valores de clearance cerca de términos de aislamiento
        pattern = r'clearance\s+([\d\.]+)'
        clearances = [float(c) for c in re.findall(pattern, content)]

        max_found = max(clearances) if clearances else 0

        return {
            "status": "SUCCESS" if max_found >= min_clearance else "WARNING",
            "max_clearance_found": max_found,
            "required_clearance": min_clearance,
            "rule_detected": "clearance" in content.lower()
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ERROR", "message": "Uso: python check_isolation.py <archivo.kicad_pcb>"}))
        sys.exit(1)

    result = check_pcb_isolation_rule(sys.argv[1])
    print(json.dumps(result, indent=4))
    if result["status"] == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)