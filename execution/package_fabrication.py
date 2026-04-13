import os
import zipfile
import json
import sys

def package_gerbers(gerber_dir, output_zip):
    """
    Empaqueta todos los archivos contenidos en el directorio de gerbers en un archivo ZIP.
    """
    if not os.path.exists(gerber_dir):
        print(json.dumps({"status": "ERROR", "message": f"El directorio {gerber_dir} no existe."}))
        return False

    files_to_include = [f for f in os.listdir(gerber_dir) if os.path.isfile(os.path.join(gerber_dir, f))]
    
    if not files_to_include:
        print(json.dumps({"status": "ERROR", "message": "No se encontraron archivos Gerber para empaquetar."}))
        return False

    # Validar archivos mínimos para fabricación (Soporta nombres con '.' o '_')
    mandatory_patterns = [
        ["F_Cu", "F.Cu"], ["B_Cu", "B.Cu"],          # Cobre
        ["F_Mask", "F.Mask"], ["B_Mask", "B.Mask"],  # Máscara
        ["F_Silk", "F.SilkS"], ["B_Silk", "B.SilkS"], # Serigrafía
        ["Edge_Cuts", "Edge.Cuts"],                  # Contorno
        [".drl"]                                     # Perforaciones
    ]
    
    missing = []
    for variants in mandatory_patterns:
        if not any(any(v in f for v in variants) for f in files_to_include):
            missing.append(variants[0])

    result = {"status": "SUCCESS", "files_found": len(files_to_include)}

    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_include:
                file_path = os.path.join(gerber_dir, file)
                zipf.write(file_path, arcname=file)
        
        result["zip_file"] = output_zip
        if missing:
            result["status"] = "WARNING"
            result["msg"] = f"ZIP generado pero faltan capas críticas: {', '.join(missing)}"
        else:
            result["msg"] = "Paquete de fabricación generado con éxito (Set Completo)."
        
        print(json.dumps(result))
        return True
    except Exception as e:
        print(json.dumps({"status": "ERROR", "message": str(e)}))
        return False

if __name__ == "__main__":
    # Definición de rutas absolutas basadas en el contexto del proyecto
    BASE_DIR = "/home/cero/MEGA/VS_CODE_WORKSPACE/DATA_LOGER"
    GERBER_PATH = os.path.join(BASE_DIR, "hardware/gerbers")
    OUTPUT_FILE = os.path.join(BASE_DIR, "hardware/DATA_LOGER_fabrication.zip")

    success = package_gerbers(GERBER_PATH, OUTPUT_FILE)
    if success:
        sys.exit(0)
    sys.exit(1)