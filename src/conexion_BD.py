from flask import Flask
from flask_cors import CORS
from colecciones.mongo_setup import create_collections
from rutas.api_routes import api

app = Flask(__name__)
CORS(app)  # Habilitar CORS para toda la aplicación

# Configurar las colecciones al iniciar la aplicación
create_collections()

# Registrar el blueprint para las rutas
app.register_blueprint(api)

@app.route('/')
def home():
    return "API de Peces Aquapacifico"

if __name__ == '__main__':
    app.run(debug=True)
