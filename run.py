import sys
import base64
import random
import string
from flask import Flask, redirect, request, flash
from flask.cli import click, with_appcontext
from flask_admin.actions import action
from flask_admin.helpers import get_redirect_target
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, expose
from wtforms import HiddenField, IntegerField, Form
from wtforms.validators import InputRequired


# Flask commands
@click.command('create-database')
@with_appcontext
def create_database():
    db.drop_all()
    db.create_all()

    for _ in range(0, 100):
        _cost = random.randrange(1, 1000)
        _project = Project(
            name=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)),
            cost=_cost
        )
        db.session.add(_project)

    db.session.commit()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.cli.add_command(create_database)


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/project">Click me to get to the projects!</a>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    cost = db.Column(db.Integer(), nullable=False)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return "Name: {name}; Cost : {cost}".format(name=self.name, cost=self.cost)


class ChangeForm(Form):
    ids = HiddenField()
    cost = IntegerField(validators=[InputRequired()])


class ProjectView(ModelView):
    # don't call the custom page list.html as you'll get a recursive call
    list_template = 'admin/model/custom_list.html'
    page_size = 10

    # omitting the third argument suppresses the confirmation alert
    @action('change_cost', 'Change Cost')
    def action_change_cost(self, ids):
        url = get_redirect_target() or self.get_url('.index_view')
        return redirect(url, code=307)

    @expose('/', methods=['POST'])
    def index(self):
        if request.method == 'POST':
            url = get_redirect_target() or self.get_url('.index_view')
            ids = request.form.getlist('rowid')
            joined_ids = ','.join(ids)
            change_form = ChangeForm()
            change_form.ids.data = joined_ids
            self._template_args['url'] = url
            self._template_args['change_form'] = change_form
            self._template_args['change_modal'] = True
            return self.index_view()

    @expose('/update/', methods=['POST'])
    def update_view(self):
        if request.method == 'POST':
            url = get_redirect_target() or self.get_url('.index_view')
            change_form = ChangeForm(request.form)
            if change_form.validate():
                ids = change_form.ids.data.split(',')
                cost = change_form.cost.data
                _update_mappings = [{'id': rowid, 'cost': cost} for rowid in ids]
                db.session.bulk_update_mappings(Project, _update_mappings)
                db.session.commit()
                flash(f"Set cost for {len(ids)} record{'s' if len(ids) > 1 else ''} to {cost}.", category='info')
                return redirect(url)
            else:
                # Form didn't validate
                self._template_args['url'] = url
                self._template_args['change_form'] = change_form
                self._template_args['change_modal'] = True
                return self.index_view()


admin = Admin(app, template_mode="bootstrap3")
admin.add_view(ProjectView(Project, db.session))

