import os
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
import pulp
import ssl
import jwt
import random
import string
from colecciones.mongo_setup import db  # Asegúrate de que la ruta es correcta

api = Blueprint('api', __name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('PASSWORD')
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT'))
reset_codes = {}  # Almacenará temporalmente los códigos de restablecimiento

# Ruta para registrar un nuevo usuario
@api.route('/register', methods=['POST'])
def register_user():
    data = request.json
    # Verificar que todos los campos requeridos están presentes
    if not all(key in data for key in ('nombre', 'correo', 'cargo', 'password', 'confirmPassword')):
        return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400

    if data['password'] != data['confirmPassword']:
        return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400

    result = db.usuarios.insert_one({
        "nombre": data.get('nombre'),
        "correo": data.get('correo'),
        "cargo": data.get('cargo'),
        "password": data.get('password')
    })
    return jsonify({"success": True, "inserted_id": str(result.inserted_id)})

# Ruta para iniciar sesión
@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = db.usuarios.find_one({"correo": data['correo']})

        if user and user['password'] == data['password']:
            # Crear token JWT
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, SECRET_KEY, algorithm='HS256')
            
            return jsonify({"success": True, "token": token})
        else:
            return jsonify({"success": False, "message": "Correo o contraseña incorrectos"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Ruta protegida para obtener información del usuario
@api.route('/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"success": False, "message": "Token faltante"}), 403
    
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = db.usuarios.find_one({"_id": ObjectId(data['user_id'])})
        return jsonify({"success": True, "user": {"nombre": user['nombre'], "correo": user['correo'], "cargo": user['cargo']}})
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Token expirado"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Token inválido"}), 403

# Rutas de cargos
@api.route('/cargos', methods=['GET'])
def get_cargos():
    cargos = db.cargos.find()
    cargos_list = [{"id": str(cargo["_id"]), "nombre": cargo["nombre"]} for cargo in cargos]
    return jsonify(cargos_list)

@api.route('/cargos', methods=['POST'])
def add_cargo():
    data = request.json
    result = db.cargos.insert_one({"nombre": data["nombre"]})
    return jsonify({"inserted_id": str(result.inserted_id)})

def enviar_correo(correo, codigo):
    try:
        mensaje = EmailMessage()
        mensaje['From'] = smtp_user
        mensaje['To'] = correo
        mensaje['Subject'] = "Restablecer Contraseña"
        mensaje.set_content(f"Tu código de restablecimiento es: {codigo}")

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(mensaje)
        
        print("Correo enviado exitosamente")
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

@api.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('correo')
    confirm_email = data.get('confirmCorreo')
    
    if email != confirm_email:  
        return jsonify({"success": False, "message": "Los correos electrónicos no coinciden"}), 400

    user = db.usuarios.find_one({"correo": email})
    if user:
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        reset_codes[email] = codigo
        if enviar_correo(email, codigo):
            print("Correo enviado exitosamente")
            return jsonify({"success": True}), 200
        else:
            print("Error al enviar el correo")
            return jsonify({"success": False, "message": "Error al enviar el correo"}), 500
    else:
        print("Correo no encontrado")
        return jsonify({"success": False, "message": "Correo no encontrado"}), 404

@api.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    code = data.get('code')
    
    # Buscar el correo asociado al código dado
    email = next((k for k, v in reset_codes.items() if v == code), None)

    if email:
        del reset_codes[email]  # Eliminar el código verificado para seguridad
        return jsonify({"success": True, "email": email}), 200  # Devolver el correo verificado
    else:
        return jsonify({"success": False, "message": "Código incorrecto"}), 400

@api.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('correo')
    new_password = data.get('newPassword')
    user = db.usuarios.find_one({"correo": email})
    
    if user:
        db.usuarios.update_one({"correo": email}, {"$set": {"password": new_password}})
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Error al restablecer la contraseña"}), 400


@api.route('/congrio-etapas', methods=['GET'])
def get_congrio_etapas():
    etapas = db.peces.distinct("etapa", {"nombre": "Congrio"})
    return jsonify({"success": True, "etapas": etapas})

@api.route('/corvina-etapas', methods=['GET'])
def get_corvina_etapas():
    etapas = db.peces.distinct("etapa", {"nombre": "Corvina"})
    return jsonify({"success": True, "etapas": etapas})


@api.route('/cojinova-etapas', methods=['GET'])
def get_cojinova_etapas():
    etapas = db.peces.distinct("etapa", {"nombre": "Cojinova"})
    return jsonify({"success": True, "etapas": etapas})

@api.route('/palometa-etapas', methods=['GET'])
def get_palometa_etapas():
    etapas = db.peces.distinct("etapa", {"nombre": "Palometa"})
    return jsonify({"success": True, "etapas": etapas})

@api.route('/congrio-food', methods=['POST'])
def congrio_food():
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
    congrio = db.peces.find_one({"nombre": "Congrio", "etapa": etapa})

    if not congrio:
        return jsonify({"success": False, "message": "Etapa no encontrada"}), 404

    if peso_objetivo == "aumentar":
        proteina_necesaria = congrio["proteina"]["max"]
        lipido_necesario = congrio["lipidos"]["max"]
        carbohidrato_necesario = congrio["carbohidratos"]["max"]
    elif peso_objetivo == "mantener":
        proteina_necesaria = congrio["proteina"]["mantener"]
        lipido_necesario = congrio["lipidos"]["mantener"]
        carbohidrato_necesario = congrio["carbohidratos"]["mantener"]
    elif peso_objetivo == "disminuir":
        proteina_necesaria = congrio["proteina"]["min"]
        lipido_necesario = congrio["lipidos"]["min"]
        carbohidrato_necesario = congrio["carbohidratos"]["min"]
    else:
        return jsonify({"success": False, "message": "Peso objetivo inválido"}), 400

    # Calcular biomasa y alimento diario
    biomasa = cantidad_peces * peso_promedio
    alimento_diario = biomasa * 0.03

    # Calcular gramos necesarios de cada nutriente
    proteinas_necesarias = proteina_necesaria * alimento_diario
    lipidos_necesarios = lipido_necesario * alimento_diario
    carbohidratos_necesarios = carbohidrato_necesario * alimento_diario

    print("Biomasa: ", biomasa)
    print("Alimento Diario: ", alimento_diario)
    print("Proteinas Necesarias: ", proteinas_necesarias)
    print("Lipidos Necesarios: ", lipidos_necesarios)
    print("Carbohidratos Necesarios: ", carbohidratos_necesarios)

    # Obtener todos los ingredientes de la base de datos
    ingredientes = {ing["nombre"]: ing for ing in db.ingredientes.find()}

    # Crear el problema de minimización de costo
    problema = pulp.LpProblem("Minimizar_Costo_Alimento", pulp.LpMinimize)

    # Definir variables con límites inferiores de 0 para evitar valores negativos
    variables = {ing.replace(" ", "_"): pulp.LpVariable(ing.replace(" ", "_"), lowBound=0) for ing in ingredientes}

    # Función objetivo: minimizar el costo total
    problema += pulp.lpSum([ingredientes[ing]["coste"] * variables[ing.replace(" ", "_")] for ing in ingredientes])

    # Restricciones nutricionales básicas
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= proteinas_necesarias
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= lipidos_necesarios
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= carbohidratos_necesarios

    # Rango tolerable de nutrientes (10% de margen)
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= proteinas_necesarias * 1.1
    problema += pulp.lpSum([ingredientes[ing]["proteinas"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= proteinas_necesarias * 0.9
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= lipidos_necesarios * 1.1
    problema += pulp.lpSum([ingredientes[ing]["lipidos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= lipidos_necesarios * 0.9
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) <= carbohidratos_necesarios * 1.1
    problema += pulp.lpSum([ingredientes[ing]["carbohidratos"] * variables[ing.replace(" ", "_")] for ing in ingredientes]) >= carbohidratos_necesarios * 0.9

    # Restricción de cantidad total de la mezcla (2% de margen)
    problema += pulp.lpSum([variables[ing.replace(" ", "_")] for ing in ingredientes]) >= alimento_diario * 0.98
    problema += pulp.lpSum([variables[ing.replace(" ", "_")] for ing in ingredientes]) <= alimento_diario * 1.02

    # Restricciones específicas de levadura (0.1% mínimo y 1% máximo del alimento diario)
    problema += variables["Levadura"] >= 0.001 * alimento_diario  # Mínimo 0.1%
    problema += variables["Levadura"] <= min(ingredientes["Levadura"]["stock"], 0.01 * alimento_diario)  # Máximo 1% o stock disponible

    # Resolver el problema
    problema.solve()

    # Obtener resultados y valores intermedios
    resultados = {var.name: var.varValue for var in variables.values()}

    # Imprimir resultados intermedios
    for ing, cantidad in resultados.items():
        print(f"{ing}: {cantidad} gramos")

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


@api.route('/cojinova-food', methods=['POST'])
def cojinova_food():
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
    cojinova = db.peces.find_one({"nombre": "Cojinova", "etapa": etapa})

    if not cojinova:
        return jsonify({"success": False, "message": "Etapa no encontrada"}), 404

    if peso_objetivo == "aumentar":
        proteina_necesaria = cojinova["proteina"]["max"]
        lipido_necesario = cojinova["lipidos"]["max"]
        carbohidrato_necesario = cojinova["carbohidratos"]["max"]
    elif peso_objetivo == "mantener":
        proteina_necesaria = cojinova["proteina"]["mantener"]
        lipido_necesario = cojinova["lipidos"]["mantener"]
        carbohidrato_necesario = cojinova["carbohidratos"]["mantener"]
    elif peso_objetivo == "disminuir":
        proteina_necesaria = cojinova["proteina"]["min"]
        lipido_necesario = cojinova["lipidos"]["min"]
        carbohidrato_necesario = cojinova["carbohidratos"]["min"]
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

@api.route('/palometa-food', methods=['POST'])
def palometa_food():
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
    palometa = db.peces.find_one({"nombre": "Palometa", "etapa": etapa})

    if not palometa:
        return jsonify({"success": False, "message": "Etapa no encontrada"}), 404

    if peso_objetivo == "aumentar":
        proteina_necesaria = palometa["proteina"]["max"]
        lipido_necesario = palometa["lipidos"]["max"]
        carbohidrato_necesario = palometa["carbohidratos"]["max"]
    elif peso_objetivo == "mantener":
        proteina_necesaria = palometa["proteina"]["mantener"]
        lipido_necesario = palometa["lipidos"]["mantener"]
        carbohidrato_necesario = palometa["carbohidratos"]["mantener"]
    elif peso_objetivo == "disminuir":
        proteina_necesaria = palometa["proteina"]["min"]
        lipido_necesario = palometa["lipidos"]["min"]
        carbohidrato_necesario = palometa["carbohidratos"]["min"]
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

@api.route('/congrio-edit', methods=['GET', 'PUT'])
def get_congrio_data():
    try:
        if request.method == 'GET':
            # Filtrar los datos de los peces que son congrio
            congrio_data = list(db.peces.find({"nombre": "Congrio"}))
            # Convertir ObjectId a cadena de texto para la respuesta JSON
            for data in congrio_data:
                data['_id'] = str(data['_id'])
            return jsonify(congrio_data), 200
        elif request.method == 'PUT':
            data = request.json
            # Verificar que el ID está presente
            if '_id' not in data:
                return jsonify({"success": False, "message": "ID no proporcionado"}), 400

            # Extraer el ID
            id = data['_id']
            del data['_id']

            # Convertir los campos a float si es posible
            update_fields = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        try:
                            update_fields[f"{key}.{sub_key}"] = float(sub_value)
                        except ValueError:
                            update_fields[f"{key}.{sub_key}"] = sub_value
                else:
                    try:
                        update_fields[key] = float(value)
                    except ValueError:
                        update_fields[key] = value

            # Actualizar solo los campos específicos en la base de datos
            result = db.peces.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

            if result.matched_count == 0:
                return jsonify({"success": False, "message": "No se encontró el registro a actualizar"}), 404

            return jsonify({"success": True, "message": "Datos actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@api.route('/palometa-edit', methods=['GET', 'PUT'])
def get_palometa_data():
    try:
        if request.method == 'GET':
            # Filtrar los datos de los peces que son palometa
            palometa_data = list(db.peces.find({"nombre": "Palometa"}))
            # Convertir ObjectId a cadena de texto para la respuesta JSON
            for data in palometa_data:
                data['_id'] = str(data['_id'])
            return jsonify(palometa_data), 200
        elif request.method == 'PUT':
            data = request.json
            # Verificar que el ID está presente
            if '_id' not in data:
                return jsonify({"success": False, "message": "ID no proporcionado"}), 400

            # Extraer el ID
            id = data['_id']
            del data['_id']

            # Convertir los campos a float si es posible
            update_fields = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        try:
                            update_fields[f"{key}.{sub_key}"] = float(sub_value)
                        except ValueError:
                            update_fields[f"{key}.{sub_key}"] = sub_value
                else:
                    try:
                        update_fields[key] = float(value)
                    except ValueError:
                        update_fields[key] = value

            # Actualizar solo los campos específicos en la base de datos
            result = db.peces.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

            if result.matched_count == 0:
                return jsonify({"success": False, "message": "No se encontró el registro a actualizar"}), 404

            return jsonify({"success": True, "message": "Datos actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500    

@api.route('/cojinova-edit', methods=['GET', 'PUT'])
def get_cojinova_data():
    try:
        if request.method == 'GET':
            # Filtrar los datos de los peces que son cojinova
            cojinova_data = list(db.peces.find({"nombre": "Cojinova"}))
            # Convertir ObjectId a cadena de texto para la respuesta JSON
            for data in cojinova_data:
                data['_id'] = str(data['_id'])
            return jsonify(cojinova_data), 200
        elif request.method == 'PUT':
            data = request.json
            # Verificar que el ID está presente
            if '_id' not in data:
                return jsonify({"success": False, "message": "ID no proporcionado"}), 400

            # Extraer el ID
            id = data['_id']
            del data['_id']

            # Convertir los campos a float si es posible
            update_fields = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        try:
                            update_fields[f"{key}.{sub_key}"] = float(sub_value)
                        except ValueError:
                            update_fields[f"{key}.{sub_key}"] = sub_value
                else:
                    try:
                        update_fields[key] = float(value)
                    except ValueError:
                        update_fields[key] = value

            # Actualizar solo los campos específicos en la base de datos
            result = db.peces.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

            if result.matched_count == 0:
                return jsonify({"success": False, "message": "No se encontró el registro a actualizar"}), 404

            return jsonify({"success": True, "message": "Datos actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/corvina-edit', methods=['GET', 'PUT'])
def get_corvina_data():
    try:
        if request.method == 'GET':
            # Filtrar los datos de los peces que son corvina
            corvina_data = list(db.peces.find({"nombre": "Corvina"}))
            # Convertir ObjectId a cadena de texto para la respuesta JSON
            for data in corvina_data:
                data['_id'] = str(data['_id'])
            return jsonify(corvina_data), 200
        elif request.method == 'PUT':
            data = request.json
            # Verificar que el ID está presente
            if '_id' not in data:
                return jsonify({"success": False, "message": "ID no proporcionado"}), 400

            # Extraer el ID
            id = data['_id']
            del data['_id']

            # Convertir los campos a float si es posible
            update_fields = {}
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        try:
                            update_fields[f"{key}.{sub_key}"] = float(sub_value)
                        except ValueError:
                            update_fields[f"{key}.{sub_key}"] = sub_value
                else:
                    try:
                        update_fields[key] = float(value)
                    except ValueError:
                        update_fields[key] = value

            # Actualizar solo los campos específicos en la base de datos
            result = db.peces.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

            if result.matched_count == 0:
                return jsonify({"success": False, "message": "No se encontró el registro a actualizar"}), 404

            return jsonify({"success": True, "message": "Datos actualizados correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api.route('/ingredientes', methods=['GET'])
def get_ingredientes():
    try:
        ingredientes = list(db.ingredientes.find())
        for ingrediente in ingredientes:
            ingrediente['_id'] = str(ingrediente['_id'])
        return jsonify(ingredientes), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/ingredientes', methods=['POST'])
def add_ingrediente():
    data = request.json
    try:
        nuevo_ingrediente = {
            "nombre": data.get("nombre"),
            "coste": float(data.get("coste")),
            "proteinas": float(data.get("proteinas")),
            "lipidos": float(data.get("lipidos")),
            "carbohidratos": float(data.get("carbohidratos")),
            "stock": float(data.get("stock"))
        }
        db.ingredientes.insert_one(nuevo_ingrediente)
        return jsonify({"success": True, "message": "Ingrediente agregado correctamente"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/ingredientes/<id>', methods=['PUT'])
def update_ingrediente(id):
    data = request.json
    try:
        ingrediente_actualizado = {
            "nombre": data.get("nombre"),
            "coste": float(data.get("coste")),
            "proteinas": float(data.get("proteinas")),
            "lipidos": float(data.get("lipidos")),
            "carbohidratos": float(data.get("carbohidratos")),
            "stock": float(data.get("stock"))
        }
        db.ingredientes.update_one({"_id": ObjectId(id)}, {"$set": ingrediente_actualizado})
        return jsonify({"success": True, "message": "Ingrediente actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/ingredientes/<id>', methods=['DELETE'])
def delete_ingrediente(id):
    try:
        db.ingredientes.delete_one({"_id": ObjectId(id)})
        return jsonify({"success": True, "message": "Ingrediente eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
