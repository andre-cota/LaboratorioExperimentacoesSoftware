import time


class RepoSearchService:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_popular_repos(self, search_query: str, target_count: int):
        all_repos = []
        cursor = None
        batch_size = 10

        while len(all_repos) < target_count:
            query = """
            query($searchQuery: String!, $limit: Int!, $cursor: String) {
              search(
                query: $searchQuery,
                type: REPOSITORY,
                first: $limit,
                after: $cursor
              ) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  ... on Repository {
                    name
                    url
                    stargazerCount
                    createdAt
                    updatedAt
                    primaryLanguage { name }
                    pullRequests(states: MERGED) { totalCount }
                    releases { totalCount }
                    totalIssues: issues { totalCount }
                    closedIssues: issues(states: CLOSED) { totalCount }
                    description
                  }
                }
              }
            }
            """
            variables = {"searchQuery": search_query,
                         "limit": batch_size, "cursor": cursor}

            try:
                result = self.api_client.execute_query(query, variables)
                data = result.get("data", {}).get("search", {})
                nodes = data.get("nodes", [])

                for repo in nodes:
                    if self.is_software_system(repo):
                        all_repos.append(repo)
                        if len(all_repos) >= target_count:
                            break

                page_info = data.get("pageInfo", {})
                if (not page_info.get("hasNextPage") or
                        len(all_repos) >= target_count):
                    break

                cursor = page_info.get("endCursor")
                print(f"Progress: {len(all_repos)}/{target_count}...")
                time.sleep(1)

            except Exception as e:
                print(
                    f"Batch error: {e}. "
                    "Trying again in 5 seconds...")
                time.sleep(5)
                continue

        return all_repos

    def is_software_system(self, repo):
        name = repo['name'].lower()
        description = (repo.get('description') or "").lower()
        blacklisted = ['awesome', 'list', 'tutorial',
                       'course', 'book', 'interview']

        if any(term in name or term in description for term in blacklisted):
            return False
        return repo.get('primaryLanguage') is not None
