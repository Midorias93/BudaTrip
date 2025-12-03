from flask import Flask, render_template
from config import Config
from routes import register_blueprints
from DataBase.models import initialize_database, close_database
from DataBase.BKK import Stations
import os

# Configure Flask to use frontend directories
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
static_dir = os.path.join(frontend_dir, 'static')
template_dir = os.path.join(frontend_dir, 'templates')

app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
app.config.from_object(Config)

# Register all blueprints
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
    return f"File exists: {exists}<br>Path: {static_path}"

def initDB():
    try:
        initialize_database()
        Stations.clear_bkk_table()
        Stations.fill_bkk_table()
        return False
    except Exception as e:
        print(f"Database connection error: {e}")
        return True

if initDB():
    exit(1)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8000)