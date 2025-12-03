from flask import Flask, render_template
from config import Config
from routes import register_blueprints
from DataBase import Tables
from DataBase.BKK import Stations
import asyncio
import os

# Configure Flask to use frontend directories
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
static_dir = os.path.join(frontend_dir, 'static')
template_dir = os.path.join(frontend_dir, 'templates')

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
app.config.from_object(Config)

# Enregistrer tous les blueprints
register_blueprints(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hello-world', methods=['GET'])
def hello_world():
    return {'hello': 'world'}, 200

@app.route('/test-static')
def test_static():
    static_path = os.path.join(app.static_folder, 'css', 'style.css')
    exists = os.path.exists(static_path)
    return f"Fichier existe: {exists}<br>Chemin: {static_path}"

async def initDB():
    try:
        await Tables.create_table()
        await Stations.clear_bkk_table()
        await Stations.fill_bkk_table()
        return False
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return True

if asyncio.run(initDB()):
    exit(1)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)