"""
github_client.py
Cliente robusto para GitHub GraphQL API v4
"""

import time
import logging
import random
import requests
import certifi
from typing import Optional

logger = logging.getLogger(__name__)


class GitHubClient:
    GRAPH_URL = "https://api.github.com/graphql"

    def __init__(self, token: str, max_retries: int = 7, retry_delay: float = 2.0):
        if not token:
            raise ValueError("GitHub token obrigatório.")

        self.token = token
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.session = requests.Session()
        self.session.verify = certifi.where()

        adapter = requests.adapters.HTTPAdapter(max_retries=0)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        })

        self.last_request_time = 0
        self.min_interval = 0.5  # segundos


    def _throttle(self):
        now = time.time()
        elapsed = now - self.last_request_time

        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        self.last_request_time = time.time()

    def _backoff(self, attempt: int) -> float:
        delay = min(self.retry_delay * (2 ** (attempt - 1)), 60.0)
        return delay + random.uniform(0, 1)

    def wait_for_rate_limit(self):
        rl = self.get_rate_limit()
        remaining = rl.get("remaining", 0)

        if remaining < 100:
            reset_at = rl.get("resetAt")
            reset_ts = int(time.mktime(
                time.strptime(reset_at, "%Y-%m-%dT%H:%M:%SZ")))
            wait = max(reset_ts - int(time.time()), 5)

            logger.warning(
                "Rate-limit baixo (%d). Aguardando %ds...", remaining, wait)
            time.sleep(wait)


    def graphql(self, query: str, variables: Optional[dict] = None) -> dict:
        payload = {"query": query, "variables": variables or {}}

        for attempt in range(1, self.max_retries + 1):
            self._throttle()

            try:
                resp = self.session.post(
                    self.GRAPH_URL,
                    json=payload,
                    timeout=15
                )
            except Exception as exc:
                wait = self._backoff(attempt)
                logger.warning(
                    "Erro transporte (%s). Retry em %.1fs", exc, wait)
                time.sleep(wait)
                continue

            # Rate limit HTTP
            if resp.status_code in (403, 429):
                reset = int(resp.headers.get(
                    "x-ratelimit-reset", time.time() + 60))
                wait = max(reset - int(time.time()), 5)

                logger.warning("Rate-limit HTTP. Aguardando %ds...", wait)
                time.sleep(wait)
                continue

            # Erros servidor
            if resp.status_code >= 500:
                wait = self._backoff(attempt)
                logger.warning("Erro %d. Retry em %.1fs",
                               resp.status_code, wait)
                time.sleep(wait)
                continue

            resp.raise_for_status()

            try:
                data = resp.json()
            except ValueError:
                wait = self._backoff(attempt)
                logger.warning("JSON inválido. Retry em %.1fs", wait)
                time.sleep(wait)
                continue

            # GraphQL errors
            if "errors" in data:
                msgs = [e.get("message", "").lower() for e in data["errors"]]

                if any("rate limit" in m for m in msgs):
                    reset = int(resp.headers.get(
                        "x-ratelimit-reset", time.time() + 60))
                    wait = max(reset - int(time.time()), 5)

                    logger.warning(
                        "Rate-limit (GraphQL). Aguardando %ds...", wait)
                    time.sleep(wait)
                    continue

                if any("timeout" in m or "something went wrong" in m for m in msgs):
                    wait = self._backoff(attempt)
                    logger.warning(
                        "Erro transitório GraphQL. Retry em %.1fs", wait)
                    time.sleep(wait)
                    continue

                logger.debug("GraphQL errors: %s", msgs)

            # Log de custo
            rl = (data.get("data") or {}).get("rateLimit") or {}
            if rl:
                logger.info("Cost: %s | Remaining: %s",
                            rl.get("cost"), rl.get("remaining"))

            return data

        raise RuntimeError("GraphQL falhou após várias tentativas.")


    _RATE_LIMIT_QUERY = """
    query {
      rateLimit {
        limit
        remaining
        resetAt
        cost
      }
    }
    """

    def get_rate_limit(self) -> dict:
        resp = self.session.post(self.GRAPH_URL, json={
                                 "query": self._RATE_LIMIT_QUERY})
        try:
            return resp.json().get("data", {}).get("rateLimit", {})
        except:
            return {}


    _SEARCH_REPOS_QUERY = """
    query($queryStr: String!, $after: String) {
      search(query: $queryStr, type: REPOSITORY, first: 50, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          ... on Repository {
            nameWithOwner
            stargazerCount
            isArchived
            isDisabled
            isFork
          }
        }
      }
    }
    """

    def search_top_repos(self, n: int = 200):
        repos = []
        cursor = None

        while len(repos) < n:
            self.wait_for_rate_limit()

            resp = self.graphql(
                self._SEARCH_REPOS_QUERY,
                {"queryStr": "stars:>1000 sort:stars-desc fork:false", "after": cursor},
            )

            search = (resp.get("data") or {}).get("search", {})
            nodes = search.get("nodes", [])

            for node in nodes:
                if not node:
                    continue
                if node.get("isArchived") or node.get("isDisabled") or node.get("isFork"):
                    continue

                repos.append({
                    "full_name": node["nameWithOwner"],
                    "stargazers_count": node["stargazerCount"],
                })

                if len(repos) >= n:
                    break

            page_info = search.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break

            cursor = page_info.get("endCursor")

        return repos[:n]

 
    _PR_QUERY = """
    query($owner: String!, $name: String!, $states: [PullRequestState!], $after: String) {
      rateLimit {
        remaining
        resetAt
        cost
      }
      repository(owner: $owner, name: $name) {
        pullRequests(
          first: 30,
          states: $states,
          after: $after,
          orderBy: { field: CREATED_AT, direction: DESC }
        ) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            number
            state
            createdAt
            closedAt
            mergedAt

            additions
            deletions
            changedFiles

            bodyText

            comments { totalCount }
            reviews  { totalCount }
          }
        }
      }
    }
    """

    def fetch_prs(self, owner: str, name: str, states=None, max_prs=2000):
        states = states or ["MERGED", "CLOSED"]
        results = []
        cursor = None

        while len(results) < max_prs:
            self.wait_for_rate_limit()

            resp = self.graphql(
                self._PR_QUERY,
                {"owner": owner, "name": name, "states": states, "after": cursor},
            )

            data = resp.get("data") or {}
            repo = data.get("repository") or {}
            prs = repo.get("pullRequests") or {}

            if not prs:
                break

            for pr in prs.get("nodes") or []:
                if pr:
                    results.append(pr)

            page_info = prs.get("pageInfo") or {}
            if not page_info.get("hasNextPage"):
                break

            cursor = page_info.get("endCursor")

        return results
