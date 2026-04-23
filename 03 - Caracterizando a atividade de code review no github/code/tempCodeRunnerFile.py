"""
main.py
Ponto de entrada do LAB03.

Configuração via .env (ou variável de ambiente):
    GITHUB_TOKEN=ghp_xxxxxxxxxxxx

Flags opcionais (CLI sobrescreve o .env):
    --token         Token do GitHub (sobrescreve GITHUB_TOKEN do .env)
    --repos         Número de repositórios (padrão: 200)
    --workers       Threads paralelas (padrão: 4)
    --confidence    IC da amostra: 0.90 | 0.95 | 0.99 (padrão: 0.95)
    --margin-error  Margem de erro da amostra (padrão: 0.05)
    --output        Diretório de saída (padrão: output)
    --cache         CSV de cache para reutilizar coleta anterior
    --dry-run       Lista repos sem coletar PRs
    --log-level     DEBUG | INFO | WARNING (padrão: INFO)
"""

from repository_analyzer import RepositoryAnalyzer
from pr_collect_service import PRCollectService
from github_client import GitHubClient
import pandas as pd
from dotenv import load_dotenv
import argparse
import logging
import os
import sys
from pathlib import Path

# Garante que o diretório do script esteja no sys.path,
# independentemente de onde o Python foi invocado.
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def _setup_logging(level: str) -> None:
    fmt = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        datefmt="%H:%M:%S",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="LAB03 – Caracterizando Code Review no GitHub",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--token",
        default=None,
        help="GitHub PAT (sobrescreve GITHUB_TOKEN do .env)",
    )
    p.add_argument("--repos",        type=int,   default=200,
                   help="Qtd. de repositórios")
    p.add_argument("--workers",      type=int,   default=4,
                   help="Threads de coleta paralelas")
    p.add_argument("--confidence",   type=float,
                   default=0.95,  help="IC para amostragem")
    p.add_argument("--margin-error", type=float, default=0.05,
                   help="Margem de erro da amostra")
    p.add_argument("--output",       default="output",
                   help="Diretório de saída")
    p.add_argument("--cache",        default=None,
                   help="CSV de cache (pula coleta)")
    p.add_argument("--dry-run",      action="store_true",
                   help="Lista repos sem coletar PRs")
    p.add_argument("--log-level",    default="INFO",
                   help="Nível de log")
    return p.parse_args(argv)


# ---------------------------------------------------------------------------
# Carrega token priorizando: CLI → .env → variável de ambiente
# ---------------------------------------------------------------------------

def _resolve_token(cli_token: str | None) -> str:
    # 1. Carrega o .env (se existir) — não sobrescreve variáveis já definidas no shell
    # Busca o .env sempre relativo ao diretório do main.py
    _BASE_DIR = Path(__file__).resolve().parent
    _env_path = _BASE_DIR / ".env"
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path, override=True)
        print(f"[dotenv] .env carregado de: {_env_path}")
    else:
        print(f"[dotenv] Arquivo .env não encontrado em: {_env_path}")

    token = cli_token or os.getenv("GITHUB_TOKEN", "").strip()

    if not token:
        raise SystemExit(
            "\n[ERRO] Token do GitHub não encontrado.\n"
            "Opções:\n"
            "  1. Crie um arquivo .env com:  GITHUB_TOKEN=ghp_xxx\n"
            "  2. Exporte no shell:          export GITHUB_TOKEN=ghp_xxx\n"
            "  3. Passe via flag:            python main.py --token ghp_xxx\n"
        )
    return token


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> None:
    logger = logging.getLogger("main")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    # 1. Resolve token (dotenv + CLI + env var)
    token = _resolve_token(args.token)

    # 2. GitHub Client (100% GraphQL)
    logger.info("Autenticando na API do GitHub via GraphQL…")
    client = GitHubClient(token=token, max_retries=7, retry_delay=4.0)

    rl = client.get_rate_limit()
    logger.info(
        "Rate-limit: %s/%s pts disponíveis (reset: %s)",
        rl.get("remaining", "?"),
        rl.get("limit", "?"),
        rl.get("resetAt", "?"),
    )

    # 3. Seleção de repositórios
    logger.info(
        "Buscando os %d repositórios mais populares via GraphQL…", args.repos)
    repos = client.search_top_repos(n=args.repos)
    logger.info("%d repositórios obtidos.", len(repos))

    repo_list_path = output / "repos_selecionados.csv"
    pd.DataFrame(repos).to_csv(repo_list_path, index=False)
    logger.info("Lista salva em '%s'", repo_list_path)

    if args.dry_run:
        logger.info("Dry-run: encerrando antes da coleta de PRs.")
        return

    # 4. Coleta de PRs (com cache)
    cache_path = Path(args.cache) if args.cache else output / \
        "dataset_cache.csv"

    if cache_path.exists():
        logger.info("Cache encontrado: carregando '%s'…", cache_path)
        df = pd.read_csv(cache_path)
        logger.info("%d PRs carregados do cache.", len(df))
    else:
        logger.info(
            "Iniciando coleta (IC=%.0f%%, margem=%.0f%%, %d workers)…",
            args.confidence * 100, args.margin_error * 100, args.workers,
        )
        service = PRCollectService(
            client=client,
            confidence=args.confidence,
            margin_error=args.margin_error,
            workers=args.workers,
        )
        df = service.collect(repos)

        if df.empty:
            logger.error("Nenhum PR coletado. Verifique o token e os filtros.")
            sys.exit(1)

        df.to_csv(cache_path, index=False)
        logger.info("Dataset salvo em '%s' (%d PRs).", cache_path, len(df))

    # 5. Análise e relatório
    logger.info("Iniciando análise estatística…")
    analyzer = RepositoryAnalyzer(df=df, output_dir=str(output))
    analyzer.run()

    logger.info("=" * 60)
    logger.info("CONCLUÍDO! Artefatos em '%s':", output)
    for f in sorted(output.iterdir()):
        logger.info("  %s", f.name)
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = _parse_args()
    _setup_logging(args.log_level)
    run(args)
