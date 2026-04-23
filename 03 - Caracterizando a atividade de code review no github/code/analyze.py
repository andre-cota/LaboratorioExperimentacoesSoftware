"""
analyze.py
Executa análise estatística a partir de um dataset CSV.

Uso:
    python analyze.py --input output/dataset_cache.csv
"""

import pandas as pd
import argparse
import logging
from pathlib import Path

from repository_analyzer import RepositoryAnalyzer


# -------------------------------------------------
# Logging
# -------------------------------------------------

def setup_logging(level="INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)s — %(message)s",
        datefmt="%H:%M:%S",
    )


# -------------------------------------------------
# CLI
# -------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Análise estatística do dataset de PRs"
    )

    parser.add_argument(
        "--input",
        default="output/dataset_cache.csv",
        help="Caminho do CSV"
    )

    parser.add_argument(
        "--output",
        default="output",
        help="Diretório de saída dos gráficos"
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        help="DEBUG | INFO | WARNING"
    )

    return parser.parse_args()


# -------------------------------------------------
# Validação do dataset
# -------------------------------------------------

def validate_columns(df: pd.DataFrame):
    required = [
        "state",
        "additions",
        "deletions",
        "analysis_time_h",
        "body_len",
        "participants",
        "comments",
        "reviews",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise SystemExit(f"[ERRO] Colunas obrigatórias ausentes: {missing}")


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    args = parse_args()
    setup_logging(args.log_level)

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise SystemExit(f"[ERRO] Arquivo não encontrado: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    logging.info("Carregando dataset: %s", input_path)

    df = pd.read_csv(input_path)

    if df.empty:
        raise SystemExit("[ERRO] Dataset vazio.")

    logging.info("Total de PRs: %d", len(df))

    # 🔥 valida estrutura
    validate_columns(df)

    # 🔥 limpeza básica (evita bugs silenciosos)
    df = df.dropna(subset=["state"])

    # 🔥 normalização simples
    df["state"] = df["state"].str.upper()

    logging.info("Iniciando análise...")

    analyzer = RepositoryAnalyzer(
        df=df,
        output_dir=str(output_path)
    )

    analyzer.run()

    logging.info("=" * 50)
    logging.info("ANÁLISE CONCLUÍDA")
    logging.info("Arquivos gerados em: %s", output_path.resolve())
    logging.info("=" * 50)


# -------------------------------------------------
# Entry point
# -------------------------------------------------

if __name__ == "__main__":
    main()