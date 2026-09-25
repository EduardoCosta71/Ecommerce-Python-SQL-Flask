from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection

def perfil_registrar(app):

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


        return render_template("/usuarios/perfil.html", usuario=usuario)