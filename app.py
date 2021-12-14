from flask.templating import render_template_string
from markupsafe import escape
from werkzeug.wrappers import response
from models import *
from sendEmail import *
from datetime import datetime
from transacciones import *
from datetime import date

import json

loremLipsum='''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec vestibulum aliquet metus, sed hendrerit quam maximus ut. Sed cursus mi ut ligula dapibus elementum. Proin vel finibus arcu. Ut tincidunt ornare velit, vel lacinia lectus. Fusce ante mi, posuere nec feugiat at, suscipit non magna. Ut facilisis ultricies enim, in rutrum sapien tempus vehicula. In imperdiet dolor sed volutpat sodales'''

@app.context_processor
def utility_processor():
    return dict()

def crearFecha(date, format):
    str = 'No definida'
    if date != None:
        str = date.strftime(format)
    return str

def crearFechaHora(date, hour):
    datehour = date + ' ' + hour + ':00'
    date_time_obj = datetime.strptime(datehour, '%Y-%m-%d %H:%M:%S')
    return date_time_obj

def dateFromStr(str):
    date_time_obj = datetime.strptime(str, '%Y-%m-%d')
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

def to_dict(row):
    if row is None: return None
    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict

# =============== creacion de un administrador primigenio =============== #

usuario_admin = Usuario.query.filter_by(
    username = 'admin',
    tipoUsuario = 'Admin',
    password = 'admin',
    nombre = 'Administrador',
    email = 'admin@sge.com'
).first()

if usuario_admin:
    print("Admin exists")
else:
    nuevo_usuario = Usuario(
        username = 'admin',
        tipoUsuario = 'Admin',
        password = 'admin',
        nombre = 'Administrador',
        email = 'admin@sge.com'
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

# ============================== eventos ============================== #
@app.route('/listaEventos', methods=['POST','GET'])
def listaEventos():
    usuario_evento = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario'])
    usuario = Usuario.query.get_or_404(session['idUsuario'])
    listaIdEventos = []
    for usr_evt in usuario_evento:
        listaIdEventos.append(usr_evt.idEvento)
    datos = []
    plantilla = []
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
            'estadoEvento':evento.estado,
            'tipoEvento':evento.tipo,
        })
        if evento.plantilla == True:
            plantilla.append(datos[-1])
    session.pop('idEvento', None)

    lens = {
        "general":len(datos),
        "plantilla":len(plantilla),
    }
   
    return render_template('SCV-B01VisualizarListaEventosAdmin.html', nombreUsuario=usuario.nombre,general=datos,len = lens,plantilla=plantilla,tipoUsuario="Admin",nombreEvento="Our Point",notShow=True)

@app.route('/seleccionarevento', methods=['POST'])
def seleccionarevento():
    if request.method == 'POST':
        id = request.form.get('selection')
        if id==None:
            return redirect(url_for('listaEventos'), code=302)
    if session['tipoUsuario'] == 'Caja':
        return redirect(url_for('validarInscripcion'), code=302)
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

    # actualizar fecha inicial y final
    if actividades:
        fechaMin = miEvento.fechaInicio
        fechaMax = miEvento.fechaFin
        for actividad in actividades:
            if not fechaMin:
                fechaMin = actividad.fechaInicio.date()
            if not fechaMax:
                fechaMax = actividad.fechaFin.date()
            if actividad.fechaInicio.date() < fechaMin:
                fechaMin = actividad.fechaInicio.date()
            if actividad.fechaFin.date() > fechaMax:
                fechaMax = actividad.fechaFin.date()
        miEvento.fechaInicio = fechaMin
        miEvento.fechaFin = fechaMax
        db.session.commit()

    return render_template(
        'SCV-B01MenuEventoAdmin.html',
        idEvento = session['idEvento'],
        estado = miEvento.estado,
        descripcion = miEvento.descripcion,
        lugar = miEvento.lugar,
        tipoEvento = miEvento.tipo,
        actividad = listaAct,
        lenActividad = len(listaAct),
        nombreEvento = miEvento.nombre)

@app.route('/crearEvento', methods=['POST'])
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
        idUsuario = session['idUsuario'],
        estaInscrito = False
    )

    db.session.add(nuevoEventoUsuario)
    db.session.commit()

    return redirect(url_for('evento',idEvento=nuevoEvento.id), code=302)

@app.route('/modificarEvento', methods=['POST'])
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

@app.route('/obtenerPlantillas', methods=['POST','GET'])
def obtenerPlantillas():

    plantillas = []
 
    usuario_evento = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario'])
    listaIdEventos = []
    for usr_evt in usuario_evento:
        listaIdEventos.append(usr_evt.idEvento)

    for idEvt in listaIdEventos:
        evento = Evento.query.get_or_404(idEvt)
        plantillas.append({
            "id":evento.id,
            "Nombre":evento.nombre,
            "Fecha":crearFecha(evento.fechaInicio,"%d/%m/%Y"),
            "TipoEvento":evento.tipo
        })

    return json.dumps(plantillas)

@app.route('/crearEventoPlantilla', methods=['POST'])
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

@app.route('/lanzarEvento', methods=['POST'])
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

# @app.route('/registrarMovimiento', methods=['GET','POST'])
# def registrarMovimiento():
#     datos = [{"concepto":"Evento01","detalle":"Evento1",'monto':'05/05/21'}]

#     return render_template('SCV-B0XRegistrarMovimiento.html', nombreUsuario='Joe',contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point")

#genera problemas al compilar (comentar route movimiento hasta que no este culminado)
@app.route('/movimiento', methods=['GET','POST'])
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
            balanceGeneral += movimiento.monto
        else:
            numeroEgreso += 1
            egresos.append({
                "numero":numeroEgreso,
                "numeroRecibo":movimiento.factura,
                "concepto":movimiento.nombre,
                "monto":movimiento.monto
            })
            balanceEgreso += movimiento.monto
            balanceGeneral -= movimiento.monto
        general.append({
            "numero":numeroGeneral,
            "concepto":movimiento.nombre,
            "tipo":movimiento.tipo,
            "monto":movimiento.monto
        })

    balance={
        "general":balanceGeneral,
        "ingresos":balanceIngreso,
        "egresos":balanceEgreso
    }
    lens={
        "general" : len(general),
        "ingresos" : len(ingresos),
        "egresos" : len(egresos)
    }
    return render_template('SCV-B09RegistrarMovimiento.html',
        idEvento = session['idEvento'],
        general=general,
        ingresos=ingresos,
        egresos=egresos,
        balance=balance,
        len=lens
    )

@app.route('/nuevoIngreso', methods=['POST'])
def nuevoIngreso():
    miNuevoIngreso = Movimiento(
        nombre = request.form.get('nombre'),
        tipo = 'Ingreso',
        factura = request.form.get('factura'),
        detalle = request.form.get('detalle'),
        monto = request.form.get('monto'),
        idEvento = session['idEvento']
    )

    db.session.add(miNuevoIngreso)
    db.session.commit()
      
    return redirect(url_for('movimiento'), code=302)


@app.route('/nuevoEgreso', methods=['POST'])
def nuevoEgreso():
    miNuevoEgreso = Movimiento(
        nombre = request.form.get('concepto'),
        tipo = 'Egreso',
        factura = request.form.get('factura'),
        detalle = request.form.get('detalle'),
        monto = request.form.get('monto'),
        idEvento = session['idEvento']
    )

    db.session.add(miNuevoEgreso)
    db.session.commit()
      
    return redirect(url_for('movimiento'), code=302)
# ============================== actividades ============================== #

@app.route('/crearActividad', methods=['GET','POST'])
def crearActividad():
    if request.method == 'POST':
        nuevaActividad = Actividad(
            nombre = request.form.get('nombreActividad'),
            tipo = request.form.get('tipoActividad'),
            descripcion = request.form.get('descripcionActividad'),
            consideraciones = request.form.get('consideracionesAsistentes'),
            ponente = request.form.get('expositor'),
            fechaInicio = crearFechaHora(request.form.get('fechaInicio'),request.form.get('horaInicio')),
            fechaFin = crearFechaHora(request.form.get('fechaFin'),request.form.get('horaFin')),
            idEvento = session['idEvento']
        )
        db.session.add(nuevaActividad)
        db.session.commit()

        return redirect(url_for('actividad',id=nuevaActividad.id), code=302)

    # mostrar form con valores x defecto para crear actividad
    nuevaActividadDict = {
        "nombreActividad": "Nombre de la Actividad",
        "descripcion": "Breve descripcion",
        "consideraciones": "Consideraciones para asistentes",
        "tipoActividad": "Tipo de actividad",
        "expositor": "Expositor",
        "fechaInicio": crearFecha(datetime.now(),"%Y-%m-%d"),
        "fechaFin": crearFecha(datetime.now(),"%Y-%m-%d"),
        "horaInicio": "07:00",
        "horaFin": "22:30"
    }

    return render_template(
        'SCV-B02MenuActividad.html',
        actividad = nuevaActividadDict,
        estado = "Borrador",
        idEvento = session['idEvento'],
        ambientes=[], lenAmbientes = 0,
        materiales=[], lenMateriales = 0,
        nuevaActividad = True)

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
        idEvento=session['idEvento'],
        nuevaActividad = False)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(
            email = request.form.get('usuario'),
            password = request.form.get('contra')
        ).first()

        if user:
            session['tipoUsuario'] = user.tipoUsuario
            session['idUsuario'] = user.id
            if ('eventoReg' in session) and user.tipoUsuario == 'Participante':
                usuario_evento = Usuario_Evento.query.filter_by(
                    idUsuario = user.id,
                    idEvento = session['eventoReg']
                ).first()
                if usuario_evento == None:
                    nom_Evento = registrarUsuario(session['idUsuario'],session['cat_pqt'])
                    return render_template("Mensaje.html",tipoUsuario = 'Participante',Titulo = "Registro Exitoso",Mensaje="Ya estas registrado en el evento "+nom_Evento)
            if session['tipoUsuario'] == 'Admin':
                return redirect(url_for('listaEventos'))
            return redirect(url_for('index'))
        else:
            miAlerta ={
                "tipo":"failiure",
                "title":"Error",
                "texto":"Usuario no encontrado",
                "masTexto":"Por favor, ingrese un correo o contraseña válidos.",#opcional
            }
            return render_template('SCV-B04Login.html',alerta=miAlerta,tipoUsuario='Visitante')
    else:
        return render_template('SCV-B04Login.html',tipoUsuario='Visitante')

def registrarUsuario(id,idCat_Paq):
    nuevo_inscrito = Usuario_Evento(
        idEvento = session['eventoReg'],
        idUsuario = id,
        estaInscrito = False,
        idCategoria_Paquete = idCat_Paq
    )

    monEvent = Evento.query.get(session['eventoReg'])
    
    session.pop('eventoReg', None)
    session.pop('cat_pqt', None)
    session['idUsuario'] = id # login automatico
    session['tipoUsuario'] = 'Participante'
    db.session.add(nuevo_inscrito)
    db.session.commit()

    return monEvent.nombre

@app.route('/signup')
def register():
    profesion = [
        {"value":"ING","texto":"Ingeniero"},
        {"value":"ARQ","texto":"Arquitecto"},
        {"value":"SIS","texto":"Sistemas"},
        {"value":"EST","texto":"Estudiante"}
    ]
    alert = {
        'existe':False,
        'mensaje':''
    }
    # categoriad = [
    #     {"id":"CAT","texto":"Estudiante"},
    #     {"id":"CAT2","texto":"Profesor"},
    # ]
    # lens ={
    #     "Categoria":len(categoriad),
    # }
    return render_template('SCV-B20Signup.html',tipoUsuario='Visitante', profesion=profesion, lenProfesion=len(profesion),msg_alerta=alert)

@app.route('/create-user', methods=['POST'])
def create_user():
    alert = {
        'existe':False,
        'mensaje':''
    }
    # registro en la pagina
    user = Usuario.query.filter_by(username = request.form.get('usuario')).first()
    mail = Usuario.query.filter_by(email = request.form.get('correo')).first()
    if user:
        alert['existe'] = True
        alert['mensaje'] = 'Nombre de Usuario ya existente'
        return render_template('Signup.html',tipoUsuario='Visitante',msg_alerta=alert)
    if mail:
        alert['existe'] = True
        alert['mensaje'] = 'El correo ingresado ya tiene una cuenta asociada'
        return render_template('Signup.html',tipoUsuario='Visitante',msg_alerta=alert)
    nuevo_usuario = Usuario(
        username = request.form.get('usuario'),
        tipoUsuario = 'Participante',
        password = request.form.get('contra'),
        nombre = request.form.get('nombre'),
        email = request.form.get('correo'),
        tipodoc = request.form.get('tipo_doc'),
        doc = request.form.get('doc'),
        profesion = request.form.get('profesion')
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    sedEmail(request.form.get('correo'))
    
    # registro en el evento
    if 'eventoReg' in session:
        nom_Evento = registrarUsuario(nuevo_usuario.id,session['cat_pqt'])
        return render_template("Mensaje.html",tipoUsuario = 'Participante',Titulo = "Registro Exitoso",Mensaje="Ya estas registrado en el evento "+nom_Evento)
    return redirect(url_for('login'))

@app.route('/')#para probar la vista de participante
def index():
    var_notShow = False
    if 'eventoReg' in session:
        session.pop('eventoReg', None)
    if 'tipoUsuario' not in session:
        session['tipoUsuario'] = 'Visitante'
    else:
        if session['tipoUsuario'] == 'Admin' :
            var_notShow = True
    eventos = []
    info = Evento.query.all()
    nom_usuario = 'no existe'
    if 'idUsuario' in session:
        usuario = Usuario.query.get_or_404(session['idUsuario'])
        nom_usuario = usuario.nombre
    for evento in info:
        if evento.estado == 'Inscripciones':
            eventos.append({
                "id" : evento.id,
                "title" : evento.nombre,
                "summary" : evento.descripcion
            })
    renderEventos, arrSizes, size = breakArr(eventos,3)
    print(var_notShow)
    return render_template('SCV-B05SeleccionarEventoParticipante.html',nombreUsuario=nom_usuario,tipoUsuario=session['tipoUsuario'],evento=renderEventos,arrSizes=arrSizes,size=size,notShow=var_notShow)

@app.route('/registrarse/<id>', methods=['POST'])
def registrarse(id):
    
    categoria = request.form.get('categoria')
    paquete = request.form.get('paquete')
    categoria_paquete = Categoria_Paquete.query.filter_by(
            idCategoria = categoria,
            idPaquete = paquete
        ).first()
    
    # si ya esta logeado
    if 'idUsuario' in session and session['tipoUsuario'] == 'Participante':
        # buscar si ya esta inscrito en el evento
        usuario_evento = Usuario_Evento.query.filter_by(
            idUsuario = session['idUsuario'],
            idEvento = id
        ).first()
        if usuario_evento == None:
            session['eventoReg'] = id
            session['cat_pqt'] = categoria_paquete.id
            nom_Evento = registrarUsuario(session['idUsuario'],categoria_paquete.id)
            return render_template("Mensaje.html",tipoUsuario = 'Participante',Titulo = "Registro Exitoso",Mensaje="Ya estas registrado en el evento "+nom_Evento)
    session['eventoReg'] = id
    session['cat_pqt'] = categoria_paquete.id
    return redirect(url_for('login'))

@app.route('/visualizarEvento/<id>')
def verEvento(id):
    miEvento = Evento.query.get_or_404(id)
    mePuedoInscribir = True
    if 'idUsuario' in session:
        usuario_evento = Usuario_Evento.query.filter_by(
            idUsuario = session['idUsuario'],
            idEvento = id
        ).first()
        if usuario_evento:
            mePuedoInscribir = False
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
        delta = actividad.fechaFin - actividad.fechaInicio
        duracion = str(delta.seconds//3600) + ' hora'
        if duracion != '1 hora':
            duracion += 's'
        actividades.append({
            "nombre": actividad.nombre,
            "duracion": duracion,
            "ponente": actividad.ponente
        })

    paquete = []
    categoria = []
    categoria_paquete_mtrx = []
    cat_dict = []


    misPaquetes = miEvento.paquetes
    misCategorias = miEvento.categorias

    for pqt_reg in misPaquetes:
        paquete.append(pqt_reg.nombre)
    
    for cat_reg in misCategorias:
        categoria.append(cat_reg.nombre)
        cat_dict.append({
            "id":cat_reg.id,
            "texto":cat_reg.nombre
        })

    cat_number = 0
    for cat in misCategorias:
        categoria_paquete_mtrx.append([])
        for pqt in misPaquetes:
            misCat_Paq = Categoria_Paquete.query.filter_by(
                idPaquete = pqt.id,
                idCategoria = cat.id
            ).first()
            categoria_paquete_mtrx[cat_number].append(misCat_Paq.monto)
        cat_number += 1

    lens ={
        "Categoria":len(categoria),
    }
    return render_template('SCV-B07VisualizarEventoParticipante.html',
        notShow=True,
        evento=evento,
        actividad=actividades,
        lenActividad=len(actividades),
        categoria_paquete=categoria_paquete_mtrx,
        categorias=len(categoria),
        paquetes=len(paquete),
        paquete=paquete,
        categoria=categoria,
        cat=cat_dict,
        disponible=mePuedoInscribir,
        len=lens,
        tipoUsuario = session['tipoUsuario']
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/navbar/<tipoUsuario>')
def navbar(tipoUsuario):
    #Visitante, Colaborador, Caja, Admin
    return render_template("Layout.html",tipoUsuario=tipoUsuario)

# ================== gestionar inscripciones ==================
@app.route('/obtenerNombreActividades', methods=['GET','POST'])
def obtenerNombreActividades():
    miEvento = Evento.query.get_or_404(session['idEvento'])
    misActividades = miEvento.actividades
    actividades = []
    for act in misActividades:
        actividades.append({
            "id":act.id,
            "nombre":act.nombre
        })
    return json.dumps(actividades)

@app.route('/crearCategoria', methods=['POST'])
def crearCategoria():
    nombreCategoria = request.form.get('nombreCategoria')

    if nombreCategoria != None:
        nuevaCategoria = Categoria(
            idEvento = session['idEvento'],
            nombre = request.form.get('nombreCategoria')
        )
        db.session.add(nuevaCategoria)

        paquetes = Paquete.query.filter_by(idEvento=session['idEvento'])
        for paq in  paquetes:
            nuevo_cat_paq = Categoria_Paquete(
                idCategoria = nuevaCategoria.id,
                idPaquete = paq.id,
                monto = 0
            )
            db.session.add(nuevo_cat_paq)

        db.session.commit()

    return redirect(url_for('gestionar_inscripcion'))

@app.route('/crearPaquete', methods=['POST'])
def crearPaquete():

    nombrePaquete = request.form.get('nombrePaquete')

    if nombrePaquete != None:   
        nuevoPaquete = Paquete(
            idEvento = session['idEvento'],
            nombre = request.form.get('nombrePaquete')
        )
        db.session.add(nuevoPaquete)

        categorias = Categoria.query.filter_by(idEvento=session['idEvento'])
        for cat in  categorias:
            nuevo_cat_paq = Categoria_Paquete(
                idPaquete = nuevoPaquete.id,
                idCategoria = cat.id,
                monto = 0
            )
            db.session.add(nuevo_cat_paq)

        db.session.commit()

    return redirect(url_for('gestionar_inscripcion'))

@app.route('/guardar-precios', methods=['POST'])
def guardar_precios():
    miEvento = Evento.query.get_or_404(session['idEvento'])
    misCategorias = miEvento.categorias
    misPaquetes = miEvento.paquetes
    
    for cat in misCategorias:
        for pqt in misPaquetes:
            cat_pqt = Categoria_Paquete.query.filter_by(
                idPaquete = pqt.id,
                idCategoria = cat.id
            ).first()
            cat_pqt.monto = request.form.get(str(cat.id) + '&' + str(pqt.id))

    db.session.commit()
    return redirect(url_for('gestionar_inscripcion'))

@app.route('/gestionar_inscripcion', methods=['GET','POST'])
def gestionar_inscripcion():
    miEvento = Evento.query.get_or_404(session['idEvento'])
    if request.method == 'POST':
        miEvento.fechaAprtrInscripcion = dateFromStr(request.form.get('cierrePreInscripcion'))
        miEvento.fechaCierreInscripcion = dateFromStr(request.form.get('CierreInscripciones'))
        miEvento.fechaLmtDscnto = dateFromStr(request.form.get('fechaLimiteDescuento'))
        miEvento.prcntjDscnto = request.form.get('descuento')

        db.session.commit()

    # fechas del evento
    fecha = {
        "Preinscripcion" : crearFecha(miEvento.fechaAprtrInscripcion,"%Y-%m-%d"),
        "Inscripciones": crearFecha(miEvento.fechaCierreInscripcion,"%Y-%m-%d"),
        "Descuento": crearFecha(miEvento.fechaLmtDscnto,"%Y-%m-%d")
    }
    #numero del 1 al 100
    descuento = miEvento.prcntjDscnto
    
    #categoriaPaquete
    misCategorias = miEvento.categorias
    misPaquetes = miEvento.paquetes
    listCategorias = []
    listPaquetes = []

    #  Ids categoria paquete #
    ids_categoria = []
    ids_paquete= []

    for categoria in misCategorias:
        ids_categoria.append(categoria.id)
        listCategorias.append(categoria.nombre)

    for paquete in misPaquetes:
        ids_paquete.append(paquete.id)
        listPaquetes.append(paquete.nombre)

    categoria_paquete_mtrx = []
    cat_number = 0
    for cat in misCategorias:
        categoria_paquete_mtrx.append([])
        for pqt in misPaquetes:
            misCat_Paq = Categoria_Paquete.query.filter_by(
                idPaquete = pqt.id,
                idCategoria = cat.id
            ).first()
            categoria_paquete_mtrx[cat_number].append(misCat_Paq.monto)
        cat_number += 1

    #  Usuarios en el Evento #
    idUsuariosG = []
    idUsuariosPre = []
    idUsuariosIns = []
    
    usuarioEventos = Usuario_Evento.query.filter_by(idEvento = session['idEvento'])
    for ue in usuarioEventos:
        if ue.estaInscrito == True: 
            idUsuariosIns.append(ue.idUsuario)
        elif ue.estaInscrito == False:
            idUsuariosPre.append(ue.idUsuario)
        idUsuariosG.append(ue.idUsuario)

    #  Listado de Usuarios General #
    general = []
    usuarios = Usuario.query.filter(Usuario.id.in_(idUsuariosG)).all()
    for usuario in usuarios:
        if usuario.tipoUsuario == 'Participante':
            general.append({
                "numero":usuario.id,
                "nombre":usuario.nombre,
                "documento":usuario.doc,
                "tipoDocumento":usuario.tipodoc
            })

    #  Listado de Usuarios PreInscritos #
    preinscritos = []
    usuarios = Usuario.query.filter(Usuario.id.in_(idUsuariosPre)).all()
    for usuario in usuarios:
        if usuario.tipoUsuario == 'Participante':
            preinscritos.append({
                "numero":usuario.id,
                "nombre":usuario.nombre,
                "documento":usuario.doc,
                "tipoDocumento":usuario.tipodoc
            })
    
    #  Listado de Usuarios Inscritos #
    inscritos = []
    usuarios = Usuario.query.filter(Usuario.id.in_(idUsuariosIns)).all()
    for usuario in usuarios:
        preinscritos.append({
            "numero":usuario.id,
            "nombre":usuario.nombre,
            "documento":usuario.doc,
            "tipoDocumento":usuario.tipodoc
        })
        
    lens={
        "general" : len(general),
        "preinscritos" : len(preinscritos),
        "inscritos" : len(inscritos)
    }

    return render_template(
        "SCV-B03GestionarConfiguracionInscripcion.html",
        idEvento=miEvento.id, estado=miEvento.estado, nombreEvento=miEvento.nombre,
        general=general, preinscritos=preinscritos, inscritos=inscritos,
        len=lens,
        categoria_paquete=categoria_paquete_mtrx,
        categorias=len(listCategorias),
        paquetes=len(listPaquetes),
        paquete=listPaquetes,
        categoria=listCategorias,
        tipoUsuario = session['idUsuario'],
        fecha = fecha,
        descuento = descuento,
        ids_categoria=ids_categoria,
        ids_paquete=ids_paquete
    )

@app.route('/eliminarCategoria/<id>', methods=['POST','GET'])
def eliminarCategoria(id): 
    #Eliminar Categoria en Categoria-Paquete
    CategoriaPaquete = Categoria_Paquete.query.filter_by(idCategoria=id)
    
    for cat_pqt in CategoriaPaquete:
        db.session.delete(cat_pqt)
    
    #Eliminar Categoria
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    
    db.session.commit()
    
    return redirect(url_for('gestionar_inscripcion'))
                                       
@app.route('/eliminarPaquete/<id>', methods=['POST','GET'])
def eliminarPaquete(id):
    #Eliminar Paquete en Categoria-Paquete#
    CategoriaPaquete = Categoria_Paquete.query.filter_by(idPaquete=id)
    
    for cat_pqt in CategoriaPaquete:
        db.session.delete(cat_pqt)
    
    #Eliminar Paquete
    paquete = Paquete.query.get(id)
    db.session.delete(paquete)

    db.session.commit()
    
    return redirect(url_for('gestionar_inscripcion'))

# ================== gestion administrativa ==================

@app.route('/gestionarUsuario', methods=['POST','GET'])
def gestionarUsuario():
    if request.method == 'POST':
        nuevoUsuario = Usuario(
            tipoUsuario = request.form.get('profesion'),
            username = request.form.get('nombreUsuario'),
            password = request.form.get('contrasenia'),
            nombre = request.form.get('nombreCompleto'),
            email = request.form.get('correo')
        )
        db.session.add(nuevoUsuario)
        db.session.commit()
        
        nuevoUsuarioEvento = Usuario_Evento(
            idUsuario = nuevoUsuario.id,
            idEvento = session['idEvento'],
            idCategoria_Paquete = '0',
            estaInscrito = False
        )
        db.session.add(nuevoUsuarioEvento)
        db.session.commit()
        
    idUsuarios = []
    usuarioEventos = Usuario_Evento.query.filter_by(idEvento = session['idEvento'])
    for ue in usuarioEventos:
        idUsuarios.append(ue.idUsuario)

    listaUsuarios = []
    usuarios = Usuario.query.filter(Usuario.id.in_(idUsuarios)).all()
    for usuario in usuarios:
        permisoUsuario = ""
        if usuario.tipoUsuario == "Admin":
            permisoUsuario = "Todos"
        else:
            permisoUsuario = "Restringido"
        
        if usuario.tipoUsuario != "Participante":
            listaUsuarios.append({
                "tipoUsuario":usuario.tipoUsuario,
                "nombre":usuario.nombre,
                "correo":usuario.email,
                "permisos":permisoUsuario
            })

    lens={
        'general' : len(listaUsuarios)
    }
    return render_template(
        "SCV-B19CrearUsuario.html",
        idEvento=session['idEvento'],
        general=listaUsuarios,
        len = lens
    )

@app.route('/listaEventosParticipante', methods=['POST','GET'])
def listaEventosParticipante():
    usuarioEventos = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario'])
    idEventos = []
    for ue in usuarioEventos:
        idEventos.append(ue.idEvento)
    listaIdEventos = []
    for idEvento in idEventos:
        evento = Evento.query.get_or_404(idEvento)
        usuarioEvento = Usuario_Evento.query.filter_by(
            idUsuario = session['idUsuario'],
            idEvento = evento.id).first()
        estaInscrito = "No"
        if usuarioEvento.estaInscrito == True:
            estaInscrito = "Sí"
        listaIdEventos.append({
            "idEvento":evento.id,
            "nombre":evento.nombre,
            "estado":evento.estado,
            "fechaInicioEvento":evento.fechaInicio.strftime("%d/%m/%Y"),
            "estaInscrito": estaInscrito
        })
    lens={
        'general' : len(listaIdEventos)
    }
    return render_template(
        "SCV-B06VisualizarListaEventosParticipante.html",
        general=listaIdEventos,
        len = lens,
        tipoUsuario = session['tipoUsuario']
    )

# ================== validacion de inscripcion de participante ==================
@app.route('/porTransferencia', methods=['POST','GET'])
def porTransferencia():
    '''Agrega un nuevo movimiento del tipo transferencia para la validacion de la inscripcion
        y actualiza el estado del participante en el evento como INSCRITO'''
    #Agregar nuevo movimiento del tipo validacion de inscripcion - transferencia
    nuevoMovimiento = Movimiento(
        tipo = "Transferencia",
        nombre = "Validacion de inscripcion",
        factura = request.form.get('numeroOperacion'),
        monto = request.form.get('monto'),
        idEvento = session['idEvento']
    )
    db.session.add(nuevoMovimiento)
    db.session.commit()
    #Actualizar estado de participante
    usuarioParticipante = request.form.get('usuarioParticipante')
    miParticipante = Usuario.query.filter_by(username = usuarioParticipante, tipoUsuario = "Participante").first()
    idParticipante = miParticipante.id

    miUsuarioEvento = Usuario_Evento.query.filter_by(idUsuario = idParticipante, idEvento = session['idEvento']).first()
    miUsuarioEvento.estaInscrito = True
    db.session.commit()

    return redirect(url_for('validarInscripcion'), code=302)

@app.route('/porEfectivo', methods=['POST','GET'])
def porEfectivo():
    '''Agrega un nuevo movimiento del tipo efectivo para la validacion de la inscripcion
        y actualiza el estado del participante en el evento como INSCRITO'''
    #Agregar nuevo movimiento del tipo validacion de inscripcion - transferencia
    nuevoMovimiento = Movimiento(
        tipo = "Efectivo",
        nombre = "Validacion de inscripcion",
        factura = "EF",
        monto = request.form.get('monto'),
        idEvento = session['idEvento']
    )
    db.session.add(nuevoMovimiento)
    db.session.commit()
    #Actualizar estado de participante
    usuarioParticipante = request.form.get('usuarioParticipante')
    miParticipante = Usuario.query.filter_by(username = usuarioParticipante, tipoUsuario = "Participante").first()
    idParticipante = miParticipante.id

    miUsuarioEvento = Usuario_Evento.query.filter_by(idUsuario = idParticipante, idEvento = session['idEvento']).first()
    miUsuarioEvento.estaInscrito = True
    db.session.commit()

    return redirect(url_for('validarInscripcion'), code=302)

@app.route('/validarInscripcion', methods=['POST','GET'])
def validarInscripcion():
    '''Devuelve la lista de aquellos movimientos correspondientes al tipo de validaciones de inscripciones
        realizadas por los participantes.'''
    movimientos = Movimiento.query.filter_by(idEvento = session['idEvento'])
    listaMovimientos = []
    for movimiento in movimientos:
        if movimiento.nombre == "Validacion de inscripcion":
            listaMovimientos.append({
                "codigoPago":movimiento.factura,
                "categoria":movimiento.tipo,
                "monto":movimiento.monto
            })
    lens={
        "general":len(listaMovimientos)
    }
    return render_template(
        "SCV-B08ValidarInscripcion.html",
        general = listaMovimientos,
        lens = lens,
        tipoUsuario = session['tipoUsuario']
    )

@app.route('/registraAsistencia', methods=['POST','GET'])
def registraAsistencia():
    return "Registra asistencia de: "

@app.route('/materiales', methods=['POST','GET'])
def materiales():

    #Obtener id del evento
    usuarios_eventos = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario']).first()
    id_evento = usuarios_eventos.idEvento

    #Obtener ids de las actividades del evento
    actividades = Actividad.query.filter_by(idEvento = id_evento)
    listaIdActividades = []
    for actividad in actividades:
        listaIdActividades.append(actividad.id)

    #Obtener ids de ambientes
    listaAmbientes = []
    ambientes = Ambiente.query.filter(Ambiente.id.in_(listaIdActividades)).all()
    for ambiente in ambientes:
        listaAmbientes.append({
            "id":ambiente.id,
            "texto":ambiente.nombre
        })
    
    lens={
        "Ambiente":len(listaAmbientes)
        
    }
    return render_template(
        "SCV-B11EntregaMaterial.html",
        ambiente=listaAmbientes,
        len=lens
    )

@app.route('/obtenerCodigoQR', methods=['POST','GET'])
def obtenerCodigoQR():
    return "obtenerCodigoQR de: "

@app.route('/colaborador', methods=['POST','GET'])
def colaborador():
    print("poner en el index")
    general=[
        {"nombreEvento":"Evento 1"}
    ]
    len = {
        "general":1,
    }
    return render_template(
        "PaginaColaborador.html",
        general=general,
        len=len,
        idEvento=1,
        tipoUsuario = "Colaborador"
    )

@app.route('/obtenerActividadesAmbiente/<idAmb>', methods=['POST','GET'])
def obtenerActividadesAmbiente(idAmb):
    
    listaIdsActividades = []
    ambientes = Ambiente.query.filter_by(id = idAmb)
    for ambiente in ambientes:
        listaIdsActividades.append(ambiente.idActividad)
    
    listaActividades = []
    actividades = Actividad.query.filter(Actividad.id.in_(listaIdsActividades))
    for actividad in actividades:
        listaActividades.append({
            "id":actividad.id,
            "nombre":actividad.nombre
        })
    
    response ={
        "actividad":listaActividades
    }
    
    return response

@app.route('/obtenerCategoriasPaquete/<idCat>', methods=['POST','GET'])
def obtenerCategoriasPaquete(idCat):
    
    CategoriaPaquete = Categoria_Paquete.query.filter_by(idCategoria = idCat)
    idPaquetes = []
    for cp in CategoriaPaquete:
        idPaquetes.append(cp.idPaquete)
        
    paquetes = Paquete.query.filter(Paquete.id.in_(idPaquetes)).all()
    
    listaPaquetes = []
    for paquete in paquetes:
        listaPaquetes.append({
            "id":paquete.id,
            "nombre":paquete.nombre
        })
        
    response ={
        "paquete":listaPaquetes
    }
    return response


@app.route('/obtenerParticipantesActividadAmbiente/<idAct>', methods=['POST','GET'])
def obtenerParticipantesActividadAmbiente(idAct):
    ''' Devuelve la relacion de participantes inscritos y que hayan registrado su asistencia para un ambiente
        acompaniado del material que se le debe entregar dependiendo de la actividad elegida'''
    idAmbiente = ""
    ambientes = Ambiente.query.filter_by(idActividad = idAct)
    for ambiente in ambientes:
        idAmbiente = ambiente.id
    
    listaIdUsuarios = []
    idUsuarios = Asistencia.query.filter_by(idAmbiente = idAmbiente)
    for iU in idUsuarios:
        listaIdUsuarios.append(iU.idUsuario)

    listaParticipantes = []
    participantes = Usuario.query.filter(Usuario.id.in_(listaIdUsuarios)).all()
    for participante in participantes:
        if participante.tipoUsuario == "Participante":
            listaParticipantes.append({
                "id": participante.id,
                "nombre":participante.nombre
            })
    
    materialesEntregar = ""
    materiales = Material.query.filter_by(idActividad = idAct)
    for material in materiales:
        if material.tipo == "Material participantes":
            materialesEntregar = material.nombre

    listaParticipantesMaterial = []
    for i in range(len(listaParticipantes)):
        listaParticipantesMaterial.append({
            "participante":listaParticipantes[i].get("nombre"),
            "materialAsignado":materialesEntregar,
            "idParticipante":listaParticipantes[i].get("id")
        })
    
    participante = [
        {"participante":"Pepe","materialAsignado":materialesEntregar,"idParticipante":"1"}
    ]
    response ={
        "participante":participante #listaParticipantesMaterial
    }
    
    return response

@app.route('/nosotros', methods=['GET'])
def nosotros():
    return render_template("Nosotros.html",tipoUsuario="Visitante")

# ================== funcionalidades para COLABORADOR ==================
@app.route('/asistencia', methods=['GET','POST'])
def asistencia():
    '''Generar registro de asistencia por participante y ambiente programado para cada actividad del evento'''
    #Obtener id del evento
    usuarios_eventos = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario']).first()
    id_evento = usuarios_eventos.idEvento

    #Obtener ids de las actividades del evento
    actividades = Actividad.query.filter_by(idEvento = id_evento)
    listaIdActividades = []
    for actividad in actividades:
        listaIdActividades.append(actividad.id)

    #Obtener ids de ambientes
    listaAmbientes = []
    ambientes = Ambiente.query.filter(Ambiente.id.in_(listaIdActividades)).all()
    for ambiente in ambientes:
        listaAmbientes.append({
            "id":ambiente.id,
            "texto":ambiente.nombre
        })
    
    lens={
        "Ambiente":len(listaAmbientes)
    }
    #Obtener datos de la asistencia
    ahora = datetime.now()
    horaAhora = ahora.hour
    diaAhora = ahora.day
    mesAhora = ahora.strftime("%b")
    turno = ""
    if horaAhora < 12:
        turno = "Mañana"
    elif horaAhora < 18:
        turno = "Tarde"
    else:
        turno = "Noche"
    diaAhora = (mesAhora) + "  " + str(diaAhora)

    listaIdsUsuarios = []
    participantes_eventos = Usuario_Evento.query.filter_by(idEvento = id_evento)
    for pe in participantes_eventos:
        listaIdsUsuarios.append(pe.idUsuario)
    
    listaIdsParticipantes = []
    participantes = Usuario.query.filter(Usuario.id.in_(listaIdsUsuarios)).all()
    for participante in participantes:
        if participante.tipoUsuario == "Participante":
            listaIdsParticipantes.append(participante.id)

    asistencia ={
        "turno":turno,
        "dia":diaAhora,
        "participantes":len(listaIdsParticipantes)
    }
    codigo = {
        "rutaImagen":"qr/qrqrqr.jpg",
        "sesion":"codigoSesionAsistencia"
    }
    return render_template(
        "SCV-B12RegistrarAsistencia.html",
        tipoUsuario="Colaborador",
        ambiente=listaAmbientes,
        len=lens,
        codigo = codigo,
        asistencia=asistencia,
    )

@app.route('/obtenerParticipantesAmbienteAsistencia/<idAmb>', methods=['GET','POST'])
def obtenerParticipantesAmbienteAsistencia(idAmb):
    #idAmb #mandamos en el request
    listaIdUsuarios = []
    listaHoras = []
    
    idUsuarios = Asistencia.query.filter_by(idAmbiente = idAmb)
    for iU in idUsuarios:
        listaIdUsuarios.append(iU.idUsuario)
        listaHoras.append({
            "id":iU.id,
            "horaIng":(str(iU.fechaAsistencia.hour) + ":" + str(iU.fechaAsistenca.minute))
        })
    horasOrdenadas = sorted(listaHoras, key = lambda k : k["id"])

    listaParticipantes = []
    participantes = Usuario.query.filter(Usuario.id.in_(listaIdUsuarios)).all()
    for participante in participantes:
        if participante.tipoUsuario == "Participante":
            listaParticipantes.append({
                "id": participante.id,
                "nombre":participante.nombre
            })
    participantesOrdenados = sorted(listaParticipantes, key = lambda k : k["id"])

    listaAsistencias = []
    for i in range(len(horasOrdenadas)):
        listaAsistencias.append({
            "participante":participantesOrdenados[i].get("nombre"),
            "horaIngreso":horasOrdenadas[i].get("horaIng")
        })
    '''
    #prueba
    listaPrueba = []
    horaPrueba = [{
        "id":"1",
        "horaIng":"10:20"
    }]
    participantePrueba = [{
        "id":"1",
        "nombre":"Felipe"
    }]
    for i in range(len(horaPrueba)):
        listaPrueba.append({
            "participante":participantePrueba[i].get("nombre"),
            "horaIngreso":horaPrueba[i].get("horaIng")
        })
    
    listaEjemplo = [{
        "participante":idAmb,
        "horaIngreso":"10:50"
    }]
    '''
    response = {
        "participante":listaAsistencias
    }
    return response

@app.route('/obtenerQRAsistencia', methods=['GET'])
def obtenerQRAsistencia():
    #idAmb #mandamos en el request
    response = {
        "imgSrc":"static\qrs\CODECODE.png",
        "session":"codigoSesionTomadoAsistencia"
    }
    return response

@app.route('/terminarAsistencia', methods=['GET'])
def terminarAsistencia():
    return "Que los juegos del hambre comiencen"

# ======== REPORTES ========
@app.route('/reporteInscritos', methods=['POST','GET'])
def reporteInscritos():
    paquete = [{"id":"id","texto":"texto"}]
    
    lens ={
        "Paquete":len(paquete)
    }
    return render_template(
        "SCV-B16ReporteInscritos.html",
        paquete=paquete,
        len=lens
    )
@app.route('/obtenerQRParticipantes', methods=['POST','GET'])
def obtenerCodigoQRParticipante():
    response ={
        "fileName":"Códigos QR.pdf",
        "url" : "/static/pdfs/pdf.pdf"#no se olviden de generar el url
    }
    return response

@app.route('/obtenerCategoriasPaquetesIns', methods=['POST','GET'])
def obtenerCategoriasPaquetesIns():
    categoria=[
        {"id":"IDIDID","nombre":"puesNombre"}
    ]
    response={
        "categoria":categoria
    }
    return response

@app.route('/obtenerInscritosCategoriasPaquetes', methods=['POST','GET'])
def obtenerInscritosCategoriasPaquetes():
    inscrito=[
        {"idParticipante":"IDIDID","nombre":"puesNombre","paquete":"paquete","categoria":"categoria","fecha":"ayer"},

        {"idParticipante":"IDIDID","nombre":"puesNombre","paquete":"paquete","categoria":"categoria","fecha":"ayer"}
    ]
    response={
        "inscrito":inscrito
    }
    return response

@app.route('/obtenerQRparticipante', methods=['POST','GET'])
def obtenerQRparticipante():
    # No olvidar cambiar el qr
    participante= {"nombre":"Dino","qr":"/static/qrs/CODECODE.png"}
    return participante

@app.route('/obtenerReporteInscritos/', methods=['POST','GET'])
def obtenerReporteInscritos():
    # No olvidar generar el pdf
    response ={
        "fileName":"Reporte Inscritos.pdf",
        "url" : "/static/pdfs/pdf.pdf"
    }
    return response

# Reporte Materiales

@app.route('/reporteMateriales', methods=['POST','GET'])
def reporteMateriales():
    
    ambiente = [
        {"id":"AMBAMB","texto":"Ambientito"}
    ]
    lens={
        "Ambiente":len(ambiente)
    }
    return render_template(
        "SCV-B18reporteMateriales.html",
        ambiente=ambiente,
        len=lens
    )

@app.route('/obtenerDetalleMaterial/', methods=['POST','GET'])
def obtenerDetalleMaterial():
    # se manda el idMaterial en el request
    material = {
        "nombre":"nombre",
        "tipo":"tipo",
        "descripcion":"descripcion",
        "estado":"estado",
    }
    return material

@app.route('/obtenerReporteMaterial/', methods=['POST','GET'])
def obtenerReporteMaterial():
    # No olvidar generar el pdf
    response ={
        "fileName":"Reporte Materiales.pdf",
        "url" : "/static/pdfs/pdf.pdf"
    }
    return response

@app.route('/obtenerMaterialesActividadesAmbientes', methods=['POST','GET'])
def obtenerMaterialesActividadesAmbientes():
    material=[
        {
        "idMaterial":"IDIDID",
        "nombre":"puesNombre",
        "participante":"paquete",
        "estado":"categoria",
        "fecha":"ayer"
        }
    ]
    response={
        "material":material
    }
    return response


# Reporte Asistencia

@app.route('/reporteAsistencias', methods=['POST','GET'])
def reporteAsistencias():
    
    ambiente = [
        {"id":"AMBAMB","texto":"Ambientito"}
    ]
    lens={
        "Ambiente":len(ambiente)
    }
    return render_template(
        "SCV-B17ReporteAsistencia.html",
        ambiente=ambiente,
        len=lens
    )

@app.route('/obtenerReporteAsistencia/', methods=['POST','GET'])
def obtenerReporteAsistencia():
    # No olvidar generar el pdf
    response ={
        "fileName":"Reporte Asistencia.pdf",
        "url" : "/static/pdfs/pdf.pdf"
    }
    return response


@app.route('/obtenerAsistenciasActividadesAmbientes', methods=['POST','GET'])
def obtenerAsistenciasActividadesAmbientes():
    asistencia=[
        {
        "idAsistencia":"IDIDID",
        "nombre":"puesNombre",
        "turno":"puesTurno",
        "fecha":"En los anios 1600",
        "hora":"pan pan pan",
        "asistio":"harina!"
        }
    ]
    response={
        "asistencia":asistencia
    }
    return response

# Generar Certificados

@app.route('/reporteCertificado', methods=['POST','GET'])
def reporteCertificado():
    return render_template(
        "SCV-B14GenerarCertificados.html",
    )

@app.route('/obtenerReporteCertificados', methods=['POST','GET'])
def obtenerReporteCertificados():

    # No olvidar generar el pdf
    response ={
        "fileName":"Certificados.pdf",
        "url" : "/static/pdfs/pdf.pdf"
    }
    return response


@app.route('/obtenerParticipantesCertificados', methods=['POST','GET'])
def obtenerParticipantesCertificados():
    #Todos los particpantes de un evento
    idid = session['idEvento']
    participanteQuery = Usuario_Evento.query.filter_by(estaInscrito = True).filter_by(idEvento = idid)
    pariticipantesId = []
    for pa in participanteQuery:
        pariticipantesId.append(pa.id)

    participantes =[]
    for pa in pariticipantesId:
        participante = Usuario.query.get_or_404(pa)
        participantes.append({
            "id":participante.id,
            "nombre":participante.nombre,
        })
    response={
        "participantes":participantes
    }
    return response

# Reporte Caja

@app.route('/reporteCaja', methods=['POST','GET'])
def reporteCaja():
    #tipos son ingreso, egreso, otro son para el color de la celda
    idEvento = session['idEvento']
    movimientos = Movimiento.query.filter_by(idEvento = session['idEvento']).order_by(Movimiento.fechaCreacion) 
    #usuario = Usuario.query.get_or_404(session['idUsuario'])
    movimientosId = []
    for mov in movimientos:
        movimientosId.append(mov.id)
    cierreEvento = 0
    general = []
    for idMov in movimientosId:
        movimiento = Movimiento.query.get_or_404(idMov)
        tipo =""
        if movimiento.tipo == 'Ingreso': cierreEvento+=movimiento.monto
        else: cierreEvento -= movimiento.monto
        if cierreEvento<0: tipo = "egreso"
        else: tipo = "ingreso"
        general.append({
            'num':movimiento.id,
            'fecha':movimiento.fechaCreacion.strftime("%d/%m/%Y"),
            'cierre':cierreEvento,#dinero de la caja
            'tipo':tipo
        })
    movimientos = Movimiento.query.filter_by(idEvento = session['idEvento']).filter_by(fechaCreacion = date.today())
    movimientosId = []
    for mov in movimientos: movimientosId.append(mov.id)
    cierreDiario = 0
    for idMov in movimientosId:
        movimiento = Movimiento.query.get_or_404(idMov)
        cierreDiario+=movimiento.monto

    lens = {
        "general":len(general)
    }
    return render_template(
        "SCV-B10ReporteCaja.html",
        cierreEvento=cierreEvento,
        cierreDiario=cierreDiario,
        general=general,
        len = lens
    )

# Asistencia movil
@app.route('/qrPArticipanteAsistencia', methods=['POST','GET'])
def qrPArticipanteAsistencia():
    # No olvidar generar el pdf
    response ={
        "estado":"Rechazado",
    }
    return response

@app.route('/registrarAsistenciaMovil', methods=['POST','GET'])
def registrarAsistenciaMovil():
    
    return render_template("SCV-B13RegistrarAsistenciaMovil.html")

@app.route('/cargarTransacciones', methods=['POST','GET'])
def cargarTransacciones():
    t = Transacciones(db)
    return 'ok'

if __name__ == '__main__':
    app.run()
