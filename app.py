import datetime
from markupsafe import escape

from flask import Flask, request, redirect, url_for, session
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy, SQLAlchemy
from sqlalchemy.orm import defaultload
import json

app = Flask(__name__)
app.secret_key = b'192b9bdd22ab9ed4d12e236c77823bcbf'
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

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    lugar = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default="Borrador")
    fechaCreacion = db.Column(db.Date, default=datetime.datetime.utcnow)
    fechaPreInscripcion = db.Column(db.Date)
    fechaAprtrInscripcion = db.Column(db.Date)
    fechaLmtDscnto = db.Column(db.Date)
    fechaCierreInscripcion = db.Column(db.Date)
    fechaInicio = db.Column(db.Date)
    fechaFin = db.Column(db.Date)
    cntInscritos = db.Column(db.Integer, default=0)
    cntPreInscritos = db.Column(db.Integer, default=0)
    prcntjDscnto = db.Column(db.Float, default=0)
    plantilla = db.Column(db.Boolean, default=False)
    
loremLipsum='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum aliquet metus, sed hendrerit quam maximus ut. Sed cursus mi ut ligula dapibus elementum. Proin vel finibus arcu. Ut tincidunt ornare velit, vel lacinia lectus. Fusce ante mi, posuere nec feugiat at, suscipit non magna. Ut facilisis ultricies enim, in rutrum sapien tempus vehicula. In imperdiet dolor sed volutpat sodales'''

def crearFecha(date, format):
    str = 'No definida'
    if date != None:
        str = date.strftime(format)
    return str

@app.route('/')
def index():
    datos = []
    eventos = Evento.query.all()
    for evento in eventos:
        datos.append({
            "id":evento.id,
            "nombre":evento.nombre,
            'fechaCreacion':crearFecha(evento.fechaCreacion,"%d/%m/%Y"),
            'fechaCierreInscripcion':crearFecha(evento.fechaCierreInscripcion,"%d/%m/%Y"),
            'fechaInicioEvento':crearFecha(evento.fechaInicio,"%d/%m/%Y"),
            'fechaCierreEvento':crearFecha(evento.fechaFin,"%d/%m/%Y"),
            'estadoEvento':evento.estado
        })
    return render_template('SCV-B01VisualizarListaEventos.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point")

@app.route('/seleccionarevento/', methods=['POST'])
def seleccionarevento():
    if request.method == 'POST':
        id = request.form.get('selection')
        if id==None:
            return redirect(url_for('index'), code=302)
    return redirect(url_for('evento',idEvento=id), code=302)
    

@app.route('/evento/<idEvento>', methods=['GET','POST'])
def evento(idEvento):
    miEvento = Evento.query.filter_by(
        id = idEvento
    ).first()
    session['idEvento'] = idEvento
    actividad = [
        {"nombre":"Exposicion de materiales","id":"id-actividad"},
        {"nombre":"Exposicion de IA","id":"id-actividad"},
        {"nombre":"Exposicion de Machine Learning","id":"id-actividad"},
        {"nombre":"Exposicion de BigData","id":"id-actividad"}
    ]
    return render_template(
        'SCV-B01MenuEvento.html',
        estado = miEvento.estado,
        descripcion = miEvento.descripcion,
        lugar = miEvento.lugar,
        tipoEvento = miEvento.tipo,
        actividad = actividad,
        lenActividad = len(actividad),
        nombreEvento = miEvento.nombre)

@app.route('/crearEvento/', methods=['POST'])
def crearEvento():
    nuevoEvento = Evento(
        nombre = request.form.get('nombreEvento'),
        tipo = request.form.get('tipoEvento'),
        descripcion = request.form.get('descripcionBreve'),
        lugar = request.form.get('lugar')
    )

    db.session.add(nuevoEvento)
    db.session.commit()

    return redirect(url_for('evento',idEvento=nuevoEvento.id), code=302)

@app.route('/modificarEvento/', methods=['POST'])
def modificarEvento():
    miEvento = Evento.query.get_or_404(session['idEvento'])

    miEvento.nombre = request.form.get('nombreEvento')
    miEvento.tipo = request.form.get('tipoEvento')
    miEvento.descripcion = request.form.get('descripcion')
    miEvento.lugar = request.form.get('lugar')
    try:
        db.session.commit()
    except:
        print("Error")
    return redirect(url_for('evento',idEvento=miEvento.id), code=302)

@app.route('/lanzarEvento/', methods=['POST'])
def lanzarEvento():
    return "aqui lanzaria evento y redirecciona a la pagina de este evento"


@app.route('/obtenerPlantillas/', methods=['POST','GET'])
def obtenerPlantillas():
    #headers=["Nombre","Fecha","TipoEvento"]

    plantillas = []
    eventos = Evento.query.all()
    for evento in eventos:
        plantillas.append({
            "id":evento.id,
            "Nombre":evento.nombre,
            "Fecha":crearFecha(evento.fechaInicio,"%d/%m/%Y"),
            "TipoEvento":evento.tipo
        })

    return json.dumps(plantillas)

@app.route('/crearEventoPlantilla/', methods=['POST'])
def crearEventoPlantilla():
    id = request.form.get('selection')
    if id == None:
        return redirect(url_for('index'), code=302)
    
    baseEvento = Evento.query.get_or_404(id)

    nuevoEvento = Evento(
        nombre = baseEvento.nombre,
        tipo = baseEvento.tipo,
        descripcion = baseEvento.descripcion,
        lugar = baseEvento.lugar,
        plantilla = True
    )

    db.session.add(nuevoEvento)
    db.session.commit()

    return redirect(url_for('evento',idEvento=nuevoEvento.id), code=302)

@app.route('/eliminarActividad/', methods=['GET','POST'])
def eliminarActividad():
    return "aqui elimina actividad"
    return render_template('SCV-B01MenuEvento.html',estado='Borrador',descripcion=loremLipsum,lugar="/lugar/",tipoEvento="/tipoEvento/",actividad = actividad,lenActividad = len(actividad))

@app.route('/registrarMovimiento/', methods=['GET','POST'])
def registrarMovimiento():
    datos = [{"concepto":"Evento01","detalle":"Evento1",'monto':'05/05/21'}]

    return render_template('SCV-B0XRegistrarMovimiento.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point")

# ============================== login ============================== #

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

if __name__ == '__main__':
    app.run()
