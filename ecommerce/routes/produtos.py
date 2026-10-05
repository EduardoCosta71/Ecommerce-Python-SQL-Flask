from flask import Blueprint, render_template, request, redirect, url_for, session
import pyodbc
from config import get_db_connection
import os
from werkzeug.utils import secure_filename

def produtos_registrar(app):

    #Rota para  as ofertas
    @app.route('/ofertas')
    def ofertas():  
            
        return render_template('/produtos/ofertas.html')
        
     
    #Rota para cadastrar o produto
    @app.route('/cadastre')
    def cadastre():

       return render_template('/produtos/cadastrar.html')


    @app.route('/produtos')
    def produtos():

        #Listar Produtos
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""SELECT Id, Nome, Descricao, Preco, Imagem, Estoque
                          FROM Produtos
                          WHERE Estoque > 0
                        """)
        produtos = cursor.fetchall()

        
        conn.close()

        return render_template('/produtos/listar.html', produtos=produtos)
        
                    

    #Rota responsavel por cadastrar os produtos da loja.
    @app.route('/produtos/cadastrar', methods=['GET', 'POST'])
    def cadastrar_produtos():

        if request.method == 'POST':

            nome = request.form['nome']
            descricao = request.form['descricao']
            preco = request.form['preco']
            estoque = request.form['estoque']
            categoriaId = request.form['categoriaId']

            #Recebe o arquivo de imagem enviado pelo formulário
            imagem = request.files['imagem']

            if imagem and imagem.filename:

                #Garante que o nome do arquivo seja seguro para uso no sistema de arquivos
                nome_imagem = secure_filename(imagem.filename)

                #Cria a pasta "uploads" dentro da pasta "static" se ela não existir
                pasta_uploads = os.path.join(app.root_path, 'static/uploads')


                #Cria a pasta "uploads" dentro da pasta "static" se ela não existir
                os.makedirs(pasta_uploads, exist_ok=True)


                #Salva a imagem na pasta "uploads" dentro da pasta "static"
                caminho_imagem = os.path.join(pasta_uploads, nome_imagem)

                imagem.save(caminho_imagem)

            else:

                nome_imagem = None

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('INSERT INTO Produtos (Nome, Descricao, Preco, Estoque, Imagem, CategoriaId ) VALUES (?, ?, ?, ?, ?, ?)',
                           (nome, descricao, preco, estoque, nome_imagem, categoriaId))
            
            conn.commit()
            conn.close()

            return redirect(url_for('cadastre'))
        
        return render_template('produtos/cadastrar.html')
    

    #Rota responsavel por listar os produtos cadastrados do vendedor. "listar.html"
    @app.route('/consultar_produtos/<int:id>')
    def consultar_produtos(id):

        conn = get_db_connection
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Produtos WHERE Id = ?', (id,))
        produto = cursor.fetchone()

        conn.close()
        return render_template('listar_html', produto=produto)
    
    #Rota responsavel por atualizar os produtos cadastrados do vendedor. "atualizar.html"
    @app.route('/atualizar_produtos/<int:produto_id>', methods=['GET', 'POST'])
    def atualizar_produtos(produto_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':

            nome = request.form['nome']
            descricao = request.form['descricao']
            preco = request.form['preco']
            estoque = request.form['estoque']
            categoriaId = request.form['categoriaId']

            imagem = request.files['imagem']

        # Busca a imagem atual
            cursor.execute(""" SELECT Imagem
                               FROM Produtos
                               WHERE Id = ?
                               """, (produto_id,))

            produto = cursor.fetchone()

            nome_imagem = produto.Imagem

        # Se uma nova imagem foi selecionada
            if imagem and imagem.filename:

                nome_imagem = secure_filename(imagem.filename)

                pasta_uploads = os.path.join(app.root_path, 'static','uploads')

                os.makedirs(pasta_uploads, exist_ok=True)

                caminho_imagem = os.path.join(pasta_uploads, nome_imagem)

                imagem.save(caminho_imagem)

        # Atualiza o produto
            cursor.execute("""
            UPDATE Produtos
            SET Nome = ?,
                Descricao = ?,
                Preco = ?,
                Estoque = ?,
                Imagem = ?,
                CategoriaId = ?
            WHERE Id = ?
        """, (
            nome,
            descricao,
            preco,
            estoque,
            nome_imagem,
            categoriaId,
            produto_id
        ))

            conn.commit()
            conn.close()

            return redirect(url_for('produtos_admin'))

    # Busca os dados atuais do produto
        cursor.execute("""SELECT * FROM Produtos
                            WHERE Id = ?
                            """, (produto_id,))

        produte = cursor.fetchone()

        conn.close()

        return render_template('admin/atualizar.html', produte=produte)

        
    #Rota responsavel por excluir os produtos "listar.html" 
    @app.route('/excluir_produto/<int:id>')
    def excluir_produto(id):

        conn = get_db_connection()
        cursor = conn.cursor()

    # Verifica se o produto já foi usado em algum pedido
        cursor.execute("""
            SELECT COUNT(*)
            FROM ItensPedidos
            WHERE ProdutoId = ?
        """, (id,))

        quantidade = cursor.fetchone()[0]

    # Se já estiver em algum pedido, não permite excluir
        if quantidade > 0:

            conn.close()

            return "Não é possível excluir este produto porque ele já possui pedidos."

    # Se não estiver em nenhum pedido, pode excluir
        cursor.execute("""
            DELETE FROM Produtos
            WHERE Id = ?
        """, (id,))

        conn.commit()
        conn.close()

        return render_template('/admin/produtos.html')


#==================================================


    #Rota para as categorias
    @app.route('/categorias')
    def categorias():

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" SELECT Id, Nome
                            FROM Categorias
                             ORDER BY Nome
                             """)

        categorias = cursor.fetchall()

        conn.close()

        return render_template('/produtos/categorias.html', categorias=categorias)




    # Rota para mostrar os produtos de uma categoria específica
    @app.route('/categoria/<int:categoria_id>')
    def produtos_categoria(categoria_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" SELECT Id, Nome, Descricao, Preco, Imagem
                            FROM Produtos
                            WHERE CategoriaId = ?
                            """, (categoria_id,))

        produtos = cursor.fetchall()

        conn.close()

        return render_template('/produtos/produtos_categoria.html', produtos=produtos)

    #===================================================================================================

    #Rota para pesquisar produtos
    @app.route('/pesquisar', methods=['GET'])
    def pesquisar_produtos():

    # Pesquisa
        query = request.args.get('q', '').strip()

    # Categoria
        categoria = request.args.get('categoria', '').strip()

    # Ordenação
        ordenar = request.args.get('ordenar', '').strip()

        conn = get_db_connection()
        cursor = conn.cursor()

    # Consulta base
        sql = """
        SELECT
            p.Id,
            p.Nome,
            p.Descricao,
            p.Preco,
            p.Imagem,
            p.Estoque,
            c.Nome AS Categorias

        FROM Produtos p

        LEFT JOIN Categorias c
            ON p.CategoriaId = c.Id

        WHERE 1 = 1
    """

        parametros = []

    # ==================================================
    # PESQUISA POR NOME OU DESCRIÇÃO
    # ==================================================

        if query:

            sql += """
            AND (
                p.Nome LIKE ?
                OR p.Descricao LIKE ?
            )
        """

            parametros.append('%' + query + '%')
            parametros.append('%' + query + '%')


    # ==================================================
    # FILTRO POR CATEGORIA
    # ==================================================

        if categoria:

            sql += """
            AND p.CategoriaId = ?
        """

            parametros.append(categoria)


    # ==================================================
    # ORDENAÇÃO
    # ==================================================

        if ordenar == 'menor_preco':

            sql += """
            ORDER BY p.Preco ASC
        """

        elif ordenar == 'maior_preco':

            sql += """
            ORDER BY p.Preco DESC
        """

        elif ordenar == 'mais_vendidos':

            sql += """
            ORDER BY p.Id DESC
        """

        else:

            sql += """
            ORDER BY p.Id DESC
        """


    # ==================================================
    # EXECUTA A CONSULTA DOS PRODUTOS
    # ==================================================

        cursor.execute(sql, parametros)

        produtos = cursor.fetchall()


    # BUSCA AS CATEGORIAS
  
        cursor.execute("""
        SELECT Id, Nome
        FROM Categorias
        ORDER BY Nome
    """)

        categorias = cursor.fetchall()
        conn.close()


        return render_template('/produtos/listar.html', produtos=produtos, query=query, categorias=categorias, categoria_selecionada=categoria, ordenar=ordenar)