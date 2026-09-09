from flask import render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection


def contato_registrar(app):

    @app.route('/contato', methods=['GET', 'POST'])
    def contato():

        if request.method == 'POST':

            nome = request.form['nome']
            email = request.form['email']
            assunto = request.form['assunto']
            mensagem = request.form['mensagem']

        #Se não tiver esses campos preenchidos vai dar erro
            if not nome or not email or not assunto or not mensagem:

                return render_template('/admin/contato.html', error="Por favor, preencha todos os campos do formulário.")

            conn = get_db_connection()
            cursor = conn.cursor()  

            cursor.execute('INSERT INTO MensagensContato (Nome, Email, Assunto, Mensagem) VALUES (?, ?, ?, ?)',
                           (nome, email, assunto, mensagem))

            conn.commit()
            conn.close()
        
        

            return render_template('/admin/contato.html', success="Mensagem enviada com sucesso!")
        


        
        return render_template('/admin/contato.html')