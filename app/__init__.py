from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail



app = Flask(__name__)
app.secret_key = 'clave_super_segura'  # <-- Necesario para sesiones y flash

app.config.from_object('config')

db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'mmayor200610@gmail.com'
app.config['MAIL_PASSWORD'] = 'ziivqasnthnvnnhk '
app.config['MAIL_DEFAULT_SENDER'] = 'mmayor200610@gmail.com'

mail = Mail(app)


from app import routes, models  # Importa rutas y modelos para registrar con Flask y SQLAlchemy

