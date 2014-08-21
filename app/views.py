from flask import render_template, redirect, request, url_for
from app import app
from app.form import BeerForm
import redis
import json
import operator

locations = [
        'broadway',
        'huebner',
        'gastropub',
        ]

@app.route('/<location>/entry', methods=['GET', 'POST'])
def entry(location):
    if location not in locations:
        return 'Unknown Location'
    form = BeerForm()
    if request.method == 'POST':
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        beer = {
            'name': form.beername.data,
            'brewery': form.brewery.data,
            'type': form.beertype.data,
            'content': form.alcohols.data,
            'location': location
        }

        if form.pricepint.data != "":
            beer['pint'] = float(form.pricepint.data)

        if form.pricehalf.data:
            beer['half'] = float(form.pricehalf.data)

        elif 'pint' in beer:

            beer['half'] = beer['pint'] + 2

        if form.pricegrowler.data:
            beer['growler'] = float(form.pricegrowler.data)
        elif 'half' in beer:
            beer['growler'] = beer['half'] * 2

        if hasattr(form.notes, 'data'):
            beer['notes'] = form.notes.data

        beer['active'] = True

        r.set('beer_{0}_{1}_{2}'.format(
            location,
            form.brewery.data.replace(' ', ''),
            form.beername.data.replace(' ', '')),
            json.dumps(beer)
        )

        r.save()
        return redirect('/{0}/entry'.format(location))
    else:
        return render_template('entry.html', title='Entry', form=form)

@app.route('/<location>/scroll', methods=['GET'])
def scroll(location):
    if location not in locations:
        return 'Unknown Location'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_{0}_*'.format(location))]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('scroll.html', title='Beer List',
                           beers=[beer for beer in beers if beer['active']])


@app.route('/<location>/edit', methods=['GET', 'POST'])
def editlist(location):
    if location not in locations:
        return 'Unknown Location'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_{0}*'.format(location))]
    if request.method == 'POST':
        for beer in beers:
            beername = 'beer_{0}_{1}_{2}'.format(
                location,
                beer['brewery'].replace(' ', ''),
                beer['name'].replace(' ', '')
            )

            beer['active'] = True if beername in \
                request.form.getlist('checks') else False
            r.set(beername, json.dumps(beer))
            r.save()
        for beer in request.form.getlist('delete'):
            r.delete(beer)
        beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_{0}_*'.format(location))]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    if request.method == 'POST':
        return redirect(location)
    return render_template('edit.html', title='Beer List', beers=beers)


@app.route('/<location>')
@app.route('/<location>/')
def bars(location):
    if location not in locations:
        return 'Unknown Location'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_{0}_*'.format(location))]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('index.html', title='Beer List',
                           beers=[beer for beer in beers if beer['active']])

@app.route('/')
def index():
    return render_template('links.html', title='links', locations=locations)
