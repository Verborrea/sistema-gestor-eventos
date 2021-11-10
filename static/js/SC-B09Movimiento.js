var MOVIMIENTO = MOVIMIENTO ||{};
MOVIMIENTO.atributos = {
    infoIngreso: null,
    tipoMovimiento: null,
    nombreEgreso: null,
    facturaEgreso: null,
    detalleEgreso: null,
    cantidadEgreso: null,
    montoEgreso: null,
}
MOVIMIENTO.eventos = {
    seleccionaregistrarIngreso(){},
    modalFormularioNuevo(){},
    ingresaConceptoIngreso(){},
    ingresaDetalleIngreso(){},
    ingresamontoIngreso(){},
    seleccionarTipoMovimiento(){},
    visualizarMovimientosPorTipo(movimientos){},
    almacenarDatos(){},
    cerrarVentanaYActualizar(){},
};