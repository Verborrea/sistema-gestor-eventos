from datetime import datetime
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
    tipoUsuario = db.Column(db.String(10), nullable=False)
    tipodoc = db.Column(db.String(10), nullable=True)
    doc = db.Column(db.String(10), nullable=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    profesion = db.Column(db.String(30), nullable=True)

    usuarios_eventos = db.relationship('Usuario_Evento', backref='usuario', lazy=True)

class Usuario_Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(130), nullable=False)
    lugar = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default="Borrador")
    fechaCreacion = db.Column(db.Date, default=datetime.utcnow)
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

    actividades = db.relationship('Actividad', backref='evento', lazy=True)
    usuarios_eventos = db.relationship('Usuario_Evento', backref='evento', lazy=True)
    movimientos = db.relationship('Movimiento', backref='evento', lazy=True)

class Actividad(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(30))
    descripcion = db.Column(db.String(130))
    consideraciones = db.Column(db.String(100))
    fechaInicio = db.Column(db.DateTime)
    fechaFin = db.Column(db.DateTime)
    ponente = db.Column(db.String(50))

    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    ambientes = db.relationship('Ambiente', backref='actividad', lazy = True)
    materiales = db.relationship('Material', backref='actividad', lazy = True)

class Ambiente(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.String(100))
    aforo = db.Column(db.Integer, nullable = False)

    idActividad = db.Column(db.Integer, db.ForeignKey('actividad.id'), nullable=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.String(100))
    stockInicial = db.Column(db.Integer, nullable = False)
    costoUnitario = db.Column(db.Float, nullable = False)

    idActividad = db.Column(db.Integer, db.ForeignKey('actividad.id'), nullable=False)
    
class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    factura = db.Column(db.String(30), nullable=False)
    detalle = db.Column(db.String(90))
    cantidad = db.Column(db.Integer)
    monto = db.Column(db.Float, nullable = False)
    
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)

   

    
loremLipsum='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum aliquet metus, sed hendrerit quam maximus ut. Sed cursus mi ut ligula dapibus elementum. Proin vel finibus arcu. Ut tincidunt ornare velit, vel lacinia lectus. Fusce ante mi, posuere nec feugiat at, suscipit non magna. Ut facilisis ultricies enim, in rutrum sapien tempus vehicula. In imperdiet dolor sed volutpat sodales'''

@app.context_processor
def utility_processor():
    def modulo(a,b):
        return a%b
    return dict(modulo=modulo)

def crearFecha(date, format):
    str = 'No definida'
    if date != None:
        str = date.strftime(format)
    return str

def crearFechaHora(date, hour):
    datehour = date + ' ' + hour + ':00'
    date_time_obj = datetime.strptime(datehour, '%Y-%m-%d %H:%M:%S')
    return date_time_obj

def breakArr(array,division):
    arr =[]
    sizes = []
    for i in range(0,len(array),division):
        arr.append([])
        sizes.append(0)
        for j in range(i,i+division):
            if j<len(array):
                arr[i//division].append(array[j])
                sizes[i//division]=sizes[i//division]+1
    return arr,sizes, len(sizes)

# ============================== eventos ============================== #

@app.route('/listaEventos')
def listaEventos():
    usuario_evento = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario'])
    listaIdEventos = []
    for usr_evt in usuario_evento:
        listaIdEventos.append(usr_evt.idEvento)
    datos = []
    # eventos = Evento.query.all()
    for idEvt in listaIdEventos:
        evento = Evento.query.get_or_404(idEvt)
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
    return render_template('SCV-B10VisualizarListaEventos.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point")

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
        'SCV-B10MenuEvento.html',
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

    nuevoEventoUsuario = Usuario_Evento(
        idEvento = nuevoEvento.id,
        idUsuario = session['idUsuario']
    )

    db.session.add(nuevoEventoUsuario)
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
    miEvento = Evento.query.get_or_404(session['idEvento'])
    miEvento.estado = 'Inscripciones'
    try:
        db.session.commit()
    except:
        print("ERROR al lanzar Evento " + miEvento.nombre)
    return redirect(url_for('evento',idEvento=miEvento.id), code=302)

@app.route('/cargarEjemplos', methods=['GET'])
def cargarEjemplos():
    aEvnt = Evento(
        nombre = "IntArtificial",
        tipo = "Congreso",
        descripcion = "Super Descripcion",
        lugar = "Arequipa",
        estado = "Inscripciones",
    )
    bEvnt = Evento(
        nombre = "Festidanza",
        tipo = "Danza",
        descripcion = "Nueva Descripcion",
        lugar = "Cusco",
        estado = "Borrador",
    )
    cEvnt = Evento(
        nombre = "IoT",
        tipo = "Charla",
        descripcion = "Otra Descripcion",
        lugar = "Lima",
        estado = "En Curso",
    )
    dEvnt = Evento(
        nombre = "Porcesamiento de lenguaje",
        tipo = "Congreso",
        descripcion = "Mas Descripcion",
        lugar = "Lima",
        estado = "Finalizado",
    )
    eEvnt = Evento(
        nombre = "Liderazgo",
        tipo = "Simposio",
        descripcion = "Aprendizaje continuo",
        lugar = "Arequipa",
        estado = "Borrador",
    )
    db.session.add(aEvnt)
    db.session.add(bEvnt)
    db.session.add(cEvnt)
    db.session.add(dEvnt)
    db.session.add(eEvnt)
    db.session.commit()
    return redirect(url_for('index'), code=302)

# ============================== movimiento ============================== #

@app.route('/registrarMovimiento/', methods=['GET','POST'])
def registrarMovimiento():
    datos = [{"concepto":"Evento01","detalle":"Evento1",'monto':'05/05/21'}]

    return render_template('SCV-B0XRegistrarMovimiento.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point")

#genera problemas al compilar (comentar route movimiento hasta que no este culminado)
@app.route('/movimiento/', methods=['GET','POST'])
def movimiento():
    general = []
    ingresos = []
    egresos = []
    movimientos = Movimiento.query.filter_by(idEvento = session['idEvento'])
    numeroIngreso = 0
    numeroEgreso = 0
    numeroGeneral = 0
    balanceIngreso = 0
    balanceEgreso = 0
    balanceGeneral = 0
    for movimiento in movimientos:
        numeroGeneral += 1
        if movimiento.tipo == 'Ingreso':
            numeroIngreso += 1
            ingresos.append({
                "numero":numeroIngreso,
                "concepto":movimiento.nombre,
                "monto":movimiento.monto
            })
            balanceIngreso += movimiento.monto
        else:
            numeroEgreso += 1
            egresos.append({
                "numero":numeroEgreso,
                "numeroRecibo":movimiento.factura,
                "concepto":movimiento.nombre,
                "monto":movimiento.monto,
                "cantidad":movimiento.cantidad
            })
            balanceEgreso += movimiento.monto
        general.append({
            "numero":numeroGeneral,
            "concepto":movimiento.nombre,
            "tipo":movimiento.tipo,
            "monto":movimiento.monto,
        })
        balanceGeneral += movimiento.monto

    balance={
        "general":balanceIngreso,
        "ingresos":balanceEgreso,
        "egresos":balanceGeneral
    }
    lens={
        "general" : len(general),
        "ingresos" : len(ingresos),
        "egresos" : len(egresos)
    }
    return render_template('SCV-B04-B05RegistrarMovimiento.html',
        general=general,
        ingresos=ingresos,
        egresos=egresos,
        balance=balance,
        len=lens
    )

@app.route('/nuevoEgreso/', methods=['POST'])
def nuevoEgreso():
    return "creado"

@app.route('/nuevoIngreso/', methods=['POST'])
def nuevoIngreso():
    return "creado"

# ============================== actividades ============================== #

@app.route('/crearActividad', methods=['POST'])
def crearActividad():
    nuevaActividad = Actividad(
        nombre = 'Nombre de la Actividad',
        tipo = 'Tipo de actividad',
        descripcion = 'Breve descripcion',
        consideraciones = 'Consideraciones para asistentes',
        ponente = 'Expositor',
        fechaInicio = datetime.utcnow(),
        fechaFin = datetime.utcnow(),
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

    miActividad = Actividad.query.get_or_404(id)

    miActividad.nombre = request.form.get('nombreActividad')
    miActividad.tipo = request.form.get('tipoActividad')
    miActividad.descripcion = request.form.get('descripcionActividad')
    miActividad.consideraciones = request.form.get('consideracionesAsistentes')
    miActividad.ponente = request.form.get('expositor')
    miActividad.fechaInicio = crearFechaHora(request.form.get('fechaInicio'),request.form.get('horaInicio'))
    miActividad.fechaFin = crearFechaHora(request.form.get('fechaFin'),request.form.get('horaFin'))

    db.session.commit()
    
    return redirect(url_for('actividad',id=id), code=302)

@app.route('/actividad/<id>', methods=['GET','POST'])
def actividad(id):
    miEvento = Evento.query.get_or_404(session['idEvento'])
    estadoEvento = miEvento.estado

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

    listaAmbientes = []
    ambientes = Ambiente.query.filter_by(idActividad = id)
    for ambiente in ambientes:
        listaAmbientes.append({
            "nombre":ambiente.nombre,
            "id":ambiente.id
        })
    
    listaMateriales = []
    materiales = Material.query.filter_by(idActividad = id)
    for material in materiales:
        listaMateriales.append({
            "nombre":material.nombre,
            "id":material.id
        })

    return render_template(
        'SCV-B02MenuActividad.html',
        actividad=datos,
        estado = estadoEvento,
        ambientes=listaAmbientes,
        lenAmbientes = len(listaAmbientes),
        materiales=listaMateriales,
        lenMateriales = len(listaMateriales),
        idEvento=session['idEvento'])

# ============================== AMBIENTE ============================== #
@app.route('/<idActividad>/eliminarAmbiente/<idAmbiente>', methods=['GET','POST'])
def eliminarAmbiente(idActividad,idAmbiente):
    miAmbiente = Ambiente.query.get_or_404(idAmbiente)
    db.session.delete(miAmbiente)
    db.session.commit()
    return redirect(url_for('actividad',id=idActividad), code=302)

@app.route('/<idActividad>/modificarAmbiente', methods=['GET','POST'])
def modificarAmbiente(idActividad):
    id = request.form.get('idAmbiente')
    miAmbiente = Ambiente.query.get_or_404(id)

    miAmbiente.nombre = request.form.get('nombreAmbiente')
    miAmbiente.tipo = request.form.get('tipoAmbiente')
    miAmbiente.descripcion = request.form.get('descripcionBreve')
    miAmbiente.aforo = request.form.get('aforo')

    db.session.commit()
    return redirect(url_for('actividad',id=idActividad), code=302)

@app.route('/<idActividad>/crearAmbiente', methods=['GET','POST'])
def crearAmbiente(idActividad):
    nuevoAmbiente = Ambiente(
        nombre = request.form.get('nombreAmbiente'),
        tipo = request.form.get('tipoAmbiente'),
        descripcion = request.form.get('descripcionBreve'),
        aforo = request.form.get('aforo'),
        idActividad = idActividad
    )
    db.session.add(nuevoAmbiente)
    db.session.commit()

    return redirect(url_for('actividad',id=idActividad), code=302)

@app.route('/obtenerAmbiente/<idAmb>', methods=['GET','POST'])
def obtenerAmbiente(idAmb):
    miAmbiente = Ambiente.query.get_or_404(idAmb)
    ambienteDict = {
        "idAmbiente" : idAmb,
        "nombreAmbiente" : miAmbiente.nombre,
        "tipoAmbiente" : miAmbiente.tipo,
        "descripcionBreve" : miAmbiente.descripcion,
        "aforo" : miAmbiente.aforo
    }
    return json.dumps(ambienteDict)

# ============================== material ============================== #
@app.route('/<idActividad>/eliminarMaterial/<idMaterial>', methods=['GET','POST'])
def eliminarMaterial(idActividad,idMaterial):
    miMaterial = Material.query.get_or_404(idMaterial)
    db.session.delete(miMaterial)
    db.session.commit()
    return redirect(url_for('actividad',id=idActividad), code=302)

@app.route('/<idActividad>/modificarMaterial', methods=['POST'])
def modificarMaterial(idActividad):
    id = request.form.get('idMaterial')
    miMaterial = Material.query.get_or_404(id)

    miMaterial.nombre = request.form.get('nombreMaterial')
    miMaterial.tipo = request.form.get('tipoMaterial')
    miMaterial.descripcion = request.form.get('descripcionBreve')
    miMaterial.stockInicial = request.form.get('stockInicial')
    miMaterial.costoUnitario = request.form.get('costoUnitario')

    db.session.commit()
    return redirect(url_for('actividad',id=idActividad), code=302)

@app.route('/<idActividad>/crearMaterial', methods=['GET','POST'])
def crearMaterial(idActividad):
    nuevoMaterial = Material(
        nombre = request.form.get('nombreMaterial'),
        tipo = request.form.get('tipoMaterial'),
        descripcion = request.form.get('descripcionBreve'),
        stockInicial = request.form.get('stockInicial'),
        costoUnitario = request.form.get('costoUnitario'),
        idActividad = idActividad
    )
    db.session.add(nuevoMaterial)
    db.session.commit()

    return redirect(url_for('actividad',id=idActividad), code=302)

@app.route('/obtenerMaterial/<idMat>', methods=['GET','POST'])
def obtenerMaterial(idMat):
    miMaterial = Material.query.get_or_404(idMat)
    materialDict = {
        "idMaterial" : idMat,
        "nombreMaterial" : miMaterial.nombre,
        "tipoMaterial" : miMaterial.tipo,
        "descripcionBreve" : miMaterial.descripcion,
        "stockInicial" : miMaterial.stockInicial,
        "costoUnitario" : miMaterial.costoUnitario
    }
    return json.dumps(materialDict)

# ============================== login ============================== #

@app.route('/profile/<username>')
def profile(username):
    return render_template('usuario.html', usuario=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(
            email = request.form.get('usuario'),
            password = request.form.get('contra')
        ).first()

        if user:
            session['tipoUsuario'] = user.tipoUsuario
            if session['tipoUsuario'] == 'Admin':
                session['idUsuario'] = user.id
                return redirect(url_for('listaEventos'))
            return redirect(url_for('index'))
        else:
            return 'Usuario no existente'
    else:
        return render_template('login.html',tipoUsuario='Visitante')

@app.route('/signup')
def register():
    return render_template('signup.html',tipoUsuario='Visitante')

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
        tipoUsuario = 'Admin',
        password = request.form.get('contra'),
        nombre = request.form.get('nombre'),
        email = request.form.get('correo'),
        tipodoc = request.form.get('tipo_doc'),
        doc = request.form.get('doc'),
        profesion = request.form.get('profesion')
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    print(Usuario.query.all())
    return redirect(url_for('login'))

@app.route('/')#para probar la vista de participante
def index():
    session['tipoUsuario'] = 'Visitante'
    eventos = []
    info = Evento.query.all()
    for evento in info:
        if evento.estado == 'Inscripciones':
            eventos.append({
                "id" : evento.id,
                "title" : evento.nombre,
                "summary" : evento.descripcion
            })
    renderEventos, arrSizes, size = breakArr(eventos,3)
    #en el render template deberia quitarse tipoUsuario Visitante y guardarlo en la sesion
    return render_template('SCV-B03SeleccionarEvento.html',tipoUsuario='Visitante',evento=renderEventos,arrSizes=arrSizes,size=size)

@app.route('/registrarse/<id>')
def registrarse(id):
    return "te estas registrando en: "+id

@app.route('/visualizarEvento/<id>')
def verEvento(id):
    miEvento = Evento.query.get_or_404(id)

    evento = {
        "id": id,
        "title": miEvento.nombre,
        "descripcion": miEvento.descripcion,
        "lugar": miEvento.lugar,
        "fechas": miEvento.fechaCierreInscripcion
    }

    actividades = []

    datos = Actividad.query.filter_by(
            idEvento = id
        )
    for actividad in datos:
        actividades.append({
            "nombre": actividad.nombre,
            "duracion": actividad.tipo,
            "ponente": actividad.ponente
        })

    actividad =[
        {
            "nombre":"Actividad1",
            "duracion":"1 anio",
            "ponente":"FulanoPerez"
        },
        {
            "nombre":"Actividad2",
            "duracion":"1/2 anio",
            "ponente":"FulanoJuarez"
        }
    ]
    paquete=["Paquete 1","Paquete 2","Paquete 3"]
    categoria=["Categoria 1","Categoria 2"]
    categoria_paquete = {
        "Categoria 1":{
            "Paquete 1":5,
            "Paquete 2":10,
            "Paquete 3":7,
        },
        "Categoria 2":{
            "Paquete 1":6,
            "Paquete 2":11,
            "Paquete 3":6,
        }
    }
    categorias = 2
    paquetes = 3
    lenActividad = len(actividades)
    return render_template('SCV-B01VisualizarEvento.html',
        evento=evento,
        actividad=actividades,
        lenActividad=len(actividades),
        categoria_paquete=categoria_paquete,
        categorias=categorias,
        paquetes=paquetes,
        paquete=paquete,
        categoria=categoria
        )

@app.route('/logout/')
def logout():
    return "Cierra sesion y manda a lista eventos de visitante"

@app.route('/navbar/<tipoUsuario>')
def navbar(tipoUsuario):
    #Visitante, Colaborador, Caja, Admin
    return render_template("Layout.html",tipoUsuario=tipoUsuario)

if __name__ == '__main__':
    app.run()
