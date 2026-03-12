"""
Script de Análise de Repositórios Populares do GitHub
Analisa dados coletados e gera gráficos para responder às RQs da pesquisa.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class RepositoryAnalyzer:
    def __init__(self, csv_file=None):
        """Inicializa o analisador e carrega os dados."""
        if csv_file is None:
            script_dir = Path(__file__).parent
            candidate_paths = [
                script_dir / '../../repositorios.csv',
                script_dir / '../../../repositorios.csv',
                Path.cwd() / 'repositorios.csv',
            ]

            csv_file = next((path for path in candidate_paths if path.exists()), candidate_paths[0])
        
        self.csv_file = Path(csv_file).resolve()
        self.df = None
        self.current_date = datetime.now()
        self.output_dir = Path(__file__).parent.parent / 'docs'
        self.output_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """Carrega dados do CSV e faz o pré-processamento."""
        print(f"Carregando dados de {self.csv_file}...")
        self.df = pd.read_csv(self.csv_file)
        
        self.df['createdAt'] = pd.to_datetime(self.df['createdAt']).dt.tz_localize(None)
        self.df['pushedAt'] = pd.to_datetime(self.df['pushedAt']).dt.tz_localize(None)
        
        self.df['age_days'] = (self.current_date - self.df['createdAt']).dt.days
        self.df['age_years'] = self.df['age_days'] / 365.25
        self.df['days_since_update'] = (self.current_date - self.df['pushedAt']).dt.days
        
        if 'closedIssues' in self.df.columns:
            self.df['closed_issues_ratio'] = self.df.apply(
                lambda row: (row['closedIssues'] / row['totalIssues'] * 100) 
                if row['totalIssues'] > 0 else 0, 
                axis=1
            )
        else:
            print("⚠ Aviso: Coluna 'closedIssues' não encontrada. RQ06 não será calculada.")
            self.df['closed_issues_ratio'] = 0
        
        print(f"✓ Dados carregados: {len(self.df)} repositórios")
        print(f"✓ Período: {self.df['createdAt'].min().date()} a {self.df['createdAt'].max().date()}")
        print(f"✓ Linguagens encontradas: {self.df['primaryLanguage'].nunique()}")
        
    def rq01_repository_age(self):
        """RQ01: Sistemas populares são maduros/antigos?
        Métrica: idade do repositório (em anos)
        """
        print("\n=== RQ01: Maturidade dos Repositórios ===")
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        axes[0].hist(self.df['age_years'], bins=30, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Idade (anos)')
        axes[0].set_ylabel('Número de Repositórios')
        axes[0].set_title('RQ01: Distribuição da Idade dos Repositórios')
        axes[0].axvline(self.df['age_years'].median(), color='red', 
                        linestyle='--', label=f'Mediana: {self.df["age_years"].median():.1f} anos')
        axes[0].axvline(self.df['age_years'].mean(), color='green', 
                        linestyle='--', label=f'Média: {self.df["age_years"].mean():.1f} anos')
        axes[0].legend()
        
        axes[1].boxplot(self.df['age_years'], vert=True)
        axes[1].set_ylabel('Idade (anos)')
        axes[1].set_title('RQ01: Boxplot da Idade dos Repositórios')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ01_idade_repositorios.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Média de idade: {self.df['age_years'].mean():.2f} anos")
        print(f"Mediana de idade: {self.df['age_years'].median():.2f} anos")
        print(f"Desvio padrão: {self.df['age_years'].std():.2f} anos")
        print(f"Repositório mais antigo: {self.df['age_years'].max():.2f} anos")
        print(f"Repositório mais novo: {self.df['age_years'].min():.2f} anos")
        
    def rq02_pull_requests(self):
        """RQ02: Sistemas populares recebem muita contribuição externa?
        Métrica: total de pull requests aceitas e stars
        """
        print("\n=== RQ02: Pull Requests Aceitas e Stars ===")

        fig, axes = plt.subplots(1, 2, figsize=(18, 6))

        top_prs = self.df.nlargest(20, 'pullRequests')[['name', 'pullRequests']]
        axes[0].barh(range(len(top_prs)), top_prs['pullRequests'])
        axes[0].set_yticks(range(len(top_prs)))
        axes[0].set_yticklabels(top_prs['name'], fontsize=8)
        axes[0].set_xlabel('Pull Requests Aceitas')
        axes[0].set_title('RQ02: Top 20 Repositórios - PRs Aceitas')
        axes[0].invert_yaxis()

        top_stars = self.df.nlargest(20, 'stargazerCount')[['name', 'stargazerCount']]
        axes[1].barh(range(len(top_stars)), top_stars['stargazerCount'])
        axes[1].set_yticks(range(len(top_stars)))
        axes[1].set_yticklabels(top_stars['name'], fontsize=8)
        axes[1].set_xlabel('Número de Stars')
        axes[1].set_title('RQ02: Top 20 Repositórios - Stars')
        axes[1].invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ02_pull_requests.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Média de PRs: {self.df['pullRequests'].mean():.2f}")
        print(f"Mediana de PRs: {self.df['pullRequests'].median():.2f}")
        print(f"Total de PRs: {self.df['pullRequests'].sum()}")
        print(f"\nMédia de Stars: {self.df['stargazerCount'].mean():.2f}")
        print(f"Mediana de Stars: {self.df['stargazerCount'].median():.2f}")
        print(f"Total de Stars: {self.df['stargazerCount'].sum()}")
        
    def rq03_releases(self):
        """RQ03: Sistemas populares lançam releases com frequência?
        Métrica: total de releases
        """
        print("\n=== RQ03: Releases ===")

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        ax.hist(self.df['releases'], bins=50, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Número de Releases')
        ax.set_ylabel('Número de Repositórios')
        ax.set_title('RQ03: Distribuição de Releases')
        ax.axvline(self.df['releases'].median(), color='red', 
                   linestyle='--', label=f'Mediana: {self.df["releases"].median():.0f}')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ03_releases.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Média de releases: {self.df['releases'].mean():.2f}")
        print(f"Mediana de releases: {self.df['releases'].median():.2f}")
        repos_sem_release = (self.df['releases'] == 0).sum()
        print(f"Repositórios sem releases: {repos_sem_release} ({repos_sem_release/len(self.df)*100:.1f}%)")
        
    def rq04_update_frequency(self):
        """RQ04: Sistemas populares são atualizados com frequência?
        Métrica: tempo até a última atualização (em dias)
        """
        print("\n=== RQ04: Frequência de Atualização ===")
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        axes[0].hist(self.df['days_since_update'], bins=30, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Dias desde a última atualização')
        axes[0].set_ylabel('Número de Repositórios')
        axes[0].set_title('RQ04: Distribuição do Tempo desde Última Atualização')
        axes[0].axvline(self.df['days_since_update'].median(), color='red', 
                        linestyle='--', label=f'Mediana: {self.df["days_since_update"].median():.0f} dias')
        axes[0].legend()
        
        categories = []
        for days in self.df['days_since_update']:
            if days <= 7:
                categories.append('Última semana')
            elif days <= 30:
                categories.append('Último mês')
            elif days <= 180:
                categories.append('Últimos 6 meses')
            else:
                categories.append('Mais de 6 meses')
        
        self.df['update_category'] = categories
        category_counts = self.df['update_category'].value_counts()
        
        axes[1].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%')
        axes[1].set_title('RQ04: Categorias de Atualização')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ04_update_frequency.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Média de dias desde última atualização: {self.df['days_since_update'].mean():.2f}")
        print(f"Mediana: {self.df['days_since_update'].median():.2f} dias")
        print(f"Atualizados na última semana: {(self.df['days_since_update'] <= 7).sum()}")
        
    def rq05_programming_languages(self):
        """RQ05: Sistemas populares são escritos nas linguagens mais populares?
        Métrica: linguagem primária
        """
        print("\n=== RQ05: Linguagens de Programação ===")
        
        language_counts = self.df['primaryLanguage'].value_counts().head(15)
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        axes[0].barh(range(len(language_counts)), language_counts.values)
        axes[0].set_yticks(range(len(language_counts)))
        axes[0].set_yticklabels(language_counts.index)
        axes[0].set_xlabel('Número de Repositórios')
        axes[0].set_title('RQ05: Top 15 Linguagens mais Populares')
        axes[0].invert_yaxis()
        
        for i, v in enumerate(language_counts.values):
            axes[0].text(v, i, f' {v}', va='center')
        
        top10_langs = language_counts.head(10)
        axes[1].pie(top10_langs.values, labels=top10_langs.index, autopct='%1.1f%%')
        axes[1].set_title('RQ05: Distribuição das Top 10 Linguagens')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ05_languages.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Total de linguagens diferentes: {self.df['primaryLanguage'].nunique()}")
        print("\nTop 10 linguagens:")
        for lang, count in language_counts.head(10).items():
            print(f"  {lang}: {count} ({count/len(self.df)*100:.1f}%)")
        
    def rq06_closed_issues_ratio(self):
        """RQ06: Sistemas populares possuem um alto percentual de issues fechadas?
        Métrica: razão entre issues fechadas e total de issues
        """
        print("\n=== RQ06: Razão de Issues Fechadas ===")
        
        df_with_issues = self.df[self.df['totalIssues'] > 0].copy()
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        axes[0].hist(df_with_issues['closed_issues_ratio'], bins=30, 
                     edgecolor='black', alpha=0.7, range=(0, 100))
        axes[0].set_xlabel('Percentual de Issues Fechadas (%)')
        axes[0].set_ylabel('Número de Repositórios')
        axes[0].set_title('RQ06: Distribuição da Razão de Issues Fechadas')
        axes[0].axvline(df_with_issues['closed_issues_ratio'].median(), color='red', 
                        linestyle='--', label=f'Mediana: {df_with_issues["closed_issues_ratio"].median():.1f}%')
        axes[0].axvline(df_with_issues['closed_issues_ratio'].mean(), color='green', 
                        linestyle='--', label=f'Média: {df_with_issues["closed_issues_ratio"].mean():.1f}%')
        axes[0].legend()
        
        axes[1].boxplot(df_with_issues['closed_issues_ratio'])
        axes[1].set_ylabel('Percentual de Issues Fechadas (%)')
        axes[1].set_title('RQ06: Boxplot da Razão de Issues Fechadas')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ06_closed_issues_ratio.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Média de issues fechadas: {df_with_issues['closed_issues_ratio'].mean():.2f}%")
        print(f"Mediana: {df_with_issues['closed_issues_ratio'].median():.2f}%")
        repos_high_closure = (df_with_issues['closed_issues_ratio'] >= 80).sum()
        print(f"Repositórios com ≥80% de issues fechadas: {repos_high_closure} ({repos_high_closure/len(df_with_issues)*100:.1f}%)")
        
    def rq07_metrics_by_language(self):
        """RQ07 (BÔNUS): Sistemas escritos em linguagens mais populares recebem mais contribuições?
        Analisa RQ02, RQ03 e RQ04 divididos por linguagem
        """
        print("\n=== RQ07 (BÔNUS): Métricas por Linguagem ===")
        
        top_languages = self.df['primaryLanguage'].value_counts().head(10).index
        df_top_langs = self.df[self.df['primaryLanguage'].isin(top_languages)]
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 16))
        
        prs_by_lang = df_top_langs.groupby('primaryLanguage')['pullRequests'].agg(['mean', 'median'])
        prs_by_lang = prs_by_lang.sort_values('mean', ascending=False)
        
        x = np.arange(len(prs_by_lang))
        width = 0.35
        axes[0].bar(x - width/2, prs_by_lang['mean'], width, label='Média', alpha=0.8)
        axes[0].bar(x + width/2, prs_by_lang['median'], width, label='Mediana', alpha=0.8)
        axes[0].set_xlabel('Linguagem')
        axes[0].set_ylabel('Pull Requests')
        axes[0].set_title('RQ07: Pull Requests Aceitas por Linguagem (Top 10)')
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(prs_by_lang.index, rotation=45, ha='right')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='y')
        
        releases_by_lang = df_top_langs.groupby('primaryLanguage')['releases'].agg(['mean', 'median'])
        releases_by_lang = releases_by_lang.sort_values('mean', ascending=False)
        
        x = np.arange(len(releases_by_lang))
        axes[1].bar(x - width/2, releases_by_lang['mean'], width, label='Média', alpha=0.8)
        axes[1].bar(x + width/2, releases_by_lang['median'], width, label='Mediana', alpha=0.8)
        axes[1].set_xlabel('Linguagem')
        axes[1].set_ylabel('Releases')
        axes[1].set_title('RQ07: Releases por Linguagem (Top 10)')
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(releases_by_lang.index, rotation=45, ha='right')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3, axis='y')
        
        days_by_lang = df_top_langs.groupby('primaryLanguage')['days_since_update'].agg(['mean', 'median'])
        days_by_lang = days_by_lang.sort_values('mean')
        
        x = np.arange(len(days_by_lang))
        axes[2].bar(x - width/2, days_by_lang['mean'], width, label='Média', alpha=0.8)
        axes[2].bar(x + width/2, days_by_lang['median'], width, label='Mediana', alpha=0.8)
        axes[2].set_xlabel('Linguagem')
        axes[2].set_ylabel('Dias desde última atualização')
        axes[2].set_title('RQ07: Frequência de Atualização por Linguagem (Top 10)')
        axes[2].set_xticks(x)
        axes[2].set_xticklabels(days_by_lang.index, rotation=45, ha='right')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'RQ07_metrics_by_language.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("\nPull Requests por linguagem (média):")
        for lang, row in prs_by_lang.head(5).iterrows():
            print(f"  {lang}: {row['mean']:.0f}")
            
        print("\nReleases por linguagem (média):")
        for lang, row in releases_by_lang.head(5).iterrows():
            print(f"  {lang}: {row['mean']:.0f}")
            
        print("\nDias desde atualização por linguagem (média):")
        for lang, row in days_by_lang.head(5).iterrows():
            print(f"  {lang}: {row['mean']:.1f}")
    
    def generate_summary_report(self):
        """Gera um relatório resumido em texto."""
        print("\n" + "="*60)
        print("RELATÓRIO RESUMIDO DA ANÁLISE")
        print("="*60)
        
        report = f"""
ANÁLISE DE {len(self.df)} REPOSITÓRIOS POPULARES DO GITHUB
Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}

RESUMO GERAL:
-------------
• Período analisado: {self.df['createdAt'].min().date()} a {self.df['createdAt'].max().date()}
• Total de stars: {self.df['stargazerCount'].sum():,}
• Total de PRs aceitas: {self.df['pullRequests'].sum():,}
• Total de releases: {self.df['releases'].sum():,}
• Total de issues: {self.df['totalIssues'].sum():,}
• Linguagens diferentes: {self.df['primaryLanguage'].nunique()}

PRINCIPAIS DESCOBERTAS:
----------------------

RQ01 - MATURIDADE:
  → Idade média: {self.df['age_years'].mean():.1f} anos
  → Mediana: {self.df['age_years'].median():.1f} anos
  → Conclusão: {'Repositórios tendem a ser maduros' if self.df['age_years'].median() > 5 else 'Repositórios relativamente novos'}

RQ02 - CONTRIBUIÇÕES EXTERNAS:
  → Média de PRs: {self.df['pullRequests'].mean():.0f}
  → Mediana de PRs: {self.df['pullRequests'].median():.0f}
  → Conclusão: {'Alta contribuição externa' if self.df['pullRequests'].median() > 100 else 'Contribuição externa moderada'}

RQ03 - RELEASES:
  → Média de releases: {self.df['releases'].mean():.0f}
  → Mediana: {self.df['releases'].median():.0f}
  → Sem releases: {(self.df['releases'] == 0).sum()} ({(self.df['releases'] == 0).sum()/len(self.df)*100:.1f}%)

RQ04 - FREQUÊNCIA DE ATUALIZAÇÃO:
  → Média de dias desde última atualização: {self.df['days_since_update'].mean():.1f}
  → Mediana: {self.df['days_since_update'].median():.1f}
  → Atualizados na última semana: {(self.df['days_since_update'] <= 7).sum()} ({(self.df['days_since_update'] <= 7).sum()/len(self.df)*100:.1f}%)
  → Conclusão: {'Repositórios muito ativos' if self.df['days_since_update'].median() < 30 else 'Atualizações moderadas'}

RQ05 - LINGUAGENS POPULARES:
  → Linguagem #1: {self.df['primaryLanguage'].value_counts().index[0]} ({self.df['primaryLanguage'].value_counts().values[0]} repos)
  → Linguagem #2: {self.df['primaryLanguage'].value_counts().index[1]} ({self.df['primaryLanguage'].value_counts().values[1]} repos)
  → Linguagem #3: {self.df['primaryLanguage'].value_counts().index[2]} ({self.df['primaryLanguage'].value_counts().values[2]} repos)

RQ06 - ISSUES FECHADAS:
  → Média de issues fechadas: {self.df[self.df['totalIssues'] > 0]['closed_issues_ratio'].mean():.1f}%
  → Mediana: {self.df[self.df['totalIssues'] > 0]['closed_issues_ratio'].median():.1f}%
  → Com ≥80% fechadas: {(self.df['closed_issues_ratio'] >= 80).sum()} repos

ARQUIVOS GERADOS:
----------------
• RQ01_idade_repositorios.png
• RQ02_pull_requests.png
• RQ03_releases.png
• RQ04_update_frequency.png
• RQ05_languages.png
• RQ06_closed_issues_ratio.png
• RQ07_metrics_by_language.png
• relatorio_analise.txt (este arquivo)

"""
        print(report)
        
        with open(self.output_dir / 'relatorio_analise.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✓ Relatório salvo em: {self.output_dir / 'relatorio_analise.txt'}")
    
    def run_all_analyses(self):
        """Executa todas as análises e gera todos os gráficos."""
        print("\n" + "="*60)
        print("INICIANDO ANÁLISE COMPLETA DOS REPOSITÓRIOS")
        print("="*60)
        
        self.load_data()
        
        self.rq01_repository_age()
        self.rq02_pull_requests()
        self.rq03_releases()
        self.rq04_update_frequency()
        self.rq05_programming_languages()
        self.rq06_closed_issues_ratio()
        self.rq07_metrics_by_language()
        
        self.generate_summary_report()
        
        print("\n" + "="*60)
        print("✓ ANÁLISE COMPLETA FINALIZADA!")
        print(f"✓ Gráficos salvos em: {self.output_dir.absolute()}")
        print("="*60 + "\n")


if __name__ == '__main__':
    analyzer = RepositoryAnalyzer()
    analyzer.run_all_analyses()
