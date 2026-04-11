import subprocess
import sys
import os
import json

def run_kicad_cmd(project_dir, cmd):
    """
    Ejecuta un comando de kicad-cli dentro de un contenedor Docker.
    """
    abs_project_path = os.path.abspath(project_dir)
    
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_project_path}:/project",
        "-w", "/project",
        "kicad/kicad:8.0",
        "kicad-cli"
    ] + cmd

    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)
        return {"status": "SUCCESS", "stdout": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "ERROR", "stderr": e.stderr, "stdout": e.stdout}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    # Ejemplo de uso: python run_kicad_sandbox.py pcb export drv --output reports/drc.rpt board.kicad_pcb
    if len(sys.argv) < 2:
        print(json.dumps({"status": "ERROR", "message": "Faltan argumentos de comando KiCad"}))
        sys.exit(1)

    # Asumimos que la carpeta de hardware es el contexto
    hardware_dir = "hardware"
    kicad_args = sys.argv[1:]
    
    response = run_kicad_cmd(hardware_dir, kicad_args)
    print(json.dumps(response, indent=4))
    
    if response["status"] == "SUCCESS":
        sys.exit(0)
    else:
        sys.exit(1)