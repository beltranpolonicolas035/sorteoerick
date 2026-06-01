from functools import wraps
from flask import session, redirect, url_for

def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logeado' not in session:
            return redirect(url_for('ingreso.login')) # Ajusta 'ingreso.login' a tu ruta real de login
        return f(*args, **kwargs)
    return decorated_function