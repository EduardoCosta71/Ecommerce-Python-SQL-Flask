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

def produtos_registrar(app):
    #Rota para cadastrar o produto
    @app.route('/cadastre')
    def cadastre():

       return render_template('/produtos/cadastrar.html')


    @app.route('/produtos')
    def produtos():

        #Listar Produtos
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Produtos')
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
            imagem = request.form['imagem']
            categoriaId = request.form['categoriaId']

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('INSERT INTO Produtos (Nome, Descricao, Preco, Estoque, Imagem, CategoriaId ) VALUES (?, ?, ?, ?, ?, ?)',
                           (nome, descricao, preco, estoque, imagem, categoriaId))
            
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
    

    #Rota responsavel para o vendedor atualizar informaçoes do produto. "listar.html"
    @app.route('/atualizar_produtos/<int:id>', methods=['GET', 'POST'])
    def atualizar_produtos(id):
        
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':

            nome = request.form['nome']
            descricao = request.form['preco']
            preco = request.form['preco']
            estoque = request.form['estoque']
            imagem = request.form['imagem']

            cursor.execute('UPDATE Produtos SET Nome = ?, Descricao = ?, Preco = ?, Estoque = ?, Imagem = ?',
                           (nome, descricao, preco, estoque, imagem))
            
            conn.commit()
            conn.close()

            return redirect(url_for('listar'))
        
        cursor.execute('SELECT * FROM Produtos WHERE Id = ?', (id,))
        produte = cursor.fetchone()

        conn.close()
        return render_template('produtos/listar.html', produte=produte)

        
    #Rota responsavel por excluir os produtos "listar.html" 
    @app.route('/excluir_produto/<int:id>')
    def excluir_produto(id):
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM Produtos WHERE Id = ?', (id,))
    
        conn.commit()
        conn.close()
        return redirect(url_for('listar_medicamentos'))


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
