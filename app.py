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
    return render_template('pages/placeholder.home.html', username=session["username"])


@app.route('/locations')
@login_required
def locations():
    with conn.cursor() as cursor:
        # Create a new record
        sql = "SELECT * FROM ServiceLocations WHERE cid = %s"
        affected_rows = cursor.execute(sql, (session["cid"]))
        data = cursor.fetchall()

        conn.commit()

    return render_template('pages/service_locations.html', locations=data)


@app.route('/locations/<int:lid>')
@login_required
def location_devices(lid: int):
    with conn.cursor() as cursor:
        # Create a new record
        sql_devices = """
                SELECT * FROM ServiceLocations SL
                    JOIN Devices D ON SL.lid = D.lid
                    JOIN AvailableModels AM ON D.mid = AM.mid
                WHERE SL.cid = %s AND SL.lid = %s
              """
        affected_rows = cursor.execute(sql_devices, (session["cid"], lid))
        devices = cursor.fetchall()

        sql_location = "SELECT unit, address, zcode FROM ServiceLocations WHERE lid = %s"
        cursor.execute(sql_location, (lid))
        location = cursor.fetchone()

        conn.commit()

    return render_template('pages/devices.html', devices=devices, location=location)


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

    return render_template('forms/login.html', form=form)


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

    return render_template('forms/register.html', form=form)


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
