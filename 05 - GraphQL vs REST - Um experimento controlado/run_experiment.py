import time
import httpx
import pandas as pd

URL_REST_BASE = "https://jsonplaceholder.typicode.com/users/1" 
URL_GQL_BASE = "https://countries.trevorblades.com/"           

HEADERS = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

ITERATIONS = 110 
WARM_UP_THRESHOLD = 10

def coletar_dados_experimento():
    results = []
    print(f"🚀 Iniciando coleta de dados ({ITERATIONS} iterações)...")
    
    with httpx.Client(timeout=10.0) as client:
        
        print("📥 Coletando dados do bloco REST...")
        for i in range(1, ITERATIONS + 1):
            is_warm_up = i <= WARM_UP_THRESHOLD
            
            start_time = time.perf_counter()
            try:
                response = client.get(URL_REST_BASE, headers=HEADERS)
                end_time = time.perf_counter()
                
                tempo_ms = (end_time - start_time) * 1000
                tamanho_bytes = len(response.content)
                status_code = response.status_code
            except Exception as e:
                print(f"❌ Erro na requisição REST {i}: {e}")
                continue
            
            if not is_warm_up and status_code == 200:
                results.append({
                    "Iteracao": i - WARM_UP_THRESHOLD,
                    "Tecnologia": "REST",
                    "Tempo_ms": tempo_ms,
                    "Tamanho_Bytes": tamanho_bytes
                })
                
        print("📥 Coletando dados do bloco GraphQL...")
        gql_query = {"query": "{ country(code: \"BR\") { name currency capital } }"}
        
        for i in range(1, ITERATIONS + 1):
            is_warm_up = i <= WARM_UP_THRESHOLD
            
            start_time = time.perf_counter()
            try:
                response = client.post(URL_GQL_BASE, json=gql_query, headers=HEADERS)
                end_time = time.perf_counter()
                
                tempo_ms = (end_time - start_time) * 1000
                tamanho_bytes = len(response.content)
                status_code = response.status_code
            except Exception as e:
                print(f"❌ Erro na requisição GraphQL {i}: {e}")
                continue
                
            if not is_warm_up and status_code == 200:
                results.append({
                    "Iteracao": i - WARM_UP_THRESHOLD,
                    "Tecnologia": "GraphQL",
                    "Tempo_ms": tempo_ms,
                    "Tamanho_Bytes": tamanho_bytes
                })

    df_resultados = pd.DataFrame(results)
    output_file = "experimento_raw.csv"
    df_resultados.to_csv(output_file, index=False)
    print(f"✅ Coleta finalizada! Dados salvos com sucesso em: '{output_file}'")

if __name__ == "__main__":
    coletar_dados_experimento()