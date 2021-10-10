from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import Admin, User

user_bp = Blueprint("user_bp", __name__, template_folder="templates", static_folder="static")


@user_bp.route("/sign-in/", methods=['GET'])
def sign_in_view():
    return render_template("user/sign_in.html")


@user_bp.route("/sign-in/", methods=['POST'])
def sign_in_fun():

    user = User.query.filter(User.email == request.form["email"]).first()

    if user and user.check_password(request.form["password"]):

        if request.form.get("auto-fill"):
            login_user(user, remember=True)
        else:
            login_user(user)

        flash("Vitaj späť", "success")
        return redirect(url_for("main_page"))

    admin = Admin.query.filter(Admin.email == request.form["email"]).first()

    if admin and admin.check_password(request.form["password"]):

        login_user(admin)
        session["permit"] = admin.rank

        flash("Vitaj späť", "success")
        return redirect(url_for("main_page"))

    flash("Chybný email alebo heslo", "danger")
    return render_template("user/sign_in.html")


@user_bp.route("/sign-out/")
@login_required
def sign_out():
    logout_user()
    if "permit" in session:
        session.pop("permit")
    flash("Bol si odhlásený","success")
    return redirect(url_for("main_page"))


@user_bp.route("/sign-up/", methods=['GET'])
def sign_up_view():
    return render_template("user/sign_up.html")
