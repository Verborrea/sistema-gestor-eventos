from datetime import datetime
from markupsafe import escape

from flask import Flask, request, redirect, url_for
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy, SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/sge.db'

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tipodoc = db.Column(db.String(10), nullable=False)
    doc = db.Column(db.String(10), nullable=False)

loremLipsum='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum aliquet metus, sed hendrerit quam maximus ut. Sed cursus mi ut ligula dapibus elementum. Proin vel finibus arcu. Ut tincidunt ornare velit, vel lacinia lectus. Fusce ante mi, posuere nec feugiat at, suscipit non magna. Ut facilisis ultricies enim, in rutrum sapien tempus vehicula. In imperdiet dolor sed volutpat sodales.
'''

@app.route('/')
def index():
    datos = [{"id":"Evento01","nombre":"Evento1",'fechaCreacion':'05/05/21','fechaCierreInscripcion':'No definida','fechaInicioEvento':'No definida','fechaCierreEvento':'No definida','estadoEvento':'Borrador'}]
    return render_template('SCV-B01VisualizarListaEventos.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",NombreEvento="Our Point")

@app.route('/seleccionarevento/', methods=['POST'])
def seleccionarevento():
    if request.method == 'POST':
        id = request.form.get('selection')
        if id==None:
            return redirect(url_for('index'), code=302)
    return redirect(url_for('evento'), code=302)
    

@app.route('/evento/', methods=['GET','POST'])
def evento():
    #infoEvento = {'estado':'Borrador'}
    actividad = [
        {"nombre":"Exposicion de materiales"},
        {"nombre":"Exposicion de IA"},
        {"nombre":"Exposicion de Machine Learning"},
        {"nombre":"Exposicion de BigData"}
    ]
    return render_template('SCV-B01MenuEvento.html',estado='Borrador',descripcion=loremLipsum,lugar="/lugar/",tipoEvento="/tipoEvento/",actividad = actividad,lenActividad = len(actividad))


@app.route('/profile/<username>')
def profile(username):
    return render_template('usuario.html', usuario=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(
            username = request.form.get('usuario'),
            password = request.form.get('contra')
        ).first()

        if user:
            return redirect(url_for('profile', username=request.form.get('usuario')))
        else:
            return 'Usuario no existente'
    else:
        return render_template('login.html')

@app.route('/signup')
def register():
    return render_template('signup.html')

@app.route('/create-user', methods=['POST'])
def create_user():
    user = Usuario.query.filter_by(username = request.form.get('usuario')).first()
    mail = Usuario.query.filter_by(email = request.form.get('correo')).first()
    if user:
        return 'Usuario ya existente'
    if mail:
        return 'El correo ingresado ya tiene una cuenta asociada'
    nuevo_usuario = Usuario(
        username = request.form.get('usuario'),
        password = request.form.get('contra'),
        nombre = request.form.get('nombre'),
        email = request.form.get('correo'),
        tipodoc = request.form.get('tipo_doc'),
        doc = request.form.get('doc')
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    print(Usuario.query.all())
    return redirect(url_for('login'))

#MODIFY


#
if __name__ == '__main__':
    app.run()
