import os
import io
import csv
import pytz
from datetime import datetime
from flask_wtf import FlaskForm
from flask import Response, current_app as app
from wtforms import StringField, TextAreaField, validators
from flask import Blueprint, Flask, redirect, render_template, request, jsonify, url_for, flash, session, make_response
from app import mongo, bcrypt
import requests

main = Blueprint('main', __name__)

class ContactForm(FlaskForm):
    nombre = StringField('Nombre', [validators.DataRequired()])
    apellidos = StringField('Apellidos', [validators.DataRequired()])
    email = StringField('Correo Electrónico', [validators.DataRequired(), validators.Email()])
    telefono = StringField('Número de teléfono móvil', [validators.Optional()])
    asunto = StringField('Asunto', [validators.DataRequired()])
    mensaje = TextAreaField('Mensaje', [validators.DataRequired()])

DEFAULT_USERNAME = 'MiguelCuba'
DEFAULT_PASSWORD = 'angel.cuba117'
current_setpoint = 0
local_tz = pytz.timezone('America/Mexico_City')
fecha = datetime.now(local_tz).strftime("%Y-%m-%d")

#############################################################################
####################################INICIO################################################################################################################
##################################Login.html##############################################################################################################
#############################################################################

@main.route('/', methods=['GET', 'POST'])
def login():
    local_time = datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST':
        users = mongo.db.users # Colección para registrar los accesos correctos
        wrong_access = mongo.db.wrongaccess  # Colección para registrar los accesos incorrectos
        
        login_user = users.find_one({'name': request.form['username']})

        # Si el usuario no existe, verifica si es el usuario por defecto
        if not login_user and request.form['username'] == DEFAULT_USERNAME:
            hashed_pass = bcrypt.generate_password_hash(DEFAULT_PASSWORD).decode('utf-8')
            users.insert_one({
                'timestamp': local_time,
                'name': DEFAULT_USERNAME, 
                'password': hashed_pass
                })
            
            login_user = {'name': DEFAULT_USERNAME, 'password': hashed_pass}  # Recrea el objeto login_user para la verificación posterior

        # Verifica la contraseña solo si login_user existe
        if login_user:
            if bcrypt.check_password_hash(login_user['password'], request.form['pass']):
                # session['username'] = request.form['username']  # Descomentar si vas a usar sesiones
                return redirect(url_for('main.MO'))
            else:
                # Contraseña incorrecta
                flash('Contraseña incorrecta', 'error')
                wrong_access.insert_one({
                    'username': request.form['username'],
                    'timestamp': local_time,
                    'pass': request.form['pass'],
                    'type': 'password incorrecta'
                }) 
        
        else:
            # Usuario no existe
            flash('El usuario no existe', 'error')  # 'error' es una categoría para el mensaje
            wrong_access.insert_one({
                'username': request.form['username'],
                'timestamp': local_time,
                'type': 'usuario no existe',
                'pass': request.form['pass']
                
            })  # Registra el intento incorrecto
        return redirect(url_for('main.login'))

    # Método GET o autenticación fallida
    resp = make_response(render_template('login.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@main.route('/recuperar_contraseña')
def forgot_password():
    # Aquí implementarás la lógica de recuperación de contraseña más adelante
    return 'Forgot password'

@main.route('/crear_cuenta')
def create_account():
    # Aquí implementarás la lógica de creación de cuenta más adelante
    return 'Create account'

#############################################################################
#################################MO.html##################################################################################################################
#############################################################################

@main.route('/MO')
def MO():
    return render_template('MO.html')

@main.route("/submit_data", methods=["POST"])
def submit_data():
    local_time = datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S")
    fecha = datetime.now(local_tz).strftime("%Y-%m-%d")
    # Recibir datos de temperatura desde la Raspberry Pi como una lista
    temperature_list = request.form.getlist("temperature")  # Obtener una lista de temperaturas

    # Definir la estructura de la base de datos
    data_entry = {
        "fecha": fecha,
        "time": local_time,
        "setpoint": current_setpoint  # Como current_setpoint siempre tiene un valor, lo añadimos directamente
    }

    # Lista para almacenar datos que se escribirán en el archivo txt
    data_for_txt = []

    # Agregar los valores de temperatura a la estructura de datos
    for i in range(7):
        sensor_key = f"sensor{i+1}"  # Crear claves de "sensor1" a "sensor7"
        if i < len(temperature_list):
            temperature_value = float(temperature_list[i])
            data_entry[sensor_key] = temperature_value
            data_for_txt.append(str(temperature_value))
        else:
            # Si no se proporciona un valor para el sensor, establecerlo en 0
            data_entry[sensor_key] = 0.0
            data_for_txt.append("0.0")

    # Guardar los datos en MongoDB
    mongo.db.temperature_data.insert_one(data_entry)

    # Escribir los datos en datos.txt
    with open("datos.txt", "a") as file:
        file.write(", ".join(data_for_txt) + "\n")

    return jsonify({"message": "Data received and saved."})

@main.route("/get_data")
def get_data():
    
  # Consulta los datos de temperatura desde la base de datos
    temperature_data = mongo.db.temperature_data.find()
    
    # Convierte los resultados de la consulta en una lista de diccionarios
    data = []
    for entry in temperature_data:
        data_point = {
            "time": entry["time"],  # Asegúrate de que tus documentos tengan un campo 'time'
            "temperature": entry["temperature"],  # Asegúrate de que tus documentos tengan un campo 'temperature'
        }
        data.append(data_point)

    # Devuelve los datos en formato JSON
    return jsonify(data)

@main.route("/latest_data_for_graph")
def latest_data_for_graph():
    # The sensor parameter is optional. If not provided, all sensors will be included.
    sensor_param = request.args.get('sensor')
    # Define the number of entries to return
    n = 25

    # Initialize your data structures
    label = []  # For storing X-axis labels
    data = {
        "value1": [],
        "value2": [],
        "value3": [],
        "value4": [],
        "value5": [],
        "value6": [],
        "value7": [],
        "value0": []  # For the setpoint
    }

    # Query the database for the last n entries
    recent_data = mongo.db.temperature_data.find().sort([('_id', -1)]).limit(n)

    # Populate your data structures with the query results
    for entry in recent_data:
        label.append(entry["time"])  # Assuming "time" is a string that represents the timestamp
        for i in range(1, 8):  # Assuming there are 7 sensors
            sensor_key = f"sensor{i}"
            if sensor_key in entry:
                data[f"value{i}"].append(entry[sensor_key])
        # Special handling for setpoint
        if 'setpoint' in entry:
            data["value0"].append(entry["setpoint"])

    # Reverse the data lists so the oldest data is first
    label.reverse()
    for key in data:
        data[key].reverse()

    # If a specific sensor is requested, only return that data
    if sensor_param and sensor_param != 'setpoint':
        sensor_key = 'value' + sensor_param[-1]
        filtered_data = {sensor_key: data[sensor_key], "label": label}
        return jsonify(filtered_data)
    elif sensor_param == 'setpoint':  # Check if the setpoint is requested
        return jsonify({"label": label, "value0": data["value0"]})
    else:
        # Return all data if no specific sensor is requested
        data["label"] = label
        return jsonify(data)


@main.route("/latest_data")
def latest_data():
    # Consulta el último registro en MongoDB que contenga tanto las temperaturas como el setpoint
    last_record = mongo.db.temperature_data.find().sort([('_id', -1)]).limit(1)
    
    data = list(last_record)
    
    if data:
        data = data[0]
        del data['_id']  # Eliminar el ID ya que no es serializable
    else:
        data = {}
    
    return jsonify(data)

@main.route("/update_setpoint", methods=["POST"])
def update_setpoint():
    global current_setpoint  # Acceder a la variable global
    try:
        setpoint = float(request.form.get("setpoint"))
        current_setpoint = round(setpoint, 2)
        
        # Envía el setpoint a la Raspberry Pi:
        response = requests.post("http://192.168.100.206:8080/receive_setpoint", data={"setpoint": current_setpoint})
        
        if response.status_code == 200:
            return jsonify({"message": "Setpoint updated and sent to Raspberry Pi successfully."})
        else:
            return jsonify({"message": "Failed to send setpoint to Raspberry Pi.", "error": response.text}), 500
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 400
    
#############################################################################
############################Gemelo digital.html###########################################################################################################
#############################################################################

@main.route("/Gemelo_digital")
def gemelo_digital():
    return render_template("Gemelo_digital.html")

#############################################################################
############################base de datos.html############################################################################################################
#############################################################################

@main.route("/base_de_datos")
def base_de_datos():
    
    # Consulta todos los registros de temperatura en MongoDB
    temperature_records = mongo.db.temperature_data.find()
    users = mongo.db.users.find()
    wrong = mongo.db.wrongaccess.find()

    # Convertir los registros en una lista para poder pasarlos al template
    data_list = list(temperature_records)
    data_list1 = list(users)
    data_list2 = list(wrong)

    return render_template("base_de_datos.html", data=data_list, data1=data_list1, data2=data_list2)

@main.route('/download-csv/<string:collection_name>')
def download_csv(collection_name):
    variant = request.args.get('variant')
    # Usamos io.StringIO para crear un archivo en memoria
    si = io.StringIO()
    cw = csv.writer(si)

    if collection_name == "temperature_data":
        records = mongo.db.temperature_data.find()

        if variant == "pid":
            cw.writerow(['Tiempo', 'Setpoint', 'Sensor1']) 
            for record in records:
                cw.writerow([record['time'], record['setpoint'], record['sensor1']])  
            filename = "temperature_data_pid.csv"
        else:
            cw.writerow(['Tiempo', 'Setpoint', 'Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'sensor5', 'Sensor6', 'Sensor7'])
            for record in records:
                cw.writerow([record['time'], record['setpoint'], record['sensor1'], record['sensor2'], record['sensor3'], record['sensor4'], record['sensor5'], record['sensor6'], record['sensor7']])
            filename = "temperature_data.csv"

    elif collection_name == "users":
        records = mongo.db.users.find()
        cw.writerow(['Tiempo', 'Nombre', 'password'])  
        for record in records:
            cw.writerow([record['timestamp'], record['name'], record['password']])  
        filename = "access.csv"

    elif collection_name == "wrongaccess":
        records = mongo.db.wrongaccess.find()
        cw.writerow(['Tiempo', 'Nombre', 'password', 'Tipo'])  
        for record in records:
            cw.writerow([record['timestamp'], record['username'], record['pass'], record['type']]) 
        filename = "access_denied.csv"
    
    else:
        return jsonify({"error": "Invalid collection name"}), 400

    # Movemos el puntero al inicio del archivo
    si.seek(0)
    
    # Devolvemos el archivo CSV como respuesta
    return Response(si, mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})



#############################################################################
################################reportes.html#############################################################################################################
#############################################################################

@main.route("/reportes")
def reportes():
    return render_template("reportes.html")


@main.route('/crear-reporte', methods=['POST'])
def crear_reporte():
    Usuario = request.form['Usuario']
    fecha_incidente = request.form['fecha-incidente']
    elemento = request.form['elemento']
    incidente = request.form['incidente']
    
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    archivo_nombre = f"{fecha_actual}_{Usuario.split()[-1]}.txt"
    
    with open(os.path.join('code', 'reportes', archivo_nombre), 'w') as archivo:
        archivo.write(f"Usuario: {Usuario}\n")
        archivo.write(f"Fecha del Incidente: {fecha_incidente}\n")
        archivo.write(f"Elemento Afectado: {elemento}\n")
        archivo.write(f"Incidente: {incidente}\n")
    
    return jsonify({'mensaje': 'Reporte creado con éxito'})

@main.route('/obtener-reportes')
def obtener_reportes():
    reportes = os.listdir('reportes')
    return jsonify({'reportes': reportes})

@main.route('/obtener-reporte/<nombre_archivo>')
def obtener_reporte(nombre_archivo):
    with open(os.path.join('reportes', nombre_archivo), 'r') as archivo:
        contenido = archivo.read()
    return jsonify({'contenido': contenido})

#############################################################################
##################################faq.html################################################################################################################
#############################################################################

@main.route("/faq")
def faq():
    return render_template("faq.html")

#############################################################################
###################################contact.html###########################################################################################################
#############################################################################

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    
    form = ContactForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Creando un 'documento' con los datos del formulario
            contacto = {
                "nombre": form.nombre.data,
                "apellidos": form.apellidos.data,
                "email": form.email.data,
                "telefono": form.telefono.data,
                "asunto": form.asunto.data,
                "mensaje": form.mensaje.data
            }

            # Guardando el 'documento' en la colección 'contactos'
            mongo.db.contactos.insert_one(contacto)
            flash('Mensaje enviado correctamente')
            return redirect(url_for('contacto'))  # Redirecciona de nuevo al formulario de contacto.
        else:
            flash('Error en el formulario', 'danger')

    return render_template('contact.html', form=form)

#############################################################################
####################################FIN###################################################################################################################
#############################################################################