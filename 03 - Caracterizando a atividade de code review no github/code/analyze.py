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


def setup_logging(level="INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s  %(levelname)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Análise estatística do dataset de PRs"
    )

    parser.add_argument(
        "--input",
        default="output/dataset_cache.csv",
        help="Caminho do CSV (ex: output/dataset_cache.csv)"
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

    logging.info("Total de registros: %d", len(df))

    analyzer = RepositoryAnalyzer(df=df, output_dir=str(output_path))
    analyzer.run()

    logging.info("=" * 50)
    logging.info("ANÁLISE CONCLUÍDA")
    logging.info("Arquivos gerados em: %s", output_path.resolve())
    logging.info("=" * 50)


if __name__ == "__main__":
    main()
