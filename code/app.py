import os
import pytz
from flask import Flask, redirect, render_template, request, jsonify, url_for, flash, session, make_response
from wtforms import StringField, TextAreaField, validators
from flask_pymongo import PyMongo, MongoClient
from flask_wtf import FlaskForm
from datetime import datetime

import requests
from flask_bcrypt import Bcrypt
 
# Configuración
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/proyecto'

mongo = None
bcrypt = None

def create_app():
    global mongo, bcrypt
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializaciones aquí
    mongo = PyMongo(app)
    bcrypt = Bcrypt(app)


    # Registro de blueprints
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    last_record = mongo.db.temperature_data.find().sort([('_id', -1)]).limit(1)
    data = list(last_record)

    if data:
        data = data[0]
        current_setpoint = data.get('setpoint', 0)
    else:
        current_setpoint = 0


    return app

app = create_app()

#if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5000)