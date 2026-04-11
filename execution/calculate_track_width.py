import sys
import json
import argparse

def calculate_pcb_width(current, temp_rise, thickness_oz, is_internal=False):
    """
    Calcula el ancho de pista basado en aproximaciones de la norma IPC-2152.
    
    Args:
        current (float): Corriente en Amperios.
        temp_rise (float): Aumento de temperatura permitido en °C.
        thickness_oz (float): Grosor del cobre en oz/ft^2 (típicamente 1.0).
        is_internal (bool): Si la pista es interna o externa.
    """
    # Conversión de oz/ft^2 a mils (1 oz = 1.37 mils)
    thickness_mils = thickness_oz * 1.37

    # Coeficientes para la fórmula Area = (I / (k * ΔT^b))^(1/c)
    # Nota: Estos son valores derivados para aproximar las curvas de IPC-2152/2221
    if is_internal:
        k, b, c = 0.024, 0.44, 0.725
    else:
        k, b, c = 0.048, 0.44, 0.725

    try:
        # Cálculo del área de la sección transversal en sq mils
        area = (current / (k * (temp_rise**b)))**(1/c)
        
        # Ancho = Area / Grosor
        width_mils = area / thickness_mils
        width_mm = width_mils * 0.0254

        return {
            "status": "SUCCESS",
            "parameters": {
                "current_amps": current,
                "temp_rise_c": temp_rise,
                "copper_thickness_oz": thickness_oz,
                "layer": "internal" if is_internal else "external"
            },
            "results": {
                "min_width_mm": round(width_mm, 4),
                "min_width_mils": round(width_mils, 2),
                "cross_section_sq_mils": round(area, 2)
            }
        }
    except ZeroDivisionError:
        return {"status": "ERROR", "message": "El aumento de temperatura no puede ser cero."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculador de ancho de pistas PCB (IPC-2152)")
    parser.add_argument("--current", type=float, required=True, help="Corriente en Amperios")
    parser.add_argument("--temp_rise", type=float, default=10.0, help="ΔT permitido (default: 10°C)")
    parser.add_argument("--thickness", type=float, default=1.0, help="Grosor cobre en oz/ft^2 (default: 1.0)")
    parser.add_argument("--internal", action="store_true", help="Usar coeficientes para capas internas")

    args = parser.parse_args()

    result = calculate_pcb_width(
        args.current, 
        args.temp_rise, 
        args.thickness, 
        args.internal
    )

    print(json.dumps(result, indent=4))
    
    if result["status"] == "SUCCESS":
        # Validación técnica: Si la corriente es alta y el ancho es pequeño, advertir
        if args.current > 2.0 and result["results"]["min_width_mm"] < 0.5:
             sys.stderr.write("ADVERTENCIA: Corriente alta detectada. Considere aumentar el ancho manualmente por seguridad.\n")
        sys.exit(0)
    else:
        sys.exit(1)