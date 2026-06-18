import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, wilcoxon

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 11})

def analisar_experimento():
    csv_path = "experimento_raw.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Arquivo '{csv_path}' não encontrado. Execute o script de coleta primeiro.")
        return

    df_raw = pd.read_csv(csv_path)
    
    df = df_raw[df_raw["Tecnologia"].isin(["REST", "GraphQL"])].copy()
    
    df["Tempo_ms"] = pd.to_numeric(df["Tempo_ms"], errors="coerce")
    df["Tamanho_Bytes"] = pd.to_numeric(df["Tamanho_Bytes"], errors="coerce")
    df = df.dropna()

    rest_data = df[df["Tecnologia"] == "REST"].sort_values(by="Iteracao")
    gql_data = df[df["Tecnologia"] == "GraphQL"].sort_values(by="Iteracao")
    
    iteracoes_comuns = np.intersect1d(rest_data["Iteracao"], gql_data["Iteracao"])
    
    rest_data = rest_data[rest_data["Iteracao"].isin(iteracoes_comuns)]
    gql_data = gql_data[gql_data["Iteracao"].isin(iteracoes_comuns)]
    
    df = pd.concat([rest_data, gql_data])

    print("\n" + "="*50)
    print("📊 ANÁLISE DESCRITIVA DOS DADOS COLETADOS (TRATADOS)")
    print("="*50)
    print(df.groupby("Tecnologia")[["Tempo_ms", "Tamanho_Bytes"]].agg(["mean", "median", "std"]))
    print(f"\nTotal de amostras pareadas válidas: {len(iteracoes_comuns)} para cada tecnologia.")
    
    print("\n" + "="*50)
    print("🧪 PASSO 4: VALIDAÇÃO E TESTES ESTATÍSTICOS")
    print("="*50)
    
    _, p_shapiro_r = shapiro(rest_data["Tempo_ms"])
    _, p_shapiro_g = shapiro(gql_data["Tempo_ms"])
    
    print(f"• Shapiro-Wilk (REST Tempo): p-valor = {p_shapiro_r:.5f}")
    print(f"• Shapiro-Wilk (GraphQL Tempo): p-valor = {p_shapiro_g:.5f}")
    
    print("\n--- Resultado do Teste de Hipótese para RQ1 ---")
    
    _, p_wilcoxon = wilcoxon(rest_data["Tempo_ms"], gql_data["Tempo_ms"])
    print(f"• Teste Pareado de Wilcoxon (Tempo): p-valor = {p_wilcoxon:.5f}")
    
    if p_wilcoxon < 0.05:
        print("👉 Conclusão Estatística: Rejeitamos a Hipótese Nula (H01)!")
        print("   Há diferença estatisticamente significativa entre os tempos de resposta.")
    else:
        print("👉 Conclusão Estatística: Falha em rejeitar a Hipótese Nula (H01).")
        print("   Não há diferença significativa nos tempos de resposta.")

    os.makedirs("IMG", exist_ok=True)
    
    plt.figure(figsize=(10, 5.5))
    
    sns.lineplot(data=rest_data, x="Iteracao", y="Tempo_ms", 
                 label="REST", color="#66c2a5", linewidth=2, marker="o", markersize=4)
    sns.lineplot(data=gql_data, x="Iteracao", y="Tempo_ms", 
                 label="GraphQL", color="#fc8d62", linewidth=2, marker="s", markersize=4)
    
    mediana_rest = rest_data["Tempo_ms"].median()
    mediana_gql = gql_data["Tempo_ms"].median()
    plt.axhline(y=mediana_rest, color="#1b9e77", linestyle="--", alpha=0.7, linewidth=1.5)
    plt.axhline(y=mediana_gql, color="#d95f02", linestyle="--", alpha=0.7, linewidth=1.5)
    
    plt.text(1, mediana_rest + (mediana_gql * 0.03), f"Mediana REST: {mediana_rest:.2f} ms", color="#1b9e77", fontweight="bold")
    plt.text(1, mediana_gql + (mediana_gql * 0.03), f"Mediana GraphQL: {mediana_gql:.2f} ms", color="#d95f02", fontweight="bold")

    plt.title("RQ1: Evolução do Tempo de Resposta por Iteração\n[Menor é melhor]", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Número da Iteração (Ordem dos Disparos)", fontsize=11, labelpad=10)
    plt.ylabel("Tempo de Resposta (ms)", fontsize=11, labelpad=10)
    plt.xlim(1, len(iteracoes_comuns))
    plt.legend(loc="center right", frameon=True)
    plt.tight_layout()
    plt.savefig("IMG/rq01_time_comparison.png", dpi=300)
    plt.close()
    print("\n📈 Gráfico de evolução temporal para RQ1 gerado com sucesso!")

    plt.figure(figsize=(8, 6))
    cores_rq2 = {"REST": "#fbb4ae", "GraphQL": "#b3cde3"}
    
    ax2 = sns.barplot(data=df, x="Tecnologia", y="Tamanho_Bytes", palette=cores_rq2, errorbar=None, width=0.35)
    
    valores = []
    for p in ax2.patches:
        height = p.get_height()
        valores.append(height)
        ax2.annotate(f"{int(height)} Bytes",
                     (p.get_x() + p.get_width() / 2., height),
                     ha='center', va='bottom', fontsize=11, fontweight='bold', color='#2c3e50',
                     xytext=(0, 5), textcoords='offset points')
    
    if len(valores) == 2:
        economia = ((valores[0] - valores[1]) / valores[0]) * 100
        plt.text(0.5, max(valores) * 0.5, f"⬇ Economia de\nBanda: {economia:.1f}%", 
                 ha='center', va='center', color='#c0392b', fontsize=12, fontweight='bold',
                 bbox=dict(facecolor='#f9ebea', edgecolor='#e6b0aa', boxstyle='round,pad=0.5'))

    plt.title("RQ2: Tamanho do Payload Transmitido (Bytes)\n[Menor é melhor]", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Estilo Arquitetural", fontsize=11, labelpad=10)
    plt.ylabel("Tamanho da Resposta (Bytes)", fontsize=11, labelpad=10)
    plt.ylim(0, max(valores) * 1.15)  # Espaço dinâmico extra no topo
    plt.tight_layout()
    plt.savefig("IMG/rq02_payload_comparison.png", dpi=300)
    plt.close()
    print("📈 Gráfico autoexplicativo 'IMG/rq02_payload_comparison.png' gerado com sucesso!")
    print("="*50)

if __name__ == "__main__":
    analisar_experimento()