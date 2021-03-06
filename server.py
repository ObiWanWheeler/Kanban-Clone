from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
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
    column = SelectField(label="Column", choices=[("todo", "TODO"), ("wip", "In Progress"), ("finished", "Finished")])


class NewListForm(FlaskForm):
    list_name = StringField(label="List Name", validators=[DataRequired()])
    list_summary = TextAreaField(label="List Summary", validators=[DataRequired()])


class TODOList(db.Model):
    __tablename__ = "todolist"
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(50), nullable=False, unique=True)
    list_summary = db.Column(db.String(300), nullable=False)
    last_edited = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    sub_lists = db.relationship("ListColumn", backref="parent_list", lazy=True)


class ListColumn(db.Model):
    __tablename__ = "listcolumn"
    id = db.Column(db.Integer, primary_key=True)
    list_type = db.Column(db.String(20), nullable=False)
    parent_list_id = db.Column(db.Integer, db.ForeignKey("todolist.id"), nullable=False)
    list_items = db.relationship("ListItem", backref="list", lazy=True)

    def __repr__(self):
        return str(self.list_type) + ", " + str(self.parent_list_id) + str(self.list_items)


class ListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_list_id = db.Column(db.Integer, db.ForeignKey("listcolumn.id"), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    task_description = db.Column(db.String(200), nullable=False)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/lists", methods=["GET"])
def lists():
    all_lists = db.session.query(TODOList).all()
    form = NewListForm()
    return render_template("lists.html", form=form, lists=all_lists)


@app.route("/add-list", methods=["POST"])
def add_list():
    form = NewListForm()
    if form.validate_on_submit():
        new_list = TODOList(list_name=form.list_name.data, list_summary=form.list_summary.data)

        db.session.add(new_list)
        db.session.commit()
        print(new_list.id)

        new_todo = ListColumn(list_type="todo", parent_list_id=new_list.id)
        new_wip = ListColumn(list_type="wip", parent_list_id=new_list.id)
        new_finished = ListColumn(list_type="finished", parent_list_id=new_list.id)

        print(new_todo, new_wip, new_finished, sep="\n")

        db.session.add(new_todo)
        db.session.add(new_wip)
        db.session.add(new_finished)

        db.session.commit()
        return redirect(url_for("list", list_id=new_list.id))
    return redirect(url_for("lists"))


@app.route("/lists/<int:list_id>", methods=["GET"])
def list(list_id):
    requested_list = db.session.query(TODOList).get(list_id)
    if requested_list is not None:
        print('here')
        form = ListItemForm()
        return render_template("list.html", form=form, list=requested_list)
    else:
        return redirect(url_for("lists"))


@app.route("/add-item/<int:list_id>", methods=["POST"])
def add_item(list_id):
    form = ListItemForm()
    list = db.session.query(TODOList).get(list_id)
    if form.validate_on_submit():
        column_to_append_to = None
        for list in list.sub_lists:
            print(list.list_type)
            if list.list_type == form.column.data:
                column_to_append_to = list
                break
        if column_to_append_to is not None:
            new_item = ListItem(parent_list_id=column_to_append_to.id,
                                task_description=form.task_description.data, task_name=form.task_name.data)
            db.session.add(new_item)
            db.session.commit()

    return redirect(url_for("list", list_id=list_id))


@app.route("/delete-item/<int:list_id>/<int:item_id>")
def delete_item(item_id, list_id):
    item_to_delete = db.session.query(ListItem).get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for("list", list_id=list_id))


@app.route("/edit-item/<int:list_id>/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id, list_id):
    item_to_edit = db.session.query(ListItem).get(item_id)
    list = db.session.query(TODOList).get(list_id)

    if list is None:
        return redirect(url_for("lists"))
    if item_to_edit is None:
        return redirect(url_for("list", list_id=list.id))

    form = ListItemForm(task_name=item_to_edit.task_name, task_description=item_to_edit.task_description)

    if form.validate_on_submit():
        list = db.session.query(TODOList).get(list_id)
        item_to_edit.task_name = form.task_name.data
        item_to_edit.task_description = form.task_description.data
        list.last_edited = dt.utcnow()
        column_to_append_to = None
        for list in list.sub_lists:
            if list.list_type == form.column.data:
                column_to_append_to = list
                break
        if column_to_append_to is not None:
            item_to_edit.parent_list_id = column_to_append_to.id
        db.session.commit()
        return redirect(url_for("list", list_id=list_id))
    else:
        return render_template("edit.html", form=form, list=list)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
