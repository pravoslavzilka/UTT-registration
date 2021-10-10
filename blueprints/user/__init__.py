from flask import Blueprint, render_template

user_bp = Blueprint("user_bp", __name__, template_folder="templates", static_folder="static")


@user_bp.route("/sign-in/", methods=['GET'])
def sign_in_view():
    return render_template("user/sign_in.html")