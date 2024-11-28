from flask import Flask, jsonify, render_template, request, url_for, redirect, session
from flask_cors import CORS
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import pandas as pd
import os
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'
CORS(app)
bcrypt = Bcrypt(app)

# Conexión a MongoDB
client = MongoClient(os.environ.get('MONGO_URI', 'mongodb://mongo:27017/'))
db = client['tu_base_de_datos']
users_collection = db['usuarios']

# Cargar tweets una sola vez al inicio
try:
    df = pd.read_csv('archive/covid19_tweets.csv')
    tweets_data = df[['text']].to_dict(orient='records')
except Exception as e:
    print(f"Error al cargar tweets: {e}")
    tweets_data = []

@app.route('/')
def index():
    if 'user' in session:
        with open('static/js/users.js', 'r') as file:
            content = file.read()
            json_str = content[content.find('['):content.rfind(']')+1]
            users_array = json.loads(json_str)
        return render_template('tweets.html', tweets=tweets_data[:15], users=users_array)
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Aquí va tu lógica de registro
        # ...
        
        return jsonify({'success': '¡Registro exitoso!'})
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Por ahora, simplemente autenticamos sin verificar contraseña
        session['user'] = username
        return jsonify({'success': '¡Inicio de sesión exitoso!'})
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/tweets')
def tweets():
    if 'user' not in session:
        return redirect('/login')
    
    try:
        with open('static/js/users.js', 'r') as file:
            content = file.read()
            json_str = content[content.find('['):content.rfind(']')+1]
            users_array = json.loads(json_str)
    except Exception as e:
        print(f"Error loading users: {e}")
        users_array = []
    
    return render_template('tweets.html', tweets=tweets_data[:15], users=users_array)

@app.route('/random_user')
def random_user():
    with open('static/js/users.js', 'r') as file:
        content = file.read()
        json_str = content[content.find('['):content.rfind(']')+1]
        users_array = json.loads(json_str)
    return jsonify(random.choice(users_array))

@app.route('/api/tweets')
def get_more_tweets():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 15))
    
    more_tweets = tweets_data[offset:offset+limit]
    return jsonify(more_tweets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
