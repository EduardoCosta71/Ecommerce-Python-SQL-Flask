from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc

def get_db_connection():
    #Função para estabelecer conexão com o banco de dados SQL Server
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'  # Substitua pelo nome do seu servidor e instância
        'DATABASE=Ecommerce;'  # Substitua pelo nome do seu banco de dados
        'Trusted_Connection=yes;'
    )

def admin_registrar(app):

    @app.route('/admin')
    def admin():
        return "Tela de Administração"

