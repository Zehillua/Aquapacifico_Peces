@api.route('/corvina-food', methods=['POST'])
def corvina_food():
    data = request.json

    # Obtener datos del formulario
    etapa = data.get('etapa')
    cantidad_peces = int(data.get('cantidad_peces'))
    peso_promedio = float(data.get('peso_promedio'))
    peso_objetivo = data.get('peso_objetivo')
    levadura_gramos = float(data.get('levadura_gramos'))
    proteina_actual = float(data.get('proteina_actual'))
    lipido_actual = float(data.get('lipido_actual'))
    carbohidrato_actual = float(data.get('carbohidrato_actual'))

    # Obtener los valores de proteína, lípidos y carbohidratos para la etapa
    corvina = db.peces.find_one({"nombre": "Corvina", "etapa": etapa})

    if not corvina:
        return jsonify({"success": False, "message": "Etapa no encontrada"}), 404

    if peso_objetivo == "aumentar":
        proteina_necesaria = corvina["proteina"]["max"]
        lipido_necesario = corvina["lipidos"]["max"]
        carbohidrato_necesario = corvina["carbohidratos"]["max"]
    elif peso_objetivo == "mantener":
        proteina_necesaria = corvina["proteina"]["mantener"]
        lipido_necesario = corvina["lipidos"]["mantener"]
        carbohidrato_necesario = corvina["carbohidratos"]["mantener"]
    elif peso_objetivo == "disminuir":
        proteina_necesaria = corvina["proteina"]["min"]
        lipido_necesario = corvina["lipidos"]["min"]
        carbohidrato_necesario = corvina["carbohidratos"]["min"]
    else:
        return jsonify({"success": False, "message": "Peso objetivo inválido"}), 400

    # Calcular biomasa y alimento diario
    biomasa = cantidad_peces * peso_promedio
    alimento_diario = biomasa * 0.03

    # Calcular gramos necesarios de cada nutriente
    proteinas_necesarias = proteina_necesaria * alimento_diario
    lipidos_necesarios = lipido_necesario * alimento_diario
    carbohidratos_necesarios = carbohidrato_necesario * alimento_diario
    print("Proteinas: ", proteinas_necesarias)
    print("Lipidos: ", lipidos_necesarios)
    print("Carbo: ", carbohidratos_necesarios)
    # Actualizar los valores de la levadura en la base de datos
    db.ingredientes.update_one(
        {"nombre": "Levadura"},
        {"$set": {
            "proteinas": proteina_actual,
            "lipidos": lipido_actual,
            "carbohidratos": carbohidrato_actual,
            "stock": levadura_gramos
        }}
    )

    # Obtener todos los ingredientes de la base de datos
    ingredientes = {ing["nombre"]: ing for ing in db.ingredientes.find()}

    # Crear el problema de minimización de costo
    problema = pulp.LpProblem("Minimizar_Costo_Alimento", pulp.LpMinimize)

    # Definir variables
    variables = {ing.replace(" ", "_"): pulp.LpVariable(ing.replace(" ", "_"), lowBound=0, upBound=ingredientes[ing]["stock"]) for ing in ingredientes}

    # Función objetivo
    problema += pulp.lpSum([ingredientes[ing]["coste"] * variables[ing.replace(" ", "_")] for ing in ingredientes])

    # Restricciones nutricionales básicas
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= proteinas_necesarias
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= lipidos_necesarios
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= carbohidratos_necesarios

    # Rango tolerable de nutrientes
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= proteinas_necesarias * 1.1
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= proteinas_necesarias * 0.9
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= lipidos_necesarios * 1.1
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= lipidos_necesarios * 0.9
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= carbohidratos_necesarios * 1.1
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= carbohidratos_necesarios * 0.9

    # Restricción de cantidad total de la mezcla (variabilidad)
    problema += pulp.lpSum([variables[ing.replace(" ", "_")] for ing in ingredientes]) >= alimento_diario * 0.98
    problema += pulp.lpSum([variables[ing.replace(" ", "_")] for ing in ingredientes]) <= alimento_diario * 1.02

    # Restricciones específicas de levadura (volumen) y stock ajustadas
    problema += variables["Levadura"] >= 0.001 * alimento_diario  # Min 0.1%
    problema += variables["Levadura"] <= min(ingredientes["Levadura"]["stock"], 0.01 * alimento_diario)  # Máx 1% y stock disponible

    # Resolver el problema
    problema.solve()

    # Obtener resultados y valores intermedios
    resultados = {var.name: var.varValue for var in variables.values()}
    # Filtrar solo los ingredientes utilizados
    ingredientes_usados = []
    for ing, datos in ingredientes.items():
        cantidad_usada = resultados.get(ing.replace(" ", "_"), 0)
        if cantidad_usada > 0:
            ingrediente_info = {
                "nombre": ing,
                "cantidad_gramos": cantidad_usada,
                "stock_usado": cantidad_usada > datos["stock"],
                "stock_restante": max(0, datos["stock"] - cantidad_usada)
            }
            if cantidad_usada > datos["stock"]:
                gramos_adicionales = cantidad_usada - datos["stock"]
                ingrediente_info["cantidad_adicional"] = gramos_adicionales
                ingrediente_info["mensaje_adicional"] = f'Se necesitan {gramos_adicionales:.4f} gramos adicionales de {ing} para cumplir con la cantidad necesaria.'
            ingredientes_usados.append(ingrediente_info)
            # Descontar del stock del ingrediente
            db.ingredientes.update_one(
                {"nombre": ing},
                {"$inc": {"stock": -cantidad_usada}}
            )

    # Calcular porcentaje de levadura utilizado
    levadura_usada = resultados.get("Levadura", 0)
    if levadura_usada > 0:
        porcentaje_levadura = (levadura_usada * 100) / ingredientes["Levadura"]["stock"]
    else:
        porcentaje_levadura = 0

    # Verificar deficiencias en nutrientes
    deficiencia_proteinas = max(0, proteinas_necesarias - sum(ingredientes[ing]["proteinas"] * resultados.get(ing.replace(" ", "_"), 0) for ing in ingredientes))
    deficiencia_lipidos = max(0, lipidos_necesarios - sum(ingredientes[ing]["lipidos"] * resultados.get(ing.replace(" ", "_"), 0) for ing in ingredientes))
    deficiencia_carbohidratos = max(0, carbohidratos_necesarios - sum(ingredientes[ing]["carbohidratos"] * resultados.get(ing.replace(" ", "_"), 0) for ing in ingredientes))

    # Preparar respuesta
    respuesta = {
        "success": True,
        "ingredientes_usados": ingredientes_usados,
        "proteina_necesaria_total": proteinas_necesarias,
        "lipido_necesario_total": lipidos_necesarios,
        "carbohidrato_necesario_total": carbohidratos_necesarios,
        "porcentaje_levadura": porcentaje_levadura,
        "deficiencia_proteinas": deficiencia_proteinas,
        "deficiencia_lipidos": deficiencia_lipidos,
        "deficiencia_carbohidratos": deficiencia_carbohidratos,
        "mensaje": "Cálculo completado"
    }

    return jsonify(respuesta), 200