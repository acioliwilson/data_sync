import requests
import json
import os
import schedule
import time
from flask import Flask, jsonify

app = Flask(__name__)

# Função para colorir o texto
def print_colored(text, color):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors[color]}{text}{colors['reset']}")

# URL do JSON
url = "https://loteriascaixa-api.herokuapp.com/api/megasena/latest"

# Cabeçalhos para a solicitação
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}

# Caminho do arquivo JSON
file_path = "json/megasena.json"

# Função para verificar e atualizar o JSON
def check_and_update_json():
    try:
        # Enviar uma solicitação GET para a URL do JSON com cabeçalhos
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

        # Obter o JSON da resposta
        new_data = response.json()

        # Criar a pasta 'json' se não existir
        os.makedirs("json", exist_ok=True)

        # Verificar se o arquivo JSON já existe
        if os.path.exists(file_path):
            # Ler o conteúdo atual do arquivo JSON
            with open(file_path, "r", encoding="utf-8") as file:
                current_data = json.load(file)

            # Comparar o JSON atual com o novo JSON
            if current_data == new_data:
                # Se forem iguais, exibe a mensagem em verde
                print_colored("Nenhuma alteração necessária. O JSON já está atualizado.", "green")
            else:
                # Se forem diferentes, atualizar o arquivo JSON
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(new_data, file, indent=4, ensure_ascii=False)
                print_colored("O JSON foi atualizado com sucesso.", "blue")
        else:
            # Se o arquivo não existir, criar e salvar o novo JSON
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(new_data, file, indent=4, ensure_ascii=False)
            print_colored("Arquivo JSON criado com sucesso.", "blue")

    except requests.RequestException as e:
        print_colored(f"Erro ao acessar a URL ou processar a resposta: {e}", "red")

# Rota para servir o JSON
@app.route('/megasena-json', methods=['GET'])
def get_json():
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return jsonify(data)
    else:
        return jsonify({"error": "Arquivo JSON não encontrado"}), 404

# Agendando para rodar nas terças, quintas e sábados às 23h
schedule.every().tuesday.at("23:00").do(check_and_update_json)
schedule.every().thursday.at("23:00").do(check_and_update_json)
schedule.every().saturday.at("23:00").do(check_and_update_json)

# Função para rodar o agendador em segundo plano
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    # Iniciar o servidor Flask em segundo plano
    from threading import Thread
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    # Obter a porta a partir da variável de ambiente 'PORT' ou usar 5000 como padrão
    port = int(os.environ.get('PORT', 5000))
    
    # Iniciar o servidor Flask, especificando host e porta
    app.run(host='0.0.0.0', port=port)

