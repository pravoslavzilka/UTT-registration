from flask import Blueprint, render_template, redirect, url_for, session, flash
from models import TicketTypeType, TicketType, Ticket, User
from functools import wraps
from database import db_session

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
