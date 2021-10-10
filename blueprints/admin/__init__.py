from flask import Blueprint, render_template, redirect, url_for, request, flash

admin_bp = Blueprint("admin_bp", __name__, template_folder="templates", static_folder="static")

