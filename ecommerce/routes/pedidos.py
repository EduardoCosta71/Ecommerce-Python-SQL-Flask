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
    

#Metodo para salvar endereço do cliente

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
