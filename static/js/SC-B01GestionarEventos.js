var GESTIONAREVENTOS = GESTIONAREVENTOS ||{};
GESTIONAREVENTOS.atributos = {
    optSeleccionada: null,
    optCrear: null,
    idPlantilla: null,
    idEvento: null,
    infoEvento: null,
    optModificar: null,
    optGestionar: null,
    estadoEvento: null,
}
GESTIONAREVENTOS.eventos = {
    seleccionarGestionarEvento(){},
    seleccionarOpcion(){},
    mostrarEventosInformacion(){},
    mostrarOpcionesEventos(){},
    mostrarOpcionesCrearEventos(){},
    seleccionarOptCrearEvento(){},
    mostrarListaPlantillasEvento(){},
    seleccionarPlantillaEvento(){},

    ingresaNombreEvento(idEvento){},
    ingresaTipoEvento(idEvento){},
    ingresaLugarEvento(idEvento){},
    ingresaDescripcionEvento(idEvento){},

    mostrarOpcionesModificar(estadoEvento){},
    seleccionarOpcionModificar(){},
    informarErrorIntentoModificacion(){},

    mostrarOpcionesGestionarRecursos(){},
    seleccionarOptGestionar(){},
    obtenerEvento(){},
    
    visualizarActividades(){},
    editarActividad(){},
    guardarDatos(){},
    desvincularActividad(){},
    seleccionarActividad(){},
    visualizarEditarActividad(){},
    visualizarActividad(){},
    agregarActividad(){},
    seleccionarTipoActividad(){},
};