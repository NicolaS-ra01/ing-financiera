import math
from datetime import date, timedelta
from typing import List, Dict

# La precisión de cierre para evitar saldos residuales.
CERO_FINANCIERO = 0.000001
REDONDEO = 2
DIAS_PERIODO = 30 # Asumido para cálculo de fechas en la interfaz (aproximado)

def calcular_tasa_periodica(tasa_anual: float, frecuencia_pago: int, tipo_tasa: str) -> float:
    """Convierte la tasa anual (ya en factor decimal) a la Tasa Efectiva Periódica (vencida)."""
    
    if tipo_tasa.upper() == 'EFECTIVA':
        # Tasa Efectiva Anual (TEA) a Periódica
        i = (1 + tasa_anual) ** (1 / frecuencia_pago) - 1
    elif tipo_tasa.upper() == 'NOMINAL':
        # Tasa Nominal Anual (TNA)
        i = tasa_anual / frecuencia_pago
    elif tipo_tasa.upper() == 'ANTICIPADA':
        # Tasa Nominal Anticipada (TNAA) a Vencida Periódica
        tasa_anticipada_per = tasa_anual / frecuencia_pago
        if tasa_anticipada_per >= 1.0:
             raise ValueError("Tasa anticipada excesivamente alta (>100%). No es aplicable.")
        i = tasa_anticipada_per / (1 - tasa_anticipada_per)
    else:
        raise ValueError("Tipo de tasa no reconocido. Use: EFECTIVA, NOMINAL o ANTICIPADA.")
    
    return i

def calcular_cuota_constante(principal: float, tasa_per: float, n_periodos: int) -> float:
    """Calcula la cuota constante (PMT) usando la fórmula de anualidad vencida."""
    if tasa_per == 0:
        return round(principal / n_periodos, REDONDEO)
    
    factor = (1 + tasa_per) ** n_periodos
    cuota = principal * (tasa_per * factor) / (factor - 1)
    return round(cuota, REDONDEO)

def generar_tabla_base(principal: float, tasa_per: float, cuota: float, n_periodos: int, frecuencia_pago: int, fecha_inicio: date) -> List[Dict]:
    """Genera la tabla de amortización inicial."""
    tabla = []
    saldo = principal
    fecha_actual = fecha_inicio

    # Calcular el salto en días basado en la frecuencia anual (aproximado)
    salto_dias = round(365 / frecuencia_pago)

    for periodo in range(1, n_periodos + 1):
        interes = round(saldo * tasa_per, REDONDEO)
        
        # *** CORRECCIÓN CLAVE: Definir cuota_periodo antes de los condicionales ***
        cuota_periodo = cuota 

        if periodo == n_periodos:
            # Ajuste de la última cuota para evitar saldo residual (cierre exacto)
            amortizacion = saldo
            cuota_periodo = amortizacion + interes
            saldo_final = 0.0
        else:
            amortizacion = round(cuota - interes, REDONDEO)
            saldo_final = round(saldo - amortizacion, REDONDEO)

        # Si la amortización es mayor al saldo, ajustamos
        if saldo_final < 0 or saldo_final < CERO_FINANCIERO:
            amortizacion = saldo
            cuota_periodo = amortizacion + interes
            saldo_final = 0.0
            
        tabla.append({
            'periodo': periodo,
            'fecha': fecha_actual.strftime("%Y-%m-%d"),
            'saldo_inicial': round(saldo, REDONDEO),
            'interes': interes,
            'cuota_original': cuota,
            'cuota_pagada': round(cuota_periodo, REDONDEO), # Variable siempre definida
            'amortizacion': amortizacion,
            'abono_adhoc': 0.0,
            'saldo_final': saldo_final,
            'recalculado': False
        })
        saldo = saldo_final
        fecha_actual += timedelta(days=salto_dias)

    return tabla

def aplicar_abono_y_recalcular(tabla_original: List[Dict], periodo_abono: int, monto_abono: float, opcion_recalculo: str, tasa_per: float, plazo_original: int, frecuencia_pago: int) -> List[Dict]:
    """Aplica un abono ad-hoc y recalcula el resto de la tabla."""
    
    idx = periodo_abono - 1
    
    if idx >= len(tabla_original):
        raise IndexError("El período de abono está fuera del rango de la tabla.")

    # 1. Aplicar abono
    saldo_antes_abono = tabla_original[idx]['saldo_final']
    tabla_original[idx]['abono_adhoc'] = monto_abono
    saldo_recalculo = round(saldo_antes_abono - monto_abono, REDONDEO)
    tabla_original[idx]['saldo_final'] = saldo_recalculo
    
    # Si se salda el crédito, terminamos la tabla
    if saldo_recalculo <= CERO_FINANCIERO:
        for i in range(idx + 1, len(tabla_original)):
            tabla_original[i]['saldo_inicial'] = 0.0
            tabla_original[i]['interes'] = 0.0
            tabla_original[i]['cuota_pagada'] = 0.0
            tabla_original[i]['amortizacion'] = 0.0
            tabla_original[i]['saldo_final'] = 0.0
        return tabla_original
    
    # 2. Recalcular a partir del período siguiente
    periodo_inicio_recalculo = periodo_abono + 1
    
    # Ajuste de fechas para el re-cálculo
    salto_dias = round(365 / frecuencia_pago)
    fecha_actual = date.fromisoformat(tabla_original[idx]['fecha']) + timedelta(days=salto_dias)

    if opcion_recalculo.lower() == 'plazo':
        # Opción 1: Reducción de Plazo (mantener cuota original)
        cuota_original = tabla_original[idx]['cuota_original']
        saldo = saldo_recalculo
        tabla_nueva = tabla_original[:periodo_inicio_recalculo] # Mantiene hasta la fila del abono

        # Recorrer los períodos a partir del siguiente
        while saldo > CERO_FINANCIERO and periodo_inicio_recalculo <= plazo_original + 100:
            interes = round(saldo * tasa_per, REDONDEO)
            
            # Ajuste final: si el saldo restante es menor a la amortización
            if saldo + interes < cuota_original:
                cuota_pagada = round(saldo + interes, REDONDEO)
                amortizacion = saldo
                saldo_final = 0.0
            else:
                cuota_pagada = cuota_original
                amortizacion = round(cuota_pagada - interes, REDONDEO)
                saldo_final = round(saldo - amortizacion, REDONDEO)
            
            tabla_nueva.append({
                'periodo': periodo_inicio_recalculo,
                'fecha': fecha_actual.strftime("%Y-%m-%d"),
                'saldo_inicial': round(saldo, REDONDEO),
                'interes': interes,
                'cuota_original': tabla_original[idx]['cuota_original'],
                'cuota_pagada': cuota_pagada,
                'amortizacion': amortizacion,
                'abono_adhoc': 0.0,
                'saldo_final': saldo_final,
                'recalculado': True
            })
            saldo = saldo_final
            periodo_inicio_recalculo += 1
            fecha_actual += timedelta(days=salto_dias)
            
        return tabla_nueva

    elif opcion_recalculo.lower() == 'cuota':
        # Opción 2: Reducción de Cuota (mantener el plazo original)
        n_periodos_restantes = plazo_original - (periodo_abono) 
        
        # 2.1. Calcular la nueva cuota con el plazo restante
        nueva_cuota = calcular_cuota_constante(saldo_recalculo, tasa_per, n_periodos_restantes)
        
        # 2.2. Recalcular las filas restantes, sobrescribiendo las entradas anteriores
        saldo = saldo_recalculo
        
        tabla_nueva = tabla_original[:periodo_abono] # Mantiene hasta la fila del abono

        for i in range(periodo_abono, plazo_original):
            interes = round(saldo * tasa_per, REDONDEO)
            
            # Ajuste de la última cuota para evitar saldo residual
            if i == plazo_original - 1:
                amortizacion = saldo
                cuota_periodo = amortizacion + interes
                saldo_final = 0.0
            else:
                amortizacion = round(nueva_cuota - interes, REDONDEO)
                saldo_final = round(saldo - amortizacion, REDONDEO)
                cuota_periodo = nueva_cuota

            tabla_nueva.append({
                'periodo': i + 1,
                'fecha': fecha_actual.strftime("%Y-%m-%d"),
                'saldo_inicial': round(saldo, REDONDEO),
                'interes': interes,
                'cuota_original': tabla_original[idx]['cuota_original'],
                'cuota_pagada': round(cuota_periodo, REDONDEO),
                'amortizacion': amortizacion,
                'abono_adhoc': 0.0,
                'saldo_final': saldo_final,
                'recalculado': True
            })
            saldo = saldo_final
            fecha_actual += timedelta(days=salto_dias)
            
        return tabla_nueva
        
    else:
        raise ValueError("Opción de re-cálculo no válida. Use: PLAZO o CUOTA.")

def exportar_tabla_csv(tabla: List[Dict], nombre_archivo: str = "tabla_amortizacion.csv"):
    """Exporta la tabla a un archivo CSV."""
    import csv
    if not tabla:
        return
    
    keys = tabla[0].keys()
    with open(nombre_archivo, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(tabla)
    
    return f"Tabla exportada a {nombre_archivo}"