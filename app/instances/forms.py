from flask.ext.wtf import Form
from wtforms import StringField, SelectField, \
    BooleanField, SubmitField
from wtforms.validators import Required, Length, \
    Regexp, EqualTo

class CreateServerForm(Form):
    servername = StringField('Server Name', validators=[Required(), Length(1,64)])
    imageselected = SelectField('Images', validators=[Required()])
    flavorselected = SelectField('Flavors', validators=[Required()])
    networkselected = SelectField('Network(s)', validators=[Required()])
    submit = SubmitField('Create')