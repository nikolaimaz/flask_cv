from flask import Flask, render_template, url_for, request, flash, session, redirect,send_file
from flask_sqlalchemy import SQLAlchemy
import smtplib
import os
from dotenv import load_dotenv
from datetime import date
import re


# for downloading configurations
load_dotenv()

# App configurations

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')

# Connecting to Postgres
DB_CONFIGS = os.getenv('DB_CONF')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_CONF')
db = SQLAlchemy(app)

# SMTP configs
MY_MAIL=os.getenv('MAIL')
MY_PASS=os.getenv('PASS')

# Switching off track modifications
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Connecting to existing database and model
class Contacts (db.Model):
    table = db.Table('contacts', db.metadata, autoload=True, autoload_with=db.engine)


# Main page

@app.route("/", methods=["POST", "GET"])
def message_form():
    if request.method == 'POST':
        check_name = re.compile('([a-z])', re.IGNORECASE)                                  # Symbols checker
        form_name = check_name.search(request.form['name'])
        data = request.form
        if len(request.form['name']) > 2 and form_name:                                    # Name length checker
            flash('Message has been sent', category='success')
            send_mail(data['name'], data['email'], data['message'])
            today_date= date.today()
            a = Contacts(name=data['name'], email=data['email'], message=data['message'], date=today_date)  # Process of adding in DB
            db.session.add(a)
            db.session.flush()
            db.session.commit()                                                             # Pushed to DB
            return redirect(url_for("message_form"))
        else:
            return render_template("index.html")
            flash("Error please check you're name ", category='error')
    return render_template("index.html")


@app.route("/download", methods=["GET"])
def download():
    if request.method == 'GET':
        return send_file(os.getenv('CV'), attachment_filename='Mikolai_Mazurek_VisualCV_Resume.pdf')


@app.errorhandler(404)
def not_found(error):
    return ('Error 404'), 404


def send_mail(name, email, message):
    message_to_me = f'Subject:New Message\n\nName: {name}\nEmail: {email}\nMessage: {message}'
    message_to_client = f'Subject:Mikolai Autoreply\n' \
                        f'\nThanks for contacting me,I will review  message as soon as possible :)'
    with smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls()
        connection.login(user=MY_MAIL, password=MY_PASS)
        connection.sendmail(from_addr=MY_MAIL, to_addrs="mikolajmazurekwork@gmail.com", msg=message_to_me)
        connection.sendmail(from_addr=MY_MAIL, to_addrs=email, msg=message_to_client)


if __name__ == "__main__":
    app.run(debug=True)
