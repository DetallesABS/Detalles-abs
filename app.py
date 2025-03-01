from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "floristeria.db"

# Inicializar la base de datos
def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    precio REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pedidos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente TEXT NOT NULL,
                    flor_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (flor_id) REFERENCES flores (id)
                )
            ''')
            conn.commit()
            print("Base de datos creada exitosamente.")

# Conectar a la base de datos
def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventario')
def inventario():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flores")
    flores = cursor.fetchall()
    conn.close()
    return render_template('inventario.html', flores=flores)

@app.route('/pedidos')
def pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pedidos.id, pedidos.cliente, flores.nombre, pedidos.cantidad, pedidos.total 
        FROM pedidos JOIN flores ON pedidos.flor_id = flores.id
    ''')
    pedidos = cursor.fetchall()
    conn.close()
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/agregar_flor', methods=['POST'])
def agregar_flor():
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    stock = int(request.form['stock'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO flores (nombre, precio, stock) VALUES (?, ?, ?)", (nombre, precio, stock))
    conn.commit()
    conn.close()
    
    return redirect(url_for('inventario'))

@app.route('/editar_precio', methods=['POST'])
def editar_precio():
    flor_id = request.form['flor_id']
    nuevo_precio = float(request.form['nuevo_precio'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE flores SET precio = ? WHERE id = ?", (nuevo_precio, flor_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('inventario'))

@app.route('/registrar_pedido', methods=['POST'])
def registrar_pedido():
    cliente = request.form['cliente']
    flor_id = request.form['flor_id']
    cantidad = int(request.form['cantidad'])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT precio FROM flores WHERE id = ?", (flor_id,))
    precio_data = cursor.fetchone()
    
    if precio_data:
        precio = precio_data["precio"]
        total = precio * cantidad
        cursor.execute("INSERT INTO pedidos (cliente, flor_id, cantidad, total) VALUES (?, ?, ?, ?)", 
                       (cliente, flor_id, cantidad, total))
        conn.commit()
    
    conn.close()
    return redirect(url_for('pedidos'))

import os

if __name__ == '__main__':
    # Si el archivo de la base de datos existe, lo eliminamos
    if os.path.exists("floristeria.db"):
        os.remove("floristeria.db")

    init_db()  # Volver a crear la base de datos y las tablas
    print("Base de datos creada nuevamente en Render.")
    app.run(debug=True)

