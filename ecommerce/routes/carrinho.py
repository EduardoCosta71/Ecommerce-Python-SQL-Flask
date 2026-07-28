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

def carrinho_registrar(app):

    @app.route('/carrinho')
    def carrinho():

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                IC.Id,
                P.Nome,
                P.Descricao,
                P.Preco,
                P.Imagem,
                IC.Quantidade

            FROM Carrinhos C

            INNER JOIN ItensCarrinho IC
                ON C.Id = IC.CarrinhoId

            INNER JOIN Produtos P
                ON P.Id = IC.ProdutoId

            WHERE C.UsuarioId = ?
        """, (usuario_id,))

        itens = cursor.fetchall()

        total = 0

        for item in itens:
            
            total += item.Preco * item.Quantidade

        conn.close()

        return render_template("carrinho/carrinho.html", itens=itens, total=total)
    

    #Rota para o produto ser adicionado no carrinho.
    #É feito os calculos dos produtos também.
    @app.route('/carrinho/adicionar/<int:produto_id>')
    def adicionar_carrinho(produto_id):

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Procura um carrinho do usuário
        cursor.execute(
            "SELECT Id FROM Carrinhos WHERE UsuarioId = ?",
            (usuario_id,)
        )

        carrinho = cursor.fetchone()

        # Se não existir, cria um
        if not carrinho:

            cursor.execute(
                "INSERT INTO Carrinhos (UsuarioId, DataCriacao) VALUES (?, GETDATE())",
                (usuario_id,)
            )

            conn.commit()

            cursor.execute(
                "SELECT Id FROM Carrinhos WHERE UsuarioId = ?",
                (usuario_id,)
            )

            carrinho = cursor.fetchone()

        carrinho_id = carrinho[0]

        # Verifica se o produto já está no carrinho
        cursor.execute("""
            SELECT Id, Quantidade
            FROM ItensCarrinho
            WHERE CarrinhoId = ? AND ProdutoId = ?
        """, (carrinho_id, produto_id))

        item = cursor.fetchone()

        if item:

            cursor.execute("""
                UPDATE ItensCarrinho
                SET Quantidade = Quantidade + 1
                WHERE Id = ?
            """, (item[0],))

        else:

            cursor.execute("""
            INSERT INTO ItensCarrinho
                (CarrinhoId, ProdutoId, Quantidade)
                VALUES (?, ?, 1)
            """, (carrinho_id, produto_id))

        conn.commit()
        conn.close()

        return redirect(url_for('carrinho'))
    
    #Rota para excluir produto do carrinho de compras.
    #Foi adicionado uma verificação para só usuarios logado.
    @app.route('/carrinho/remover/<int:item_id>')
    def remover_carrinho(item_id):

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM ItensCarrinho WHERE Id = ?', (item_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('carrinho'))


    #Rota para diminiuir a quantidade de itens do carrinho.
    @app.route('/carrinho/diminuir/<int:item_id>')
    def diminuir_carrinho(item_id):

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']

        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""SELECT Quantidade
                       FROM ItensCarrinho
                       WHERE Id = ?
                       """, (item_id,))

        item = cursor.fetchone()

        if not item:

            conn.close()
            return redirect(url_for('carrinho'))

        if item.Quantidade > 1:

            cursor.execute(""" UPDATE ItensCarrinho
                           SET Quantidade = Quantidade - 1
                           WHERE Id = ?
                           """, (item_id,))
            
        else: 
            
            cursor.execute(""" DELETE FROM ItensCarrinho
                           WHERE Id = ?
                           """, (item_id,))
            
        conn.commit()
        conn.close()

        return redirect(url_for('carrinho'))
    
    #Rota para aumentar os itens do carrinho.
    @app.route('/carrinho/aumentar/<item_id>')
    def aumentar_carrinho(item_id):

        if 'usuario_id' not in session:
            return redirect(url_for('usuarios'))

        usuario_id = session['usuario_id']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(""" SELECT IC.Quantidade, P.Estoque
                       FROM ItensCarrinho IC
                       INNER JOIN Produtos P
                       ON IC.ProdutoId = P.Id
                       WHERE IC.Id = ?
                       """, (item_id,))
        
        item = cursor.fetchone()

    # Verifica se ainda há estoque
        if not item:
            conn.close()
            return redirect(url_for('carrinho'))
        
        if item.Quantidade >= item.Estoque:
            conn.close()
            return redirect(url_for('carrinho'))
        
    
        cursor.execute(""" UPDATE ItensCarrinho
                        SET Quantidade = Quantidade + 1
                        WHERE Id = ?
                        """, (item_id,))
        
        conn.commit()
        conn.close()

        return redirect(url_for('carrinho'))



    