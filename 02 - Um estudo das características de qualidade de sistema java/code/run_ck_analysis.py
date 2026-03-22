import pandas as pd
import subprocess
from pathlib import Path

CK_JAR = Path("../tools/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar")
repos_csv = "repositorios_java.csv"

repos_dir = Path("repos")
repos_dir.mkdir(exist_ok=True)

ck_output = Path("ck_output")
ck_output.mkdir(exist_ok=True)

df = pd.read_csv(repos_csv)

results = []


def has_java_files(repo_path):
    return any(repo_path.rglob("*.java"))


for repo in df.itertuples():

    repo_url = repo.url
    repo_name = repo.name.replace("/", "_")

    repo_path = repos_dir / repo_name

    try:

        if not repo_path.exists():

            print("Clonando:", repo_name)

            subprocess.run([
                "git",
                "clone",
                "--depth",
                "1",
                repo_url,
                str(repo_path)
            ], check=True)

        if not has_java_files(repo_path):
            print("Sem arquivos Java:", repo_name)
            continue

        repo_output = ck_output / repo_name
        repo_output.mkdir(exist_ok=True)

        print("Rodando CK:", repo_name)

        subprocess.run([
            "java",
            "-jar",
            str(CK_JAR),
            str(repo_path),
            "false",
            "0",
            "false",
            str(repo_output)
        ], check=True)

        class_file = repo_output / "class.csv"

        if not class_file.exists():
            continue

        df_metrics = pd.read_csv(class_file)

        if df_metrics.empty:
            print("Sem classes analisáveis:", repo_name)
            continue

        results.append({
            "name": repo.name,
            "stargazerCount": repo.stargazerCount,
            "createdAt": repo.createdAt,
            "releases": repo.releases,
            "LOC": df_metrics["loc"].sum(),
            "CBO": df_metrics["cbo"].mean(),
            "DIT": df_metrics["dit"].mean(),
            "LCOM": df_metrics["lcom"].mean()
        })

    except Exception as e:
        print("Erro no repositório:", repo_name, e)


final_df = pd.DataFrame(results)

final_df.to_csv("dataset_final.csv", index=False)

print("Dataset final criado!")