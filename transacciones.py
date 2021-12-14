from models import *

def crearFechaHora(date, hour):
    datehour = date + ' ' + hour + ':00'
    date_time_obj = datetime.strptime(datehour, '%Y-%m-%d %H:%M:%S')
    return date_time_obj



class Transacciones:
    def __init__(self,bd):
        self.db=bd
        self.eventos = {}
        self.restartDB()
        self.crearUsuarios()
        self.crearEventos()
        self.session = {
            'idUsuario':'',
        }
        self.cargarEjemploFeriaLibro()
        self.cargarEjemploGame()
        self.cargarEjemploGameJam()

    def restartDB(self):
        db.drop_all()
        db.session.commit()
        db.create_all()
        db.session.commit()
        print("Vacio la BD")

    def crearUsuarios(self):
        nuevo_usuario = Usuario(
            username = 'admin',
            tipoUsuario = 'Admin',
            password = 'admin',
            nombre = 'Administrador',
            email = 'admin@sge.com')
        db.session.add(nuevo_usuario)
        nuevo_usuario = Usuario(
            username = 'caja',
            tipoUsuario = 'Caja',
            password = 'caja',
            nombre = 'Caja',
            email = 'caja@sge.com')
        db.session.add(nuevo_usuario)
        nuevo_usuario = Usuario(
            username = 'colaborador',
            tipoUsuario = 'Colaborador',
            password = 'colaborador',
            nombre = 'Colaborador',
            email = 'colaborador@sge.com')
        db.session.add(nuevo_usuario)
        db.session.commit()
        print("Creo Usuarios")
        self.user = Usuario.query.filter_by(email = 'admin@sge.com',password = 'admin').first()
        self.session={
            'idUsuario' :1
        }
        
    def crearEventos(self):
        # Crearemos uno en estado finalizado y otro en curso
        self.eventos["Game"] = Evento(
            id="1",
            nombre = "International Conference on Entertainment Computing",
            tipo = "Conference",
            descripcion = "This is the longest lasting and prime scientific conference series in the area of entertainment computing.",
            lugar = "Universidad Católica San Pablo",
            estado= 'Finalizado',
            fechaPreInscripcion = crearFechaHora("2019-11-01","09:00"),
            fechaAprtrInscripcion = crearFechaHora("2019-11-05","09:00"),
            fechaLmtDscnto = crearFechaHora("2019-11-10","09:00"),
            fechaCierreInscripcion = crearFechaHora("2019-11-11","09:00"),
            fechaInicio = crearFechaHora("2019-11-11","09:00"),
            fechaFin = crearFechaHora("2019-11-15","09:00"),
        )
        db.session.add(self.eventos["Game"])
        db.session.commit()
        nuevoEventoUsuario = Usuario_Evento(
            idEvento = self.eventos["Game"].id,
            idUsuario = self.session['idUsuario'],
            estaInscrito = False
        )
        db.session.add(nuevoEventoUsuario)


        self.eventos["libro"] = Evento(
            id="2",
            nombre = "Feria Internacional del Libro Arequipa",
            tipo = "Evento Cultural",
            descripcion = "La Feria Internacional del Libro Arequipa es el evento más importante de la ciudad en torno la industria editorial, fomento y difusión del libro y la lectura a público de todas las edades.",
            lugar = "Parque Libertad de Expresión",
            estado= 'En Curso',
            fechaPreInscripcion = crearFechaHora("2021-12-05","09:00"),
            fechaAprtrInscripcion = crearFechaHora("2021-12-10","09:00"),
            fechaLmtDscnto = crearFechaHora("2021-12-12","09:00"),
            fechaCierreInscripcion = crearFechaHora("2021-12-12","09:00"),
            fechaInicio = crearFechaHora("2021-12-13","09:00"),
            fechaFin = crearFechaHora("2021-12-23","09:00"),
        )
        
        db.session.add(self.eventos["libro"] )
        db.session.commit()
        nuevoEventoUsuario = Usuario_Evento(
            idEvento = self.eventos["libro"].id,
            idUsuario = self.session['idUsuario'],
            estaInscrito = False
        )
        db.session.add(nuevoEventoUsuario)


        self.eventos["gameJam"] = Evento(
            id="3",
            nombre = "Global Game Jam 2020",
            tipo = "Hackaton",
            descripcion = "The Global Game Jam® (GGJ) is the world's largest game jam event (game creation) taking place around the world at physical locations. Think of it as a hackathon focused on game development.",
            lugar = "Universidad Catolica San Pablo",
            estado= 'Finalizado',
            plantilla=True,
            fechaPreInscripcion = crearFechaHora("2020-01-10","09:00"),
            fechaAprtrInscripcion = crearFechaHora("2020-01-15","09:00"),
            fechaLmtDscnto = crearFechaHora("2020-01-23","09:00"),
            fechaCierreInscripcion = crearFechaHora("2020-01-23","09:00"),
            fechaInicio = crearFechaHora("2020-01-24","09:00"),
            fechaFin = crearFechaHora("2020-01-26","09:00")
        )
        db.session.add(self.eventos["gameJam"] )
        db.session.commit()
        nuevoEventoUsuario = Usuario_Evento(
            idEvento = self.eventos["gameJam"].id,
            idUsuario = self.session['idUsuario'],
            estaInscrito = True
        )
        db.session.add(nuevoEventoUsuario)
        db.session.commit()
        
        print("Creo Eventos")

    '''
    def crearActividades(self):
        self.crearActividadesEvento2()

    def crearActividadesEvento2(self):
        # Universitas
        self.crearActividadMaterialesAmbientes_E2_A1()
        self.crearActividadMaterialesAmbientes_E2_A2()
        self.crearActividadMaterialesAmbientes_E3_A1()
        '''

    def crearActividadMaterialesAmbientes_E2_A1(self):
        nuevaActividad = Actividad(
            id =3,
            nombre = "Dessigning Serious Mobile Location-based Augmented Reality Games",
            tipo = "Workshop",
            descripcion = "In this workshop we are going to see three differents proposes about Enviromental Sustainability",
            consideraciones = "Creditaje otorgado por la Escuela de Ciencia de la Computación y la Escuela de Ingenieria Ambiental de 0.25",
            ponente = "Sobah Abbas Petersen",
            fechaInicio = crearFechaHora("2019-11-11","09:00"),
            fechaFin = crearFechaHora("2019-11-11","10:00"),
            idEvento = self.eventos["Game"].id
        )
        db.session.add(nuevaActividad)
        db.session.commit()

        nuevoMaterial = Material(
            nombre = "Lapicero",
            tipo = "Entregable",
            descripcion = "Lapiceros con el logo de la Universidad Católica San Pablo",
            stockInicial = 500,
            costoUnitario = 1.5,
            idActividad = 5

        )
        db.session.add(nuevoMaterial)
        db.session.commit()

        nuevoAmbiente = Ambiente(
            nombre = "Auditorio Juan Pablo II",
            tipo = "Auditorio",
            descripcion = "El auditorio Juan Pablo II es una instalacion de la universidad con un aforo considerable",
            aforo = 250,
            idActividad = 5
        )
        db.session.add(nuevoAmbiente)
        db.session.commit()
        
    def crearActividadMaterialesAmbientes_E2_A2(self):
        nuevaActividad = Actividad(
            id =4,
            nombre = "Virtual Reality",
            tipo = "Technical Session ",
            descripcion = "In this technical session we talk about virtual reality, we are going to see four proposes with interesting applications",
            consideraciones = "Creditaje otorgado por la Escuela de Ciencia de la Computación de 0.25",
            ponente = "Polona Caserman",
            fechaInicio = crearFechaHora("2019-11-12","10:00"),
            fechaFin = crearFechaHora("2019-11-12","11:00"),
            idEvento = self.eventos["Game"].id
        )
        db.session.add(nuevaActividad)
        db.session.commit()

        nuevoMaterial = Material(
            nombre = "USB",
            tipo = "Entregable",
            descripcion = "USB de la marca Kingston de 64 GB",
            stockInicial = 100,
            costoUnitario = 20,
            idActividad = 4
        )
        db.session.add(nuevoMaterial)
        db.session.commit()

        nuevoAmbiente = Ambiente(
            nombre = "Salon de Eventos de la UCSP",
            tipo = "Salon de Eventos",
            descripcion = "El Salon de Eventos es un espacio fuera de las instalaciones de la UCSP",
            aforo = 300,
            idActividad = 4
        )
        db.session.add(nuevoAmbiente)
        db.session.commit()

    def crearActividadMaterialesAmbientes_E3_A1(self):
        nuevaActividad = Actividad(
            id =5,
            nombre = "Rules about Global Game Jam 2020",
            tipo = "Charla",
            descripcion = "In this session we are going to explain the rules about this awesome event",
            consideraciones = "Creditaje otorgado por la Escuela de Ciencia de la Computación  de 0.25",
            ponente = "ACM UCSP",
            fechaInicio = crearFechaHora("2020-01-24","09:00"),
            fechaFin = crearFechaHora("2019-01-24","10:00"),
            idEvento = self.eventos["gameJam"].id
        )
        db.session.add(nuevaActividad)
        db.session.commit()

        nuevoMaterial = Material(
            nombre = "Manual de Reglas",
            tipo = "Entregable",
            descripcion = "Manual que contiene las reglas para participar de este evento",
            stockInicial = 100,
            costoUnitario = 5,
            idActividad = 5
        )
        db.session.add(nuevoMaterial)
        db.session.commit()

        nuevoAmbiente = Ambiente(
            nombre = "Auditorio Juan Pablo II",
            tipo = "Auditorio",
            descripcion = "El auditorio Juan Pablo II es una instalacion de la universidad con un aforo considerable",
            aforo = 250,
            idActividad = 5
        )
        db.session.add(nuevoAmbiente)
        db.session.commit()

    def crearActividadMaterialesAmbientesLibro(self):
        nuevaActividad = Actividad(
            id =1,
            nombre = "Charla de Mapa Literario",
            tipo = "Charla",
            descripcion = "El Mapa Literario busca aproximarnos a la ciudad desde la literatura, vincular al lector con las obras incluso más allá de las páginas, más allá del hábito solitario y silencioso de la lectura.",
            consideraciones = "Ninguna",
            ponente = "Erika Aguirre y Madeleine Vázquez",
            fechaInicio = crearFechaHora("2021-09-24","15:00"),
            fechaFin = crearFechaHora("2021-09-24","16:00"),
            idEvento = self.eventos["libro"].id
        )
        db.session.add(nuevaActividad)
        db.session.commit()

        nuevoMaterial = Material(
            nombre = "Lapicero",
            tipo = "Entregable",
            descripcion = "Lapiceros con el logo de 'Casa de la literatura'",
            stockInicial = 200,
            costoUnitario = 1.5,
            idActividad = 1
        )
        db.session.add(nuevoMaterial)
        db.session.commit()

        nuevoAmbiente = Ambiente(
            nombre = "Facebook Live",
            tipo = "Transmisión",
            descripcion = "Se transmitira el evento desde la cuenta de facebook de la 'Feria Internacional del Libro Arequipa'",
            aforo = 2000,
            idActividad = 1
        )
        db.session.add(nuevoAmbiente)
        db.session.commit()
        
        # ACTIVIDAD 2
        nuevaActividad = Actividad(
            id =2,
            nombre = "La literatura peruana en el cine: apuntes generales",
            tipo = "Ponencia",
            descripcion = "Se presentarán aspectos generales y reflexiones para mostrar la relación entre el cine y la literatura peruana a partir de diferentes adaptaciones y producciones peruanas fílmicas que han ahondado en esta relación.",
            consideraciones = "Ninguna",
            ponente = "David Durand Ato y Jean Paul Espinoza",
            fechaInicio = crearFechaHora("2021-09-26","17:00"),
            fechaFin = crearFechaHora("2021-09-26","18:00"),
            idEvento = self.eventos["libro"].id
        )
        db.session.add(nuevaActividad)
        db.session.commit()

        nuevoAmbiente = Ambiente(
            nombre = "Google Meet",
            tipo = "Transmisión",
            descripcion = "Se transmitira el evento por medio de la plataforma Google Meet enviado al correo de los particpantes",
            aforo = 200,
            idActividad = 2
        )
        db.session.add(nuevoAmbiente)
        db.session.commit()

    def crearTransaccionesLibro(self):
        movimiento = Movimiento(
            nombre = "Lapicero",
            tipo = "Egreso",
            factura = "F123654564",
            detalle = "Adquisicion de Lapiceros",
            monto = 300,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-14","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Donación",
            tipo = "Ingreso",
            factura = "C12367904812",
            detalle = "Donación anónima",
            monto = 2000,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-13","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C1236532",
            detalle = "Inscripcion aporte voluntario",
            monto = 120,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C12352532",
            detalle = "Inscripcion aporte voluntario",
            monto = 80,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-13","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C8756532",
            detalle = "Inscripcion aporte voluntario",
            monto = 80,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-13","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Iluminación",
            tipo = "Egreso",
            factura = "F352054564",
            detalle = "Instalación de Equipo de Luces en el Escenario Principal",
            monto = 450,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Sonido",
            tipo = "Egreso",
            factura = "F352054564",
            detalle = "Instalación de Equipo de Sonido en el Escenario Principal",
            monto = 350,
            idEvento = self.eventos["libro"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        db.session.commit()

    def crearTransaccionesGame(self):
        movimiento = Movimiento(
            nombre = "USBs",
            tipo = "Egreso",
            factura = "F16980119",
            detalle = "adquisicion de USBs para entregar a los ponentes",
            monto = 2000,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-14","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Donación Coffee Break",
            tipo = "Ingreso",
            factura = "C12367904812",
            detalle = "Donación anónima para el Coffee Break",
            monto = 2750,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C98021819",
            detalle = "Inscripcion paquete Basico",
            monto = 150,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-11","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C17961819",
            detalle = "Inscripcion paquete Estudiante",
            monto = 80,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C13953012",
            detalle = "Inscripcion paquete Estudiante",
            monto = 80,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-10","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Cena en restaurante CHICHA ",
            tipo = "Egreso",
            factura = "F09049519",
            detalle = "Reservación del Restaurante Chicha",
            monto = 1500,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Polos para Staff",
            tipo = "Egreso",
            factura = "F06159619",
            detalle = "Polos para el STAFF",
            monto = 350,
            idEvento = self.eventos["Game"].id,
            fechaCreacion=crearFechaHora("2021-12-10","00:00")
        )
        db.session.add(movimiento)
        db.session.commit()
        
    def crearTransaccionesGameJam(self):
        movimiento = Movimiento(
            nombre = "Manual de Reglas",
            tipo = "Egreso",
            factura = "F97071119",
            detalle = "Adquisicion de Manual de Reglas para los participantes",
            monto = 750,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-11","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Donación regalo por participación",
            tipo = "Ingreso",
            factura = "C541656513565451",
            detalle = "Donación para dar un presente a los participantes",
            monto = 2550,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-15","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C95081908",
            detalle = "Inscripcion Estudiante",
            monto = 90,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-14","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C17961819",
            detalle = "Inscripcion paquete Profesional",
            monto = 160,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-10","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Inscripción",
            tipo = "Ingreso",
            factura = "C1653215316",
            detalle = "Inscripcion paquete Profesional",
            monto = 160,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-11","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Contrato para lunchs",
            tipo = "Egreso",
            factura = "F09049519",
            detalle = "Contrato para la preparación de lunchs para los participantes",
            monto = 2700,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-14","00:00")
        )
        db.session.add(movimiento)

        movimiento = Movimiento(
            nombre = "Polos para participantes",
            tipo = "Egreso",
            factura = "F97041219",
            detalle = "Polos para participantes",
            monto = 350,
            idEvento = self.eventos["gameJam"].id,
            fechaCreacion=crearFechaHora("2021-12-12","00:00")
        )
        db.session.add(movimiento)

        db.session.commit()
        
    def registrarParticipantesEventoCategoria(self):
        nuevaCategoria = Categoria(
            idEvento = self.eventos["libro"].id,
            nombre = "Todos"
        )
        db.session.add(nuevaCategoria)
        nuevoPaquete = Paquete(
            idEvento = self.eventos["libro"].id,
            nombre = "General"
        )
        db.session.add(nuevoPaquete)
        db.session.commit()

        nuevaCategoriaPaquete = Categoria_Paquete(
            idCategoria = nuevaCategoria.id,
            idPaquete = nuevoPaquete.id,
            monto = 50
        )
        db.session.add(nuevaCategoriaPaquete)
        db.session.commit()

        # Regitro de Usuario
        nuevo_usuario = Usuario(
            id=4,
            username = "daniel",
            tipoUsuario = 'Participante',
            password = "daniel",
            nombre = "Daniel Rojas",
            email = "daniel@gmail.com",
            tipodoc = "DNI",
            doc = 70707878,
            profesion = "Estudiante")
        db.session.add(nuevo_usuario)
        db.session.commit()
        nuevo_inscrito = Usuario_Evento(
            idEvento = self.eventos["libro"].id,
            idUsuario = nuevo_usuario.id,
            estaInscrito = False,
            idCategoria_Paquete = nuevaCategoriaPaquete.id)
        db.session.add(nuevo_inscrito)
        db.session.commit()

        nuevo_usuario = Usuario(
            id=5,
            username = "martin",
            tipoUsuario = 'Participante',
            password = "martin",
            nombre = "Martin Perez",
            email = "martin@gmail.com",
            tipodoc = "DNI",
            doc = 70807878,
            profesion = "Estudiante")
        db.session.add(nuevo_usuario)
        db.session.commit()
        nuevo_inscrito = Usuario_Evento(
            idEvento = self.eventos["libro"].id,
            idUsuario = nuevo_usuario.id,
            estaInscrito = False,
            idCategoria_Paquete = nuevaCategoriaPaquete.id)
        db.session.add(nuevo_inscrito)
        db.session.commit()

        nuevo_usuario = Usuario(
            id=6,
            username = "violeta",
            tipoUsuario = 'Participante',
            password = "violeta",
            nombre = "Violeta Juarez",
            email = "violeta@gmail.com",
            tipodoc = "DNI",
            doc = 78817878,
            profesion = "Estudiante")
        db.session.add(nuevo_usuario)
        db.session.commit()
        nuevo_inscrito = Usuario_Evento(
            idEvento = self.eventos["libro"].id,
            idUsuario = nuevo_usuario.id,
            estaInscrito = False,
            idCategoria_Paquete = nuevaCategoriaPaquete.id)
        db.session.add(nuevo_inscrito)
        db.session.commit()
        
        nuevo_usuario = Usuario(
            id=7,
            username = "diego",
            tipoUsuario = 'Participante',
            password = "diego",
            nombre = "Diego Lazarte",
            email = "diego@gmail.com",
            tipodoc = "DNI",
            doc = 69864878,
            profesion = "Abogado")
        db.session.add(nuevo_usuario)
        db.session.commit()
        nuevo_inscrito = Usuario_Evento(
            idEvento = self.eventos["libro"].id,
            idUsuario = nuevo_usuario.id,
            estaInscrito = False,
            idCategoria_Paquete = nuevaCategoriaPaquete.id)
        db.session.add(nuevo_inscrito)
        db.session.commit()

        nuevo_usuario = Usuario(
            id=8,
            username = "luisa",
            tipoUsuario = 'Participante',
            password = "luisa",
            nombre = "Luisa Vizcarra",
            email = "luisa@gmail.com",
            tipodoc = "DNI",
            doc = 69844578,
            profesion = "Profesora")
        db.session.add(nuevo_usuario)
        db.session.commit()
        nuevo_inscrito = Usuario_Evento(
            idEvento = self.eventos["libro"].id,
            idUsuario = nuevo_usuario.id,
            estaInscrito = False,
            idCategoria_Paquete = nuevaCategoriaPaquete.id)
        db.session.add(nuevo_inscrito)
        db.session.commit()


    def cargarEjemploFeriaLibro(self):
        self.crearActividadMaterialesAmbientesLibro()
        self.crearTransaccionesLibro()
        self.registrarParticipantesEventoCategoria()
        print("Cargo ejemplo Feria del Libro")

    def cargarEjemploGame(self):
        self.crearActividadMaterialesAmbientes_E2_A1()
        self.crearActividadMaterialesAmbientes_E2_A2()
        self.crearTransaccionesGame()
        #self.registrarParticipantesEventoCategoria()
        print("Cargo ejemplo Game Conference")

    def cargarEjemploGameJam(self):
        self.crearActividadMaterialesAmbientes_E3_A1()
        self.crearTransaccionesGameJam()
        #self.registrarParticipantesEventoCategoria()
        print("Cargo ejemplo Game Conference")