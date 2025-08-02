from flask import Blueprint, render_template
welcome_bp = Blueprint('welcome', __name__)

@welcome_bp.route('/')
def welcome():
    return render_template('welcome/welcome.html')