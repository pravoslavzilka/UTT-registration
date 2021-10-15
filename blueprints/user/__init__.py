from flask import Blueprint, render_template, session, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import Admin, User, TicketType, Ticket, TicketTypeType
from database import db_session
import uuid

user_bp = Blueprint("user_bp", __name__, template_folder="templates", static_folder="static")


@user_bp.route("/user-page/")
def user_page():
    ttts = TicketTypeType.query.all()
    tts = TicketType.query.all()
    return render_template("user/user_page.html",  tts=tts, ttts=ttts, user=current_user)


@user_bp.route("/user-page-ar/")
def user_page_after_reg():
    ttts = TicketTypeType.query.all()
    tts = TicketType.query.all()
    return render_template("user/user_page.html", tts=tts, ttts=ttts, user=current_user, after_reg=True)


@user_bp.route("/add-ticket/", methods=['POST'])
def add_ticket():

    ticket_id = request.form["ticket-id"]
    tt = TicketType.query.filter(TicketType.id == ticket_id).first()

    already_ticket = Ticket.query.filter(Ticket.user == current_user, Ticket.ticket_type == tt).first()

    if tt and len(tt.tickets) < tt.max_cap and not already_ticket:
        ticket = Ticket(tt, current_user)
        db_session.add(ticket)
        db_session.commit()
        flash(f"'{tt.name}' bol pridaný do tvojho lístku", "success")

    flash("Na tento program už máte rezervovaný lístok", "info")

    return redirect(url_for("user_bp.user_page"))


@user_bp.route("/change-ticket/", methods=['POST'])
def change_ticket():

    ticket_id = request.form["ticket-id"]
    original_id = int(request.form["original-ticket"])

    original_ticket = Ticket.query.filter(Ticket.id == original_id).first()
    if original_ticket in current_user.tickets:

        tt = TicketType.query.filter(TicketType.id == ticket_id).first()

        already_ticket = Ticket.query.filter(Ticket.user == current_user, Ticket.ticket_type == tt).first()

        if tt and len(tt.tickets) < tt.max_cap and not already_ticket:
            ticket = Ticket(tt, current_user)
            db_session.add(ticket)
            db_session.delete(original_ticket)
            db_session.commit()
            flash(f"'{tt.name}' bol pridaný do tvojho lístku", "success")

        flash("Na tento program už máte rezervovaný lístok", "info")

    return redirect(url_for("user_bp.user_page"))


@user_bp.route("/delete-ticket/<int:ticket_id>/")
def del_ticket(ticket_id):
    ticket = Ticket.query.filter(Ticket.id == ticket_id).first()
    db_session.delete(ticket)
    db_session.commit()

    return redirect(url_for("user_bp.user_page"))


@user_bp.route("/change-profile/", methods=['POST'])
def change_profile():
    current_user.name = request.form["user-name"]
    current_user.age = request.form["user-age"]
    current_user.email = request.form["user-email"]
    current_user.city = request.form["user-city"]

    db_session.commit()
    flash("Profil bol úspešne upravený", "success")
    return redirect(url_for("user_bp.user_page"))


@user_bp.route("/confirm-user/<hash_user>/", methods=['GET'])
def confirm_user_view(hash_user):
    user = User.query.filter(User.code == hash_user).first()
    if user.confirm:
        return redirect(url_for("user_bp.user_page"))

    flash("Na potvrdenie registrácie si vytvorte heslo do vášho konta", "info")
    return render_template("user/confirm_reg.html", user=user)


@user_bp.route("/confirm-user/<hash_user>/", methods=['POST'])
def confirm_user_fun(hash_user):
    user = User.query.filter(User.code == hash_user).first()

    user.email = request.form["user-email"]
    user.confirm = True
    user.set_password(request.form["user-password"])
    db_session.commit()

    login_user(user)
    flash("Vitajte vo svojom konte. Pred festivalom sa ujistite, že máte svoj QR kód s lístok na lestival stiahnutý", "success")
    return redirect(url_for("user_bp.user_page"))


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
        return redirect(url_for("user_bp.user_page"))

    admin = Admin.query.filter(Admin.email == request.form["email"]).first()

    if admin and admin.check_password(request.form["password"]):

        login_user(admin)
        session["permit"] = admin.rank

        flash("Vitaj späť", "success")
        return redirect(url_for("user_bp.user_page"))

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
    tts = TicketType.query.all()
    return render_template("user/sign_up.html", tts=tts)


@user_bp.route("/sign-up/", methods=['POST'])
def sign_up_fun():
    name = request.form["user-name"]
    age = request.form["user-age"]
    email = request.form["user-email"]
    password = request.form["user-password"]
    city = request.form["user-city"]
    otp = request.form["user-otp"]
    who = request.form["user-who"]
    where = request.form["user-where"]

    block1 = TicketType.query.filter(TicketType.name == request.form["user-block1"]).first()
    block2 = TicketType.query.filter(TicketType.name == request.form["user-block2"]).first()
    block3 = TicketType.query.filter(TicketType.name == request.form["user-block3"]).first()

    user = User.query.filter(User.email == email).first()

    if user:
        flash("Tento email je už používaný iným uživateľom", "danger")
        return redirect(url_for("user_bp.sign_up_view"))

    user = User(name, email)
    user.set_password(password)
    user.city = city
    user.age = age
    user.otp = otp
    user.who = who
    user.where = where
    user.code = uuid.uuid4().hex
    user.confirm = True

    if request.form.get("user-news"):
        user.news = True
    else:
        user.news = False
    if block1:
        if block1.max_cap <= len(Ticket.query.filter(Ticket.ticket_type == block1).all()):
            ticket1 = Ticket(block1, user)
            db_session.add(ticket1)
    if block2:
        if block2.max_cap <= len(Ticket.query.filter(Ticket.ticket_type == block2).all()):
            ticket2 = Ticket(block2, user)
            db_session.add(ticket2)
    if block3:
        if block3.max_cap <= len(Ticket.query.filter(Ticket.ticket_type == block2).all()):
            ticket3 = Ticket(block3, user)
            db_session.add(ticket3)

    db_session.add(user)
    db_session.commit()

    ttt = TicketTypeType.query.filter(TicketTypeType.name == "Prednášky").first()
    tts = TicketType.query.filter(TicketType.ticket_type_type == ttt).all()

    for tt in tts:
        if request.form.get("user-"+str(tt.id)):
            ticket = Ticket(tt, user)
            db_session.add(ticket)
            db_session.commit()

    login_user(user)

    flash("Tvoj profil bol úspešne vytvorený", "success")
    return redirect(url_for("user_bp.user_page_after_reg"))
