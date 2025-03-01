from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Inicializar la base de datos
def init_db():
    with sqlite3.connect('floristeria.db') as conn:
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inventario')
def inventario():
    with sqlite3.connect('floristeria.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flores")
        flores = cursor.fetchall()
    return render_template('inventario.html', flores=flores)

@app.route('/pedidos')
def pedidos():
    with sqlite3.connect('floristeria.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pedidos.id, pedidos.cliente, flores.nombre, pedidos.cantidad, pedidos.total 
            FROM pedidos JOIN flores ON pedidos.flor_id = flores.id
        ''')
        pedidos = cursor.fetchall()
    return render_template('pedidos.html', pedidos=pedidos)

@app.route('/agregar_flor', methods=['POST'])
def agregar_flor():
    nombre = request.form['nombre']
    precio = float(request.form['precio'])
    stock = int(request.form['stock'])
    
    with sqlite3.connect('floristeria.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flores (nombre, precio, stock) VALUES (?, ?, ?)", (nombre, precio, stock))
        conn.commit()
    
    return redirect(url_for('inventario'))

@app.route('/editar_precio', methods=['POST'])
def editar_precio():
    flor_id = request.form['flor_id']
    nuevo_precio = float(request.form['nuevo_precio'])
    
    with sqlite3.connect('floristeria.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE flores SET precio = ? WHERE id = ?", (nuevo_precio, flor_id))
        conn.commit()
    
    return redirect(url_for('inventario'))

@app.route('/registrar_pedido', methods=['POST'])
def registrar_pedido():
    cliente = request.form['cliente']
    flor_id = request.form['flor_id']
    cantidad = int(request.form['cantidad'])
    
    with sqlite3.connect('floristeria.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT precio FROM flores WHERE id = ?", (flor_id,))
        precio = cursor.fetchone()[0]
        total = precio * cantidad
        cursor.execute("INSERT INTO pedidos (cliente, flor_id, cantidad, total) VALUES (?, ?, ?, ?)", 
                       (cliente, flor_id, cantidad, total))
        conn.commit()
    
    return redirect(url_for('pedidos'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
