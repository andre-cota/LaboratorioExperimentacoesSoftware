import os
from dotenv import load_dotenv
from client.github_client import GitHubClient
from services.repo_search import RepoSearchService


def main():
    load_dotenv()

    target_quantity = 1000
    token = os.getenv('API_KEY')

    if not token:
        print("Erro: API_KEY não encontrada no arquivo .env")
        return

    client = GitHubClient(token)
    service = RepoSearchService(client)
    queries = [
        ("stars:>200 created:2010-01-01..2019-12-31 "
         "fork:false size:>3000"),
        ("stars:>200 created:2020-01-01..2022-12-31 "
         "fork:false size:>3000"),
        ("stars:>200 created:2023-01-01..2026-12-31 "
         "fork:false size:>3000")
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


if __name__ == "__main__":
    main()
