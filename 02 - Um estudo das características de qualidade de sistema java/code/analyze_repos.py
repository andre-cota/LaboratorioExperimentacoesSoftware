"""
Análise de Repositórios Java Populares do GitHub

Objetivo:
Correlacionar métricas de processo de desenvolvimento com métricas de
qualidade interna obtidas pela ferramenta CK.

RQ01 – Popularidade x Qualidade
RQ02 – Maturidade x Qualidade
RQ03 – Atividade x Qualidade
RQ04 – Tamanho x Qualidade
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path

sns.set(style="darkgrid")
plt.rcParams["figure.figsize"] = (10,6)


class RepositoryAnalyzer:

    def __init__(self, csv_file="repositorios_java.csv"):

        self.csv_file = Path(csv_file)
        self.df = None
        self.now = datetime.now()

        self.output_dir = Path("docs")
        self.output_dir.mkdir(exist_ok=True)


    def load_data(self):

        print("Carregando dados...")
        self.df = pd.read_csv(self.csv_file)
        self.df["createdAt"] = pd.to_datetime(
            self.df["createdAt"], utc=True
        ).dt.tz_localize(None)
        self.df["age_years"] = (self.now - self.df["createdAt"]).dt.days / 365.25
        print(f"{len(self.df)} repositórios carregados")

    # -------------------------------------------------
    # RQ01 – Popularidade vs Qualidade
    # -------------------------------------------------

    def rq01_popularity_quality(self):

        print("\nRQ01 – Popularidade x Qualidade")

        fig, axes = plt.subplots(1,3, figsize=(18,5))

        sns.scatterplot(data=self.df, x="stargazerCount", y="CBO", ax=axes[0])
        axes[0].set_title("Stars vs CBO")

        sns.scatterplot(data=self.df, x="stargazerCount", y="DIT", ax=axes[1])
        axes[1].set_title("Stars vs DIT")

        sns.scatterplot(data=self.df, x="stargazerCount", y="LCOM", ax=axes[2])
        axes[2].set_title("Stars vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ01_popularity_quality.png")
        plt.close()

        print(self.df[["stargazerCount","CBO","DIT","LCOM"]].corr())


    # -------------------------------------------------
    # RQ02 – Maturidade vs Qualidade
    # -------------------------------------------------

    def rq02_maturity_quality(self):

        print("\nRQ02 – Maturidade x Qualidade")

        fig, axes = plt.subplots(1,3, figsize=(18,5))

        sns.scatterplot(data=self.df, x="age_years", y="CBO", ax=axes[0])
        axes[0].set_title("Idade vs CBO")

        sns.scatterplot(data=self.df, x="age_years", y="DIT", ax=axes[1])
        axes[1].set_title("Idade vs DIT")

        sns.scatterplot(data=self.df, x="age_years", y="LCOM", ax=axes[2])
        axes[2].set_title("Idade vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ02_maturity_quality.png")
        plt.close()

        print(self.df[["age_years","CBO","DIT","LCOM"]].corr())


    # -------------------------------------------------
    # RQ03 – Atividade vs Qualidade
    # -------------------------------------------------

    def rq03_activity_quality(self):

        print("\nRQ03 – Atividade x Qualidade")

        fig, axes = plt.subplots(1,3, figsize=(18,5))

        sns.scatterplot(data=self.df, x="releases", y="CBO", ax=axes[0])
        axes[0].set_title("Releases vs CBO")

        sns.scatterplot(data=self.df, x="releases", y="DIT", ax=axes[1])
        axes[1].set_title("Releases vs DIT")

        sns.scatterplot(data=self.df, x="releases", y="LCOM", ax=axes[2])
        axes[2].set_title("Releases vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ03_activity_quality.png")
        plt.close()

        print(self.df[["releases","CBO","DIT","LCOM"]].corr())


    # -------------------------------------------------
    # RQ04 – Tamanho vs Qualidade
    # -------------------------------------------------

    def rq04_size_quality(self):

        print("\nRQ04 – Tamanho x Qualidade")

        fig, axes = plt.subplots(1,3, figsize=(18,5))

        sns.scatterplot(data=self.df, x="LOC", y="CBO", ax=axes[0])
        axes[0].set_title("LOC vs CBO")

        sns.scatterplot(data=self.df, x="LOC", y="DIT", ax=axes[1])
        axes[1].set_title("LOC vs DIT")

        sns.scatterplot(data=self.df, x="LOC", y="LCOM", ax=axes[2])
        axes[2].set_title("LOC vs LCOM")

        plt.tight_layout()
        plt.savefig(self.output_dir / "RQ04_size_quality.png")
        plt.close()

        print(self.df[["LOC","CBO","DIT","LCOM"]].corr())


    # -------------------------------------------------
    # Matriz de correlação geral
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
            "LCOM"
        ]

        corr = self.df[cols].corr()

        plt.figure(figsize=(10,8))
        sns.heatmap(corr, annot=True, cmap="coolwarm")
        plt.title("Correlação entre métricas de processo e qualidade")

        plt.tight_layout()
        plt.savefig(self.output_dir / "correlation_matrix.png")
        plt.close()


    # -------------------------------------------------
    # Execução geral
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
        print(f"Gráficos salvos em {self.output_dir}")


if __name__ == "__main__":

    analyzer = RepositoryAnalyzer("dataset_final.csv")
    analyzer.run()