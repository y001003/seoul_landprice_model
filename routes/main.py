from flask import Flask, Blueprint, render_template

bp = Blueprint('main',__name__,url_prefix='/')

@bp.route('/')
def result():
    return render_template('main.html')

