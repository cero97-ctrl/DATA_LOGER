import sys
import json

def validate_tps5430(v_out_target, r_up, r_down):
    # Vref constante para el TPS5430 es 1.221V
    V_REF = 1.221
    v_calc = V_REF * (1 + r_up / r_down)
    
    error = abs(v_calc - v_out_target) / v_out_target
    
    return {
        "calculated_vout": round(v_calc, 3),
        "error_percentage": round(error * 100, 2),
        "status": "PASS" if error < 0.05 else "FAIL"
    }

if __name__ == "__main__":
    # Valores propuestos: R_up=31.6k, R_down=10k para 5V
    try:
        target = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
        r1 = float(sys.argv[2]) if len(sys.argv) > 2 else 31600
        r2 = float(sys.argv[3]) if len(sys.argv) > 3 else 10000
        
        result = validate_tps5430(target, r1, r2)
        print(json.dumps(result))
        
        if result["status"] == "FAIL":
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)