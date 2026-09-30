from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
import random
import time

from config import get_db_connection


def recuperar_senha_registrar(app):

    # SOLICITAR RECUPERAÇÃO
    @app.route('/recuperar_senha', methods=['GET', 'POST'])
    def recuperar_senha():

        if request.method == 'POST':

            email = request.form.get('email')

            # Verifica se o email foi fornecido
            if not email:
                flash('Digite seu e-mail.', 'erro')
                return redirect(url_for('recuperar_senha'))

            conexao = get_db_connection()
            cursor = conexao.cursor()

            cursor.execute(
                'SELECT Id, Email FROM Usuarios WHERE Email = ?',
                (email,)
            )

            usuario = cursor.fetchone()

            cursor.close()
            conexao.close()

            if not usuario:
                flash('E-mail não encontrado.', 'erro')
                return redirect(url_for('recuperar_senha'))

            # Gera um código de 6 números
            codigo = str(random.randint(100000, 999999))

            # Guarda temporariamente na sessão
            session['codigo_recuperacao'] = codigo
            session['usuario_recuperacao'] = usuario.Id
            session['codigo_expira'] = time.time() + 300  # 5 minutos

            # Para desenvolvimento:
            # mostra o código na tela
            return render_template('usuarios/solicitar_recuperacao.html', codigo=codigo)

        return render_template('usuarios/solicitar_recuperacao.html')


    # REDEFINIR SENHA
 
    @app.route('/redefinir_senha', methods=['GET', 'POST'])
    def redefinir_senha():

        # Verifica se o código de recuperação está na sessão
        if 'codigo_recuperacao' not in session:
            flash('Nenhuma recuperação de senha foi iniciada.', 'erro')
            return redirect(url_for('redefinir_senha'))
        
       
        if request.method == 'POST':

            codigo = request.form.get('codigo')
            nova_senha = request.form.get('senha')
            confirmar_senha = request.form.get('confirmar_senha')

            # Verifica se o código expirou
            if time.time() > session.get('codigo_expira', 0):

                session.pop('codigo_recuperacao', None)
                session.pop('usuario_recuperacao', None)
                session.pop('codigo_expira', None)

                flash('O código expirou. Solicite um novo código.', 'erro')

                return redirect(url_for('redefinir_senha'))

            # Verifica o código
            if codigo != session.get('codigo_recuperacao'):

                flash('Código de recuperação inválido.', 'erro')

                return render_template('usuarios/redefinir_senha.html')

            # Verifica tamanho da senha
            if not nova_senha or len(nova_senha) < 8:

                flash('A senha deve ter pelo menos 8 caracteres.', 'erro')

                return render_template('usuarios/redefinir_senha.html')

            # Confirmação da senha
            if nova_senha != confirmar_senha:

                flash('As senhas não são iguais.', 'erro')

                return render_template('usuarios/redefinir_senha.html')

            usuario_id = session.get('usuario_recuperacao')

            # Cria o hash da nova senha
            senha_hash = generate_password_hash(nova_senha)

            conexao = get_db_connection()
            cursor = conexao.cursor()

            cursor.execute(
                '''
                UPDATE Usuarios
                SET Senha = ?
                WHERE Id = ?
                ''',
                (senha_hash, usuario_id)
            )

            conexao.commit()

            cursor.close()
            conexao.close()

            # Limpa os dados da recuperação
            session.pop('codigo_recuperacao', None)
            session.pop('usuario_recuperacao', None)
            session.pop('codigo_expira', None)

            flash('Senha alterada com sucesso!', 'sucesso')

            return redirect(url_for('perfil'))

        return render_template('usuarios/redefinir_senha.html')
    