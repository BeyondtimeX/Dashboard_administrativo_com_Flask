from flask import Flask, request, redirect, render_template, Response, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user
from functools import wraps
from admin.Admin import start_views
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
import datetime

from forms import LoginForm
import controllers as ctrl

# Criação e configuração da aplicação
def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config.from_pyfile('config.py')
    
    app.secret_key = config.SECRET
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_ADMIN_SWATCH'] = 'paper'

    # Inicialização das extensões
    db = SQLAlchemy(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    Bootstrap(app)
    csrf = CSRFProtect(app)
    
    db.init_app(app)
    config.APP = app
    
    start_views(app, db)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    return app, db, login_manager

# Função principal para iniciar a aplicação
def main(config):
    app, db, login_manager = create_app(config)
    
    @login_manager.user_loader
    def load_user(user_id):
        return ctrl.getUserById(user_id)

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            user = ctrl.login(form.email.data, form.password.data)
            if user:
                if user.role == 2:
                    data = {'status': 401, 'msg': 'Seu usuário não tem permissão para acessar o admin', 'type': 2, 'form': form}
                else:
                    login_user(user, remember=True, duration=datetime.timedelta(minutes=5), fresh=True)
                    return redirect('/admin')
            else:
                data = {'status': 401, 'msg': 'Dados de usuário incorretos', 'type': 1, 'form': form}
        else:
            data = {'status': 401, 'msg': 'Formulário inválido', 'type': 1, 'form': form}
        
        return render_template('login.html', data=data)

    @app.route('/report', methods=['POST'])
    def report():
        if not current_user.is_authenticated:
            return jsonify({'error': 'Não autorizado'}), 401
        
        state = request.form.get('state')
        disease = request.form.get('disease')
        estadoSaude = request.form.get('estadoSaude')
        if not state or not disease:
            return jsonify({'error': 'Parâmetros incompletos'}), 400

        patients = ctrl.reportByState(state, disease)
        return jsonify(patients), 200

    @app.route('/logout')
    def logout_send():
        logout_user()
        form = LoginForm()
        return render_template('login.html', data={'status': 200, 'msg': 'Usuário deslogado com sucesso!', 'type': 3, 'form': form})

    return app

if __name__ == '__main__':
    from config import Config  # Certifique-se de que existe um módulo de configuração
    app = main(Config)
    app.run(debug=True)  # Remover debug=True em produção
