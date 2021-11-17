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

    activities = db.relationship('Actividad', backref='evento', lazy=True)

class Actividad(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(30))
    descripcion = db.Column(db.String(100))
    consideraciones = db.Column(db.String(100))
    fechaInicio = db.Column(db.Date)
    fechaFin = db.Column(db.Date)
    ponente = db.Column(db.String(50))

    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    
loremLipsum='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum aliquet metus, sed hendrerit quam maximus ut. Sed cursus mi ut ligula dapibus elementum. Proin vel finibus arcu. Ut tincidunt ornare velit, vel lacinia lectus. Fusce ante mi, posuere nec feugiat at, suscipit non magna. Ut facilisis ultricies enim, in rutrum sapien tempus vehicula. In imperdiet dolor sed volutpat sodales'''

def crearFecha(date, format):
    str = 'No definida'
    if date != None:
        str = date.strftime(format)
    return str

def crearFechaHora(date, hour):
    datehour = date + ' ' + hour
    date_time_obj = datetime.strptime(datehour, '%d/%m/%Y %H:%M:%S')

# ============================== eventos ============================== #

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
    session.pop('idEvento', None)
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
    
    listaAct = []
    actividades = Actividad.query.filter_by(idEvento = session['idEvento'])
    for actividad in actividades:
        listaAct.append({
            "id":actividad.id,
            "nombre":actividad.nombre
        })

    return render_template(
        'SCV-B01MenuEvento.html',
        estado = miEvento.estado,
        descripcion = miEvento.descripcion,
        lugar = miEvento.lugar,
        tipoEvento = miEvento.tipo,
        actividad = listaAct,
        lenActividad = len(listaAct),
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

@app.route('/lanzarEvento/', methods=['POST'])
def lanzarEvento():
    return "aqui lanzaria evento y redirecciona a la pagina de este evento"

@app.route('/cargarEjemplos', methods=['GET'])
def cargarEjemplos():
    aEvnt = Evento(
        nombre = "Primer Ejemplo",
        tipo = "Congreso",
        descripcion = "Super Descripcion",
        lugar = "Arequipa",
    )
    bEvnt = Evento(
        nombre = "Segundo Ejemplo",
        tipo = "Danza",
        descripcion = "Nueva Descripcion",
        lugar = "Cusco",
    )
    cEvnt = Evento(
        nombre = "Tercer Ejemplo",
        tipo = "Charla",
        descripcion = "Otra Descripcion",
        lugar = "Lima",
    )
    dEvnt = Evento(
        nombre = "Cuarto Ejemplo",
        tipo = "Congreso",
        descripcion = "Mas Descripcion",
        lugar = "Lima",
    )
    eEvnt = Evento(
        nombre = "Quinto Ejemplo",
        tipo = "Simposio",
        descripcion = "ZZZZZZZZZZZZZZZZZZ",
        lugar = "Arequipa",
    )
    db.session.add(aEvnt)
    db.session.add(bEvnt)
    db.session.add(cEvnt)
    db.session.add(dEvnt)
    db.session.add(eEvnt)
    db.session.commit()
    return redirect(url_for('index'), code=302)

@app.route('/registrarMovimiento/', methods=['GET','POST'])
def registrarMovimiento():
    datos = [{"concepto":"Evento01","detalle":"Evento1",'monto':'05/05/21'}]

    return render_template('SCV-B0XRegistrarMovimiento.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point")

# ============================== actividades ============================== #

@app.route('/crearActividad', methods=['POST'])
def crearActividad():
    nuevaActividad = Actividad(
        nombre = 'Nombre de la Actividad',
        tipo = 'Tipo de actividad',
        descripcion = 'Breve descripcion',
        consideraciones = 'Consideraciones para asistentes',
        ponente = 'Expositor',
        fechaInicio = datetime.datetime.utcnow(),
        fechaFin = datetime.datetime.utcnow(),
        idEvento = session['idEvento']
    )

    db.session.add(nuevaActividad)
    db.session.commit()
        
    nuevaActividadDict = {
        "id": nuevaActividad.id,
        "nombreActividad": "Nombre de la Actividad",
        "descripcion": "Breve descripcion",
        "consideraciones": "Consideraciones para asistentes",
        "tipoActividad": "Tipo de actividad",
        "expositor": "Expositor",
        "fechaInicio": crearFecha(nuevaActividad.fechaInicio,"%Y-%m-%d"),
        "fechaFin": crearFecha(nuevaActividad.fechaFin,"%Y-%m-%d"),
        "horaInicio": "00:00",
        "horaFin": "23:59"
    }

    return render_template(
        'SCV-B02MenuActividad.html',
        actividad = nuevaActividadDict,
        estado = "Borrador",
        ambientes=[], lenAmbientes = 0,
        materiales=[], lenMateriales = 0)

@app.route('/eliminarActividad/<id>', methods=['GET','POST'])
def eliminarActividad(id):
    miActividad = Actividad.query.get_or_404(id)
    db.session.delete(miActividad)
    db.session.commit()
    return redirect(url_for('evento',idEvento=session['idEvento']), code=302)


@app.route('/modificarActividad/<id>', methods=['POST'])
def modificarActividad(id):
    print(request.form.get('Nombre de la Actividad'))

    # miActividad = Actividad.query.get_or_404(id)

    # miActividad.nombre = request.form.get('Nombre de la Actividad')
    # miActividad.tipo = request.form.get('Tipo de actividad')
    # miActividad.descripcion = request.form.get('Breve descripcion')
    # miActividad.consideraciones = request.form.get('Consideraciones para asistentes')
    # miActividad.ponente = request.form.get('Expositor')
    # miActividad.fechaInicio = crearFechaHora(1,2)
    # miActividad.fechaFin = crearFechaHora(1,2)

    # db.session.commit()
    
    return redirect(url_for('actividad',id=id), code=302)

@app.route('/actividad/<id>', methods=['GET','POST'])
def actividad(id):
    miActividad = Actividad.query.get_or_404(id)
    datos ={
        "id":miActividad.id,
        "nombreActividad":miActividad.nombre,
        "descripcion":miActividad.descripcion,
        "consideraciones":miActividad.consideraciones,
        "tipoActividad":miActividad.tipo,
        "expositor":miActividad.ponente,
        "fechaInicio":crearFecha(miActividad.fechaInicio,"%Y-%m-%d"),
        "fechaFin":crearFecha(miActividad.fechaFin,"%Y-%m-%d"),
        "horaInicio":crearFecha(miActividad.fechaInicio,"%H:%M"),
        "horaFin":crearFecha(miActividad.fechaFin,"%H:%M")
    }

    ambientes = [{"nombre":"Amb1","id":"Amb1"},{"nombre":"Amb2","id":"Amb2"}]
    materiales = [{"nombre":"Mat1","id":"Mat1"},{"nombre":"Mat2","id":"Mat2"}]
    estadoEvento="Borrador"
    return render_template('SCV-B02MenuActividad.html',actividad=datos,estado = estadoEvento,ambientes=ambientes,lenAmbientes = len(ambientes),materiales=materiales,lenMateriales = len(materiales),idEvento=1)

@app.route('/verActividad/<id>', methods=['GET','POST'])
def verActividad(id):
    #lo mismo pero el estado de evento es Ver
    datos ={
        "id":"A03",
        "nombreActividad":"Documental bailando bajo la lluvia",
        "descripcion":"El Director vendrá acompañado de Haley, un artista muy famoso y su grupo, que mostrará el documental bailando bajo la luvia",
        "consideraciones":"En caso de que llueva de verdad, hay que ir al comedor usando cascos de seguridad",
        "tipoActividad":"Concierto",
        "expositor":"Haley",
        "fechaInicio":"2000-09-30",#yyyy-MM-dd
        "fechaFin":"2000-09-30",
        "horaInicio":"05:00",#HH:mm:ss
        "horaFin":"05:30",
    }
    ambientes = [{"nombre":"Amb1","id":"Amb1"},{"nombre":"Amb2","id":"Amb2"}]
    materiales = [{"nombre":"Mat1","id":"Mat1"},{"nombre":"Mat2","id":"Mat2"}]
    estadoEvento="Ver"
    return render_template('SCV-B02MenuActividad.html',actividad=datos,estado = estadoEvento,ambientes=ambientes,lenAmbientes = len(ambientes),materiales=materiales,lenMateriales = len(materiales))

# ============================== ambiente ============================== #
@app.route('/eliminarAmbiente/<id>', methods=['GET','POST'])
def eliminarAmbiente(id):
    return "elimino ambiente"

@app.route('/crearAmbiente', methods=['GET','POST'])
def crearAmbiente():
    return "<html>Crear ambiente aqui</html>"

# ============================== material ============================== #
@app.route('/eliminarMaterial/<id>', methods=['GET','POST'])
def eliminarMaterial(id):
    return "elimino material"


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

#ambientes
@app.route('/modificarAmbiente', methods=['POST'])
def modificarAmbiente():
    #recibe id a travez del form
    return "modificar ambiente"

#
if __name__ == '__main__':
    app.run()
