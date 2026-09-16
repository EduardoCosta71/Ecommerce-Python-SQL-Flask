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

    #Responsavel por puxar as categorias do Banco de dados.
    @app.route('/categorias_admin')
    def categorias_admin():

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                        SELECT
                        C.Id,
                        C.Nome,
                        COUNT(P.Id) AS QuantidadeProdutos
                        FROM Categorias C
                        LEFT JOIN Produtos P
                        ON P.CategoriaId = C.Id
                        GROUP BY C.Id, C.Nome
                        ORDER BY C.Nome
                    """)

        categorias = cursor.fetchall()

        conn.close()
    

        return render_template('/admin/categoria_admin.html', categorias=categorias)
                

    #Responsavel por listar categorias por id 
    @app.route('/produtos_categorias_admin/<int:categoria_id>/produtos')
    def produtos_categoria_admin(categoria_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT Id, Nome, Descricao, Preco, Imagem
        FROM Produtos
        WHERE CategoriaId = ?
        """, (categoria_id,))

        produtos = cursor.fetchall()

        conn.close()

        return render_template( '/admin/produtos_lista_cate.html', produtos=produtos)