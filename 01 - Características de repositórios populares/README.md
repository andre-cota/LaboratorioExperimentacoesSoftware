# Análise de Características de Repositórios Populares

Este projeto realiza análise de repositórios populares do GitHub baseado em diversas métricas de pesquisa.

## 📋 Estrutura do Projeto

```
01 - Características de repositórios populares/
├── code/
│   ├── analyze_repos.py      # Script de análise e geração de gráficos
│   ├── main.py                # Script principal de coleta
│   ├── client/                # Cliente da API do GitHub
│   └── services/              # Serviços de busca e processamento
├── docs/                      # Documentação e resultados
│   ├── RQ01_idade_repositorios.png
│   ├── RQ02_pull_requests.png
│   ├── RQ03_releases.png
│   ├── RQ04_update_frequency.png
│   ├── RQ05_languages.png
│   ├── RQ06_closed_issues_ratio.png
│   ├── RQ07_metrics_by_language.png
│   └── relatorio_analise.txt
└── README.md
```

## 🎯 Questões de Pesquisa (RQs)

O projeto responde às seguintes questões:

### RQ01: Sistemas populares são maduros/antigos?
**Métrica:** Idade do repositório (calculado a partir da data de criação)
- Gráficos: Histograma e Boxplot da distribuição de idade

### RQ02: Sistemas populares recebem muita contribuição externa?
**Métrica:** Total de pull requests aceitas
- Gráficos: Distribuição de PRs e Top 20 repositórios

### RQ03: Sistemas populares lançam releases com frequência?
**Métrica:** Total de releases
- Gráficos: Distribuição de releases e Top 20 repositórios

### RQ04: Sistemas populares são atualizados com frequência?
**Métrica:** Tempo até a última atualização
- Gráficos: Distribuição de tempo desde última atualização e categorias

### RQ05: Sistemas populares são escritos nas linguagens mais populares?
**Métrica:** Linguagem primária de cada repositório
- Gráficos: Top 15 linguagens e distribuição

### RQ06: Sistemas populares possuem um alto percentual de issues fechadas?
**Métrica:** Razão entre número de issues fechadas pelo total de issues
- Gráficos: Distribuição e Boxplot da razão de issues fechadas
- ⚠️ **Nota:** Requer coleta de dados com a coluna `closedIssues`

### RQ07 (BÔNUS): Métricas por linguagem
Analisa como as métricas das RQ02, RQ03 e RQ04 se comportam por linguagem
- Gráficos: PRs, Releases e Frequência de atualização por linguagem (Top 10)

## 🚀 Como Usar

### 1. Coleta de Dados

```bash
# Ativar o ambiente virtual
source .venv/bin/activate

# Navegar até o diretório de código
cd "01 - Características de repositórios populares/code"

# Executar a coleta (certifique-se de ter um token GitHub no arquivo .env)
python main.py
```

O script `main.py` irá:
- Buscar repositórios populares do GitHub
- Salvar os dados em `repositorios.csv` na raiz do projeto
- Coletar métricas como: stars, PRs, releases, issues, linguagem, etc.

### 2. Análise e Geração de Gráficos

```bash
# No mesmo diretório (code/)
python analyze_repos.py
```

O script `analyze_repos.py` irá:
1. Ler o arquivo `repositorios.csv`
2. Calcular todas as métricas necessárias
3. Gerar gráficos para cada RQ em `docs/`
4. Criar um relatório resumido em `docs/relatorio_analise.txt`

## 📦 Dependências

```bash
pip install pandas matplotlib seaborn python-dotenv requests
```

Ou use o ambiente virtual já configurado:
```bash
source .venv/bin/activate  # já possui todas as dependências
```

## 📊 Resultados

Os resultados da análise incluem:

- **7 arquivos PNG** com gráficos de alta qualidade (300 DPI)
- **1 relatório em texto** com estatísticas resumidas
- Análise de **2000+ repositórios** populares do GitHub

### Exemplo de Descobertas

- **RQ01:** Repositórios têm em média ~10 anos de idade
- **RQ02:** Mediana de ~1000 PRs aceitas por repositório
- **RQ03:** Mediana de ~69 releases por repositório
- **RQ04:** 100% dos repositórios atualizados recentemente
- **RQ05:** TypeScript, JavaScript e Python são as linguagens mais populares
- **RQ07:** TypeScript tem maior média de releases, C++ maior média de PRs

## ⚠️ Observações Importantes

### RQ06 - Issues Fechadas

Para calcular corretamente a RQ06, é necessário:

1. **Reexecutar a coleta de dados** com o código atualizado que inclui `closedIssues`
2. O código de coleta (`repo_search.py`) já foi atualizado para coletar essa métrica
3. Os dados atuais em `repositorios.csv` não possuem essa coluna

Para obter dados completos da RQ06:
```bash
# 1. Deletar ou renomear o CSV antigo
mv ../../repositorios.csv ../../repositorios_old.csv

# 2. Executar nova coleta
python main.py

# 3. Executar análise novamente
python analyze_repos.py
```

## 🔧 Personalização

Você pode personalizar a análise editando `analyze_repos.py`:

- Alterar número de repositórios no Top (padrão: 10-20)
- Modificar cores e estilos dos gráficos
- Adicionar novas métricas ou visualizações
- Ajustar bins dos histogramas
- Modificar filtros de linguagens

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos no contexto da disciplina de Laboratório de Experimentações em Software.

## 👥 Autores

Desenvolvido para análise de características de repositórios populares do GitHub.
