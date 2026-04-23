import time
import csv


class RepoSearchService:

    def __init__(self, api_client):
        self.api_client = api_client
        self.filename = "repositorios.csv"

    def _save_to_csv(self, repos):

        if not repos:
            return

        file_exists = False
        try:
            with open(self.filename, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass

        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:

            headers = ['name', 'owner', 'url']

            writer = csv.DictWriter(f, fieldnames=headers)

            if not file_exists:
                writer.writeheader()

            for repo in repos:
                writer.writerow(repo)

    def get_top_repos(self, search_query: str, target_count: int = 200):

        repos = []
        cursor = None

        while len(repos) < target_count:

            query = """
            query($searchQuery: String!, $limit: Int!, $cursor: String) {
              search(query: $searchQuery, type: REPOSITORY, first: $limit, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  ... on Repository {
                    name
                    url
                    owner { login }
                    stargazerCount
                  }
                }
              }
            }
            """

            variables = {
                "searchQuery": search_query,
                "limit": 50,
                "cursor": cursor
            }

            result = self.api_client.execute_query(query, variables)
            data = result.get("data", {}).get("search", {})

            for repo in data.get("nodes", []):

                repos.append({
                    "name": repo["name"],
                    "owner": repo["owner"]["login"],
                    "url": repo["url"]
                })

                if len(repos) >= target_count:
                    break

            page_info = data.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break

            cursor = page_info.get("endCursor")

            print(f"Repos coletados: {len(repos)}/{target_count}")
            time.sleep(1)

        self._save_to_csv(repos)
        return repos
