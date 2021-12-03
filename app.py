from markupsafe import escape
from models import *
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

@app.route('/listaEventos')
def listaEventos():
    usuario_evento = Usuario_Evento.query.filter_by(idUsuario = session['idUsuario'])
    usuario = Usuario.query.get_or_404(session['idUsuario'])
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
    return render_template('SCV-B10VisualizarListaEventos.html', nombreUsuario=usuario.nombre,contenido=datos,tipoUsuario="Admin",nombreEvento="Our Point",notShow=True)

@app.route('/seleccionarevento/', methods=['POST'])
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
        idUsuario = session['idUsuario'],
        estaInscrito = False
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
        "general":balanceGeneral,
        "ingresos":balanceIngreso,
        "egresos":balanceEgreso
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

@app.route('/nuevoIngreso/', methods=['POST'])
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


@app.route('/nuevoEgreso/', methods=['POST'])
def nuevoEgreso():
    miNuevoEgreso = Movimiento(
        nombre = request.form.get('concepto'),
        tipo = 'Egreso',
        factura = 'F12345',
        detalle = request.form.get('detalle'),
        monto = request.form.get('monto'),
        idEvento = session['idEvento']
    )

    db.session.add(miNuevoEgreso)
    db.session.commit()
      
    return redirect(url_for('movimiento'), code=302)
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
            if 'eventoReg' in session:
                registrarUsuario(user.id)
                return '<h1>Ya estas registrado en el evento</h1><a href="/">Regresar</a>'
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
            return render_template('Login.html',alerta=miAlerta,tipoUsuario='Visitante')
    else:
        return render_template('Login.html',tipoUsuario='Visitante')

def registrarUsuario(id):
    nuevo_inscrito = Usuario_Evento(
        idEvento = session['eventoReg'],
        idUsuario = id,
        estaInscrito = False
    )
    session.pop('eventoReg', None)
    session['idUsuario'] = id # login automatico
    session['tipoUsuario'] = 'Participante'
    db.session.add(nuevo_inscrito)
    db.session.commit()

@app.route('/signup')
def register():
    profesion = [
        {"value":"ING","texto":"Ingeniero"},
        {"value":"ARQ","texto":"Arquitecto"},
        {"value":"SIS","texto":"Sistemas"}
    ]
    alert = {
        'existe':False,
        'mensaje':''
    }
    return render_template('Signup.html',tipoUsuario='Visitante', profesion=profesion, lenProfesion=len(profesion),msg_alerta=alert)

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
    # registro en el evento
    if 'eventoReg' in session:
        registrarUsuario(nuevo_usuario.id)
        return '<h1>Ya estas registrado en el evento</h1><a href="/">Regresar</a>'
    return redirect(url_for('login'))

@app.route('/')#para probar la vista de participante
def index():
    var_notShow = False
    if 'tipoUsuario' not in session:
        session['tipoUsuario'] = 'Visitante'
    else:
        if session['tipoUsuario'] == 'Administrador' :
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
    return render_template('SCV-B03SeleccionarEvento.html',nombreUsuario=nom_usuario,tipoUsuario=session['tipoUsuario'],evento=renderEventos,arrSizes=arrSizes,size=size,notShow=var_notShow)

@app.route('/registrarse/<id>')
def registrarse(id):
    # si ya esta logeado
    if 'idUsuario' in session and session['tipoUsuario'] == 'Participante':
        # buscar si ya esta inscrito en el evento
        usuario_evento = Usuario_Evento.query.filter_by(
            idUsuario = session['idUsuario'],
            idEvento = id
        ).first()
        if usuario_evento == None:
            session['eventoReg'] = id
            registrarUsuario(session['idUsuario'])
        return '<h1>Ya estas registrado en el evento</h1><a href="/">Regresar</a>'
    session['eventoReg'] = id
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
    #.
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
    return render_template('SCV-B01VisualizarEvento.html',
        notShow=True,
        evento=evento,
        actividad=actividades,
        lenActividad=len(actividades),
        categoria_paquete=categoria_paquete,
        categorias=categorias,
        paquetes=paquetes,
        paquete=paquete,
        categoria=categoria,
        disponible=mePuedoInscribir,
        tipoUsuario = session['tipoUsuario']
    )

@app.route('/logout/')
def logout():
    session.pop('idUsuario', None)
    session.pop('tipoUsuario', None)
    session.pop('idEvento', None)
    return redirect(url_for('index'))

@app.route('/navbar/<tipoUsuario>')
def navbar(tipoUsuario):
    #Visitante, Colaborador, Caja, Admin
    return render_template("Layout.html",tipoUsuario=tipoUsuario)

# ================== gestionar inscripciones ==================
@app.route('/obtenerNombreActividades/', methods=['GET','POST'])
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

@app.route('/crearCategoria/', methods=['POST'])
def crearCategoria():
    nombreCategoria = request.form.get('nombreCategoria')

    if nombreCategoria != None:
        nombreCategoria = Categoria(
            idEvento = session['idEvento'],
            nombre = request.form.get('nombreCategoria'),
            monto = 0
        )

        db.session.add(nombreCategoria)
        db.session.commit()

    return redirect(url_for(gestionar_inscripcion))

@app.route('/crearPaquete/', methods=['POST'])
def crearPaquete():

    nombrePaquete = request.form.get('nombrePaquete')

    if nombrePaquete != None:   
        nuevoPaquete = Paquete(
            idEvento = session['idEvento'],
            nombre = request.form.get('nombrePaquete'),
            monto = 0
        )

        db.session.add(nuevoPaquete)
        db.session.commit()

    return redirect(url_for(gestionar_inscripcion))

@app.route('/gestionar_inscripcion/', methods=['GET','POST'])
def gestionar_inscripcion():
    miEvento = Evento.query.get_or_404(session['idEvento'])
    descuento = miEvento.prcntjDscnto #numero del 1 al 100
    #fechas del evento
    fecha = {
        "Preinscripción" : miEvento.fechaPreInscripcion,
        "Inscripciones": miEvento.fechaPreInscripcion,
        "Descuento": descuento,
    }

    #categoriaPaquete
    misCategorias = miEvento.categorias
    dictCategorias = []
    dictPaquetes = []
    for categoria in misCategorias:
        dictCategorias.append({
            categoria.nombre
        })
    misPaquetes = miEvento.paquetes
    for paquete in misPaquetes:
        dictPaquetes.append({
            paquete.nombre
        })

    categoria_paquete = {}
    for cat in dictCategorias:
        categoria_paquete[cat] = {}
        for pqt in dictPaquetes:
            categoria_paquete[cat][pqt] = 5

    #Datos provisionales para probar, no llenar, reusaremos la tabla con otros datos
    general = [#la numeracion de 1 a n
        {"numero":1,"nombre":"Dino","apellido":"dino","documento":"156","tipoDocumento":"Nadie lo sabee"}
    ]
    preinscritos = [#numeracion igual a la de general
        {"numero":1,"nombre":"Dino","apellido":"dino","documento":"156","tipoDocumento":"Nadie lo sabee"}
    ]
    inscritos = [
        {"numero":1,"nombre":"Dino","apellido":"dino","documento":"156","tipoDocumento":"Nadie lo sabee"}
    ]

    lens={
        "general" : len(general),
        "preinscritos" : len(preinscritos),
        "inscritos" : len(inscritos)
    }

    return render_template(
        "SCV-B09GestionarConfiguracionInscripcion.html",
        idEvento=session['idEvento'],
        estado=miEvento.estado,
        general=general,
        preinscritos=preinscritos,
        inscritos=inscritos,
        len=lens,
        nombreEvento="nombreEvento",
        categoria_paquete=categoria_paquete,
        categorias=len(dictCategorias),
        paquetes=len(dictPaquetes),
        paquete=dictPaquetes,
        categoria=dictCategorias,
        tipoUsuario = "",
        fecha = fecha,
        descuento = descuento
    )

# ================== gestion administrativa ==================
@app.route('/gestionarUsuario/', methods=['POST','GET'])
def gestionarUsuario():
    if request.method == 'POST':
        nuevoUsuario = Usuario(
            tipoUsuario = request.form.get('tipoUsuario'),
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
        "SCV-B08CrearUsuario.html",
        idEvento=session['idEvento'],
        general=listaUsuarios,
        len = lens
    )

@app.route('/listaEventosParticipante/', methods=['POST','GET'])
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
        "SCV-B20VisualizarListaEventosParticipante.html",
        general=listaIdEventos,
        len = lens,
        tipoUsuario = session['tipoUsuario']
    )

@app.route('/porTransferencia/', methods=['POST','GET'])
def porTransferencia():
    return "yei"

@app.route('/porEfectivo/', methods=['POST','GET'])
def porEfectivo():
    return "yei"

@app.route('/validarInscripcion', methods=['POST','GET'])
def validarInscripcion():
    lens={
        "general":1
    }
    return render_template(
        "SCV-B07ValidarInscripcion.html",
        general = [
            {"codigoPago":"EST", "categoria":"Estudiante", "paquete":"Estudiante Starter Pack", "monto":70}
        ],#codigoPago, categoria, presupuesto, monto
        lens = lens,
        tipoUsuario = session['tipoUsuario']
    )

@app.route('/asistencia', methods=['POST','GET'])
def asistencia():
    return "Registra asistencia de: "

@app.route('/materiales', methods=['POST','GET'])
def materiales():

    ambiente = [
        {"id":"AMBAMB","texto":"Ambientito"}
    ]
    lens={
        "Ambiente":len(ambiente)
        
    }
    return render_template(
        "SCV-B16EntregaMaterial.html",
        ambiente=ambiente,
        len=lens
    )

@app.route('/obtenerCodigoQR', methods=['POST','GET'])
def obtenerCodigoQR():
    return "obtenerCodigoQR de: "

@app.route('/colaborador/', methods=['POST','GET'])
def colaborador():
    print("poner en el index")
    general=[
        {"nombreEvento":"Evento 1"}
    ]
    len = {
        "general":1,
    }
    return render_template(
        "SCV-B16-17PaginaColaborador.html",
        general=general,
        len=len,
        idEvento=1,
        tipoUsuario = "Colaborador"
    )

@app.route('/obtenerActividadesAmbiente/', methods=['POST','GET'])
def obtenerActividadesAmbiente():
    actividad = [
        {"id":"ACAC","nombre":"Actividad 1"}
    ]
    response ={
        "actividad":actividad
    }
    
    return response

@app.route('/obtenerParticipantesActividadAmbiente/', methods=['POST','GET'])
def obtenerParticipantesActividadAmbiente():
    participante = [
        {"participante":"Pepe","materialAsignado":"PC","idParticipante":"1"}
    ]
    response ={
        "participante":participante
    }
    
    return response



if __name__ == '__main__':
    app.run()
