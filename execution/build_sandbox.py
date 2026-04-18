#!/usr/bin/env python3
import subprocess
import os
import json
import sys

def build_sandbox():
    """
    Construye la imagen Docker pcb_sandbox necesaria para la validación de firmware.
    """
    project_root = "/home/cero/MEGA/VS_CODE_WORKSPACE/DATA_LOGER"
    dockerfile_path = os.path.join(project_root, "docker/Dockerfile")
    context_path = os.path.join(project_root, "docker")
    tag = "pcb_sandbox"

    if not os.path.exists(dockerfile_path):
        print(json.dumps({"status": "error", "message": "Dockerfile no encontrado en docker/"}))
        sys.exit(1)

    cmd = ["docker", "build", "-t", tag, "-f", dockerfile_path, context_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(json.dumps({
                "status": "success",
                "message": f"Imagen {tag} construida exitosamente.",
                "details": "Entorno con build-essential listo para validación de C."
            }))
            sys.exit(0)
        else:
            print(json.dumps({
                "status": "error",
                "error_type": "Entorno",
                "stderr": result.stderr
            }))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    build_sandbox()