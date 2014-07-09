from flask import render_template, flash, redirect
from app import app
from app.form import BeerForm
import redis
import json

@app.route('/entry', methods = ['GET', 'POST'])
def entry():
    form = BeerForm()
    if hasattr(form.beername, 'data') and form.beername.data:
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        beer = {
            'name': form.beername.data,
            'brewery': form.brewery.data,
            'type': form.beertype.data,
            'content': form.alcohols.data,
            'pint': int(form.pricepint.data),
        }
        if form.pricehalf.data:
            beer['half'] = int(form.pricehalf.data),
        else:
            beer['half'] = beer['pint'] + 2

        if form.pricegrowler.data:
            beer['growler'] = int(form.pricegrowler.data)
        else:
            beer['growler'] = beer['half'] * 2

        r.set('beer_{0}'.format(form.beername.data.replace(' ', '')), json.dumps(beer))
        r.save()
    return render_template('entry.html', title = 'Entry', form = form)

@app.route('/')
def home():
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_*')]
    return render_template('home.html', title='Beer List', beers=beers)
