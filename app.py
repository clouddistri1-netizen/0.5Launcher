import os
import threading
import requests
from flask import Flask, render_template

app = Flask(__name__)

DATA_FILE = 'services.txt'

def load_services():
    """Lê e processa o arquivo services.txt"""
    services = []
    if not os.path.exists(DATA_FILE):
        return []
        
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                # Remove espaços extras do inicio/fim de cada parte
                link = parts[0].strip()
                name = parts[1].strip()
                img = parts[2].strip()
                tags = parts[3].strip()
                
                services.append({
                    'link': link,
                    'name': name,
                    'img': img,
                    'tags': tags
                })
    return services

def ping_services(service_list):
    """Função para rodar em background e acordar os serviços"""
    print("--- A iniciar PING aos serviços ---")
    for service in service_list:
        try:
            # Timeout curto para não ficar preso
            requests.get(service['link'], timeout=2)
            print(f"[OK] Ping em {service['name']}")
        except Exception as e:
            print(f"[ERRO] Falha ao pingar {service['name']}: {e}")
    print("--- Fim do PING ---")

@app.route('/')
def index():
    services = load_services()
    
    # Inicia o ping numa thread separada para não travar o carregamento da página
    # O user vê a página instantaneamente enquanto o servidor acorda os links no fundo
    thread = threading.Thread(target=ping_services, args=(services,))
    thread.start()
    
    return render_template('index.html', services=services)

if __name__ == '__main__':
    # Host 0.0.0.0 permite acesso da rede local
    app.run(host='0.0.0.0', port=5000, debug=True)