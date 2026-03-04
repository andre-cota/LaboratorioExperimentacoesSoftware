import requests


class GitHubClient:
    def __init__(self, token: str):
        self.url = "https://api.github.com/graphql"
        self.headers = {"Authorization": f"Bearer {token}"}

    def execute_query(self, query: str, variables: dict) -> dict:
        response = requests.post(
            self.url,
            json={'query': query, 'variables': variables},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
