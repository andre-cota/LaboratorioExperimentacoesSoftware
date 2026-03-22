import os
from dotenv import load_dotenv
from client.github_client import GitHubClient
from services.repo_search import RepoSearchService
from datetime import datetime


def main():
    load_dotenv()

    target_quantity = 1000
    token = os.getenv('API_KEY')

    if not token:
        print("Erro: API_KEY não encontrada no arquivo .env")
        return

    client = GitHubClient(token)
    service = RepoSearchService(client)
    start_time = datetime.now()
    queries = [
            ("language:Java stars:>200 sort:stars-desc "
             "created:2010-01-01..2019-12-31 fork:false size:>3000 archived:false"),

            ("language:Java stars:>200 sort:stars-desc "
             "created:2020-01-01..2022-12-31 fork:false size:>3000 archived:false"),

            ("language:Java stars:>200 sort:stars-desc "
             "created:2023-01-01..2026-12-31 fork:false size:>3000 archived:false")
    ]

    total_acumulado = 0
    try:
        print(f"Iniciando coleta de {target_quantity} repositórios...")
        print("-" * 30)

        for query_search in queries:
            restante = target_quantity - total_acumulado
            if restante <= 0:
                break

            coletados = service.get_popular_repos(query_search, restante)
            total_acumulado += coletados

            print(f"Subtotal acumulado: {total_acumulado}/{target_quantity}")

        print("-" * 30)
        print("Processo finalizado com sucesso!")
        print(f"Total final salvo no CSV: {total_acumulado}")
        print("-" * 30)

    except Exception as e:
        print(f"Erro crítico: {e}")

    end_time = datetime.now()
    elapsed_time = end_time - start_time
    print(f"Tempo total de execução: {elapsed_time.total_seconds():.2f} s")


if __name__ == "__main__":
    main()
