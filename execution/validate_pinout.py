#!/usr/bin/env python3
import subprocess
import os
import sys
import json

def validate_pinout():
    """
    Valida el archivo pinout.h mediante compilación real en el sandbox de Docker.
    """
    project_root = "/home/cero/MEGA/VS_CODE_WORKSPACE/DATA_LOGER"
    tmp_dir = os.path.join(project_root, ".tmp")
    test_c_path = os.path.join(tmp_dir, "test_pinout.c")
    output_bin = "/sandbox/.tmp/test_pinout_bin"
    
    # 1. Crear el código C de prueba
    test_code = """
#include <stdio.h>
#include "pinout.h"

int main() {
    printf("--- Pinout Validation ---\\n");
    printf("RS485 TX: %d\\n", RS485_TX_IO);
    printf("RS485 RX: %d\\n", RS485_RX_IO);
    printf("SD CS:    %d\\n", SD_CS_IO);
    printf("Relay 1:  %d\\n", RELAY_1_IO);
    printf("--- Syntax Check Passed ---\\n");
    return 0;
}
"""
    
    try:
        # Asegurar que el directorio .tmp existe
        os.makedirs(tmp_dir, exist_ok=True)
        
        # Escribir el archivo de prueba
        with open(test_c_path, "w") as f:
            f.write(test_code)
            
        # 2. Comando para ejecutar en Docker
        # Montamos el root del proyecto en /sandbox
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{project_root}:/sandbox",
            "pcb_sandbox",
            "sh", "-c",
            f"gcc -I/sandbox/firmware/main /sandbox/.tmp/test_pinout.c -o {output_bin} && {output_bin}"
        ]
        
        # 3. Ejecución
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(json.dumps({
                "status": "success",
                "output": result.stdout.strip(),
                "message": "Pinout validado correctamente en el sandbox."
            }))
            sys.exit(0)
        else:
            print(json.dumps({
                "status": "error",
                "error_type": "Lógica/Sintaxis",
                "stdout": result.stdout,
                "stderr": result.stderr
            }))
            sys.exit(1)
            
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    validate_pinout()