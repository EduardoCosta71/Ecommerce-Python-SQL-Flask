from flask import Blueprint, app, render_template, request, redirect, url_for, session, flash
import pyodbc
from config import get_db_connection


def admin_registrar(app):

    @app.route('/admin')
    def admin():


        return render_template("admin/dashboard.html")
    
#-------------------PRODUTOS----------------------------------------------------------------------------------------------------------

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

    # Rota para ver os detalhes de um pedido no admin
    @app.route('/pedido_admin_detalhes/<int:pedido_id>')
    def pedido_admin_detalhes(pedido_id):

        conn = get_db_connection()
        cursor = conn.cursor()

    # Busca os produtos do pedido
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


    # Busca o status e o valor total do pedido
        cursor.execute("""
        SELECT Status, ValorTotal
        FROM Pedidos
        WHERE Id = ?
    """, (pedido_id,))

        pedido = cursor.fetchone()

        conn.close()


        return render_template("admin/pedidos_detalhes.html", itens=itens, pedido_id=pedido_id, status_pedido=pedido.Status, valor_total=pedido.ValorTotal)
    

    #Rota para finalizar um pedido no admin, para o admin poder finalizar os pedidos feitos pelos clientes.
    @app.route('/finalizar_pedido_admin/<int:pedido_id>', methods=['POST'])
    def finalizar_pedido_admin(pedido_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" UPDATE Pedidos SET Status = 'Finalizado' WHERE Id = ? """, (pedido_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('pedido_admin_detalhes', pedido_id=pedido_id))

#-------------------CATEGORIAS----------------------------------------------------------------------------------------------------------

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


#--------------------Usuarios----------------------------------------------------------------------------------------------------------
    #Rota para listar os usuarios cadastrados no banco de dados, para o admin poder visualizar.
    @app.route('/usuarios_admin')
    def usuarios_admin():

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                        SELECT Id,
                        Nome,
                        Email
                        FROM Usuarios
                        ORDER BY Nome
                    """)

        usuarios = cursor.fetchall()

        conn.close()

        return render_template('/usuario_admin/listar_usuario_admin.html', usuarios=usuarios)
    

    #Rota para deletar um usuário do banco de dados, com verificação se o usuário possui pedidos registrados.
    @app.route('/deletar_usuario/<int:usuario_id>')
    def deletar_usuario(usuario_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

        # Verifica se o usuário possui pedidos
            cursor.execute("""
            SELECT COUNT(*)
            FROM Pedidos
            WHERE UsuarioId = ?
        """, (usuario_id,))

            quantidade_pedidos = cursor.fetchone()[0]

            if quantidade_pedidos > 0:

                flash('Este usuário possui pedidos registrados e não pode ser excluído.', 'erro')

           

                return redirect(url_for('usuarios_admin'))

        # Busca o carrinho
            cursor.execute("""
            SELECT Id
            FROM Carrinhos
            WHERE UsuarioId = ?
        """, (usuario_id,))

            carrinho = cursor.fetchone()

            if carrinho:

                carrinho_id = carrinho[0]

            # Exclui itens do carrinho
                cursor.execute("""
                DELETE FROM ItensCarrinho
                WHERE CarrinhoId = ?
            """, (carrinho_id,))

            # Exclui carrinho
                cursor.execute("""
                DELETE FROM Carrinhos
                WHERE Id = ?
            """, (carrinho_id,))

        # Exclui usuário
                cursor.execute("""
                DELETE FROM Usuarios
                 WHERE Id = ?
             """, (usuario_id,))

            conn.commit()

            flash('Usuário excluído com sucesso.', 'sucesso')

        except Exception as erro:

            conn.rollback()

            print("Erro ao excluir usuário:", erro)

            flash('Ocorreu um erro ao excluir o usuário.', 'erro')

        finally:

            conn.close()

        return redirect(url_for('usuarios_admin'))
    

    #Rota para atualizar o perfil do usuário no admin, para o admin poder atualizar os dados dos usuários cadastrados.
    @app.route('/atualizar_perfil_admin/<int:perfil_id>', methods=['GET', 'POST'])
    def atualizar_perfil_admin(perfil_id):
    
        conn = get_db_connection()
        cursor = conn.cursor()
    
        if request.method == 'POST':
    
            nome = request.form['nome']
            email = request.form['email']
            
            
            cursor.execute(""" UPDATE Usuarios SET Nome = ?, Email = ?
            WHERE Id = ?  """, (nome, email, perfil_id))
    
            conn.commit()
            conn.close()
    
            return redirect(url_for('usuarios_admin'))
    
        cursor.execute('SELECT * FROM Usuarios WHERE Id = ?', (perfil_id,))
        usuario = cursor.fetchone()
        conn.close()
    
        return render_template('/usuario_admin/atualizar_usuario.html', usuario=usuario)




#=========================Mensagens Usuarios============================================================================


    @app.route('/mensagens_admin')
    def mensagens_admin():

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                        SELECT Id, Nome, Email, Assunto, Mensagem, DataEnvio, Status
                        FROM MensagensContato
                        ORDER BY Id DESC
                    """)

        mensagens = cursor.fetchall()

        conn.close()

        return render_template('/admin/mensagens_usuarios.html', mensagens=mensagens)

    @app.route('/mensagem_admin_detalhes/<int:mensagem_id>')
    def mensagem_admin_detalhes(mensagem_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
                        SELECT Id, Nome, Email, Assunto, Mensagem, DataEnvio, Status
                        FROM MensagensContato
                        WHERE Id = ?
                    """, (mensagem_id,))

        mensagem = cursor.fetchone()

        conn.close()

        return render_template('/admin/mensagem_detalhes.html', mensagem=mensagem)

    #Rota para atualizar o status da mensagem para "Lida" no banco de dados.
    @app.route('/atualizar_status_mensagem/<int:mensagem_id>', methods=['POST'])
    def atualizar_status_mensagem(mensagem_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE MensagensContato
        SET Status = 'Lida'
        WHERE Id = ?
    """, (mensagem_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('mensagens_admin'))
