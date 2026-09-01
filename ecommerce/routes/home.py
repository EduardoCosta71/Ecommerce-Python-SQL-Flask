from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc
from config import get_db_connection


def home_registrar(app):

    @app.route('/')
    def inicio():
        return redirect('/home')

    #Rota para a página inicial(Aqui você pode adicionar a lógica para exibir os produtos, categorias, etc.)
    @app.route('/home')
    def home():

       return render_template('index.html')
    
    #@app.route('/login')
    #def login():
     #   return render_template('usuarios/login.html')

    #@app.route('/cadastro')
    #def cadastro():
     #   return render_template('usuarios/cadastro.html')