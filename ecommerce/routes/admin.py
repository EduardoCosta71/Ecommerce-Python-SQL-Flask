from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection


def admin_registrar(app):

    @app.route('/admin')
    def admin():
        return "Tela de Administração"

