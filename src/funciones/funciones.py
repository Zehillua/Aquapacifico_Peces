import pulp
from colecciones.mongo_setup import db

def calcular_nutrientes(cantidad_peces, peso_promedio, porcentaje_racion_diaria, requerimientos):
    biomasa = cantidad_peces * peso_promedio
    alimento_diario = biomasa * (porcentaje_racion_diaria/100)

    proteinas_necesarias_min = requerimientos["proteina"]["min"] * alimento_diario
    proteinas_necesarias_max = requerimientos["proteina"]["max"] * alimento_diario
    lipidos_necesarios_min = requerimientos["lipidos"]["min"] * alimento_diario
    lipidos_necesarios_max = requerimientos["lipidos"]["max"] * alimento_diario
    carbohidratos_necesarios_min = requerimientos["carbohidratos"]["min"] * alimento_diario
    carbohidratos_necesarios_max = requerimientos["carbohidratos"]["max"] * alimento_diario

    porcentaje_total_nutrientes = (
        (proteinas_necesarias_min + proteinas_necesarias_max) / 2 +
        (lipidos_necesarios_min + lipidos_necesarios_max) / 2 +
        (carbohidratos_necesarios_min + carbohidratos_necesarios_max) / 2
    ) / alimento_diario

    resto = 100 - (porcentaje_total_nutrientes * 100)   
    vitaminas_minerales = resto / 2
    vitamina_c = vitaminas_minerales / 2
    vitamina_e = vitaminas_minerales / 2
    fosforo_calcio = vitaminas_minerales

    return {
        "biomasa": biomasa,
        "alimento_diario": alimento_diario,
        "proteinas_necesarias_min": proteinas_necesarias_min,
        "proteinas_necesarias_max": proteinas_necesarias_max,
        "lipidos_necesarios_min": lipidos_necesarios_min,
        "lipidos_necesarios_max": lipidos_necesarios_max,
        "carbohidratos_necesarios_min": carbohidratos_necesarios_min,
        "carbohidratos_necesarios_max": carbohidratos_necesarios_max,
        "vitamina_c": vitamina_c,
        "vitamina_e": vitamina_e,
        "fosforo_calcio": fosforo_calcio
    }

def resolver_problema_minimizacion(ingredientes, nutrientes):
    problema = pulp.LpProblem("Minimizar_Costo_Alimento", pulp.LpMinimize)
    
    # Definir variables con límites inferiores de 0 para evitar valores negativos
    variables = {ing.replace(" ", "_"): pulp.LpVariable(ing.replace(" ", "_"), lowBound=0) for ing in ingredientes}

    # Función objetivo: minimizar el costo total
    problema += pulp.lpSum([ingredientes[ing]["coste"] * variables[ing.replace(" ", "_")] for ing in ingredientes])

    # Restricciones nutricionales básicas
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["proteinas_necesarias_min"]
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["proteinas_necesarias_max"]
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["lipidos_necesarios_min"]
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["lipidos_necesarios_max"]
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["carbohidratos_necesarios_min"]
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["carbohidratos_necesarios_max"]

    # Rango tolerable de nutrientes (10% de margen)
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["proteinas_necesarias_max"] * 1.1
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["proteinas_necesarias_min"] * 0.9
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["lipidos_necesarios_max"] * 1.1
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["lipidos_necesarios_min"] * 0.9
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["carbohidratos_necesarios_max"] * 1.1
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["carbohidratos_necesarios_min"] * 0.9

    # Restricción de cantidad total de la mezcla (2% de margen)
    problema += pulp.lpSum([variables[ing.replace(" ", "_")] for ing in ingredientes]) >= nutrientes["alimento_diario"] * 0.99
    problema += pulp.lpSum([variables[ing.replace(" ", "_")] for ing in ingredientes]) <= nutrientes["alimento_diario"] * 1.01

    # Restricciones específicas de levadura (0.1% mínimo y 1% máximo del alimento diario)
    problema += variables["Levadura"] >= 0.001 * nutrientes["alimento_diario"]  # Mínimo 0.1%
    problema += variables["Levadura"] <= min(ingredientes["Levadura"]["stock"], 0.01 * nutrientes["alimento_diario"])  # Máximo 1% o stock disponible

    # Resolver el problema
    problema.solve()

    # Obtener resultados y valores intermedios
    resultados = {var.name: var.varValue for var in variables.values()}
    
    # Filtrar solo los ingredientes utilizados
    ingredientes_usados = []
    for ing, datos in ingredientes.items():
        cantidad_usada = resultados.get(ing.replace(" ", "_"), 0)
        if cantidad_usada > 0:
            stock_restante = max(0, datos["stock"] - cantidad_usada)
            ingrediente_info = {
                "nombre": ing,
                "cantidad_gramos": cantidad_usada,
                "stock_usado": cantidad_usada > datos["stock"],
                "stock_restante": stock_restante
            }
            if cantidad_usada > datos["stock"]:
                gramos_adicionales = cantidad_usada - datos["stock"]
                ingrediente_info["cantidad_adicional"] = gramos_adicionales
                ingrediente_info["mensaje_adicional"] = f'Se necesitan {gramos_adicionales:.4f} gramos adicionales de {ing} para cumplir con la cantidad necesaria.'
            ingredientes_usados.append(ingrediente_info)
            # Descontar del stock del ingrediente sin permitir valores negativos
            db.ingredientes.update_one(
                {"nombre": ing},
                {"$set": {"stock": stock_restante}}
            )

    # Calcular porcentaje de levadura utilizado
    levadura_usada = resultados.get("Levadura", 0)
    if levadura_usada > 0:
        porcentaje_levadura = (levadura_usada * 100) / ingredientes["Levadura"]["stock"]
    else:
        porcentaje_levadura = 0

    # Verificar deficiencias en nutrientes
    deficiencia_proteinas = max(0, nutrientes["proteinas_necesarias_min"] - sum(ingredientes[ing]["proteinas"] * resultados.get(ing.replace(" ", "_"), 0) for ing in ingredientes))
    deficiencia_lipidos = max(0, nutrientes["lipidos_necesarios_min"] - sum(ingredientes[ing]["lipidos"] * resultados.get(ing.replace(" ", "_"), 0) for ing in ingredientes))
    deficiencia_carbohidratos = max(0, nutrientes["carbohidratos_necesarios_min"] - sum(ingredientes[ing]["carbohidratos"] * resultados.get(ing.replace(" ", "_"), 0) for ing in ingredientes))

    return ingredientes_usados, resultados, porcentaje_levadura, deficiencia_proteinas, deficiencia_lipidos, deficiencia_carbohidratos



def calcular_nutrientes_generico(nombre_especie, cantidad_peces, peso_promedio, etapa, peso_objetivo, cantidad_levadura, cant_proteina, cant_lipidos, cant_carbohidratos, porcentaje_biomasa, dias):
    especie = db.peces.find_one({"nombre": nombre_especie, "etapa": etapa})

    if not especie:
        raise ValueError("Etapa no encontrada")

    requerimientos = especie["requerimientos"][peso_objetivo]

    biomasa = cantidad_peces * peso_promedio
    alimento_diario = (biomasa * (porcentaje_biomasa / 100) )* dias # Usar el porcentaje de biomasa para el cálculo

    proteinas_necesarias_min = round(requerimientos["proteina"]["min"] * alimento_diario, 2)
    proteinas_necesarias_max = round(requerimientos["proteina"]["max"] * alimento_diario, 2)
    lipidos_necesarios_min = round(requerimientos["lipidos"]["min"] * alimento_diario, 2)
    lipidos_necesarios_max = round(requerimientos["lipidos"]["max"] * alimento_diario, 2)
    carbohidratos_necesarios_min = round(requerimientos["carbohidratos"]["min"] * alimento_diario, 2)
    carbohidratos_necesarios_max = round(requerimientos["carbohidratos"]["max"] * alimento_diario, 2)
    
    db.ingredientes.update_one(
        {"nombre": "Levadura"},
        {"$set": {
            "proteinas": cant_proteina,
            "lipidos": cant_lipidos,
            "carbohidratos": cant_carbohidratos,
            "stock": cantidad_levadura
        }}
    )

    return {
        "biomasa": biomasa,
        "alimento_diario": alimento_diario,
        "proteinas_necesarias_min": proteinas_necesarias_min,
        "proteinas_necesarias_max": proteinas_necesarias_max,
        "lipidos_necesarios_min": lipidos_necesarios_min,
        "lipidos_necesarios_max": lipidos_necesarios_max,
        "carbohidratos_necesarios_min": carbohidratos_necesarios_min,
        "carbohidratos_necesarios_max": carbohidratos_necesarios_max
    }



def convert_and_process(data):
    """Procesa un diccionario recursivamente y convierte los valores a float si es posible."""
    for key, value in data.items():
        if isinstance(value, dict):  # Si el campo es un diccionario anidado
            convert_and_process(value)
        else:
            if isinstance(value, (int, float)):
                data[key] = float(value)  # Asegurar que los enteros también sean float
            elif isinstance(value, str) and value.replace('.', '', 1).isdigit():
                data[key] = float(value)  # Convertir strings numéricos en float

