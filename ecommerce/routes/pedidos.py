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

def pedidos_registrar(app):

    #Parte de Checkout dos Produtos comprados.
    @app.route('/checkout')
    def checkout():

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))
        
        usuario_id = session['usuario_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" SELECT
                   IC.Id,
                   P.Id,
                   P.Nome,
                   P.Preco,
                   P.Imagem,
                   IC.Quantidade,
                   (P.Preco * IC.Quantidade) AS Subtotal
                FROM ItensCarrinho IC
                INNER JOIN Produtos P 
                ON IC.ProdutoId = P.Id
                INNER JOIN Carrinhos C
                ON IC.CarrinhoId = C.Id
                WHERE C.UsuarioId = ?
                """, (usuario_id,))
    
        itens = cursor.fetchall()

        total = 0

        for item in itens:
            total += item.Subtotal


        # Buscar endereço
        cursor.execute(""" SELECT * FROM Enderecos WHERE UsuarioId = ? """, (usuario_id))

        endereco = cursor.fetchone()

        conn.close()

        return render_template("checkout/checkout.html", itens=itens, total=total)
    

    #Metodo para salvar endereço do cliente.
    @app.route('/checkout/endereco', methods=['POST'])
    def salvar_endereco():

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))


        usuario_id = session['usuario_id']

        cep = request.form['cep']
        rua = request.form['rua']
        numero = request.form['numero']
        complemento = request.form['complemento']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO Enderecos
        (UsuarioId, Cep, Rua, Numero, Complemento, Bairro, Cidade, Estado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario_id,
            cep,
            rua,
            numero,
            complemento,
            bairro,
            cidade,
            estado
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('checkout'))


    @app.route('/finalizar_pedido', methods=['POST'])
    def finalizar_pedido():

        if 'usuario_id' not in session:
                    return redirect(url_for('usuarios'))
        
        
        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        #Busca os itens do carrinho
        cursor.execute(""" SELECT IC.ProdutoId, IC.Quantidade, P.Preco
                            FROM ItensCarrinho IC
                            INNER JOIN Carrinhos C
                            ON  IC.CarrinhoId = C.Id
                            INNER JOIN Produtos P
                            ON IC.ProdutoId = P.Id
                            WHERE C.UsuarioId = ? """, (usuario_id, ))

        itens = cursor.fetchall()

        if not itens:
            conn.close()
            return redirect(url_for('carrinho'))

        #Calcular o valor total
        valor_total = 0

        for item in itens:
             valor_total += item.Preco * item.Quantidade


        #Criar pedido
        cursor.execute(""" INSERT INTO Pedidos
                        (UsuarioId, DataPedido, ValorTotal, Status)
                        VALUES (?, GETDATE(), ?, ?) """, (usuario_id, valor_total, "Pendente"))

        conn.commit()

        #Buscar o Id do pedido criado
        cursor.execute(""" SELECT TOP 1 Id
                            FROM Pedidos
                            WHERE UsuarioId = ?
                            ORDER BY Id DESC""", (usuario_id, ))

        
        pedido_id = cursor.fetchone()[0]

        #Inserir os itens do pedido
        for item in itens:

             cursor.execute(""" INSERT INTO ItensPedidos
                                (PedidoId, ProdutoId, Quantidade, PrecoUnitario)
                                VALUES (?, ?, ?, ?)""", (pedido_id, item.ProdutoId, item.Quantidade, item.Preco))

             cursor.execute(""" UPDATE Produtos
                                SET Estoque = Estoque - ?
                                WHERE Id = ? """, (item.Quantidade, item.ProdutoId))

        #Limpar o carrinho
        cursor.execute(""" DELETE IC
                        FROM ItensCarrinho IC
                        INNER JOIN Carrinhos C
                        ON IC.CarrinhoId = C.Id
                        WHERE C.UsuarioId = ? """, (usuario_id, ))

        conn.commit()
        conn.close()

        return redirect(url_for('pedido_sucesso'))


    #Pedido sucesso rota
    @app.route('/pedido_sucesso')
    def pedido_sucesso():
         
         return render_template("checkout/sucesso.html")


    #Rota para ver pedidos.
    @app.route('/meus_pedidos')
    def meus_pedidos():

        if 'usuario_id' not in session:

                    return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" SELECT
                    Id, DataPedido, ValorTotal, Status
                    FROM Pedidos
                    WHERE UsuarioId = ?
                    ORDER BY DataPedido DESC""", (usuario_id,))

        pedidos = cursor.fetchall()

        conn.close()

        return render_template("pedidos/meus_pedidos.html", pedidos=pedidos)

            

    @app.route('/pedido/<int:pedido_id>')
    def detalhes_pedido(pedido_id):

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

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

        return render_template("pedidos/detalhes_pedidos.html", itens=itens, pedido_id=pedido_id)




        
