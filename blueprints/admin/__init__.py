from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import TicketTypeType, TicketType, Ticket

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", static_folder="static")


@admin_bp.route("/check-tickets/")
def check_tickets_view():
    ttts = TicketTypeType.query.all()
    return render_template("admin/tickets_check_menu.html", ttts=ttts)


@admin_bp.route("/scan-tickets/<int:tt_id>/")
def tickets_scan(tt_id):
    tt = TicketType.query.filter(TicketType.id == tt_id).first()

    if tt:
        tickets = Ticket.query.filter(Ticket.ticket_type == tt).all()
        list_of_users = [ticket.user.code for ticket in tickets]
        return render_template("admin/tickets_scan.html", list_of_users=list_of_users, tt=tt)

    return redirect(url_for("admin.check_tickets_view"))
