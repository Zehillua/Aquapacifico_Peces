import os
from flask import Blueprint, jsonify, request
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
from email.message import EmailMessage
from functools import wraps
import smtplib
import pulp
from werkzeug.security import generate_password_hash, check_password_hash
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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"success": False, "message": "Token faltante"}), 403
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = db.usuarios.find_one({"_id": ObjectId(data['user_id'])})
            if not current_user:
                return jsonify({"success": False, "message": "Usuario no encontrado"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expirado"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Token inválido"}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def check_edicion_peces(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if not current_user.get('ed_peces'):
            return jsonify({"success": False, "message": "Permiso denegado, no tienes permisos para editar peces"}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

def check_admin(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if not current_user.get('is_admin'):
            return jsonify({"success": False, "message": "Permiso denegado, solo para administradores"}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function


def check_edicion_ingredientes(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if not current_user.get('ed_ingred'):
            return jsonify({"success": False, "message": "Permiso denegado, no tienes permisos para editar ingredientes"}), 403
        return f(current_user, *args, **kwargs)
    return decorated_function

def enviar_correo_veryfy(correo, codigo):
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
    
def enviar_correo_edicion(usuario, pez, etapa, nutriente, peso, cambio_anterior, cambio_nuevo):
    try:
        mensaje = EmailMessage()
        mensaje['From'] = smtp_user
        mensaje['To'] = "ignaciovicente04@gmail.com"
        mensaje['Subject'] = "Actualización de Información de Peces"
        mensaje.set_content(
            f"El usuario {usuario} ha realizado una actualización en el pez {pez}.\n\n"
            f"Etapa: {etapa}\n"
            f"Nutriente: {nutriente}\n"
            f"Peso: {peso}\n"
            f"Se ha cambiado de {cambio_anterior} a {cambio_nuevo}"
        )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(mensaje)
        
        print("Correo enviado exitosamente")
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return 
    

def enviar_correo_ingrediente(accion, usuario, nombre_ingrediente, cambios=None, coste=None, stock=None):
    try:
        mensaje = EmailMessage()
        mensaje['From'] = smtp_user
        mensaje['To'] = "ignaciovicente04@gmail.com"

        if accion == 'eliminar':
            mensaje['Subject'] = "Eliminación de Ingrediente"
            mensaje.set_content(
                f"El usuario {usuario} ha eliminado el ingrediente {nombre_ingrediente}."
            )
        elif accion == 'agregar':
            mensaje['Subject'] = "Agregación de Ingrediente"
            mensaje.set_content(
                f"El usuario {usuario} ha agregado un nuevo ingrediente.\n\n"
                f"Nombre: {nombre_ingrediente}\n"
                f"Coste: {coste}\n"
                f"Stock: {stock}"
            )
        elif accion == 'editar' and cambios:
            mensaje['Subject'] = "Edición de Ingrediente"
            cambios_str = "\n".join([f"{campo}: de {anterior} a {nuevo}" for campo, (anterior, nuevo) in cambios.items()])
            mensaje.set_content(
                f"El usuario {usuario} ha editado el ingrediente {nombre_ingrediente}.\n\n"
                f"Cambios realizados:\n{cambios_str}"
            )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(mensaje)
        
        print("Correo enviado exitosamente")
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False


# Ruta para registrar un nuevo usuario
@api.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not all(key in data for key in ('nombre', 'correo', 'cargo', 'password', 'confirmPassword')):
        return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400

    if data['password'] != data['confirmPassword']:
        return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    # Verificar si el correo es el del administrador
    is_admin = data['correo'] in ['katherine.alveal@aquapacifico.cl', 'miguelpradenas@hotmail.com']  # Cambia esto al correo del administrador real
    
    # Establecer permisos de edición en True si es administrador
    ed_peces = ed_ingred = is_admin

    result = db.usuarios.insert_one({
        "nombre": data.get('nombre'),
        "correo": data.get('correo'),
        "cargo": data.get('cargo'),
        "password": hashed_password,
        "is_admin": is_admin,
        "ed_peces": ed_peces,
        "ed_ingred": ed_ingred
    })
    return jsonify({"success": True, "inserted_id": str(result.inserted_id)})


# Ruta para iniciar sesión
@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = db.usuarios.find_one({"correo": data['correo']})

        if user and check_password_hash(user['password'], data['password']):
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
@token_required
def profile(current_user):
    return jsonify({
        "success": True, 
        "user": {
            "nombre": current_user['nombre'],
            "correo": current_user['correo'],
            "cargo": current_user['cargo'],
            "is_admin": current_user.get('is_admin', False),
            "ed_peces": current_user.get('ed_peces', False),
            "ed_ingred": current_user.get('ed_ingred', False)
        }
    })



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
        if enviar_correo_veryfy(email, codigo):
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
@token_required
@check_edicion_peces
def get_congrio_edit_data(current_user):
    try:
        congrio_data = list(db.peces.find({"nombre": "Congrio"}))
        for data in congrio_data:
            data['_id'] = str(data['_id'])
        return jsonify(congrio_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api.route('/pez/<id>', methods=['GET', 'PUT'])
@token_required
@check_edicion_peces
def edit_pez(current_user, id):
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

            # Obtener el valor anterior
            pez_anterior = db.peces.find_one({"_id": ObjectId(id)})
            if not pez_anterior:
                return jsonify({"success": False, "message": "No se encontró el pez a actualizar"}), 404

            convert_and_process(data)

            # Realizar la actualización
            result = db.peces.update_one({"_id": ObjectId(id)}, {"$set": data})

            if result.matched_count == 0:
                return jsonify({"success": False, "message": "No se encontró el pez a actualizar"}), 404

            # Obtener los valores del cambio
            pez_actual = db.peces.find_one({"_id": ObjectId(id)})
            
            # Extraer el nutriente y el peso específico que se cambió
            nutriente_cambiado = None
            peso_cambiado = None
            cambio_anterior = None
            cambio_nuevo = None

            for peso, requerimientos in data.get('requerimientos', {}).items():
                for nutriente, valores in requerimientos.items():
                    if (pez_anterior['requerimientos'][peso][nutriente]['min'] != pez_actual['requerimientos'][peso][nutriente]['min'] or
                        pez_anterior['requerimientos'][peso][nutriente]['max'] != pez_actual['requerimientos'][peso][nutriente]['max']):
                        nutriente_cambiado = nutriente
                        peso_cambiado = peso
                        cambio_anterior = pez_anterior['requerimientos'][peso][nutriente]
                        cambio_nuevo = pez_actual['requerimientos'][peso][nutriente]
                        break
                if nutriente_cambiado:
                    break
            
            if nutriente_cambiado and peso_cambiado:
                enviar_correo_edicion(
                    current_user['nombre'],
                    pez_actual['nombre'],
                    pez_actual['etapa'],
                    nutriente_cambiado,
                    peso_cambiado,
                    f"min: {cambio_anterior['min']}, max: {cambio_anterior['max']}",
                    f"min: {cambio_nuevo['min']}, max: {cambio_nuevo['max']}"
                )
            
            print(f"Datos después de la actualización: {db.peces.find_one({'_id': ObjectId(id)})}")

            return jsonify({"success": True, "message": "Datos actualizados correctamente"}), 200

    except Exception as e:
        print(f"⚠️ Error en PUT /pez/{id}: {e}")  # Mostrar error en la terminal
        return jsonify({"success": False, "message": str(e)}), 500
    

@api.route('/cojinova-edit', methods=['GET'])
@token_required
@check_edicion_peces
def get_cojinova_edit_data(current_user):
    try:
        cojinova_data = list(db.peces.find({"nombre": "Cojinova"}))
        for data in cojinova_data:
            data['_id'] = str(data['_id'])
        return jsonify(cojinova_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@api.route('/corvina-edit', methods=['GET'])
@token_required
@check_edicion_peces
def get_corvina_edit_data(current_user):
    try:
        corvina_data = list(db.peces.find({"nombre": "Corvina"}))
        for data in corvina_data:
            data['_id'] = str(data['_id'])
        return jsonify(corvina_data), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/palometa-edit', methods=['GET'])
@token_required
@check_edicion_peces
def get_palometa_edit_data(current_user):
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
@token_required
@check_edicion_ingredientes
def add_ingrediente(current_user):
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

        # Enviar correo de notificación para la agregación
        enviar_correo_ingrediente(
            accion='agregar',
            usuario=current_user['nombre'],
            nombre_ingrediente=nuevo_ingrediente["nombre"],
            coste=nuevo_ingrediente["coste"],
            stock=nuevo_ingrediente["stock"]
        )

        return jsonify({"success": True, "message": "Ingrediente agregado correctamente"}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/ingredientes/<id>', methods=['PUT'])
@token_required
@check_edicion_ingredientes
def update_ingrediente(current_user, id):
    data = request.json
    try:
        # Obtener el valor anterior
        ingrediente_anterior = db.ingredientes.find_one({"_id": ObjectId(id)})
        if not ingrediente_anterior:
            return jsonify({"success": False, "message": "Ingrediente no encontrado"}), 404

        ingrediente_actualizado = {
            "nombre": data.get("nombre"),
            "coste": float(data.get("coste")),
            "proteinas": float(data.get("proteinas")),
            "lipidos": float(data.get("lipidos")),
            "carbohidratos": float(data.get("carbohidratos")),
            "stock": float(data.get("stock"))
        }
        db.ingredientes.update_one({"_id": ObjectId(id)}, {"$set": ingrediente_actualizado})

        # Identificar los campos que cambiaron
        cambios = {}
        for campo in ingrediente_actualizado:
            if ingrediente_actualizado[campo] != ingrediente_anterior[campo]:
                cambios[campo] = (ingrediente_anterior[campo], ingrediente_actualizado[campo])

        # Enviar correo de notificación para la edición
        correo_enviado = enviar_correo_ingrediente(
            accion='editar',
            usuario=current_user['nombre'],
            nombre_ingrediente=ingrediente_actualizado["nombre"],
            cambios=cambios
        )

        if not correo_enviado:
            print("⚠️ Error al enviar el correo de notificación")
            return jsonify({"success": False, "message": "Error al enviar el correo de notificación"}), 500

        return jsonify({"success": True, "message": "Ingrediente actualizado correctamente"}), 200
    except Exception as e:
        print(f"⚠️ Error en PUT /ingredientes/{id}: {e}")  # Mostrar error en la terminal
        return jsonify({"success": False, "message": str(e)}), 500


@api.route('/ingredientes/<id>', methods=['DELETE'])
@token_required
@check_edicion_ingredientes
def delete_ingrediente(current_user, id):
    try:
        # Obtener el ingrediente antes de eliminarlo
        ingrediente = db.ingredientes.find_one({"_id": ObjectId(id)})
        if not ingrediente:
            return jsonify({"success": False, "message": "Ingrediente no encontrado"}), 404
        
        db.ingredientes.delete_one({"_id": ObjectId(id)})

        # Enviar correo de notificación para la eliminación
        enviar_correo_ingrediente(
            accion='eliminar',
            usuario=current_user['nombre'],
            nombre_ingrediente=ingrediente["nombre"]
        )

        return jsonify({"success": True, "message": "Ingrediente eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@api.route('/usuarios', methods=['GET'])
@token_required
@check_admin
def get_usuarios(current_user):
    try:
        # Excluir la contraseña de la respuesta
        usuarios = list(db.usuarios.find({}, {"password": 0}))
        for usuario in usuarios:
            usuario['_id'] = str(usuario['_id'])
        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/usuarios/<id>', methods=['PUT'])
@token_required
@check_admin
def update_usuario(current_user, id):
    data = request.json
    try:
        campo = data.get('campo')
        if campo not in ['ed_peces', 'ed_ingred']:
            return jsonify({"success": False, "message": "Campo no válido"}), 400

        usuario = db.usuarios.find_one({"_id": ObjectId(id)})
        if not usuario:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        # Actualizar el campo correspondiente
        db.usuarios.update_one({"_id": ObjectId(id)}, {"$set": {campo: not usuario[campo]}})
        return jsonify({"success": True, "message": "Permiso actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api.route('/usuarios/<id>', methods=['DELETE'])
@token_required
@check_admin  # O el decorador que uses para verificar permisos de eliminación
def delete_usuario(current_user, id):
    try:
        result = db.usuarios.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404
        return jsonify({"success": True, "message": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
