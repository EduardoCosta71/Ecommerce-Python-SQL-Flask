from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection


def admin_registrar(app):

    @app.route('/admin')
    def admin():


        return render_template("admin/dashboard.html")

    @app.route('/produtos_admin')
    def produtos_admin():

        #Listar Produtos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Produtos')
        produtos = cursor.fetchall()
        
        conn.close()
        
        return render_template('/admin/produtos.html', produtos=produtos)
                


        