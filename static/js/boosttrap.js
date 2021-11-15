console.log("BOOSTTRAP Version 1.0 \n Framework developed by: Magr")

var BOOSTTRAP = BOOSTTRAP ||{};

BOOSTTRAP.Utilities = {
    iconos : {"ver":"fa-eye","eliminar":"fa-trash","modificar":"fa-pencil-square-o","agregar":"fa-plus-square-o","seleccionar":"fa-hand-pointer-o"},
    basicButton(texto='Enviar',id='boton-0',classStyle='btn-outline-primary'){},//\
    buildOptions(id,buttons){},//\
    buildSelection(id, name, value,extra){},//\
    addChild(id,raw){},//\
    onlyChild(id,raw){},//\
}

BOOSTTRAP.GenerateSimple = {
    buildTable(id, headers,contenido){},//\
    buildForm(id, datos){},//\
    buildModal(titulo,body,footer,id){},//\
}

BOOSTTRAP.GenerateComplex = {
    buildTableSelection(id, headers,contenido){},//\
    buildTableOptions(id, headers,contenido, opciones=""){},//\
    buildTableModal(id, titulo, datosTabla){},//\
    buildFormModal(id,titulo, datosForm){},//\
}

BOOSTTRAP.Buttons = {
    getButton(funcion,id){},//\
    getButtons(id,types){},//\types=[ver modificar eliminar]
}

BOOSTTRAP.Forms = {
    buildRow(content){},//\
    buildTextarea(formRow){},//\
    buildInput(formRow){},//\
    buildCheck(formRow){},//\
    buildCheck(formRow){},//\
    fillForm(datos){},//\
}

BOOSTTRAP.Tables = {
    buildTableRowContent(headers,obj){},//\
    //getHeaders(row){},
    fillTable(idTable,headers,contenido,selectionBool,optionsRight){},
    buildTableContent(headers,contenido,selectionBool,optionsRight){},//\
    buildTableHeader(headers,left,right){},//
}

BOOSTTRAP.Modals = {
    buildButtonModal(idTarget,texto){},
    build2ButtonModal(text1,text2){},//
}

BOOSTTRAP.Navbar = {
    buildNavbarItems(items){},
}

let None = "";

//==================================================
// Pruebando =======================================

function probando(){
    
}

//==================================================
// Utilities =======================================
BOOSTTRAP.Utilities.basicButton = function(texto='Enviar',id='boton-0',classStyle='btn-outline-primary'){
    return String.raw`<button type="submit" id="${id}" class="btn ${classStyle}  float-right" >${texto}</button>`
}
BOOSTTRAP.Utilities.buildOptions = function(id,buttons){
    return BOOSTTRAP.buttons.getButtons(id,buttons)
}
BOOSTTRAP.Utilities.buildSelection = function(id, name, value,extra=""){
    return String.raw`
    <div class="form-check">
        <input class="form-check-input" type="radio" name="${name}" id="${id}" value="${value}" ${extra}>
    </div>
    `
}

BOOSTTRAP.Utilities.addChild = function(id,raw){
    document.getElementById(id).innerHTML += raw
}
BOOSTTRAP.Utilities.onlyChild = function(id,raw){
    document.getElementById(id).innerHTML = raw
}

// GenerateSimple =======================================
BOOSTTRAP.GenerateSimple.buildTable = function(id, headers, contenido){
    let tabla = String.raw`
    <table id="${id}" class="table dataTable table-hover dataTable">
        <thead>
            ${BOOSTTRAP.Tables.buildTableHeader(headers,false,false)}
        </thead>
        <tbody id="${id}-tbody">
            ${BOOSTTRAP.Tables.buildTableContent(headers,contenido,false,false)}
        </tbody>
    </table>
    `
    return tabla
}
BOOSTTRAP.GenerateSimple.buildForm = function(id, datos){
    let formText =String.raw`<form action="" id="${id}">`
    for(let i in datos)
        formText += BOOSTTRAP.Forms.buildRow(datos[i])
    formText += String.raw`<div class="justify-content-end">${BOOSTTRAP.Utilities.basicButton("Continuar","id","btn-outline-primary")}</div>`
    //formText+=
    formText+='</form>'
    return formText 
}

BOOSTTRAP.GenerateSimple.buildModal = function(titulo,body,footer,id="modal0"){
    let header = String.raw`
        <h5 class="modal-title">${titulo}</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>`
    let string = String.raw`
    <div class="modal" id="${id}" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    ${header}
                </div>
                <div class="modal-body">
                    ${body}
                </div>
                <div class="modal-footer">
                    ${footer}
                </div>
            </div>
        </div>
    </div>
    `
    return string
}

// GenerateComplex ======================================
BOOSTTRAP.GenerateComplex.buildTableSelection = function(id, headers,contenido){
    let tabla = String.raw`
    <table id="${id}" class="table dataTable table-hover dataTable">
        <thead>
            ${BOOSTTRAP.Tables.buildTableHeader(headers,true,false)}
        </thead>
        <tbody id="${id}-tbody">
            ${BOOSTTRAP.Tables.buildTableContent(headers,contenido,true, false)}
        </tbody>
    </table>
    `
    return tabla
}

BOOSTTRAP.GenerateComplex.buildTableOptions = function(id, headers,contenido, opciones){
    let tabla = String.raw`
    <table id="${id}" class="table dataTable table-hover dataTable">
        <thead>
            ${BOOSTTRAP.Tables.buildTableHeader(headers,false,true)}
        </thead>
        <tbody id="${id}-tbody">
            ${BOOSTTRAP.Tables.buildTableContent(headers,contenido,false,opciones)}
        </tbody>
    </table>
    `
    return tabla
}

BOOSTTRAP.GenerateComplex.buildTableModal = function(id, titulo, datosTabla){
    let tabla = String.raw`<form id='${id}-tableModalForm' method='post'><div class = "marquito"><div class = "container"><br>`
    if (datosTabla.tipo_tabla == 'Simple') tabla += BOOSTTRAP.GenerateSimple.buildTable(id+"-tableModalForm"+'-table',datosTabla.headers, datosTabla.contenido)
    else if (datosTabla.tipo_tabla == 'Seleccion') tabla += BOOSTTRAP.GenerateComplex.buildTableSelection(id+"-tableModalForm"+'-table',datosTabla.headers, datosTabla.contenido)
    else if (datosTabla.tipo_tabla == 'Opciones') tabla += BOOSTTRAP.GenerateComplex.buildTableOptions(id+"-tableModalForm"+'-table',datosTabla.headers, datosTabla.contenido,datosTabla.opciones)
    tabla += "</div></div></form>"
    return BOOSTTRAP.GenerateSimple.buildModal(titulo,tabla,"",id)
}

BOOSTTRAP.GenerateComplex.buildFormModal = function(id,titulo,datosForm){
    let form = String.raw`
        <div class = "marquito"><div class = "container"><br>
            ${BOOSTTRAP.GenerateSimple.buildForm(id+"-form",datosForm)}
        </div></div>
    `
    return BOOSTTRAP.GenerateSimple.buildModal(titulo,form,"",id)
}

// Buttons ==============================================
BOOSTTRAP.Buttons.getButton = function(funcion,id){
    var iconos = {"ver":"fa-eye","eliminar":"fa-trash","modificar":"fa-pencil-square-o","agregar":"fa-plus-square-o","seleccionar":"fa-hand-pointer-o"}
    return String.raw`
    <button id="${id}-${funcion}" type="button" class="btn btn-outline-dark" onclick="${funcion}(${id})">
        <i class="fa ${BOOSTTRAP.Utilities.iconos[funcion]}" aria-hidden="true"></i>
    </button>`
}

BOOSTTRAP.Buttons.getButtons = function(id,types){
    return String.raw`
    ${()=>{
        for (let i in types)
            buttons += BOOSTTRAP.Buttons.getButton(types[i],id)
        }
    }
    `
}

// Forms ================================================
BOOSTTRAP.Forms.buildRow = function(content){
    //if(content.tipo_dato=="multiple") return BOOSTTRAP.Forms.buildMultiple(content)
    if (content.tipo_dato=="check") return BOOSTTRAP.Forms.buildCheck(content)
    if (content.tipo_dato=="textarea") return BOOSTTRAP.Forms.buildTextarea(content)
    return BOOSTTRAP.Forms.buildInput(content)
}

BOOSTTRAP.Forms.buildTextarea = function(formRow){
    return String.raw`
        <div class="col">
            <div class="mb-3">
                <label for="id-${formRow.nombre}">${formRow.nombre}</label>
                <textarea class="form-control" id="${formRow.nombre}" name="${formRow.nombre}" ${formRow.extra}></textarea>
            </div>
        </div>    
        `
}
BOOSTTRAP.Forms.buildInput = function(formRow){
    return String.raw`
        <div class="col">
            <div class="form-group row">
                <label for="${formRow.nombre}" class="col-sm-2 col-form-label">${formRow.nombre}</label>
                <div class="col-sm-10">
                    <input type="${formRow.tipo_dato}" class="form-control" id="${formRow.nombre}" name="${formRow.nombre}" ${formRow.extra}>
                </div>
            </div>
        </div>
        `
}

BOOSTTRAP.Forms.buildCheck= function(formRow){
    let text = ""
    let values = formRow.values
    values = values.split("+");
    for (i in values){
        text += String.raw`
        <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="${formRow.nombre}" id="${formRow.nombre}-op${i}" value="${values[i]}" ${formRow.extra}>
            <label class="form-check-label" for="inlineRadio1">${values[i]}</label>
        </div>
        `
    }
    return text
}


BOOSTTRAP.Forms.fillForm = function(datos){//datos = {"id"=10.12312}
    for (let key in datos){
        //console.log(key," ",datos[key])
        //document.getElementById("id-"+key).attr('value',datos[key])
        document.getElementById("id-"+key).setAttribute('value',datos[key])
    }
}


// Tables =======================================
BOOSTTRAP.Tables.buildTableRowContent = function(headers,obj){
    row = ""
    for (let j in headers){
        let key = headers[j]
        row+=String.raw`<td class="${key}">${obj[key]}</td>`;
    }
    return row
}

BOOSTTRAP.Tables.buildTableContent = function(headers,contenido,selectionBool,optionsRight){
    let tabla = ""
    for (let i in contenido){
        var obj = contenido[i]
        tabla+=String.raw`<tr id="${obj.id}" class="table dataTable table-hover dataTable">`;
        if(selectionBool) tabla+= String.raw`<td>${BOOSTTRAP.Utilities.buildSelection(obj.id+"-s","selection",obj.id)}</td>`
        tabla+=BOOSTTRAP.Tables.buildTableRowContent(headers,obj)
        if(optionsRight) tabla += String.raw`<td>${BOOSTTRAP.Utilities.buildOptions(obj.id,optionsRight)}</td>`
        tabla +="</tr>"
    }
    return tabla
}

BOOSTTRAP.Tables.buildTableHeader = function(headers,left,right){
    let tabla = "<tr>"
    if(left)tabla+='<th scope="col">seleccion</th>'
    for (let i in headers){
        let header = headers[i]
        tabla += String.raw`<th scope="col">${header}</th>`
    }
    if(right)tabla+='<th scope="col">opciones</th>';//una fila para botones
    tabla+='</tr>'
    return tabla
}
BOOSTTRAP.Tables.fillTable = function(idTable,headers,contenido,selectionBool,optionsRight){
    let fill = BOOSTTRAP.Tables.buildTableContent(headers,contenido,selectionBool,optionsRight)
    console.log(idTable+"-tbody")
    document.getElementById(idTable+"-tbody").innerHTML = fill
}


// Modals =======================================
BOOSTTRAP.Modals.build2ButtonModal = function(text1='Cancelar',text2='Confirmar'){
    String.raw`
    <button type="button" class="btn btn-secondary" data-dismiss="modal">${text1}</button>
    <button type="button" class="btn btn-primary">${text2}</button>
    `
}
BOOSTTRAP.Modals.buildButtonModal = function(idTarget,texto){
    return String.raw`
    <!-- Button trigger modal -->
    <button id="${idTarget}-'toogle'" type="button" class="btn btn-primary" data-toggle="modal" data-target="#${idTarget}" >
        ${texto}
    </button>
    `
}

// Navbar =======================================

BOOSTTRAP.Navbar.buildNavbarItems=function(items){
    itemsText = ""
    for (let i in items){
        let it=items[i]
        itemsText += String.raw`
        <a class="dropdown-item" href="${it.enlace}"><i class="fa ${it.icon}" aria-hidden="true"></i> ${it.name} </a>
        `
    }
    return itemsText
}

//==================================================
//==                    END                       ==
//==================================================


//Ver, modificar, eliminar
function ver(id){
    var nombrePagina = document.getElementById("nombrePagina").innerHTML
    var url = String.raw`/ver/${nombrePagina}/${id}`
    window.open(url,"_self");
}
function modificar(id){
    var nombrePagina = document.getElementById("nombrePagina").innerHTML
    var url = String.raw`/modificar/${nombrePagina}/${id}`
    window.open(url,"_self");
}
function eliminar(id){
    var nombrePagina = document.getElementById("nombrePagina").innerHTML
    var url = String.raw`/remove/${nombrePagina}/${id}`
    window.open(url,"_self");
}

function agregar(id){
    var nombrePagina = document.getElementById("nombrePagina").innerHTML
    var url = String.raw`/crear/${nombrePagina}/${id}`
    window.open(url,"_self");
}

probando();