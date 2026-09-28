from flask import Blueprint, app, render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash

def perfil_registrar(app):

    #Rota para exibir o perfil do usuário logado
    @app.route('/perfil')
    def perfil():

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))  # Redireciona para a página de login se o usuário não estiver logado

        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Usuarios WHERE Id = ?", (usuario_id,))
        usuario = cursor.fetchone()

        conn.close()


        return render_template("/perfil/perfil.html", usuario=usuario)

    #Responsável por atualizar o perfil do usuário (nome e endereço), caso ele queira alterar algum dado.
    @app.route('/atualizar_perfil/<int:perfil_id>', methods=['GET', 'POST'])
    def atualizar_perfil(perfil_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':

            nome = request.form['nome']
            email = request.form['email']
        
        
            cursor.execute(""" UPDATE Usuarios SET Nome = ?, Email = ?
            WHERE Id = ?  """, (nome, email, perfil_id))

            conn.commit()
            conn.close()

            return redirect(url_for('perfil'))

        cursor.execute('SELECT * FROM Usuarios WHERE Id = ?', (perfil_id,))
        usuario = cursor.fetchone()
        conn.close()

        return render_template('/perfil/perfil_editar.html', usuario=usuario)


    #Rota responsável por atualizar o endereço do usuário, caso ele queira alterar algum dado.
    @app.route('/atualizar_perfil_endereco/<int:endereco_id>', methods=['GET', 'POST'])
    def atualizar_perfil_endereco(endereco_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':

            cep = request.form['cep']
            rua = request.form['rua']
            numero = request.form['numero']
            complemento = request.form['complemento']
            bairro = request.form['bairro']
            cidade = request.form['cidade']
            estado = request.form['estado']
            

            cursor.execute(""" UPDATE Enderecos SET Rua = ?, Numero = ?, Complemento = ?, Bairro = ?, Cidade = ?, Estado = ?, CEP = ? WHERE Id = ? """, (rua, numero, complemento, bairro, cidade, estado, cep, endereco_id))

            conn.commit()
            conn.close()

            return redirect(url_for('perfil'))

        cursor.execute('SELECT * FROM Usuarios WHERE Id = ?', (endereco_id,))

        endereco = cursor.fetchone()

        conn.close()

        return render_template('/perfil/perfil_editar_endereco.html', endereco=endereco)

    # Rota responsável por atualizar a senha do usuário
    @app.route('/atualizar_senha', methods=['GET', 'POST'])
    def atualizar_senha():

    # Verifica se o usuário está logado
        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':

            senha_atual = request.form['senha_atual']
            nova_senha = request.form['nova_senha']
            confirmar_senha = request.form['confirmar_senha']

        # Busca a senha atual do usuário
            cursor.execute("""
            SELECT Senha
            FROM Usuarios
            WHERE Id = ?
            """, (usuario_id,))

            usuario = cursor.fetchone()

        # Verifica se a senha atual está correta
            if usuario is None or not check_password_hash(usuario[0], senha_atual):
                conn.close()
                return render_template('usuarios/perfil.html', message='Senha atual incorreta.')

        # Verifica se a nova senha e a confirmação coincidem
            if nova_senha != confirmar_senha:
                conn.close()
                return render_template('usuarios/perfil.html', message='A nova senha e a confirmação não coincidem.')

            nova_senha_hash = generate_password_hash(nova_senha)

        # Atualiza a senha no banco de dados
            cursor.execute(""" UPDATE Usuarios
                               SET Senha = ?
                               WHERE Id = ? """, (nova_senha_hash, usuario_id))

            conn.commit()
            conn.close()

            return redirect(url_for('perfil'))

    # Busca os dados do usuário
        cursor.execute(""" SELECT * FROM Usuarios
                           WHERE Id = ? """, (usuario_id,))

        usuario = cursor.fetchone()

        conn.close()

        return render_template('usuarios/perfil.html',usuario=usuario)