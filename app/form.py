from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import Required
from werkzeug.datastructures import MultiDict

class BeerForm(Form):
    beername = TextField('beername', validators = [Required()])
    brewery = TextField('brewery', validators = [Required()])
    beertype = TextField('beertype', validators = [Required()])
    alcohols = TextField('alcohols', validators = [Required()])
    pricepint = TextField('pint price', validators = [Required()])
    pricehalf = TextField('half growler price')
    pricegrowler = TextField('growler price')

    def reset(self):
        blankData = MultiDict([ ('csrf', self.reset_csrf() ) ])
        self.process(blankData)
