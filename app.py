from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Cargar datos
ventas = pd.read_csv('ventas.csv')
usuarios = pd.read_csv('usuarios.csv')

# Función para recomendaciones basadas en sexo
def recomendar_productos_por_sexo(sexo, n_recomendaciones=5):
    productos_sexo = ventas[ventas['sexo'] == sexo]
    productos_populares = productos_sexo['producto_id'].value_counts().head(n_recomendaciones).index.tolist()
    return productos_populares

# Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Registro de usuario
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        sexo = request.form['sexo']
        
        nuevo_usuario = pd.DataFrame({
            'nombre': [nombre],
            'email': [email],
            'sexo': [sexo]
        })
        
        # Aquí se realiza el cambio: se usa pd.concat en lugar de append
        usuarios = pd.concat([usuarios, nuevo_usuario], ignore_index=True)
        
        # Guardar los cambios en el archivo CSV
        usuarios.to_csv('usuarios.csv', index=False)
        
        session['user'] = nombre
        session['sexo'] = sexo
        
        return redirect(url_for('recomendaciones'))
    
    return render_template('registro.html')

# Login de usuario
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = usuarios[usuarios['nombre'] == nombre]
        
        if not usuario.empty:
            session['user'] = nombre
            session['sexo'] = usuario['sexo'].values[0]
            return redirect(url_for('recomendaciones'))
        else:
            return 'Usuario no encontrado'
    
    return render_template('login.html')

# Página de recomendaciones
@app.route('/recomendaciones')
def recomendaciones():
    if 'user' in session:
        sexo = session['sexo']
        productos = recomendar_productos_por_sexo(sexo)
        return render_template('recomendaciones.html', productos=productos, sexo=sexo)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
