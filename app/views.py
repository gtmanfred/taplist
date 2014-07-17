from flask import render_template, redirect, request, url_for
from app import app
from app.form import BeerForm
import redis
import json
import operator

locations = {
        'broadway': 1,
        'huebner': 2,
        'gastropub': 3
        }


@app.route('/<location>/entry', methods=['GET', 'POST'])
def entry(location):
    print(request.form)
    form = BeerForm()
    if request.method == 'POST':
        pool = redis.ConnectionPool(host='localhost', port=6379, db=locations[location])
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

        beer['active'] = True

        r.set('beer_{0}_{1}'.format(form.brewery.data.replace(' ', ''),
                                    form.beername.data.replace(' ', '')),
              json.dumps(beer))
        r.save()
        return redirect('/{0}/entry'.format(location))
    else:
        return render_template('entry.html', title='Entry', form=form)

@app.route('/<location>/scroll', methods=['GET'])
def scroll(location):
    pool = redis.ConnectionPool(host='localhost', port=6379, db=locations[location])
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_*')]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('scroll.html', title='Beer List',
                           beers=[beer for beer in beers if beer['active']])


@app.route('/<location>/edit', methods=['GET', 'POST'])
def editlist(location):
    pool = redis.ConnectionPool(host='localhost', port=6379, db=locations[location])
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_*')]
    if request.method == 'POST':
        for beer in beers:
            beername = 'beer_{0}_{1}'.format(beer['brewery'].replace(' ', ''),
                                             beer['name'].replace(' ', ''))
            beer['active'] = True if beername in \
                request.form.getlist('checks') else False
            r.set(beername, json.dumps(beer))
            r.save()
        for beer in request.form.getlist('delete'):
            r.delete(beer)
        beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_*')]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('edit.html', title='Beer List', beers=beers)


@app.route('/<location>')
def index(location):
    pool = redis.ConnectionPool(host='localhost', port=6379, db=locations[location])
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_*')]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('index.html', title='Beer List',
                           beers=[beer for beer in beers if beer['active']])
