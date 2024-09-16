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

@app.route("/tabla")
def index():
    con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
        )
    con.close()
    return render_template("calificaciones.html")

@app.route('/evento', methods=["GET","POST"])
def evento():
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
            message = 'Usuario agregado exitosamente!'
            pusher_client.trigger('my-channel', 'my-event', {'message': f'Nuevo evento: {nombre}, {comentario}, {calificacion}'})
        except mysql.connect.Error as err:
            print("error al conectar msql:", err)
            message="Error al insertar usuario"
        finally:
             if con.is_connected():
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
        cursor.execute("SELECT * FROM tst0_experiencias")    
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
        print(cursor.rowcount, "records deleted")
        return '', 200
    except mysql.connector.Error as err:
        print("Error al eliminar con MySQL:", err)
        return '', 500
    finally:
         if con.is_connected():
            cursor.close()
            con.close()
            
    #return redirect(url_for('vistatabla'))


if __name__ == '__main__':
    app.run(debug=True)
