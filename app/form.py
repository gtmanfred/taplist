from flask.ext.wtf import Form
from wtforms import TextField, TextField, BooleanField,PasswordField
from wtforms.validators import Required

class BeerForm(Form):
    beername = TextField('beername', validators=[Required()])
    brewery = TextField('brewery', validators=[Required()])
    beertype = TextField('beertype', validators=[Required()])
    alcohols = TextField('alcohols', validators=[Required()])
    pricepint = TextField('pint price')
    pricehalf = TextField('half growler price')
    pricegrowler = TextField('growler price')
    active = BooleanField()
    notes = TextField('Note')

class LoginForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)
