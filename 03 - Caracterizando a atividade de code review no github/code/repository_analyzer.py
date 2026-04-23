"""
RepositoryAnalyzer (LAB03 - Code Review)

Analisa métricas de PRs:
- Tamanho
- Tempo de análise
- Descrição
- Interações
- Reviews
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set(style="darkgrid")
plt.rcParams["figure.figsize"] = (10, 6)


class RepositoryAnalyzer:

    def __init__(self, df=None, csv_file=None, output_dir="docs"):

        if df is None and csv_file is None:
            raise ValueError("Informe df OU csv_file")

        self.df = df
        self.csv_file = Path(csv_file) if csv_file else None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    # -------------------------------------------------
    # LOAD + FEATURE ENGINEERING
    # -------------------------------------------------

    def load_data(self):
        if self.df is None:
            print(f"Carregando CSV: {self.csv_file}")
            self.df = pd.read_csv(self.csv_file)

        print(f"{len(self.df)} PRs carregados")

        # 🔥 Features derivadas
        self.df["size"] = self.df["additions"] + self.df["deletions"]
        self.df["interactions"] = self.df["participants"] + self.df["comments"]
        self.df["merged"] = self.df["state"].apply(
            lambda x: 1 if x == "MERGED" else 0
        )

    # -------------------------------------------------
    # RQ01 — Tamanho vs Aceitação
    # -------------------------------------------------

    def rq01_size_vs_acceptance(self):
        print("\nRQ01 — Tamanho vs Aceitação")

        sns.boxplot(data=self.df, x="state", y="size")
        plt.title("Tamanho do PR vs Status")
        plt.savefig(self.output_dir / "rq01_size_vs_acceptance.png")
        plt.close()

        print(self.df.groupby("state")["size"].median())

    # -------------------------------------------------
    # RQ02 — Tempo vs Aceitação
    # -------------------------------------------------

    def rq02_time_vs_acceptance(self):
        print("\nRQ02 — Tempo de análise vs Aceitação")

        sns.boxplot(data=self.df, x="state", y="analysis_time_h")
        plt.title("Tempo de análise vs Status")
        plt.savefig(self.output_dir / "rq02_time_vs_acceptance.png")
        plt.close()

        print(self.df.groupby("state")["analysis_time_h"].median())

    # -------------------------------------------------
    # RQ03 — Descrição vs Aceitação
    # -------------------------------------------------

    def rq03_description_vs_acceptance(self):
        print("\nRQ03 — Descrição vs Aceitação")

        sns.boxplot(data=self.df, x="state", y="body_len")
        plt.title("Tamanho da descrição vs Status")
        plt.savefig(self.output_dir / "rq03_description_vs_acceptance.png")
        plt.close()

        print(self.df.groupby("state")["body_len"].median())

    # -------------------------------------------------
    # RQ04 — Interações vs Aceitação
    # -------------------------------------------------

    def rq04_interactions_vs_acceptance(self):
        print("\nRQ04 — Interações vs Aceitação")

        sns.boxplot(data=self.df, x="state", y="interactions")
        plt.title("Interações vs Status")
        plt.savefig(self.output_dir / "rq04_interactions_vs_acceptance.png")
        plt.close()

        print(self.df.groupby("state")["interactions"].median())

    # -------------------------------------------------
    # RQ05–RQ08 — Correlação com Reviews
    # -------------------------------------------------

    def correlation_with_reviews(self):
        print("\nCorrelação com número de reviews")

        cols = ["size", "analysis_time_h",
                "body_len", "interactions", "reviews"]

        corr = self.df[cols].corr(method="spearman")

        print(corr)

        plt.figure(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm")
        plt.title("Correlação (Spearman)")
        plt.savefig(self.output_dir / "correlation_reviews.png")
        plt.close()

    # -------------------------------------------------
    # RUN
    # -------------------------------------------------

    def run(self):
        print("Iniciando análise...")

        self.load_data()

        self.rq01_size_vs_acceptance()
        self.rq02_time_vs_acceptance()
        self.rq03_description_vs_acceptance()
        self.rq04_interactions_vs_acceptance()
        self.correlation_with_reviews()

        print("\nAnálise finalizada!")
        print(f"Saída em: {self.output_dir}")
