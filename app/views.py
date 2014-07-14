from flask import render_template, flash, redirect, request, url_for
from app import app
from app.form import BeerForm
import redis
import json
import operator

@app.route('/entry', methods = ['GET', 'POST'])
def entry():
    form = BeerForm()
    if request.method == 'POST':
        if form.validate():
            pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
            r = redis.Redis(connection_pool=pool)
            beer = {
                'name': form.beername.data,
                'brewery': form.brewery.data,
                'type': form.beertype.data,
                'content': form.alcohols.data,
                'pint': float(form.pricepint.data),
            }
            if form.pricehalf.data:
                beer['half'] = float(form.pricehalf.data),
            else:
                beer['half'] = beer['pint'] + 2

            if form.pricegrowler.data:
                beer['growler'] = float(form.pricegrowler.data)
            else:
                beer['growler'] = beer['half'] * 2

            r.set('beer_{0}'.format(form.beername.data.replace(' ', '')), json.dumps(beer))
            r.save()
        return redirect(url_for('entry'))
    else:
        return render_template('entry.html', title = 'Entry', form = form)


@app.route('/')
@app.route('/index.html')
def home():
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_*')]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('home.html', title='Beer List', beers=beers)
