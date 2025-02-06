from pymongo import MongoClient
import os

# Conectar a la base de datos MongoDB en Docker usando la variable de entorno
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client["Peces_Aquapacifico"]

# Crear las colecciones "usuarios", "cargos" y "peces" si no existen
def create_collections():
    if "usuarios" not in db.list_collection_names():
        db.create_collection("usuarios")
    if "cargos" not in db.list_collection_names():
        db.create_collection("cargos")
    if "peces" not in db.list_collection_names():
        db.create_collection("peces")
    if "ingredientes" not in db.list_collection_names():
        db.create_collection("ingredientes")
