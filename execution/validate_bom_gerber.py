import os
import csv
import re
import json

def validate_integrity():
    BASE = "/home/cero/MEGA/VS_CODE_WORKSPACE/DATA_LOGER"
    BOM_PATH = os.path.join(BASE, "hardware/DATA_LOGER_BOM.csv")
    GERBER_DIR = os.path.join(BASE, "hardware/gerbers")
    
    if not os.path.exists(BOM_PATH) or not os.path.exists(GERBER_DIR):
        print(json.dumps({"status": "ERROR", "message": "Faltan archivos base para la validación."}))
        return

    # 1. Extraer todas las referencias del BOM
    bom_refs = set()
    with open(BOM_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            refs = [r.strip() for re_match in re.finditer(r'[\w\d]+', row['Reference(s)']) for r in [re_match.group()]]
            bom_refs.update(refs)

    # 2. Escanear Gerbers buscando metadatos de componentes (Atributos KiCad 8)
    found_in_gerbers = set()
    gerber_files = [f for f in os.listdir(GERBER_DIR) if f.endswith('.gbr')]
    
    for g_file in gerber_files:
        path = os.path.join(GERBER_DIR, g_file)
        with open(path, 'r', errors='ignore') as f:
            content = f.read()
            # KiCad 8 inserta atributos de componente como %TF.C,Ref,U1*%
            for ref in bom_refs:
                if f"Ref,{ref}" in content:
                    found_in_gerbers.add(ref)

    # 3. Comparar
    missing = bom_refs - found_in_gerbers
    
    result = {
        "status": "SUCCESS" if not missing else "WARNING",
        "total_bom_components": len(bom_refs),
        "verified_in_gerbers": len(found_in_gerbers),
        "missing_references": list(missing),
        "summary": "Integridad verificada: Todos los componentes del BOM existen en los Gerbers." if not missing 
                   else f"Discrepancia detectada: {len(missing)} componentes del BOM no se encontraron en los metadatos Gerber."
    }
    
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    validate_integrity()