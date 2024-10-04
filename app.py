from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
from flask import jsonify
from datetime import datetime,  timedelta

import pusher
import mysql.connector

import pytz

import pusher



app = Flask(__name__)     
utc_now = datetime.now(pytz.utc)
adjusted_time = utc_now - timedelta(minutes=10)  
print("Hora ajustada en UTC:", adjusted_time)

pusher_client = pusher.Pusher(
app_id='1864238',
key='2ea386b7b90472052932',
secret='578df1dc2b254c75c850',
cluster='us2',
ssl=True
)



@app.route('/holamundo')
def hello_world():
    return 'Hola, mundo'

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id, message=None):
    con= None
    registros=[]
    try:
        con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
        if not con.is_connected():
            raise msql.connector.Error('No se pudo conectar a la base de datos')
        
        cursor = con.cursor()
        sql= "SELECT * FROM tst0_experiencias WHERE Id_Experiencia= %s"
        cursor.execute(sql,(id,))
        registros = cursor.fetchall()
        if len(registros)==0:
            message="No se encontro registro con este ID"
            return render_template('editar.html', message=message, registros=[])
        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
        message="No se pudo conectar. Verificar conexión."
    finally:
        if con and con.is_connected():
            cursor.close()
            con.close()
    
    return render_template('editar.html', registros=registros, message=message)

@app.route("/tabla")
def index():
    con=None
    try:
        con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
            )
    except mysql.connector.Error as err:
        print("Error al conectar:", err)
        return "No se pudo conectar. Verifique su conexion", 500
    finally:
        if con and con.is_connected():
            con.close()
    return render_template("calificaciones.html")

@app.route('/evento', methods=["GET","POST"])
def evento():
    con= None
    message=""
    if request.method=='POST':
        nombre=request.form['txtnombreApellido']
        comentario=request.form['txtcomentario']
        calificacion=request.form['txtcalificacion']
        
        try:
            con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
            )
            cursor = con.cursor()
            sql = "INSERT INTO tst0_experiencias (Nombre_Apellido, Comentario, Calificacion) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre,comentario,calificacion))
            con.commit()
            con.close()
            message = '¡Encuesta enviada exitosamente!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {nombre}, {comentario}, {calificacion}'})
        except mysql.connector.Error as err:
            print("error al conectar msql:", err)
            message="Error al enviar encuesta"
        finally:
             if con:
                cursor.close()
                con.close()
        
        return render_template('formulario.html', message=message)
    return render_template('formulario.html')

@app.route('/vista')
def vistatabla():
    try:
        con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
        cursor = con.cursor()
        cursor.execute("SELECT * FROM tst0_experiencias ORDER BY Id_Experiencia DESC")    
        registros = cursor.fetchall()
        print("Registros obtenidos:", registros)
    except mysql.connector.Error as err:
        print("Error al conectar con MySQL:", err)
        registros = []  
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
    
    return jsonify(registros)


@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    try:
        con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
        cursor = con.cursor()
        sql = "DELETE FROM tst0_experiencias WHERE Id_Experiencia= %s"
        cursor.execute(sql,(id,))
        con.commit()
        print(cursor.rowcount, "Eliminacion exitosa")
        pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {id}'})
        return '', 200
    except mysql.connector.Error as err:
        print("Error al eliminar con MySQL:", err)
        return '', 500
    finally:
         if con.is_connected():
            cursor.close()
            con.close()
            
    #return redirect(url_for('vistatabla'))
@app.route('/actualizar/<int:id>', methods=['GET','POST'])
def actualizar(id):
    con=None 
    if request.method=='POST':
        Nuevo_nombre=request.form['txtnombreApellido']
        Nuevo_comentario=request.form['txtcomentario']
        Nuevo_calificacion=request.form['txtcalificacion']
        try:
            con = mysql.connector.connect(
            host="185.232.14.52",
            database="u760464709_tst_sep",
            user="u760464709_tst_sep_usr",
            password="dJ0CIAFF="
            )
            cursor = con.cursor()
            sql = "UPDATE tst0_experiencias SET Nombre_Apellido=%s, Comentario=%s, Calificacion=%s WHERE Id_Experiencia= %s"
            
            cursor.execute(sql,(Nuevo_nombre, Nuevo_comentario, Nuevo_calificacion, id,))
            con.commit()
            con.close()     
            message = '¡Encuesta modificada exitosamente!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {Nuevo_nombre}, {Nuevo_comentario}, {Nuevo_calificacion}'})
        except mysql.connector.Error as err:
            print("Error al modificar con MySQL:", err)
            message="Error al modificar"
        finally:
            if con and con.is_connected():
                cursor.close()
                con.close()
        return editar(id, message=message)
    return editar(id)    

if __name__ == '__main__':
    app.run(debug=True)
