import sys
import os

# Capa de Resiliencia: Inyección de Rutas de KiCad 8.0
# El entorno Conda suele estar aislado de los dist-packages del sistema.
def _setup_kicad_env():
    # Rutas comunes en Linux (Ubuntu/PPA) donde reside la API de KiCad
    # En Noble (24.04), Python 3.12 es el estándar.
    v = sys.version_info
    system_paths = [
        f"/usr/lib/python{v.major}.{v.minor}/dist-packages",
        "/usr/lib/python3/dist-packages",
        "/usr/local/lib/python3/dist-packages",
        "/usr/lib/python3/site-packages",
        "/usr/lib/python3/dist-packages/kicad",
        "/usr/lib/kicad/plugins",
        "/usr/lib/x86_64-linux-gnu/kicad/plugins", # Ruta común en instalaciones limpias
        # Búsqueda específica para KiCad 8 en Noble
        "/usr/share/kicad/plugins/"
    ]
    for path in system_paths:
        if os.path.exists(path) and path not in sys.path:
            # Insertar al inicio (index 0) para tener prioridad sobre Conda
            sys.path.insert(0, path)

try:
    _setup_kicad_env()
    import pcbnew
except ImportError as e:
    print(f"CRITICAL: No se pudo encontrar la API 'pcbnew' de KiCad. Error: {e}")
    print(f"DEBUG_ENV: Python {sys.version.split()[0]} en {sys.executable}")
    print(f"DEBUG_SYS_PATH: {sys.path[:3]}... (solo primeros 3)")
    print("-" * 50)
    print("ERROR DE LOCALIZACIÓN: Si ya instalaste KiCad, intenta crear un enlace simbólico:")
    print(f"ln -s /usr/lib/python3/dist-packages/pcbnew.py {os.path.dirname(sys.executable)}/../lib/python3.12/site-packages/")
    print(f"ln -s /usr/lib/python3/dist-packages/_pcbnew.so {os.path.dirname(sys.executable)}/../lib/python3.12/site-packages/")
    sys.exit(1)

import numpy as np
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

"""
Script de Automatización KiCad 8.0 - ADN Agente-IA
Este script implementa la lógica de manipulación de PCB usando la API VECTOR2I.
"""

def initialize_board(output_path):
    # En KiCad 8, la creación de una placa vacía es estándar
    board = pcbnew.NewBoard(output_path)
    return board

def add_track_segment(board, start_vec, end_vec, layer=pcbnew.F_Cu, width_nm=250000):
    """
    Agrega un segmento físico a la placa.
    """
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start_vec)
    track.SetEnd(end_vec)
    track.SetWidth(width_nm)
    track.SetLayer(layer)
    board.Add(track)

def route_a_star(board, start_mm, end_mm, grid_res_mm=0.5):
    """
    Implementación de ruteo A* sobre una rejilla lógica.
    """
    scale = 1000000 # mm to nm
    # Definir área de trabajo (ej. 100x100mm para DATA_LOGER)
    width, height = 100, 100
    grid_size_x = int(width / grid_res_mm)
    grid_size_y = int(height / grid_res_mm)
    
    # 1 = transitable, 0 = obstáculo
    matrix = np.ones((grid_size_y, grid_size_x))
    
    # Mapear obstáculos existentes (Pads y Tracks)
    for pad in board.GetPads():
        pos = pad.GetPosition()
        gx = int((pos.x / scale) / grid_res_mm)
        gy = int((pos.y / scale) / grid_res_mm)
        if 0 <= gx < grid_size_x and 0 <= gy < grid_size_y:
            matrix[gy][gx] = 0

    grid = Grid(matrix=matrix.tolist())
    
    start_node = grid.node(int(start_mm[0]/grid_res_mm), int(start_mm[1]/grid_res_mm))
    end_node = grid.node(int(end_mm[0]/grid_res_mm), int(end_mm[1]/grid_res_mm))
    
    finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
    path, runs = finder.find_path(start_node, end_node, grid)
    
    if path:
        print(f"Ruta encontrada en {runs} iteraciones. Trazando segmentos...")
        for i in range(len(path) - 1):
            p1 = path[i]
            p2 = path[i+1]
            
            v1 = pcbnew.VECTOR2I(int(p1.x * grid_res_mm * scale), int(p1.y * grid_res_mm * scale))
            v2 = pcbnew.VECTOR2I(int(p2.x * grid_res_mm * scale), int(p2.y * grid_res_mm * scale))
            
            add_track_segment(board, v1, v2)
        return True
    else:
        print("Error: No se encontró camino posible.")
        return False

def export_board(board, path):
    board.Save(path)
    print(f"Placa guardada en: {path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 kicad_pcb_automation.py <output_file.kicad_pcb>")
        sys.exit(1)
        
    output_file = sys.argv[1]
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Cargar placa existente o crear nueva
        if os.path.exists(output_file):
            pcb = pcbnew.LoadBoard(output_file)
            print(f"Cargada placa existente: {output_file}")
        else:
            pcb = initialize_board(output_file)
            print("Iniciada nueva placa.")

        # Ejemplo de ruteo: Conectar punto A (10,10) a B (40,40)
        # En un flujo real, estos puntos vendrían de las coordenadas de los pads de la Netlist
        success = route_a_star(pcb, (10, 10), (40, 40))
        
        export_board(pcb, output_file)
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Error de ejecución: {str(e)}")
        sys.exit(1)