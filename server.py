from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt


app = Flask(__name__)
app.config["SECRET_KEY"] = "aPhiIUGHAadoasihdpADH;ashgkyuDS"
app.config["SQLALCHEMY_TRACK_MODIFICATInIS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
Bootstrap(app)
db = SQLAlchemy(app)


class ListItemForm(FlaskForm):
    task_name = StringField(label="Task Title", validators=[DataRequired()])
    task_description = TextAreaField(label="Task Description", validators=[DataRequired()])


class NewListForm(FlaskForm):
    list_name = StringField(label="List Name", validators=[DataRequired()])
    list_summary = TextAreaField(label="List Summary", validators=[DataRequired()])


class TODOEntry(db.Model):
    __tablename__ = "todoentry"
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(50), nullable=False, unique=True)
    last_edited = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    sub_lists = db.relationship("ListColumn", backref="parent_list", lazy=True)


class ListColumn(db.Model):
    __tablename__ = "listcolumn"
    id = db.Column(db.Integer, primary_key=True)
    parent_list_id = db.Column(db.Integer, db.ForeignKey("todoentry.id"), nullable=False)
    list_items = db.relationship("ListItem", backref="list", lazy=True)


class ListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_list_id = db.Column(db.Integer, db.ForeignKey("listcolumn.id"), nullable=False)
    content = db.Column(db.String(200), nullable=False)


db.create_all()


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/lists", methods=["GET"])
def lists():
    form = NewListForm()
    if form.validate_on_submit():
        return render_template("lists.html", form=form)
    else:
        return render_template("lists.html", form=form)


@app.route("/lists/<int:list_id>", methods=["GET", "POST"])
def list(list_id):
    form = ListItemForm()
    if form.validate_on_submit():
        return render_template("list.html", form=form)
    else:
        return render_template("list.html", form=form)


@app.route("/add-list", methods=["GET", "POST"])
def add_list():
    form = NewListForm()
    if form.validate_on_submit():
        return redirect(url_for("lists", form=form))
    else:
        return render_template("lists.html", form=form)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
