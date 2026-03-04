import time
import csv


class RepoSearchService:
    def __init__(self, api_client):
        self.api_client = api_client
        self.filename = "repositorios.csv"

    def _save_to_csv(self, repos):
        """Salva a lista atual de repositórios no arquivo CSV."""
        if not repos:
            return

        file_exists = False
        try:
            with open(self.filename, 'r'):
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        with open(self.filename, mode='a', newline='', encoding='utf-8') as f:
            headers = [
                'name', 'url', 'stargazerCount', 'createdAt', 'updatedAt',
                'primaryLanguage', 'pullRequests', 'releases', 'totalIssues'
            ]
            writer = csv.DictWriter(
                f, fieldnames=headers, extrasaction='ignore')

            if not file_exists:
                writer.writeheader()

            for repo in repos:
                row = repo.copy()
                lang = repo.get('primaryLanguage')
                row['primaryLanguage'] = lang.get('name') if lang else None
                row['pullRequests'] = repo['pullRequests']['totalCount']
                row['releases'] = repo['releases']['totalCount']
                row['totalIssues'] = repo['totalIssues']['totalCount']
                writer.writerow(row)

    def get_popular_repos(self, search_query: str, target_count: int):
        all_repos = []
        total_collected = 0
        cursor = None
        batch_size = 8

        while total_collected < target_count:
            query = """
            query($searchQuery: String!, $limit: Int!, $cursor: String) {
              search(query: $searchQuery, type: REPOSITORY, 
                     first: $limit, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  ... on Repository {
                    name url stargazerCount createdAt updatedAt description
                    primaryLanguage { name }
                    pullRequests(states: MERGED) { totalCount }
                    releases { totalCount }
                    totalIssues: issues { totalCount }
                  }
                }
              }
            }
            """
            variables = {
                "searchQuery": search_query,
                "limit": batch_size,
                "cursor": cursor
            }

            max_attempts = 3
            current_timeout = 15
            success = False

            for attempt in range(1, max_attempts + 1):
                try:
                    result = self.api_client.execute_query(query, variables)
                    data = result.get("data", {}).get("search", {})
                    nodes = data.get("nodes", [])

                    for repo in nodes:
                        if self.is_software_system(repo):
                            all_repos.append(repo)
                            total_collected += 1

                            if len(all_repos) >= 100:
                                self._save_to_csv(all_repos)
                                all_repos = []

                            if total_collected >= target_count:
                                break

                    page_info = data.get("pageInfo", {})
                    has_next = page_info.get("hasNextPage")
                    if not has_next or total_collected >= target_count:
                        cursor = None
                    else:
                        cursor = page_info.get("endCursor")

                    success = True
                    break

                except Exception as e:
                    print(f"Tentativa {attempt} falhou: {e}")
                    if attempt < max_attempts:
                        time.sleep(current_timeout)
                        current_timeout += 5
                    else:
                        self._save_to_csv(all_repos)
                        return total_collected

            if not success or cursor is None:
                break

            print(f"Progresso: {total_collected}/{target_count}...")
            time.sleep(1)

        if all_repos:
            self._save_to_csv(all_repos)

        return total_collected

    def is_software_system(self, repo):
        name = repo['name'].lower()
        desc = (repo.get('description') or "").lower()
        blacklisted = [
            'awesome', 'list', 'tutorial',
            'course', 'book', 'interview'
        ]
        if any(term in name or term in desc for term in blacklisted):
            return False
        return repo.get('primaryLanguage') is not None
