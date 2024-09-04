import requests
import json
import os
import schedule
import time

# URL do JSON
url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/"

def fetch_json_from_url():
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao acessar a URL ou processar a resposta: {e}")
        return None

def load_local_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def save_local_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def check_and_update_json():
    print("Iniciando a verificação do JSON...")

    # Caminho do arquivo JSON local
    file_path = "json/megasena.json"

    # Obter o JSON da URL
    url_data = fetch_json_from_url()
    if url_data is None:
        return

    # Obter o JSON local
    local_data = load_local_json(file_path)

    if url_data == local_data:
        print("O JSON local está atualizado. Nenhuma alteração necessária.")
    else:
        print("O JSON local está desatualizado. Atualizando o arquivo...")
        # Criar a pasta 'json' se não existir
        os.makedirs("json", exist_ok=True)
        # Atualizar o arquivo JSON
        save_local_json(file_path, url_data)
        print("Arquivo JSON atualizado com sucesso.")

# Executar imediatamente para teste
check_and_update_json()

# Agendar o script para rodar às terças, quintas e sábados às 23h
schedule.every().tuesday.at("23:00").do(check_and_update_json)
schedule.every().thursday.at("23:00").do(check_and_update_json)
schedule.every().saturday.at("23:00").do(check_and_update_json)

# Loop de execução do agendador
while True:
    schedule.run_pending()
    time.sleep(60)  # Espera 1 minuto entre verificações
