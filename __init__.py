from flask import Flask, render_template, redirect, url_for, flash
from blueprints.admin.__init__ import admin_bp
from blueprints.head_admin.__init__ import h_admin_bp
from blueprints.user.__init__ import user_bp
from database import db_session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from threading import Thread
from models import User, Admin
import os


UPLOAD_FOLDER = '/static/files'

app = Flask(__name__)


app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(h_admin_bp, url_prefix="/head-admin")
app.register_blueprint(user_bp, url_prefix="/user")


app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'


csrf = CSRFProtect(app)
UsersStatus = []

app.jinja_env.autoescape = True | False

app.config["MAIL_SERVER"] = "smtp.websupport.sk"
app.config["MAIL_PORT"] = "465"
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "registracia@uciacasatrnava.sk"
app.config["MAIL_PASSWORD"] = "LearningTT2021"
app.config['MAIL_DEFAULT_SENDER'] = "registracia@uciacasatrnava.sk"

mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_bp.sign_in_view"
login_manager.login_message = "Musíte sa prihlásiť"
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"


@app.route("/")
def main_page():
    return redirect(url_for("user_bp.user_page"))


@app.route("/send-email/<email>/")
def send_reg_email(email):

    msg = Message(sender="registracia@uciacasatrnava.sk")
    msg.subject = "Ďakujeme za vašu registráciu"
    msg.recipients = [email]
    msg.html = render_template("emails/reg-email.html")
    Thread(target=send_email, args=(app, msg)).start()

    return redirect(url_for("user_bp.user_page_after_reg"))


@app.route("/email-ask-confirm/")
def email_ask_confirm():
    users = User.query.filter(User.confirm == False).all()
    for user in users:
        msg = Message(sender="registracia@uciacasatrnava.sk")
        msg.subject = "Potvrdenie registrácie"
        msg.recipients = [user.email]
        msg.html = render_template("emails/confirm-email.html", user_hash=user.code)
        Thread(target=send_email, args=(app, msg)).start()

    flash("Užívatelia boli vyzvaný na potvrdenie registrácie", "success")
    return redirect(url_for("h_admin_bp.stats"))


def send_email(app, msg):
    with app.app_context():
        mail.send(msg)


@app.errorhandler(405)
def error_405(error):
    return render_template("404.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first() or Admin.query.filter(Admin.id == user_id).first()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
