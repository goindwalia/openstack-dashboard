from flask.ext.wtf import Form
from wtforms import StringField, SelectField, \
    BooleanField, SubmitField
from wtforms.validators import Required, Length, \
    Regexp, EqualTo

class AddImageForm(Form):
    imagename = StringField('Server Name', validators=[Required(), Length(1,64)])
    submit = SubmitField('Create')