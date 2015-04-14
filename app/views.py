from flask import render_template, redirect, request, url_for, jsonify, session, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import app
from app.form import BeerForm, LoginForm
from app.login import BarUser
from app.auth import role_required
import redis
from redis.sentinel import Sentinel
import collections
from collections import OrderedDict
import uuid
import json
import operator
import re

locations = [
        'broadway',
        'huebner',
        'gastropub',
        'thebridge'
        ]


def convert(data):
    if isinstance(data, basestring):
        return data.decode('utf8')
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


@app.route('/<location>/entry', methods=['GET', 'POST'])
@login_required
@role_required
def entry(location):
    if location not in locations:
        return 'Unknown Location'
    form = BeerForm()
    if request.method == 'POST':
        sentinel = Sentinel([('localhost', 26379)], socket_timeout=1)
        r = sentinel.master_for('mymaster', socket_timeout=1)
        beer = {
            'name': form.beername.data,
            'brewery': form.brewery.data,
            'type': form.beertype.data,
            'content': form.alcohols.data,
            'location': location
        }
        if re.match('~?[0-9]+\.?[0-9]*', beer['content']):
            beer['content'] = '%s %%' % beer['content']

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

        beer['active'] = 'True' if form.active.data else 'False' 

        r.hmset(
            'beer_{0}_{1}'.format(
                location,
                str(uuid.uuid4().get_hex().upper()[0:6])
            ),
            beer
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
    beers = convert([r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))])
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('scroll.html', title='Beer List',
                           beers=[beer for beer in beers if beer['active'] == 'True'], location=location)


@app.route('/<location>/json', methods=['GET'])
def get_json(location):
    if location not in locations:
        return 'Unknown Location'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = convert([r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))])
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return jsonify({'beers': [b for b in beers if b['active'] == 'True']})


@app.route('/<location>/edit', methods=['GET', 'POST'])
@login_required
@role_required
def editlist(location):
    if location not in locations:
        return 'Unknown Location'
    sentinel = Sentinel([('localhost', 26379)], socket_timeout=1)
    r = sentinel.master_for('mymaster', socket_timeout=1)
    if request.method == 'POST':
        beers = {key: r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))}
        for beername, beer in beers.items():
            r.hset(beername, 'active', 'True' if beername in request.form.getlist('checks') else 'False')
            #r.hmset(beername, beer)
        for beer in request.form.getlist('delete'):
            r.delete(beer)
    r.save()
    beers = []
    for key in r.keys('beer_{0}_*'.format(location)):
        beer = convert(r.hgetall(key))
        beer['beername'] = key
        beers.append(beer)
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    if request.method == 'POST':
        return redirect(location)
    return render_template('edit.html', title='Beer List', beers=beers, location=location)


@app.route('/<location>')
@app.route('/<location>/')
def bars(location):
    if location not in locations:
        return 'Unknown Location'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = convert([r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))])
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return render_template('index.html', title='Beer List',
                           beers=[beer for beer in beers if beer['active'] == 'True'], location=location)


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(request.args.get('next') or '/')
    error = None
    next = request.args.get('next')
    form = LoginForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = BarUser(username, password)
        if user.is_authenticated():
            login_user(user)
            flash("You have logged in")
            session['logged_in'] = True
            session['roles'] = user.roles
            return redirect(next or url_for('index', error=error))
        error = "Login failed"
    return render_template('login.html', login=True, next=next, error=error, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out!')
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('links.html', title='links', locations=locations)
