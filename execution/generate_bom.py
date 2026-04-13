import sys
import os
import gc
import json
import csv

def ensure_kicad_env():
    """
    Asegura que el script se ejecute en el entorno con acceso a la API de KiCad 8.
    Hereda la lógica de blindaje de entorno del ADN del proyecto.
    """
    try:
        import pcbnew
        return pcbnew
    except ImportError:
        kicad_path = "/usr/lib/python3/dist-packages"
        if kicad_path not in sys.path:
            sys.path.insert(0, kicad_path)
        
        try:
            import pcbnew
            return pcbnew
        except ImportError:
            if 'CONDA_PREFIX' in os.environ:
                os.environ['PYTHONPATH'] = kicad_path
                os.execve('/usr/bin/python3', ['python3'] + sys.argv, os.environ)
            else:
                print(json.dumps({"status": "ERROR", "message": "No se pudo cargar la API de KiCad."}))
                sys.exit(1)

pcbnew = ensure_kicad_env()

def generate_bom(pcb_path, output_csv):
    """
    Extrae los componentes de la placa y genera un archivo CSV de Lista de Materiales.
    """
    try:
        if not os.path.exists(pcb_path):
            print(json.dumps({"status": "ERROR", "message": f"Archivo no encontrado: {pcb_path}"}))
            return False
            
        board = pcbnew.LoadBoard(pcb_path)
        bom_data = {}

        for fp in board.GetFootprints():
            # Forzamos casting a string de Python puro para evitar errores de hashing con pcbnew.UTF8
            # y asegurar que las llaves del diccionario sean comparables.
            ref   = str(fp.GetReference())
            value = str(fp.GetValue())
            fpid  = str(fp.GetFPID().GetLibItemName()) if fp.GetFPID() else "Unknown"
            
            # Aseguramos que la llave sea una tupla de strings puros
            key = (str(value), str(fpid))
            if key not in bom_data:
                bom_data[key] = {"refs": [], "count": 0}
            
            bom_data[key]["refs"].append(str(ref))
            bom_data[key]["count"] += 1

        with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Item", "Quantity", "Reference(s)", "Value", "Footprint"])
            
            for i, ((value, fpid), info) in enumerate(sorted(bom_data.items()), 1):
                writer.writerow([i, info["count"], ", ".join(sorted(info["refs"])), value, fpid])

        print(json.dumps({
            "status": "SUCCESS",
            "file": output_csv,
            "items_count": len(bom_data),
            "msg": "Lista de Materiales (BOM) generada exitosamente."
        }))
        gc.collect()
        return True
    except Exception as e:
        print(json.dumps({"status": "ERROR", "message": str(e)}))
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"status": "ERROR", "message": "Uso: python3 generate_bom.py <pcb_path> <output_csv>"}))
        sys.exit(1)
    
    generate_bom(sys.argv[1], sys.argv[2])
    sys.exit(0)