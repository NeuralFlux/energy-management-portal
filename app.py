#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from functools import wraps
from flask import Flask, flash, render_template, request, session, url_for, redirect
from flask_wtf import CSRFProtect
import logging
from logging import Formatter, FileHandler
from forms import *
import os

import pymysql
import hashlib
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
csrf = CSRFProtect(app)

conn = pymysql.connect(
    host='localhost',
    user=app.config.get('MYSQL_USER_ID'),
    password=app.config.get('MYSQL_PASSWD'),
    database="SHEMS",
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)


#----------------------------------------------------------------------------#
# Utils
#----------------------------------------------------------------------------#

def login_required(f):

    @wraps(f)
    def username_dec(*args, **kwargs):
        if not "cid" in session:
            flash("Please login to access your dashboard")
            return redirect('/login')
        return f(*args, **kwargs)

    return username_dec

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
@login_required
def home():
    return render_template('pages/dashboard.html', username=session["username"], logged_in=True)


@app.route('/locations', methods=["GET", "POST"])
@login_required
def locations():
    form = ServiceLocationForm()
    with conn.cursor() as cursor:
        sql = "SELECT * FROM ServiceLocations WHERE cid = %s"
        affected_rows = cursor.execute(sql, (session["cid"]))
        data = cursor.fetchall()

        conn.commit()

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            # Create a new record
            sql = """
                    INSERT INTO ServiceLocations (cid, unit, address, zcode,
                    billing_begin_date, sq_footage, num_bedrooms, num_occupants)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                  """
            sql_vars = (
                session["cid"], form.unit.data, form.address.data, form.zcode.data,
                datetime.today().strftime('%Y-%m-%d'), form.sq_footage.data,
                form.num_bedrooms.data, form.num_bathrooms.data
            )
            affected_rows = cursor.execute(sql, sql_vars)

            if affected_rows > 0:
                flash("Successfully added new location")
                conn.commit()
                return redirect("/locations")

    return render_template('pages/service_locations.html', locations=data, form=form, logged_in=True)


@app.route('/devices', methods=["GET", "POST"])
@login_required
def devices():
    form = DeviceForm()

    with conn.cursor() as cursor:
        # Create a new record
        sql_models = """SELECT mid, type, model_num FROM AvailableModels"""
        affected_rows = cursor.execute(sql_models, ())
        models = cursor.fetchall()

        sql_locations = """SELECT SL.lid, SL.unit, SL.address, SL.zcode
                           FROM ServiceLocations SL
                                JOIN Customers C ON SL.cid = C.cid
                            WHERE SL.cid = %s
                           """
        affected_rows = cursor.execute(sql_locations, (session["cid"]))
        locs = cursor.fetchall()

        form.model_id.choices = [
            (model["mid"], " ".join([model["type"], model["model_num"]])) for model in models
        ]
        form.location_id.choices = [
            (loc["lid"], " ".join([loc["unit"], loc["address"]])) for loc in locs
        ]

        conn.commit()

    with conn.cursor() as cursor:
        # Create a new record
        sql_devices = """
                SELECT D.dev_name, AM.type, AM.model_num, SL.unit, SL.address, SL.zcode
                FROM Customers C
                    JOIN ServiceLocations SL ON C.cid = SL.cid
                    JOIN Devices D ON SL.lid = D.lid
                    JOIN AvailableModels AM ON D.mid = AM.mid
                WHERE C.cid = %s
              """
        affected_rows = cursor.execute(sql_devices, (session["cid"]))
        devices = cursor.fetchall()

        conn.commit()
    
    if form.validate_on_submit():
        with conn.cursor() as cursor:
            # Create a new record
            sql = """
                    INSERT INTO Devices (dev_name, mid, lid)
                    VALUES (%s, %s, %s)
                  """
            sql_vars = (
                form.dev_name.data, form.model_id.data, form.location_id.data
            )
            affected_rows = cursor.execute(sql, sql_vars)

            if affected_rows > 0:
                flash("Successfully added new device")
                conn.commit()
                return redirect("/devices")

    return render_template('pages/devices.html', form=form,
                           devices=devices, models=models, logged_in=True)

@app.route('/visualize')
@login_required
def visualize():
    with conn.cursor() as cursor:
        # Create a new record
        sql = """
                WITH CustFilter(cid) AS (
                    SELECT cid
                    FROM Customers
                    WHERE cid = %s
                )

                SELECT
                    D.dev_id, D.dev_name
                    SUM(E.value) AS TotalEnergyConsumption
                FROM
                    CustFilter C
                JOIN ServiceLocations SL ON C.cid = SL.cid
                JOIN Devices D ON SL.lid = D.lid
                JOIN Events E ON D.dev_id = E.dev_id
                WHERE E.label = 'energy use'
                GROUP BY
                    D.dev_id, D.dev_name
                """
        affected_rows = cursor.execute(sql, (session["cid"]))
        data = cursor.fetchall()
    
    return render_template('pages/vis.html', data=data, logged_in=True)


@app.route('/logout')
@login_required
def logout():
    session.pop('username')
    session.pop('cid')
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        with conn.cursor() as cursor:
            # Create a new record
            sql = "SELECT * FROM Customers WHERE username = %s and hashed_password = %s"
            password_hash = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
            affected_rows = cursor.execute(sql, (form.name.data, password_hash))

            # Commit the changes
            if affected_rows > 0:
                data = cursor.fetchone()
                session['username'] = form.name.data
                session['cid'] = data["cid"]
                conn.commit()
        
        if affected_rows > 0:
            return redirect('/')
        else:
            flash("Login failed", category="warning")

    return render_template('forms/login.html', form=form, logged_in=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        with conn.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `Customers` (`username`, `email`, `hashed_password`) VALUES (%s, %s, %s)"
            password_hash = hashlib.sha256(form.password.data.encode('utf-8')).hexdigest()
            affected_rows = cursor.execute(sql, (form.name.data, form.email.data, password_hash))

            # Commit the changes
            if affected_rows > 0:
                conn.commit()
            print(f"Account Creation, inserted {affected_rows}")
        
        flash("Successfully created your account, please login", category="info")
        return redirect('/login')

    return render_template('forms/register.html', form=form, logged_in=True)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
