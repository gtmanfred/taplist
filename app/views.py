from flask import render_template, redirect, request, url_for, jsonify, session, flash
from flask_login import login_required, login_user, logout_user, current_user
from app import app
from app.form import BeerForm, LoginForm
from app.login import BarUser
from app.auth import role_required
import redis
from redis.sentinel import Sentinel
import json
import operator
import re

locations = [
        'broadway',
        'huebner',
        'gastropub',
        'thebridge'
        ]

@app.route('/<location>/entry', methods=['GET', 'POST'])
@login_required
@role_required
def entry(location):
    if location not in locations:
        return 'Unknown Location'
    form = BeerForm()
    if request.method == 'POST':
        #pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        #r = redis.Redis(connection_pool=pool)
        sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
        r = sentinel.master_for('mymaster', socket_timeout=0.1)
        beer = {
            'name': form.beername.data,
            'brewery': form.brewery.data,
            'type': form.beertype.data,
            'content': form.alcohols.data,
            'location': location
        }
        if re.match('[0-9]+\.?[0-9]*', beer['content']):
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


@app.route('/<location>/json', methods=['GET'])
def get_json(location):
    if location not in locations:
        return 'Unknown Location'
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r = redis.Redis(connection_pool=pool)
    beers = [json.loads(r.get(key).decode()) for key in r.keys('beer_{0}_*'.format(location))]
    beers.sort(key=operator.itemgetter('brewery', 'name'))
    return jsonify({'beers': [b for b in beers if b['active']]})


@app.route('/<location>/edit', methods=['GET', 'POST'])
@login_required
@role_required
def editlist(location):
    if location not in locations:
        return 'Unknown Location'
    #pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    #r = redis.Redis(connection_pool=pool)
    sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
    r = sentinel.master_for('mymaster', socket_timeout=0.1)
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
    return redirect('/')


@app.route('/')
def index():
    return render_template('links.html', title='links', locations=locations)
