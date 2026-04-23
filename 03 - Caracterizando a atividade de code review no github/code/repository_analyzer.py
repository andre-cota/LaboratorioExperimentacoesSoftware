"""
RepositoryAnalyzer
Análise de métricas de repositórios (processo vs qualidade)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path

sns.set(style="darkgrid")
plt.rcParams["figure.figsize"] = (10, 6)


class RepositoryAnalyzer:

    def __init__(self, df: pd.DataFrame = None, csv_file: str = None, output_dir: str = "docs"):
        """
        Pode receber:
        - df diretamente (recomendado)
        - OU csv_file
        """
        if df is None and csv_file is None:
            raise ValueError("Informe df OU csv_file")

        self.df = df
        self.csv_file = Path(csv_file) if csv_file else None
        self.now = datetime.now()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    # -------------------------------------------------
    # Load
    # -------------------------------------------------

    def load_data(self):
        if self.df is None:
            print(f"Carregando CSV: {self.csv_file}")
            self.df = pd.read_csv(self.csv_file)

        # Normalização
        if "createdAt" in self.df.columns:
            self.df["createdAt"] = pd.to_datetime(
                self.df["createdAt"], errors="coerce", utc=True
            ).dt.tz_localize(None)

            self.df["age_years"] = (
                self.now - self.df["createdAt"]
            ).dt.days / 365.25

        print(f"{len(self.df)} registros carregados")

    # -------------------------------------------------
    # Util
    # -------------------------------------------------

    def _check_columns(self, cols):
        missing = [c for c in cols if c not in self.df.columns]
        if missing:
            raise ValueError(f"Colunas ausentes: {missing}")

    # -------------------------------------------------
    # RQ01
    # -------------------------------------------------

    def rq01_popularity_quality(self):
        print("\nRQ01 – Popularidade x Qualidade")

        cols = ["stargazerCount", "CBO", "DIT", "LCOM"]
        self._check_columns(cols)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        sns.scatterplot(data=self.df, x="stargazerCount", y="CBO", ax=axes[0])
        axes[0].set_title("Stars vs CBO")

        sns.scatterplot(data=self.df, x="stargazerCount", y="DIT", ax=axes[1])
        axes[1].set_title("Stars vs DIT")

        sns.scatterplot(data=self.df, x="stargazerCount", y="LCOM", ax=axes[2])
        axes[2].set_title("Stars vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ01_popularity_quality.png")
        plt.close()

        print(self.df[cols].corr())

    # -------------------------------------------------
    # RQ02
    # -------------------------------------------------

    def rq02_maturity_quality(self):
        print("\nRQ02 – Maturidade x Qualidade")

        cols = ["age_years", "CBO", "DIT", "LCOM"]
        self._check_columns(cols)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        sns.scatterplot(data=self.df, x="age_years", y="CBO", ax=axes[0])
        axes[0].set_title("Idade vs CBO")

        sns.scatterplot(data=self.df, x="age_years", y="DIT", ax=axes[1])
        axes[1].set_title("Idade vs DIT")

        sns.scatterplot(data=self.df, x="age_years", y="LCOM", ax=axes[2])
        axes[2].set_title("Idade vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ02_maturity_quality.png")
        plt.close()

        print(self.df[cols].corr())

    # -------------------------------------------------
    # RQ03
    # -------------------------------------------------

    def rq03_activity_quality(self):
        print("\nRQ03 – Atividade x Qualidade")

        cols = ["releases", "CBO", "DIT", "LCOM"]
        self._check_columns(cols)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        sns.scatterplot(data=self.df, x="releases", y="CBO", ax=axes[0])
        axes[0].set_title("Releases vs CBO")

        sns.scatterplot(data=self.df, x="releases", y="DIT", ax=axes[1])
        axes[1].set_title("Releases vs DIT")

        sns.scatterplot(data=self.df, x="releases", y="LCOM", ax=axes[2])
        axes[2].set_title("Releases vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ03_activity_quality.png")
        plt.close()

        print(self.df[cols].corr())

    # -------------------------------------------------
    # RQ04
    # -------------------------------------------------

    def rq04_size_quality(self):
        print("\nRQ04 – Tamanho x Qualidade")

        cols = ["LOC", "CBO", "DIT", "LCOM"]
        self._check_columns(cols)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))

        sns.scatterplot(data=self.df, x="LOC", y="CBO", ax=axes[0])
        axes[0].set_title("LOC vs CBO")

        sns.scatterplot(data=self.df, x="LOC", y="DIT", ax=axes[1])
        axes[1].set_title("LOC vs DIT")

        sns.scatterplot(data=self.df, x="LOC", y="LCOM", ax=axes[2])
        axes[2].set_title("LOC vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ04_size_quality.png")
        plt.close()

        print(self.df[cols].corr())

    # -------------------------------------------------
    # Matriz
    # -------------------------------------------------

    def correlation_matrix(self):
        print("\nGerando matriz de correlação")

        cols = [
            "stargazerCount",
            "age_years",
            "releases",
            "LOC",
            "CBO",
            "DIT",
            "LCOM",
        ]

        self._check_columns(cols)

        corr = self.df[cols].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap="coolwarm")

        plt.title("Correlação geral")
        plt.tight_layout()
        plt.savefig(self.output_dir / "correlation_matrix.png")
        plt.close()

    # -------------------------------------------------
    # RUN
    # -------------------------------------------------

    def run(self):
        print("Iniciando análise...")

        self.load_data()

        self.rq01_popularity_quality()
        self.rq02_maturity_quality()
        self.rq03_activity_quality()
        self.rq04_size_quality()

        self.correlation_matrix()

        print("\nAnálise finalizada!")
        print(f"Saída em: {self.output_dir}")
