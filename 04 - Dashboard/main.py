import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# 1. RESOLUÇÃO AUTOMÁTICA DE CAMINHOS (Evita FileNotFoundError e salva no local correto)
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

def obter_caminho(nome_arquivo):
    return os.path.join(diretorio_atual, nome_arquivo)

# Carga das bases de dados usando caminhos absolutos
df_adoption = pd.read_csv(obter_caminho('rq1_adoption_summary.csv'))
df_cluster_sum = pd.read_csv(obter_caminho('rq1_cluster_summary.csv'))
df_file_dist = pd.read_csv(obter_caminho('rq1_policy_file_distribution.csv'))
df_repo_summary = pd.read_csv(obter_caminho('rq1_repository_policy_summary.csv'))
df_eng_policy = pd.read_csv(obter_caminho('rq2_engagement_by_policy_presence.csv'))
df_eng_cluster = pd.read_csv(obter_caminho('rq2_engagement_by_cluster.csv'))
df_collab_policy = pd.read_csv(obter_caminho('rq3_collaboration_by_policy_presence.csv'))

# --- CONFIGURAÇÃO DE DESIGN DA PALETA EXECUTIVE PREMIUM ---
MAIN_BLUE = '#0F4C81'      # Classic Navy Executivo
LIGHT_BLUE = '#2A9D8F'     # Teal Moderno para Indicadores de Sucesso
GREY_BLUE = '#E5E9F0'      # Fundo neutro
ORANGE_METRIC = '#E76F51'  # Coral para Atividade/Issues
CLUSTER_COLORS = ['#3A86FF', '#8338EC', '#FF006E'] # Paleta Fina de Cores para os Clusters

# Configuração de layout limpo e transparente para os gráficos
layout_clean = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Segoe UI, Inter, sans-serif", size=12, color="#2D3748"),
    margin=dict(t=50, b=30, l=20, r=20),
    hovermode="closest"
)

# 2. CONSTRUÇÃO DAS FIGURAS INTERATIVAS VIA PLOTLY
# A. Gauge de Meta de Adoção (Estilo KPIs de Diretoria)
fig_adoption = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = 19.0,
    domain = {'x': [0, 1], 'y': [0, 1]},
    number = {'suffix': "%", 'font': {'size': 36, 'color': MAIN_BLUE, 'weight': 'bold'}},
    gauge = {
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
        'bar': {'color': MAIN_BLUE},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "#e2e8f0",
        'steps': [
            {'range': [0, 19], 'color': '#f1f5f9'},
            {'range': [19, 100], 'color': '#fafafa'}
        ],
    }
))
fig_adoption.update_layout(layout_clean, title_text="<b>Taxa de Incorporação de Governança</b>", height=240)

# B. Atividade Macro (update_yaxes corrigido)
fig_eng_policy = go.Figure([
    go.Bar(
        x=['Sem Política', 'Com Política'], y=[4027, 15942], name='Mediana de PRs', 
        marker=dict(color=MAIN_BLUE, line=dict(width=0), cornerradius=4)
    ),
    go.Bar(
        x=['Sem Política', 'Com Política'], y=[4094, 14316], name='Mediana de Issues', 
        marker=dict(color=ORANGE_METRIC, line=dict(width=0), cornerradius=4)
    )
])
fig_eng_policy.update_layout(layout_clean, barmode='group', title_text="<b>Intensidade Operacional por Grupo</b>", height=240, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
fig_eng_policy.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False)

# C. Eficiência de Colaboração (update_yaxes corrigido)
fig_collab_policy = go.Figure([
    go.Bar(
        x=['Sem Política', 'Com Política'], y=[53.76, 64.41], name='Taxa de Merge (%)', 
        marker=dict(color=LIGHT_BLUE, cornerradius=4)
    ),
    go.Bar(
        x=['Sem Política', 'Com Política'], y=[37.75, 31.10], name='Rejeições s/ Merge (%)', 
        marker=dict(color='#E63946', cornerradius=4)
    )
])
fig_collab_policy.update_layout(layout_clean, barmode='group', title_text="<b>Eficiência Logística de Fluxo (%)</b>", height=240, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
fig_collab_policy.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False)

# D. Projetos por Cluster (update_xaxes corrigido)
df_cluster_sum_sorted = df_cluster_sum.sort_values(by='unique_repositories', ascending=True)
fig_cluster_dist = go.Figure(go.Bar(
    x=df_cluster_sum_sorted['unique_repositories'], y=['C0', 'C2', 'C1'], 
    orientation='h', width=0.4, text=df_cluster_sum_sorted['unique_repositories'], textposition='outside',
    marker=dict(color=MAIN_BLUE, cornerradius=4)
))
fig_cluster_dist.update_layout(layout_clean, title_text="<b>Concentração de Amostra por Cluster</b>", height=240)
fig_cluster_dist.update_xaxes(showgrid=False, showticklabels=False)

# E. Extensão Média de Texto (update_yaxes corrigido)
fig_cluster_words = go.Figure(go.Bar(
    x=['Cluster 0', 'Cluster 1', 'Cluster 2'], y=df_cluster_sum['mean_policy_words'], 
    width=0.4, text=df_cluster_sum['mean_policy_words'].round(0), textposition='outside',
    marker=dict(color=CLUSTER_COLORS, cornerradius=4)
))
fig_cluster_words.update_layout(layout_clean, title_text="<b>Densidade Regulatória (Média de Palavras)</b>", height=240)
fig_cluster_words.update_yaxes(showgrid=True, gridcolor="#f1f5f9")

# F. Atividade por Cluster (update_yaxes corrigido)
fig_eng_cluster = go.Figure([
    go.Bar(
        x=['C0', 'C1', 'C2'], y=df_eng_cluster['prs_total_median'], name='Mediana de PRs', 
        marker=dict(color=MAIN_BLUE, cornerradius=4)
    ),
    go.Bar(
        x=['C0', 'C1', 'C2'], y=df_eng_cluster['issues_total_median'], name='Mediana de Issues', 
        marker=dict(color=ORANGE_METRIC, cornerradius=4)
    )
])
fig_eng_cluster.update_layout(layout_clean, barmode='group', title_text="<b>Volume de Operação por Cluster</b>", height=240, legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"))
fig_eng_cluster.update_yaxes(showgrid=True, gridcolor="#f1f5f9")

# G. Arquivos Usados (update_yaxes corrigido)
fig_file_dist = go.Figure(go.Bar(
    x=df_file_dist['file_category'], y=df_file_dist['unique_repositories'], 
    width=0.3, text=df_file_dist['unique_repositories'], textposition='outside',
    marker=dict(color=[MAIN_BLUE, LIGHT_BLUE], cornerradius=4)
))
fig_file_dist.update_layout(layout_clean, title_text="<b>Documento Sede da Diretriz</b>", height=240)
fig_file_dist.update_yaxes(showgrid=False, showticklabels=False)

# 3. CONVERSÃO DOS GRÁFICOS EM FRAGMENTOS HTML INTERNOS
html_adoption = pio.to_html(fig_adoption, full_html=False, include_plotlyjs=False)
html_eng_policy = pio.to_html(fig_eng_policy, full_html=False, include_plotlyjs=False)
html_collab_policy = pio.to_html(fig_collab_policy, full_html=False, include_plotlyjs=False)
html_cluster_dist = pio.to_html(fig_cluster_dist, full_html=False, include_plotlyjs=False)
html_cluster_words = pio.to_html(fig_cluster_words, full_html=False, include_plotlyjs=False)
html_eng_cluster = pio.to_html(fig_eng_cluster, full_html=False, include_plotlyjs=False)
html_file_dist = pio.to_html(fig_file_dist, full_html=False, include_plotlyjs=False)

# Construção dinâmica da tabela executiva de repositórios
table_rows = ""
for _, r in df_repo_summary.iterrows():
    table_rows += f"""
    <tr data-cluster="{r['clusters']}">
        <td class="fw-semibold text-dark"><a href="{r['url']}" target="_blank" class="text-decoration-none text-dark hover-link">🔗 {r['repo']}</a></td>
        <td><span class="badge badge-c{r['clusters']}">Cluster {r['clusters']}</span> <span class="text-muted small">{r['cluster_labels']}</span></td>
        <td><span class="badge-file">{r['policy_files']}</span></td>
        <td class="text-end font-monospace fw-bold">{r['total_policy_words']}</td>
    </tr>
    """

# 4. TEMPLATE HTML DO DASHBOARD MASTER PREMIUM
dashboard_html_content = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Briefing: Governança de IA</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plotly.com/plotly-latest.min.js"></script>
    <style>
        body {{ background-color: #f8fafc; font-family: 'Inter', -apple-system, sans-serif; color: #1e293b; }}
        .header-panel {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white; padding: 25px 40px; margin-bottom: 0px; border-bottom: 4px solid #3b82f6; }}
        .slicer-panel {{ background-color: #ffffff; border-bottom: 1px solid #e2e8f0; padding: 15px 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); }}
        .kpi-card {{ background: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03); border: 1px solid #e2e8f0; position: relative; overflow: hidden; }}
        .kpi-card:hover {{ transform: translateY(-2px); transition: transform 0.2s; }}
        .kpi-title {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; font-weight: 700; margin-bottom: 5px; }}
        .kpi-value {{ font-size: 2rem; font-weight: 800; color: #0f172a; tracking: -0.02em; }}
        .chart-card {{ background: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; height: 100%; transition: box-shadow 0.2s; }}
        .chart-card:hover {{ box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }}
        .section-header {{ font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #475569; margin: 25px 0 15px 0; border-left: 4px solid #0f4c81; padding-left: 10px; }}
        .table-card {{ background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .badge-c0 {{ background-color: #e0f2fe; color: #0369a1; font-weight: 600; padding: 4px 8px; border-radius: 4px; }}
        .badge-c1 {{ background-color: #f3e8ff; color: #6b21a8; font-weight: 600; padding: 4px 8px; border-radius: 4px; }}
        .badge-c2 {{ background-color: #fce7f3; color: #9d174d; font-weight: 600; padding: 4px 8px; border-radius: 4px; }}
        .badge-file {{ background-color: #f1f5f9; color: #334155; padding: 4px 8px; border-radius: 6px; font-family: monospace; font-size: 0.8rem; }}
        .hover-link:hover {{ color: #3b82f6 !important; text-decoration: underline !important; }}
        .form-select-premium {{ border-radius: 8px; border: 1px solid #cbd5e1; padding: 0.45rem 2rem 0.45rem 1rem; font-size: 0.875rem; color: #334155; }}
        .form-select-premium:focus {{ border-color: #0f4c81; box-shadow: 0 0 0 2px rgba(15,76,129,0.1); }}
    </style>
</head>
<body>

    <header class="header-panel d-flex justify-content-between align-items-center">
        <div>
            <h1 class="h3 mb-1 fw-bold tracking-tight">AI Governance & Policy Intelligence</h1>
            <p class="text-slate-400 mb-0 small opacity-75">Análise estratégica de regulação artificial em ecossistemas Open Source</p>
        </div>
        <div class="text-end">
            <span class="badge bg-primary px-3 py-2 rounded-pill fw-semibold" style="background-color: #3b82f6 !important;">EXECUTIVE BRIEFING VIEWER</span>
        </div>
    </header>

    <section class="slicer-panel">
        <div class="row align-items-center g-3">
            <div class="col-md-auto">
                <span class="text-muted small fw-bold text-uppercase tracking-wider">Slicers de Controle:</span>
            </div>
            <div class="col-md-3">
                <select id="viewSlicer" class="form-select form-select-premium" onchange="applyFilters()">
                    <option value="all">Visão Consolidada (Geral)</option>
                    <option value="policy">Módulo A: Presença de Política</option>
                    <option value="cluster">Módulo B: Segmentação por Clusters</option>
                </select>
            </div>
            <div class="col-md-4">
                <select id="clusterSlicer" class="form-select form-select-premium" onchange="applyFilters()">
                    <option value="all">Filtro de Registro: Todos os Clusters</option>
                    <option value="0">Cluster 0 - Uso Permitido com Divulgação Obrigatória</option>
                    <option value="1">Cluster 1 - Uso Condicionado por Custo de Revisão</option>
                    <option value="2">Cluster 2 - IA Assistiva com Revisão Humana Direta</option>
                </select>
            </div>
            <div class="col-md text-end">
                <button class="btn btn-sm btn-link text-decoration-none text-secondary fw-semibold small" onclick="resetAllFilters()">Resetar Visão</button>
            </div>
        </div>
    </section>

    <main class="container-fluid px-5 py-4">
        
        <div class="row g-3 mb-4">
            <div class="col-md-3">
                <div class="kpi-card">
                    <div class="kpi-title">Amostra Global</div>
                    <div class="kpi-value">100 <span class="fs-6 text-muted fw-normal">Projetos</span></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card" style="border-left: 4px solid #0f4c81;">
                    <div class="kpi-title">Projetos Regulados</div>
                    <div class="kpi-value">19 <span class="fs-6 text-success fw-semibold">▲ 19.0%</span></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card" style="border-left: 4px solid #a6b8c7;">
                    <div class="kpi-title">Projetos Sem Restrição</div>
                    <div class="kpi-value">81 <span class="fs-6 text-muted fw-normal">81.0%</span></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="kpi-card" style="border-left: 4px solid #2a9d8f;">
                    <div class="kpi-title" id="kpi-focused-cluster">Foco Ativo</div>
                    <div class="kpi-value text-truncate fs-5 fw-bold mt-2 text-primary" id="kpi-focused-count">Todos os Clusters Ativos</div>
                </div>
            </div>
        </div>

        <div id="section-policy">
            <h2 class="section-header">Módulo A: Macro-Análise de Impacto (Adoção de Políticas vs. Métricas Operacionais)</h2>
            <div class="row g-3">
                <div class="col-md-4"><div class="chart-card">{html_adoption}</div></div>
                <div class="col-md-4"><div class="chart-card">{html_eng_policy}</div></div>
                <div class="col-md-4"><div class="chart-card">{html_collab_policy}</div></div>
            </div>
        </div>

        <div id="section-cluster" class="mt-2">
            <h2 class="section-header">Módulo B: Segmentação Estratégica (Análise por Filosofia de Clusters)</h2>
            <div class="row g-3">
                <div class="col-md-4"><div class="chart-card">{html_cluster_dist}</div></div>
                <div class="col-md-4"><div class="chart-card">{html_eng_cluster}</div></div>
                <div class="col-md-4"><div class="chart-card">{html_cluster_words}</div></div>
            </div>
        </div>

        <div class="row g-3 mt-2 mb-5">
            <div class="col-md-3">
                <h2 class="section-header">Canais de Entrada</h2>
                <div class="chart-card">{html_file_dist}</div>
            </div>
            <div class="col-md-9">
                <h2 class="section-header">Rastreabilidade Analítica de Repositórios Modulados (N=19)</h2>
                <div class="table-card table-responsive">
                    <table class="table table-hover align-middle mb-0 table-borderless table-sm">
                        <thead style="border-bottom: 2px solid #f1f5f9;">
                            <tr class="text-muted small text-uppercase tracking-wider fw-bold">
                                <th class="pb-3">Repositório</th>
                                <th class="pb-3">Agrupamento Crítico (Cluster)</th>
                                <th class="pb-3">Canal Adotado</th>
                                <th class="pb-3 text-end">Extensão (Palavras)</th>
                            </tr>
                        </thead>
                        <tbody id="repoTableBody">
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        function applyFilters() {{
            var view = document.getElementById("viewSlicer").value;
            var cluster = document.getElementById("clusterSlicer").value;
            
            // Controle de Exibição das Seções (Filtro de Visão)
            if (view === "all") {{
                document.getElementById("section-policy").style.display = "block";
                document.getElementById("section-cluster").style.display = "block";
            }} else if (view === "policy") {{
                document.getElementById("section-policy").style.display = "block";
                document.getElementById("section-cluster").style.display = "none";
            }} else if (view === "cluster") {{
                document.getElementById("section-policy").style.display = "none";
                document.getElementById("section-cluster").style.display = "block";
            }}
            
            // Controle de Linhas da Tabela por Cluster
            var rows = document.querySelectorAll("#repoTableBody tr");
            rows.forEach(function(row) {{
                var rowCluster = row.getAttribute("data-cluster");
                if (cluster === "all" || rowCluster === cluster) {{
                    row.style.display = "";
                }} else {{
                    row.style.display = "none";
                }}
            }});
            
            // Atualização Dinâmica dos KPI Cards com base nos Clusters
            var kpiLabel = document.getElementById("kpi-focused-cluster");
            var kpiCount = document.getElementById("kpi-focused-count");
            
            if (cluster === "all") {{
                kpiLabel.innerText = "Foco Ativo";
                kpiCount.innerText = "19 Repositórios Regulados";
                kpiCount.style.color = "#0f4c81";
            }} else if (cluster === "0") {{
                kpiLabel.innerText = "Foco: Cluster 0";
                kpiCount.innerText = "4 Repos (109.8 palavras)";
                kpiCount.style.color = "#0369a1";
            }} else if (cluster === "1") {{
                kpiLabel.innerText = "Foco: Cluster 1";
                kpiCount.innerText = "9 Repos (201.8 palavras)";
                kpiCount.style.color = "#6b21a8";
            }} else if (cluster === "2") {{
                kpiLabel.innerText = "Foco: Cluster 2";
                kpiCount.innerText = "6 Repos (190.7 palavras)";
                kpiCount.style.color = "#9d174d";
            }}
            
            // Força o redimensionamento reativo dos blocos Plotly para não quebrarem o layout
            var graphDivs = document.querySelectorAll('.plotly-graph-div');
            graphDivs.forEach(function(div) {{
                if(div.id) Plotly.Plots.resize(div);
            }});
        }}

        function resetAllFilters() {{
            document.getElementById("viewSlicer").value = "all";
            document.getElementById("clusterSlicer").value = "all";
            applyFilters();
        }}
    </script>
</body>
</html>
"""

# 5. SALVAMENTO DO ARQUIVO FINAL NO DIRETÓRIO ABSOLUTO
caminho_final = obter_caminho('dashboard.html')
with open(caminho_final, 'w', encoding='utf-8') as f:
    f.write(dashboard_html_content)

print(f"\n=======================================================")
print(f"🎉 SUCESSO! Dashboard de Alto Nível gerado com sucesso.")
print(f"📍 Arquivo salvo em: {caminho_final}")
print(f"=======================================================")