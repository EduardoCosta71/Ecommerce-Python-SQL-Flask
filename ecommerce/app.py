
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
import re
import os
#Iniciação Flask
app = Flask(__name__)

from routes.home import home_registrar
from routes.usuarios import usuarios_registrar
from routes.produtos import produtos_registrar
from routes.carrinho import carrinho_registrar
from routes.admin import admin_registrar
from routes.pedidos import pedidos_registrar
from routes.contato import contato_registrar

app.secret_key = os.getenv("SECRET_KEY")
load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

home_registrar(app)
usuarios_registrar(app)
produtos_registrar(app)
carrinho_registrar(app)
admin_registrar(app)
pedidos_registrar(app)
contato_registrar(app)


if __name__ == '__main__':
    app.run(debug=True)