from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pyodbc

def get_db_connection():
    #Função para estabelecer conexão com o banco de dados SQL Server
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  # Substitua pelo nome do seu servidor e instância
        'DATABASE=Ecommerce;'  # Substitua pelo nome do seu banco de dados
        'Trusted_Connection=yes;'
    )


def usuarios_registrar(app):


    def validar_email(email):

        # Função para validar o formato do email usando regex
        padrao_email = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(padrao_email, email) is not None


    def validar_senha(senha):
        # Função para validar o formato da senha
        return len(senha) >= 6

    def email_existe(email):
        # Função para verificar se o email já existe no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Usuarios WHERE Email = ?", (email,))
        usuario = cursor.fetchone()

        conn.close()
        return usuario is not None


#================================================================================   

    @app.route('/usuarios/login', methods=['GET', 'POST'])
    def usuarios():

        #Verificar se o metodo da requisição é POST
        if request.method == 'POST':

            #Obter os dados do formulario de login
            email = request.form['email']
            senha = request.form['senha']

            #Conectar com o banco de dados
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM Usuarios WHERE Email = ?", (email,))
            usuario = cursor.fetchone()

            conn.close()

            #SE o usuario existir, verificar a senha
            if usuario and check_password_hash(usuario[3], senha):

                #Armazenar o id do usuario na sessão.
                session['usuario_id'] = usuario[0]
                return redirect(url_for('home'))  # Redirecionar para a página inicial após o login bem-sucedido
            
            else:
                return "Email ou senha inválidos. Por favor, tente novamente."
        return render_template('usuarios/login.html') 


    @app.route('/usuarios/cadastro', methods=['GET', 'POST'])
    def cadastro():

        if request.method == 'POST':
            # Processar o formulário de cadastro
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

        #Validar email e a senha

            if not validar_email(email):
                return "Email inválido. Por favor, insira um email válido."

            if not validar_senha(senha):
                return "Senha inválida. Por favor, insira uma senha com pelo menos 6 caracteres."

            # Criptografar a senha
            senha_hash = generate_password_hash(senha)

            #Conectar com o banco de dados

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Usuarios (Nome, Email, Senha) VALUES (?, ?, ?)", (nome, email, senha_hash))
        
            conn.commit()
            conn.close()

            return redirect(url_for('home'))
    
        return render_template('usuarios/cadastro.html')