import os
import csv
from dotenv import load_dotenv
from client.github_client import GitHubClient
from services.repo_search import RepoSearchService


def save_to_csv(repos, filename="github_data.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "name", "url", "stars", "created_at", "updated_at",
            "primary_language", "merged_prs", "releases",
            "total_issues", "closed_issues"
        ])

        for r in repos:
            writer.writerow([
                r['name'],
                r['url'],
                r['stargazerCount'],
                r['createdAt'],
                r['updatedAt'],
                (
                    r['primaryLanguage']['name']
                    if r['primaryLanguage'] else "N/A"
                ),
                r['pullRequests']['totalCount'],
                r['releases']['totalCount'],
                r['totalIssues']['totalCount'],
                r['closedIssues']['totalCount']
            ])
    print(f" Data saved successfully to {filename}")


def main():
    load_dotenv()

    target_quantity = 100
    query_search = "stars:>1000 sort:stars-desc fork:false size:>5000"
    client = GitHubClient(os.getenv('API_KEY'))
    service = RepoSearchService(client)

    try:
        print(
            f"Starting collection of {target_quantity} popular repositories..."
        )
        repositorios_validados = service.get_popular_repos(
            query_search, target_quantity)
        save_to_csv(repositorios_validados)

    except Exception as e:
        print(f"Critical error: {e}")


if __name__ == "__main__":
    main()
