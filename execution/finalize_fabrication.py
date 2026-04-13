import os
import json
import zipfile

def finalize():
    BASE = "/home/cero/MEGA/VS_CODE_WORKSPACE/DATA_LOGER"
    GERBER_DIR = os.path.join(BASE, "hardware/gerbers")
    OUTPUT_ZIP = os.path.join(BASE, "hardware/DATA_LOGER_fabrication.zip")
    
    # 1. Lista de archivos obsoletos a eliminar (basado en el reporte ls -l)
    obsolete = [
        "DATA_LOGER_IOT-Edge_Cuts.gm1",
        "DATA_LOGER_IOT-F_Cu.gtl",
        "DATA_LOGER_IOT-job.gbrjob"
    ]
    
    deleted_count = 0
    for f in obsolete:
        path = os.path.join(GERBER_DIR, f)
        if os.path.exists(path):
            os.remove(path)
            deleted_count += 1
            
    # 2. Empaquetar solo los archivos sincronizados (7 Gerbers + 1 Drill)
    valid_files = [f for f in os.listdir(GERBER_DIR) if f.endswith(('.gbr', '.drl'))]
    
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for f in valid_files:
            zipf.write(os.path.join(GERBER_DIR, f), arcname=f)
            
    result = {
        "status": "SUCCESS",
        "obsolete_removed": deleted_count,
        "files_in_zip": len(valid_files),
        "zip_path": OUTPUT_ZIP,
        "msg": "Proceso finalizado. El ZIP está listo para enviar al fabricante."
    }
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    finalize()