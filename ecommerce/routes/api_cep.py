from flask import render_template, request
import requests


def api_cep_registrar(app):

    @app.route('/buscar_cep/<int:endereco_id>', methods=['POST'])
    def buscar_cep(endereco_id):

        # Recebe o CEP digitado no formulário
        cep = request.form.get('cep', '').replace('-', '').strip()

        # Verifica se o CEP possui 8 números
        if len(cep) != 8 or not cep.isdigit():
            return "CEP inválido. Digite um CEP com 8 números."

        try:
            # Consulta a API ViaCEP
            resposta = requests.get(
                f"https://viacep.com.br/ws/{cep}/json/",
                timeout=10
            )

            # Verifica se a consulta foi bem-sucedida
            resposta.raise_for_status()

            # Converte a resposta para JSON
            dados = resposta.json()

            # Verifica se o CEP foi encontrado
            if 'erro' in dados:
                return "CEP não encontrado."

            # Retorna os dados para o HTML
            return render_template(
                'perfil/perfil_editar_endereco.html',
                endereco=dados,
                endereco_id=endereco_id
            )

        except requests.exceptions.RequestException:
            return "Erro ao consultar a API ViaCEP."