from flask import Blueprint

h_admin_bp = Blueprint("h_admin_bp", __name__, template_folder="templates", static_folder="static")