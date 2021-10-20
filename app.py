from datetime import datetime
from markupsafe import escape

from flask import Flask
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy, SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/sge.db'

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

@app.route("/")
def index():
    return render_template("index.html", texto="las plantillas")

if __name__ == "__main__":
    app.run()