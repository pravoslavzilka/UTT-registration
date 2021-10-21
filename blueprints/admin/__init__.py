from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import TicketTypeType, TicketType, Ticket, User
from functools import wraps
from database import db_session
import uuid

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", static_folder="static")


def check_admin(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if "permit" in session:
            return func(*args, **kwargs)
        return redirect(url_for("user_bp.user_page"))
    return inner


@admin_bp.route("/check-tickets/")
@check_admin
def check_tickets_view():
    ttts = TicketTypeType.query.all()
    return render_template("admin/tickets_check_menu.html", ttts=ttts)


@admin_bp.route("/add-user-ticket/<user_hash>/<tt_id>/")
@check_admin
def add_tickets_fun(user_hash, tt_id):
    tt = TicketType.query.filter(TicketType.id == tt_id).first()
    u = User.query.filter(User.code == user_hash).first()
    if tt and u:
        tt.users.append(u)
        db_session.commit()
        flash("User bol schválený", "success")
        return redirect(url_for("admin_bp.tickets_scan", tt_id=tt_id))

    flash("User alebo program sa nenašiel", "danger")
    return redirect(url_for("admin.check_tickets_view"))


@admin_bp.route("/scan-tickets/<int:tt_id>/")
@check_admin
def tickets_scan(tt_id):
    tt = TicketType.query.filter(TicketType.id == tt_id).first()

    if tt:
        tickets = Ticket.query.filter(Ticket.ticket_type == tt).all()
        list_of_users = [ticket.user.code for ticket in tickets]
        return render_template("admin/tickets_scan.html", list_of_users=list_of_users, tt=tt)

    return redirect(url_for("admin.check_tickets_view"))


@admin_bp.route("/user/<int:user_id>/")
@check_admin
def admin_user_page(user_id):
    user = User.query.filter(User.id == user_id).first()
    ttts = TicketTypeType.query.all()
    tts = TicketType.query.all()
    return render_template("admin/admin_user_page.html", user=user, tts=tts, ttts=ttts)


@admin_bp.route("/user-add-ticket/<int:user_id>/", methods=['POST'])
@check_admin
def add_ticket(user_id):

    ticket_id = request.form["ticket-id"]
    tt = TicketType.query.filter(TicketType.id == ticket_id).first()
    current_user = User.query.filter(User.id == user_id).first()

    already_ticket = Ticket.query.filter(Ticket.user == current_user, Ticket.ticket_type == tt).first()

    if tt and len(tt.tickets) < tt.max_cap and not already_ticket:
        ticket = Ticket(tt, current_user)
        db_session.add(ticket)
        db_session.commit()
        flash(f"'{tt.name}' bol pridaný do lístku", "success")
    else:
        flash("Na tento program už má rezervovaný lístok", "info")

    return redirect(url_for("admin_bp.admin_user_page", user_id=user_id))


@admin_bp.route("/user-change-ticket/<int:user_id>/", methods=['POST'])
@check_admin
def change_ticket(user_id):

    current_user = User.query.filter(User.id == user_id).first()

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
            flash(f"'{tt.name}' bol pridaný do lístku", "success")
        else:
            flash("Na tento program už má rezervovaný lístok", "info")

    return redirect(url_for("admin_bp.admin_user_page", user_id=user_id))


@admin_bp.route("/user-delete-ticket/<int:user_id>/<int:ticket_id>/")
@check_admin
def del_ticket(user_id, ticket_id):
    ticket = Ticket.query.filter(Ticket.id == ticket_id).first()
    db_session.delete(ticket)
    db_session.commit()

    return redirect(url_for("admin_bp.admin_user_page", user_id=user_id))


@admin_bp.route("/user-change-profile/<int:user_id>/", methods=['POST'])
@check_admin
def change_profile(user_id):
    current_user = User.query.filter(User.id == user_id).first()
    current_user.name = request.form["user-name"]
    current_user.age = request.form["user-age"]
    current_user.email = request.form["user-email"]
    current_user.city = request.form["user-city"]

    db_session.commit()
    flash("Profil bol úspešne upravený", "success")
    return redirect(url_for("admin_bp.admin_user_page", user_id=user_id))


@admin_bp.route("/delete-user/<int:user_id>/")
@check_admin
def delete_user(user_id):
    u = User.query.filter(User.id == user_id).first()
    db_session.delete(u)
    db_session.commit()

    flash(f"User {u.name} bol odstránený", "success")
    return redirect(url_for("admin_bp.admin_sign_up"))


@admin_bp.route("/public-sign-up/", methods=['GET'])
@check_admin
def admin_sign_up():
    tts = TicketType.query.all()
    return render_template("admin/admin_sign_up.html", tts=tts)


@admin_bp.route("/all-users/")
@check_admin
def all_users():
    users = User.query.all()
    return render_template("admin/users_list.html", users=users)


@admin_bp.route("/public-sign-up/", methods=['POST'])
@check_admin
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
        return redirect(url_for("admin_bp.admin_sign_up"))

    user = User(name, email)
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
        if block1.max_cap > len(Ticket.query.filter(Ticket.ticket_type == block1).all()):
            ticket1 = Ticket(block1, user)
            db_session.add(ticket1)
    if block2:
        if block2.max_cap > len(Ticket.query.filter(Ticket.ticket_type == block2).all()):
            ticket2 = Ticket(block2, user)
            db_session.add(ticket2)
    if block3:
        if block3.max_cap > len(Ticket.query.filter(Ticket.ticket_type == block2).all()):
            ticket3 = Ticket(block3, user)
            db_session.add(ticket3)

    db_session.add(user)
    db_session.commit()

    ttt = TicketTypeType.query.filter(TicketTypeType.name == "Ďaľší Program").first()
    tts = TicketType.query.filter(TicketType.ticket_type_type == ttt).all()

    for tt in tts:
        if request.form.get("user-"+str(tt.id)):
            ticket = Ticket(tt, user)
            db_session.add(ticket)
            db_session.commit()

    flash("User bol vytvorený", "success")
    return redirect(url_for("admin_bp.admin_user_page", user_id=user.id))
