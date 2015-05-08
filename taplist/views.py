import uuid
import json
import operator
import re
import yaml
import os

from collections import OrderedDict

#flask stuff
from flask import render_template, redirect, request, url_for, jsonify, session, flash
from flask.views import MethodView
from flask.ext.stormpath import groups_required, login_required, logout_user, user

#redis stuff
import redis
from redis.sentinel import Sentinel

#taplist libs
from taplist.utils import convert, get_colors
from taplist.form import BeerForm
from taplist.auth import role_required
from taplist import app

class TaplistView(MethodView):
    def __init__(self, *args, **kwargs):
        self.groups = [g.group.name for g in getattr(user, 'group_memberships', [None]) if g is not None]
        self.locations = app.config['LOCATIONS']
        self.config = app.config['CONFIG']
        super(TaplistView, self).__init__(*args, **kwargs)

class Entry(TaplistView):
    decorators=[
        login_required,
        role_required
    ]

    def _beer(self, form, location):
        beer = {
            'name': form.beername.data,
            'brewery': form.brewery.data,
            'type': form.beertype.data,
            'content': form.alcohols.data,
            'location': location
        }
        if re.match('^~?[0-9]+\.?[0-9]*$', beer['content']):
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
        return beer

    def get(self, location):
        #print([g.group.name for g in user.group_memberships])
        if location not in self.locations:
            return 'Unknown Location'
        form = BeerForm()
        beername = request.args.get('name', None)
        if beername:
            pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
            r = redis.Redis(connection_pool=pool)
            beer = r.hgetall(beername)
            form.beername.data = beer['name']
            form.brewery.data = beer['brewery']
            form.beertype.data = beer['type']
            form.pricepint.data = beer['pint']
            form.pricehalf.data = beer['half']
            form.pricegrowler.data = beer['growler']
            form.alcohols.data = beer['content']
            form.active.data = beer['active'] == 'True'
        return render_template('entry.html', title='Entry', form=form, beername=beername, roles=self.groups, locations=self.locations)

    def put(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        form = BeerForm()
        beer = self._beer(form, location)
        if app.config['DEVEL']:
            pool = redis.ConnectionPool(host='localhost', port=6379)
            r = redis.Redis(connection_pool=pool)
        else:
            sentinel = Sentinel([('localhost', 26379)], socket_timeout=1)
            r = sentinel.master_for('mymaster', socket_timeout=1)
        r.hmset(request.args.get('name'), beer)

        r.save()
        return redirect('/{0}/entry'.format(location))

    def post(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        form = BeerForm()
        print(request.form)
        beer = self._beer(form, location)
        if app.config['DEVEL']:
            pool = redis.ConnectionPool(host='localhost', port=6379)
            r = redis.Redis(connection_pool=pool)
        else:
            sentinel = Sentinel([('localhost', 26379)], socket_timeout=1)
            r = sentinel.master_for('mymaster', socket_timeout=1)
        if 'name' in request.args:
            r.hmset(request.args.get('name'), beer)
        else:
            r.hmset(
                'beer_{0}_{1}'.format(
                    location,
                    str(uuid.uuid4().get_hex().upper()[0:6])
                ),
                beer
            )

        r.save()
        return redirect('/{0}/entry'.format(location))


class Scroll(TaplistView):
    def get(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        colors = get_colors(location, self.config)
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        beers = convert([r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))])
        beers.sort(key=operator.itemgetter('brewery', 'name'))
        return render_template('scroll.html', title='Beer List',
                               beers=[beer for beer in beers if beer['active'] == 'True'], location=location,
                               colors=colors)


class Json(TaplistView):
    def get(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        beers=[]
        for key in r.keys('beer_{0}_*'.format(location)):
            beer = convert(r.hgetall(key))
            beer['beername'] = key
            beers.append(beer)
        for beer in beers:
            if 'pint' not in beer:
                continue
            beer['pint'] = beer['pint'].replace('.0', '')
            beer['half'] = beer['half'].replace('.0', '')
            beer['growler'] = beer['growler'].replace('.0', '')
        beers.sort(key=operator.itemgetter('brewery', 'name'))
        return jsonify({'beers': [b for b in beers if b['active'] == 'True']})


class Locations(TaplistView):
    def get(self):
        return jsonify({'locations': self.locations})


class Edit(TaplistView):
    decorators=[
        login_required,
        role_required
    ]

    def get(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        colors = get_colors(location, self.config)
        if app.config['DEVEL']:
            pool = redis.ConnectionPool(host='localhost', port=6379)
            r = redis.Redis(connection_pool=pool)
        else:
            sentinel = Sentinel([('localhost', 26379)], socket_timeout=1)
            r = sentinel.master_for('mymaster', socket_timeout=1)
        beers = []
        for key in r.keys('beer_{0}_*'.format(location)):
            beer = convert(r.hgetall(key))
            beer['beername'] = key
            beers.append(beer)
        beers.sort(key=operator.itemgetter('brewery', 'name'))
        return render_template('edit.html', title='Beer List', beers=beers, location=location, colors=colors, roles=self.groups, locations=self.locations)

    def post(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        if app.config['DEVEL']:
            pool = redis.ConnectionPool(host='localhost', port=6379)
            r = redis.Redis(connection_pool=pool)
        else:
            sentinel = Sentinel([('localhost', 26379)], socket_timeout=1)
            r = sentinel.master_for('mymaster', socket_timeout=1)
        beers = {key: r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))}

        for beername, beer in beers.items():
            r.hset(beername, 'active', 'True' if beername in request.form.getlist('checks') else 'False')

        for beer in request.form.getlist('delete'):
            r.delete(beer)

        r.save()
        beers = []
        for key in r.keys('beer_{0}_*'.format(location)):
            beer = convert(r.hgetall(key))
            beer['beername'] = key
            beers.append(beer)

        beers.sort(key=operator.itemgetter('brewery', 'name'))

        return redirect(location)


class BarLists(TaplistView):
    def get(self, location):
        if location not in self.locations:
            return 'Unknown Location'
        colors = get_colors(location, self.config)
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
        r = redis.Redis(connection_pool=pool)
        beers = convert([r.hgetall(key) for key in r.keys('beer_{0}_*'.format(location))])
        beers.sort(key=operator.itemgetter('brewery', 'name'))
        return render_template('index.html', title='Beer List',
                               beers=[beer for beer in beers if beer['active'] == 'True'], location=location,
                               colors=colors, locations=self.locations, roles=self.groups)


@app.route('/logout')
@login_required
def logout():
    """
    Log out a logged in user.  Then redirect them back to the main page of the
    site.
    """
    logout_user()
    session.clear()
    return redirect(url_for('index'))

class Index(TaplistView):
    def get(self):
        groups = [g.group.name for g in getattr(user, 'group_memberships', [None]) if g is not None]
        return render_template('links.html', title='links', locations=self.locations, roles=groups)
