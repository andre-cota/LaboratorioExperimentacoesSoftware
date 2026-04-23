"""
pr_collect_service.py
Orquestra a coleta de PRs, aplica filtros do enunciado e calcula
a amostra estatística para cada repositório.
"""

import math
import time
import logging
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import pandas as pd

from github_client import GitHubClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Funções de amostragem estatística
# ---------------------------------------------------------------------------

def sample_size(
    population: int,
    confidence: float = 0.95,
    margin_error: float = 0.05,
    p: float = 0.5,
) -> int:
    """
    Calcula o tamanho mínimo de amostra para estimar uma proporção
    com intervalo de confiança e margem de erro definidos.

    Fórmula (população finita):
        n = (Z² * p * (1-p)) / e²
        n_ajustado = n / (1 + (n-1)/N)

    Parâmetros
    ----------
    population   : tamanho da população (total de PRs disponíveis)
    confidence   : nível de confiança (padrão 0.95 → Z ≈ 1.96)
    margin_error : margem de erro (padrão 0.05 → 5 %)
    p            : proporção estimada (0.5 = máxima variância)

    Retorna o tamanho da amostra como inteiro.
    """
    z_scores = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
    z = z_scores.get(confidence, 1.960)

    n_inf = (z**2 * p * (1 - p)) / (margin_error**2)           # pop. infinita
    n_fin = n_inf / (1 + (n_inf - 1) / population)              # pop. finita
    return max(30, math.ceil(n_fin))                             # mínimo 30


# ---------------------------------------------------------------------------
# Filtros conforme o enunciado (Seção 1 – Criação do Dataset)
# ---------------------------------------------------------------------------

_MIN_REVIEW_HOURS = 1   # diferença criação → fechamento ≥ 1 h
_MIN_REVIEWS = 1   # pelo menos 1 revisão humana


def _parse_dt(s: Optional[str]) -> Optional[datetime.datetime]:
    if not s:
        return None
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def _apply_filters(prs: list[dict]) -> list[dict]:
    """
    Mantém apenas PRs que satisfazem:
      - status MERGED ou CLOSED  (garantido pela query, mas checamos)
      - ao menos 1 revisão
      - tempo entre criação e encerramento ≥ 1 hora
    """
    valid = []
    for pr in prs:
        # 1. revisões
        if pr.get("reviews", {}).get("totalCount", 0) < _MIN_REVIEWS:
            continue

        # 2. tempo de análise ≥ 1 h
        created = _parse_dt(pr.get("createdAt"))
        closed = _parse_dt(pr.get("mergedAt") or pr.get("closedAt"))
        if not created or not closed:
            continue
        delta_h = (closed - created).total_seconds() / 3600
        if delta_h < _MIN_REVIEW_HOURS:
            continue

        valid.append(pr)
    return valid


def _extract_metrics(pr: dict) -> dict:
    """
    Transforma um nó GraphQL de PR nas métricas do enunciado.
    """
    created = _parse_dt(pr["createdAt"])
    closed = _parse_dt(pr.get("mergedAt") or pr.get("closedAt"))
    delta_h = (closed - created).total_seconds() / \
        3600 if created and closed else None

    return {
        # identificação
        "number":       pr.get("number"),
        "state":        pr.get("state"),
        # Tamanho
        "changed_files": pr.get("changedFiles", 0),
        "additions":     pr.get("additions", 0),
        "deletions":     pr.get("deletions", 0),
        # Tempo de Análise (horas)
        "analysis_time_h": round(delta_h, 4) if delta_h else None,
        # Descrição
        "body_len":  len(pr.get("bodyText") or ""),
        # Interações
        "participants": pr.get("participants", {}).get("totalCount", 0),
        "comments":     pr.get("comments",     {}).get("totalCount", 0),
        # Variável dependente
        "reviews":      pr.get("reviews",      {}).get("totalCount", 0),
    }


# ---------------------------------------------------------------------------
# Serviço principal
# ---------------------------------------------------------------------------

class PRCollectService:
    """
    Coordena a coleta de PRs para uma lista de repositórios,
    aplicando amostragem estatística para limitar o número de
    requisições sem comprometer a validade estatística dos resultados.
    """

    def __init__(
        self,
        client: GitHubClient,
        confidence:   float = 0.95,
        margin_error: float = 0.05,
        workers:      int = 2,
        min_prs_repo: int = 100,
    ):
        """
        Parâmetros
        ----------
        client        : instância de GitHubClient
        confidence    : confiança para cálculo de amostra (0.90 / 0.95 / 0.99)
        margin_error  : margem de erro aceitável (ex.: 0.05 = 5 %)
        workers       : threads paralelas para coleta (cuidado com rate-limit)
        min_prs_repo  : repositório deve ter pelo menos este total de PRs
        """
        self.client = client
        self.confidence = confidence
        self.margin_error = margin_error
        self.workers = workers
        self.min_prs_repo = min_prs_repo

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def collect(self, repos: list[dict]) -> pd.DataFrame:
        """
        Coleta PRs de todos os repositórios e retorna um DataFrame
        com as métricas calculadas.

        O processo por repositório é:
          1. Busca um lote inicial de PRs para estimar a população.
          2. Calcula o n amostral estatístico.
          3. Filtra pelos critérios do enunciado.
          4. Amostra aleatória (se necessário).
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {}
            for i, r in enumerate(repos):
                # Stagger: pequena pausa entre submissões para não sobrecarregar a API
                if i > 0 and i % self.workers == 0:
                    time.sleep(1.0)
                futures[pool.submit(self._collect_repo, r)] = r["full_name"]
            for future in as_completed(futures):
                repo_name = futures[future]
                try:
                    df_repo = future.result()
                    if df_repo is not None and not df_repo.empty:
                        df_repo["repo"] = repo_name
                        results.append(df_repo)
                        logger.info("✓ %s — %d PRs coletados",
                                    repo_name, len(df_repo))
                except Exception as exc:
                    logger.warning("✗ %s falhou: %s", repo_name, exc)

        if not results:
            logger.error("Nenhum PR coletado.")
            return pd.DataFrame()

        df = pd.concat(results, ignore_index=True)
        logger.info("Total final: %d PRs de %d repositórios",
                    len(df), len(results))
        return df

    # ------------------------------------------------------------------
    # Coleta por repositório
    # ------------------------------------------------------------------

    def _collect_repo(self, repo: dict) -> Optional[pd.DataFrame]:
        owner, name = repo["full_name"].split("/", 1)

        # Coleta inicial para estimar população (cap de 500 para descoberta rápida)
        raw_prs = self.client.fetch_prs(owner, name, max_prs=500)
        filtered = _apply_filters(raw_prs)

        population = len(filtered)
        if population < self.min_prs_repo:
            logger.debug("%s/%s ignorado: apenas %d PRs válidos",
                         owner, name, population)
            return None

        # Amostra estatística
        n = sample_size(population, self.confidence, self.margin_error)

        if n >= population:
            sample = filtered
        else:
            import random
            sample = random.sample(filtered, n)
            logger.debug(
                "%s/%s: pop=%d, amostra=%d (IC=%.0f%%, e=%.0f%%)",
                owner, name, population, n,
                self.confidence * 100, self.margin_error * 100,
            )

        rows = [_extract_metrics(pr) for pr in sample]
        return pd.DataFrame(rows)
