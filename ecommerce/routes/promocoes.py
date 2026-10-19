from flask import Blueprint, app, render_template, request, redirect, url_for, session, flash
from config import get_db_connection

def promocoes_registrar(app):

    #rota da promoção
    @app.route('/promocao_produto/<int:produto_id>', methods=['GET', 'POST'])
    def promocao_produto(produto_id):
    
        conn = get_db_connection()
        cursor = conn.cursor()
    
        if request.method == 'POST':
    
            preco_promocional = request.form.get('preco_promocional', '').strip().replace(',', '.')
    
            try:
                preco_promocional = float(preco_promocional)
    
                cursor.execute("SELECT Preco FROM Produtos WHERE Id = ?", (produto_id,))
                produto = cursor.fetchone()
    
                if produto is None:
                    conn.close()
                    return "Produto não encontrado", 404
    
                if preco_promocional <= 0 or preco_promocional >= float(produto[0]):
                    conn.close()
                    return "O preço promocional deve ser positivo e menor que o preço original.", 400
    
                cursor.execute("""UPDATE Produtos
                                    SET EmPromocao = 1,
                                    PrecoPromocional = ?
                                    WHERE Id = ?
                                    """, (preco_promocional, produto_id))
    
                conn.commit()
                conn.close()
    
                return redirect(url_for('produtos_admin'))
    
            except ValueError:
                conn.close()
                return "Informe um preço válido.", 400
    
        cursor.execute("""SELECT Id, Nome, Preco, EmPromocao, PrecoPromocional
                            FROM Produtos
                            WHERE Id = ?
                            """, (produto_id,))
    
        produto = cursor.fetchone()
        conn.close()
    
        if produto is None:
            return "Produto não encontrado", 404
    
        return render_template('admin/promocao_produto.html', produto=produto)
    


    #Rota responsável por retirar a promoção de um produto, caso o admin queira retirar a promoção de algum produto.
    @app.route('/retirar_promocao/<int:produto_id>', methods=['POST'])
    def retirar_promocao(produto_id):
    
        conn = get_db_connection()
    
        try:
            cursor = conn.cursor()
    
            cursor.execute("""UPDATE Produtos 
                                SET EmPromocao = 0,
                                PrecoPromocional = NULL
                                WHERE Id = ?
                                """, (produto_id,))
    
            conn.commit()
    
        finally:
            conn.close()
    
        return redirect(url_for('produtos_admin'))