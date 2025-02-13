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
from funciones.funciones import calcular_nutrientes, resolver_problema_minimizacion, calcular_nutrientes_generico, convert_and_process

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
    nombre_especie = data.get('nombre_especie')
    etapa = data.get('etapa')
    cantidad_peces = int(data.get('cantidad_peces'))
    peso_promedio = float(data.get('peso_promedio'))
    peso_objetivo = data.get('peso_objetivo')
    cantidad_levadura = float(data.get('levadura_gramos'))
    cant_proteina = float(data.get('proteina_actual'))
    cant_lipidos = float(data.get('lipido_actual'))
    cant_carbohidratos = float(data.get('carbohidrato_actual'))
    porcentaje_biomasa = float(data.get('porcentaje_biomasa'))  # Nuevo campo
    days = int(data.get('dias'))

    # Calcular los nutrientes necesarios para la especie
    try:
        nutrientes = calcular_nutrientes_generico(nombre_especie, cantidad_peces, peso_promedio, etapa, peso_objetivo, cantidad_levadura, cant_proteina, cant_lipidos, cant_carbohidratos, porcentaje_biomasa,days)
        print(nutrientes)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    # Obtener todos los ingredientes de la base de datos
    ingredientes = {ing["nombre"]: ing for ing in db.ingredientes.find()}

    # Resolver el problema de minimización de costos
    ingredientes_usados, resultados, porcentaje_levadura, deficiencia_proteinas, deficiencia_lipidos, deficiencia_carbohidratos = resolver_problema_minimizacion(ingredientes, nutrientes)

    # Preparar la respuesta
    respuesta = {
        "success": True,
        "ingredientes_usados": ingredientes_usados,
        "resultados": resultados,
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
    nombre_especie = data.get('nombre_especie')
    etapa = data.get('etapa')
    cantidad_peces = int(data.get('cantidad_peces'))
    peso_promedio = float(data.get('peso_promedio'))
    peso_objetivo = data.get('peso_objetivo')
    cantidad_levadura = float(data.get('levadura_gramos'))
    cant_proteina = float(data.get('proteina_actual'))
    cant_lipidos = float(data.get('lipido_actual'))
    cant_carbohidratos = float(data.get('carbohidrato_actual'))
    porcentaje_biomasa = float(data.get('porcentaje_biomasa'))  # Nuevo campo
    days = int(data.get('dias'))

    # Calcular los nutrientes necesarios para la especie
    try:
        nutrientes = calcular_nutrientes_generico(nombre_especie, cantidad_peces, peso_promedio, etapa, peso_objetivo, cantidad_levadura, cant_proteina, cant_lipidos, cant_carbohidratos, porcentaje_biomasa,days)
        print(nutrientes)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    # Obtener todos los ingredientes de la base de datos
    ingredientes = {ing["nombre"]: ing for ing in db.ingredientes.find()}

    # Resolver el problema de minimización de costos
    ingredientes_usados, resultados, porcentaje_levadura, deficiencia_proteinas, deficiencia_lipidos, deficiencia_carbohidratos = resolver_problema_minimizacion(ingredientes, nutrientes)

    # Preparar la respuesta
    respuesta = {
        "success": True,
        "ingredientes_usados": ingredientes_usados,
        "resultados": resultados,
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
    nombre_especie = data.get('nombre_especie')
    etapa = data.get('etapa')
    cantidad_peces = int(data.get('cantidad_peces'))
    peso_promedio = float(data.get('peso_promedio'))
    peso_objetivo = data.get('peso_objetivo')
    cantidad_levadura = float(data.get('levadura_gramos'))
    cant_proteina = float(data.get('proteina_actual'))
    cant_lipidos = float(data.get('lipido_actual'))
    cant_carbohidratos = float(data.get('carbohidrato_actual'))
    porcentaje_biomasa = float(data.get('porcentaje_biomasa'))  # Nuevo campo
    days = int(data.get('dias'))

    # Calcular los nutrientes necesarios para la especie
    try:
        nutrientes = calcular_nutrientes_generico(nombre_especie, cantidad_peces, peso_promedio, etapa, peso_objetivo, cantidad_levadura, cant_proteina, cant_lipidos, cant_carbohidratos, porcentaje_biomasa,days)
        print(nutrientes)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    # Obtener todos los ingredientes de la base de datos
    ingredientes = {ing["nombre"]: ing for ing in db.ingredientes.find()}

    # Resolver el problema de minimización de costos
    ingredientes_usados, resultados, porcentaje_levadura, deficiencia_proteinas, deficiencia_lipidos, deficiencia_carbohidratos = resolver_problema_minimizacion(ingredientes, nutrientes)

    # Preparar la respuesta
    respuesta = {
        "success": True,
        "ingredientes_usados": ingredientes_usados,
        "resultados": resultados,
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
    nombre_especie = data.get('nombre_especie')
    etapa = data.get('etapa')
    cantidad_peces = int(data.get('cantidad_peces'))
    peso_promedio = float(data.get('peso_promedio'))
    peso_objetivo = data.get('peso_objetivo')
    cantidad_levadura = float(data.get('levadura_gramos'))
    cant_proteina = float(data.get('proteina_actual'))
    cant_lipidos = float(data.get('lipido_actual'))
    cant_carbohidratos = float(data.get('carbohidrato_actual'))
    porcentaje_biomasa = float(data.get('porcentaje_biomasa'))  # Nuevo campo
    days = int(data.get('dias'))

    # Calcular los nutrientes necesarios para la especie
    try:
        nutrientes = calcular_nutrientes_generico(nombre_especie, cantidad_peces, peso_promedio, etapa, peso_objetivo, cantidad_levadura, cant_proteina, cant_lipidos, cant_carbohidratos, porcentaje_biomasa,days)
        print(nutrientes)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    # Obtener todos los ingredientes de la base de datos
    ingredientes = {ing["nombre"]: ing for ing in db.ingredientes.find()}

    # Resolver el problema de minimización de costos
    ingredientes_usados, resultados, porcentaje_levadura, deficiencia_proteinas, deficiencia_lipidos, deficiencia_carbohidratos = resolver_problema_minimizacion(ingredientes, nutrientes)

    # Preparar la respuesta
    respuesta = {
        "success": True,
        "ingredientes_usados": ingredientes_usados,
        "resultados": resultados,
        "porcentaje_levadura": porcentaje_levadura,
        "deficiencia_proteinas": deficiencia_proteinas,
        "deficiencia_lipidos": deficiencia_lipidos,
        "deficiencia_carbohidratos": deficiencia_carbohidratos,
        "mensaje": "Cálculo completado"
    }

    return jsonify(respuesta), 200


@api.route('/congrio-edit', methods=['GET'])
def get_congrio_data():
    try:
        congrio_data = list(db.peces.find({"nombre": "Congrio"}))
        for data in congrio_data:
            data['_id'] = str(data['_id'])
        return jsonify(congrio_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/pez/<id>', methods=['GET', 'PUT'])
def edit_pez(id):
    try:
        if request.method == 'GET':
            pez = db.peces.find_one({"_id": ObjectId(id)})
            if not pez:
                return jsonify({"success": False, "message": "No se encontró el pez"}), 404
            pez['_id'] = str(pez['_id'])  # Convertir _id a string para evitar errores en JSON
            return jsonify(pez), 200

        elif request.method == 'PUT':
            data = request.json
            data.pop('_id', None)  # Evitar modificar el _id

            convert_and_process(data)  # Procesa el diccionario completo

            result = db.peces.update_one({"_id": ObjectId(id)}, {"$set": data})

            if result.matched_count == 0:
                return jsonify({"success": False, "message": "No se encontró el pez a actualizar"}), 404
            print(db.peces.find_one({"_id": ObjectId(id)}))

            return jsonify({"success": True, "message": "Datos actualizados correctamente"}), 200

    except Exception as e:
        print(f"⚠️ Error en PUT /pez/{id}: {e}")  # Mostrar error en la terminal
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/cojinova-edit', methods=['GET', 'PUT'])
def get_cojinova_data():
    try:
        cojinova_data = list(db.peces.find({"nombre": "Cojinova"}))
        for data in cojinova_data:
            data['_id'] = str(data['_id'])
        return jsonify(cojinova_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@api.route('/corvina-edit', methods=['GET', 'PUT'])
def get_corvina_data():
    try:
        corvina_data = list(db.peces.find({"nombre": "Corvina"}))
        for data in corvina_data:
            data['_id'] = str(data['_id'])
        return jsonify(corvina_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/palometa-edit', methods=['GET', 'PUT'])
def get_palometa_data():
    try:
        palometa_data = list(db.peces.find({"nombre": "Palometa"}))
        for data in palometa_data:
            data['_id'] = str(data['_id'])
        return jsonify(palometa_data), 200
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
