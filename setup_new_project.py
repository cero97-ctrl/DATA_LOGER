import os
import subprocess
import json
import shutil
import datetime

def create_project_structure(project_root, project_name):
    """Crea la estructura de carpetas estándar para el nuevo proyecto."""
    print(f"Creando estructura de carpetas para el proyecto '{project_name}' en '{project_root}'...")
    
    # Directorios base
    base_dirs = [
        os.path.join(project_root, "directives"),
        os.path.join(project_root, "execution"),
        os.path.join(project_root, ".tmp"),
        os.path.join(project_root, ".gemini"),
        os.path.join(project_root, "hardware"),
        os.path.join(project_root, "docker")
    ]
    # Directorios anidados
    nested_dirs = [
        os.path.join(project_root, "firmware", "main")
    ]

    for d in base_dirs + nested_dirs:
        os.makedirs(d, exist_ok=True)
        print(f"  - Creado: {d}/")

def update_agent_framework(project_root, project_name):
    """Actualiza AGENT_FRAMEWORK.md con el nombre del nuevo entorno Conda."""
    framework_path = os.path.join(project_root, ".gemini", "AGENT_FRAMEWORK.md")
    conda_env_name = f"{project_name.lower().replace(' ', '_')}_env"

    if os.path.exists(framework_path):
        with open(framework_path, 'r') as f:
            content = f.read()
        
        # Reemplazar los placeholders genéricos
        new_content = content.replace("<PROJECT_NAME>_env", conda_env_name)
        
        with open(framework_path, 'w') as f:
            f.write(new_content)
        print(f"  - Actualizado: {framework_path} con el nombre del entorno '{conda_env_name}'.")
    else:
        print(f"Advertencia: {framework_path} no encontrado. No se pudo actualizar el nombre del entorno.")

def update_run_state(project_root, project_name):
    """Inicializa o actualiza .tmp/run_state.json con la información del nuevo proyecto."""
    run_state_path = os.path.join(project_root, ".tmp", "run_state.json")
    conda_env_name = f"{project_name.lower().replace(' ', '_')}_env"
    
    run_state_data = {
        "project_name": project_name,
        "conda_environment": conda_env_name,
        "current_phase": "INITIAL_SETUP",
        "last_step_completed": 0,
        "history": [
            {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds') + "Z",
                "step": 0,
                "action": "Inicialización de nuevo proyecto",
                "exit_code": 0,
                "observations": "Estructura de carpetas creada, AGENT_FRAMEWORK.md y run_state.json actualizados."
            }
        ]
    }
    
    # Si run_state.json existe, intenta fusionar o actualizar campos específicos
    if os.path.exists(run_state_path):
        try:
            with open(run_state_path, 'r') as f:
                existing_data = json.load(f)
            existing_data["project_name"] = project_name
            existing_data["conda_environment"] = conda_env_name
            existing_data["current_phase"] = existing_data.get("current_phase", "INITIAL_SETUP")
            existing_data["last_step_completed"] = existing_data.get("last_step_completed", 0)
            
            # Añadir la entrada de historial sin borrar el existente
            new_history_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds') + "Z",
                "step": existing_data["last_step_completed"] + 1, # Incrementa el paso
                "action": "Inicialización de nuevo proyecto",
                "exit_code": 0,
                "observations": "Estructura de carpetas creada, AGENT_FRAMEWORK.md y run_state.json actualizados."
            }
            existing_data["history"].append(new_history_entry)
            existing_data["last_step_completed"] = new_history_entry["step"]
            run_state_data = existing_data
        except json.JSONDecodeError:
            print(f"Advertencia: {run_state_path} está corrupto o vacío. Se creará uno nuevo.")
    
    with open(run_state_path, 'w') as f:
        json.dump(run_state_data, f, indent=4)
    print(f"  - Actualizado: {run_state_path} con el nombre del proyecto y entorno.")

def modify_env_diagnostic_for_dynamic_title(project_root):
    """
    Modifica env_diagnostic.py para que el título del reporte sea dinámico,
    leyendo el project_name de run_state.json.
    """
    diagnostic_path = os.path.join(project_root, "env_diagnostic.py")
    run_state_path = os.path.join(project_root, ".tmp", "run_state.json")

    if not os.path.exists(diagnostic_path):
        print(f"Advertencia: {diagnostic_path} no encontrado. No se puede modificar el título dinámico.")
        return

    with open(diagnostic_path, 'r') as f:
        lines = f.readlines()

    new_lines = []
    modified = False
    for i, line in enumerate(lines):
        if "ENVIRONMENT DIAGNOSTIC REPORT -" in line and not modified:
            # Insertar código para leer project_name de run_state.json
            new_lines.append("    project_name = 'UNKNOWN_PROJECT'\n")
            new_lines.append(f"    run_state_path = os.path.join(os.path.dirname(__file__), '.tmp', 'run_state.json')\n")
            new_lines.append("    if os.path.exists(run_state_path):\n")
            new_lines.append("        try:\n")
            new_lines.append("            with open(run_state_path, 'r') as f_rs:\n")
            new_lines.append("                rs_data = json.load(f_rs)\n")
            new_lines.append("                project_name = rs_data.get('project_name', 'UNKNOWN_PROJECT')\n")
            new_lines.append("        except json.JSONDecodeError:\n")
            new_lines.append("            pass\n")
            new_lines.append(f"    print(f\"ENVIRONMENT DIAGNOSTIC REPORT - {{project_name}}\")\n")
            modified = True
        elif "ENVIRONMENT DIAGNOSTIC REPORT -" in line and modified:
            # Saltar la línea original si ya fue reemplazada
            continue
        else:
            new_lines.append(line)
    
    if modified:
        with open(diagnostic_path, 'w') as f:
            f.writelines(new_lines)
        print(f"  - Modificado: {diagnostic_path} para título dinámico.")
    else:
        print(f"Advertencia: No se encontró la línea del título en {diagnostic_path} para modificar.")

def run_environment_diagnostic(project_root):
    """Ejecuta el script env_diagnostic.py y muestra su salida."""
    print("\nEjecutando diagnóstico de entorno...")
    diagnostic_script_path = os.path.join(project_root, "env_diagnostic.py")
    if os.path.exists(diagnostic_script_path):
        try:
            result = subprocess.run(
                ["python3", diagnostic_script_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
            if result.stderr:
                print("Errores durante el diagnóstico:\n", result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar env_diagnostic.py: {e}")
            print("Salida estándar:\n", e.stdout)
            print("Salida de error:\n", e.stderr)
        except FileNotFoundError:
            print(f"Error: '{diagnostic_script_path}' no encontrado. Asegúrate de que esté en el directorio raíz del proyecto.")
    else:
        print(f"Error: '{diagnostic_script_path}' no encontrado. Asegúrate de que esté en el directorio raíz del proyecto.")

def main():
    print("--- Asistente de Configuración de Nuevo Proyecto ---")
    project_name = input("Introduce el nombre del nuevo proyecto (ej. MyNewProject): ").strip()
    if not project_name:
        print("El nombre del proyecto no puede estar vacío. Abortando.")
        return

    project_root = os.getcwd() # Asume que el script se ejecuta en la raíz del nuevo proyecto
    conda_env_name = f"{project_name.lower().replace(' ', '_')}_env"
    print(f"Se utilizará el nombre de entorno Conda: {conda_env_name}")

    create_project_structure(project_root, project_name)
    update_agent_framework(project_root, project_name)
    update_run_state(project_root, project_name)
    modify_env_diagnostic_for_dynamic_title(project_root)

    print("\n--- Pasos Siguientes ---")
    print(f"1. Crea y activa tu entorno Conda:")
    print(f"   conda create --name {conda_env_name} python=3.12 -y")
    print(f"   conda activate {conda_env_name}")
    print(f"2. Instala las dependencias (si tienes un requirements.txt):")
    print(f"   pip install -r requirements.txt")
    print(f"3. Ejecuta el diagnóstico de entorno para confirmar:")
    print(f"   python3 env_diagnostic.py")
    
    print("\n--- Diagnóstico Inicial (antes de activar el entorno Conda) ---")
    run_environment_diagnostic(project_root)

    print("\nConfiguración inicial completada. ¡Listo para empezar!")

if __name__ == "__main__":
    main()