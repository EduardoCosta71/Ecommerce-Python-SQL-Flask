from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection


def admin_registrar(app):

    @app.route('/admin')
    def admin():


        return render_template("admin/dashboard.html")
    
    

#Lista de produtos cadastrados no banco de dados, para o admin poder visualizar.
    @app.route('/produtos_admin')
    def produtos_admin():

        #Listar Produtos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Produtos')
        produtos = cursor.fetchall()
        
        conn.close()
        
        return render_template('/admin/produtos.html', produtos=produtos)


    #Rota para ver pedidos no admin, para o admin poder visualizar os pedidos feitos pelos clientes.
    @app.route('/pedidos_admin')
    def pedidos_admin():

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" SELECT
                    Id, UsuarioId, DataPedido, ValorTotal, Status
                    FROM Pedidos

                    ORDER BY DataPedido DESC""",)

        pedidos = cursor.fetchall()

        conn.close()

        return render_template("admin/pedidos_admin.html", pedidos=pedidos)


    @app.route('/pedido_admin_detalhes/<int:pedido_id>')
    def pedido_admin_detalhes(pedido_id):
    
            conn = get_db_connection()
            cursor = conn.cursor()
    
            cursor.execute("""
            SELECT
                P.Nome,
                P.Imagem,
                IP.Quantidade,
                IP.PrecoUnitario,
                (IP.Quantidade * IP.PrecoUnitario) AS Subtotal
            FROM ItensPedidos IP
            INNER JOIN Produtos P
                ON IP.ProdutoId = P.Id
            WHERE IP.PedidoId = ?
        """, (pedido_id,))
    
            itens = cursor.fetchall()
    
            conn.close()
    
            return render_template("admin/pedidos_detalhes.html", itens=itens, pedido_id=pedido_id)

    

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

        return render_template('/admin/produtos_lista_cate.html', produtos=produtos)


    

    #Rota para deletar uma categoria do banco de dados.
    @app.route('/deletar_categoria/<int:categoria_id>')
    def deletar_categoria(categoria_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
              
            SELECT COUNT(*) FROM Produtos WHERE CategoriaId = ? 
                        """, (categoria_id,))

        count = cursor.fetchone()[0]

        if count > 0:

            conn.close()
            
            return render_template('/admin/produtos_lista_cate.html', message='Não é possível deletar a categoria, pois existem produtos associados a ela.')

        # Deletar a categoria do banco de dados
        cursor.execute('DELETE FROM Categorias WHERE Id = ?', (categoria_id,))

        conn.commit()
        conn.close()

        return render_template('/admin/categoria_admin.html', message='Categoria deletada com sucesso!')


    

    #atualizar uma categoria no banco de dados.
    @app.route('/atualizar_categoria/<int:categoria_id>', methods=['GET', 'POST'])
    def atualizar_categoria(categoria_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            nome_categoria = request.form['nome_categoria']

            cursor.execute('UPDATE Categorias SET Nome = ? WHERE Id = ?', (nome_categoria, categoria_id))
            conn.commit()
            conn.close()

            return redirect(url_for('categorias_admin'))

        cursor.execute('SELECT Id, Nome FROM Categorias WHERE Id = ?', (categoria_id,))
        categoria = cursor.fetchone()
        conn.close()

        return render_template('/admin/atualizar_categoria.html', categoria=categoria)


    

     #Cadastrar uma nova categoria no banco de dados.
    @app.route('/cadastrar_categoria/nova', methods=['GET', 'POST'])
    def cadastrar_categoria():

        if request.method == 'POST':

            nome_categoria = request.form['nome_categoria']

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(""" INSERT INTO Categorias (Nome) VALUES (?) """, (nome_categoria,))

            conn.commit()
            conn.close()

            return redirect(url_for('categorias_admin'))

        return render_template('/admin/cadastrar_categoria.html')