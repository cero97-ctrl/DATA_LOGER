import sys
import platform
import os
import subprocess
import shutil
import multiprocessing

def run_diagnostic():
    """
    Script de diagnóstico adaptado para el proyecto DATA_LOGER_IOT.
    Valida el entorno de desarrollo, la conexión con el hardware y el sandbox.
    """
    print("=" * 60)
    print("ENVIRONMENT DIAGNOSTIC REPORT - DATA_LOGER_IOT")
    print("=" * 60)

    # --- CORE ---
    print(f"\n--- OPERATING SYSTEM ---")
    print(f"OS:             {platform.platform()}")
    print(f"Architecture:   {platform.machine()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Executable:     {sys.executable}")
    venv = os.environ.get('VIRTUAL_ENV') or os.environ.get('CONDA_DEFAULT_ENV')
    print(f"Environment:    {venv or 'System Python'}")

    # --- DOCKER / SANDBOX (Regla 1 & 3) ---
    print(f"\n--- DOCKER / SANDBOX ---")
    docker_bin = shutil.which("docker")
    if docker_bin:
        try:
            # Verificar si la imagen pcb_sandbox existe
            img_check = subprocess.run(
                ["docker", "images", "-q", "pcb_sandbox"], 
                capture_output=True, text=True, timeout=5
            )
            has_image = "FOUND" if img_check.stdout.strip() else "NOT FOUND"
            print(f"Docker Bin:     {docker_bin}")
            print(f"pcb_sandbox:    {has_image}")
        except subprocess.TimeoutExpired:
            print("Docker:         Timeout (¿Servicio caído?)")
        except Exception as e:
            print(f"Docker Error:   {str(e)}")
    else:
        print("Docker:         NOT INSTALLED")

    # --- HARDWARE & PORTS (Específico ESP32-S3) ---
    print(f"\n--- HARDWARE & PORTS ---")
    esp_port = "/dev/ttyACM0"
    if os.path.exists(esp_port):
        # Verificar permisos de lectura/escritura (Crítico para flashing/monitor)
        perms = "READ/WRITE OK" if os.access(esp_port, os.R_OK | os.W_OK) else "PERMISSION DENIED"
        print(f"ESP32-S3 Port:  {esp_port} ({perms})")
    else:
        print(f"ESP32-S3 Port:  {esp_port} NOT FOUND (Verificar conexión USB)")

    # --- RESOURCES (Regla 1: Límite 4GB) ---
    print(f"\n--- SYSTEM RESOURCES ---")
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if 'MemTotal' in line or 'MemAvailable' in line:
                    print(f"{line.strip()}")
    except FileNotFoundError:
        print("RAM:            Could not read /proc/meminfo (Non-Linux?)")

    # --- CRITICAL PACKAGES ---
    print(f"\n--- PYTHON PACKAGES ---")
    for pkg in ["serial", "numpy"]:
        try:
            __import__(pkg)
            print(f"{pkg:12}: INSTALLED")
        except ImportError:
            print(f"{pkg:12}: MISSING")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_diagnostic()