from flask import Flask, request, redirect, url_for, session
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy, SQLAlchemy
from sqlalchemy.orm import defaultload
from datetime import datetime

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
    asistencias = db.relationship('Asistencia', backref='usuario', lazy=True)
    materiales = db.relationship('Material_Usuario', backref='usuario', lazy=True)

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
    categorias = db.relationship('Categoria', backref='evento', lazy=True)
    paquetes = db.relationship('Paquete', backref='evento', lazy=True)

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
    asistencias = db.relationship('Asistencia', backref='ambiente', lazy = True)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    descripcion = db.Column(db.String(100))
    stockInicial = db.Column(db.Integer, nullable = False)
    costoUnitario = db.Column(db.Float, nullable = False)

    idActividad = db.Column(db.Integer, db.ForeignKey('actividad.id'), nullable=False)
    material_usuarios = db.relationship('Material_Usuario', backref='material', lazy = True)
    
class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    tipo = db.Column(db.String(30), nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    factura = db.Column(db.String(30), nullable=False)
    detalle = db.Column(db.String(90))
    cantidad = db.Column(db.Integer)
    monto = db.Column(db.Float, nullable = False)
    fechaCreacion = db.Column(db.Date, default=datetime.utcnow)

    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)

    cat_pqt = db.relationship('Categoria_Paquete', backref='categoria', lazy = True)

class Paquete(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(30), nullable=False)
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)

    cat_pqt = db.relationship('Categoria_Paquete', backref='paquete', lazy = True)

class Categoria_Paquete(db.Model):
    __tablename__ = 'categoria_paquete'
    id = db.Column(db.Integer, primary_key=True)
    idCategoria = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    idPaquete = db.Column(db.Integer, db.ForeignKey('paquete.id'), nullable=False)
    monto = db.Column(db.Float, nullable = False)
    usuarios_eventos = db.relationship('Usuario_Evento', backref='categoria_paquete', lazy = True)

class Usuario_Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    idEvento = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    idCategoria_Paquete = db.Column(db.Integer, db.ForeignKey('categoria_paquete.id'))
    estaInscrito = db.Column(db.Boolean, nullable=True)

class Asistencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idAmbiente = db.Column(db.Integer, db.ForeignKey('ambiente.id'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    turno = db.Column(db.String(30), nullable=False)
    fechaAsistencia = db.Column(db.DateTime)
    asistio = db.Column(db.Boolean, default=False)

class Material_Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    idMaterial = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    estado = db.Column(db.String(30), nullable=True)    
    fecha = db.Column(db.DateTime, nullable=True)