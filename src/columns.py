import pandas as pd


arquivo_teste = r"C:\Users\rodri\Downloads\TCC_IA\dados\dataset_eleicoes/2022-08-01-BOLSONARO NAO TRABALHA.parquet"
try:
    df = pd.read_parquet(arquivo_teste)
    print("COLUNAS ENCONTRADAS")
    print(df.columns.tolist())
    print("\n====================================\n")
    print("3 PRIMEIRAS LINHAS")
    print(df.head(3))
    
except Exception as e:
    print(f"Erro ao tentar ler: {e}")