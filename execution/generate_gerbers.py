import os
import subprocess
import json
import sys

def export_gerbers(pcb_path, output_dir):
    # Definimos las 7 capas estándar
    layers = "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        cmd = [
            "kicad-cli", "pcb", "export", "gerbers",
            "--output", output_dir,
            "--layers", layers,
            pcb_path
        ]
        subprocess.run(cmd, check=True)

        # Exportar taladros (Drill) sincronizados
        drill_cmd = [
            "kicad-cli", "pcb", "export", "drill",
            "--output", output_dir,
            pcb_path
        ]
        subprocess.run(drill_cmd, check=True)
        
        files = [f for f in os.listdir(output_dir) if f.endswith(('.gbr', '.drl'))]
        print(json.dumps({
            "status": "SUCCESS",
            "files_count": len(files),
            "msg": f"Se generaron {len(files)} archivos en {output_dir}"
        }))
        return True
    except Exception as e:
        print(json.dumps({"status": "ERROR", "message": str(e)}))
        return False

if __name__ == "__main__":
    BASE = "/home/cero/MEGA/VS_CODE_WORKSPACE/DATA_LOGER"
    export_gerbers(os.path.join(BASE, "hardware/DATA_LOGER_IOT.kicad_pcb"), os.path.join(BASE, "hardware/gerbers/"))