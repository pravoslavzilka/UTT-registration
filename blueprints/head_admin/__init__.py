from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import TicketTypeType, TicketType, Admin
import datetime
from database import db_session

h_admin_bp = Blueprint("h_admin_bp", __name__, template_folder="templates", static_folder="static")


@h_admin_bp.route("/operations/")
def operations():
    ttts = TicketTypeType.query.all()
    return render_template("head_admin/head_operations.html", ttts=ttts)


@h_admin_bp.route("/add-piece/", methods=['POST'])
def add_piece():
    name = request.form["piece-name"]
    speaker = request.form["piece-speaker"]
    start = datetime.datetime.strptime(request.form["piece-start"], '%H:%M').time()
    max_cap = int(request.form["piece-cap"])
    ttt = TicketTypeType.query.filter(TicketTypeType.id == int(request.form["piece-ttt"])).first()

    tt = TicketType(name, speaker, max_cap)
    tt.start = start
    tt.ticket_type_type = ttt

    db_session.add(tt)
    db_session.commit()

    flash(f"Nová časť programu v {ttt.name} bola pridaná", "success")
    return redirect(url_for("h_admin_bp.operations"))


@h_admin_bp.route("/edit-piece/", methods=['POST'])
def edit_piece():
    name = request.form["piece-name"]
    speaker = request.form["piece-speaker"]
    start = request.form["piece-start"]
    max_cap = int(request.form["piece-cap"])
    tt = TicketType.query.filter(TicketType.id == int(request.form["piece-id"])).first()

    tt.name = name
    tt.speaker = speaker
    if len(start)>5:
        start = datetime.datetime.strptime(start, '%H:%M:%S').time()
    else:
        start = datetime.datetime.strptime(start, '%H:%M').time()
    tt.start = start
    tt.max_cap = max_cap

    db_session.commit()

    flash(f"Časť programu '{tt.name}' bola upravená", "success")
    return redirect(url_for("h_admin_bp.operations"))


@h_admin_bp.route("/delete-piece/<int:piece_id>/")
def delete_piece(piece_id):
    tt = TicketType.query.filter(TicketType.id == piece_id).first()

    db_session.delete(tt)
    db_session.commit()

    flash(f"Časť programu '{tt.name}' bola vymazaná", "success")
    return redirect(url_for("h_admin_bp.operations"))


@h_admin_bp.route('add-admin',methods=['POST'])
def add_admin():
    admin = Admin(request.form["admin-name"], request.form["admin-email"], 2)
    admin.set_password(request.form["admin-password"])

    db_session.add(admin)
    db_session.commit()

    flash("Nový admin bol pridaný", "success")
    return redirect(url_for("h_admin_bp.operations"))

