from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pyodbc

def get_db_connection():
    #Função para estabelecer conexão com o banco de dados SQL Server
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  # Substitua pelo nome do seu servidor e instância
        'DATABASE=Ecommerce;'  # Substitua pelo nome do seu banco de dados
        'Trusted_Connection=yes;'
    )

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