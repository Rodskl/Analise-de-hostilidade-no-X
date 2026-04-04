import os
import pandas as pd
from learning import Analisar
from classifier import Julgar
import matplotlib.pyplot as plt

def main():
    caminho_base = os.path.dirname(__file__)
    caminho_parquet = os.path.join(caminho_base, '..', 'dados', 'dataset_eleicoes', '2022-08-01-BOLSONARO NAO TRABALHA.parquet')
    caminho_owl = os.path.join(caminho_base, '..', 'dados', 'ontologia', 'Ofensas.owl')

    mentor = Analisar(caminho_parquet)
    juiz = Julgar(caminho_owl)

    print("\n--- Sistema de Monitoramento de Ofensas Políticas ---")
    
    escolha = input("Deseja treinar a IA com os novos dados do modelo? (s/n): ").lower()
    
    if escolha == 's':
        mentor.treinar()
        palavras_semente = ["ladrao", "fascista", "burro", "canalha"]
        novas_descobertas = mentor.descobrir_sinonimos(palavras_semente)
        
        if novas_descobertas:
            print(f"\nIA sugere novos termos: {novas_descobertas}")
            confirmar = input("Deseja atualizar a ontologia com estes termos? (s/n): ").lower()
            if confirmar == 's':
                for termo in novas_descobertas:
                    print(f"\nEm qual classe inserir '{termo}'?")
                    print("1. Criminalizante | 2. Intelectual | 3. Moral | 4. Ignorar")
                    op = input("Opção: ")
                    
                    classe_alvo = None
                    if op == '1': classe_alvo = "Criminalizante"
                    elif op == '2': classe_alvo = "Intelectual"
                    elif op == '3': classe_alvo = "Moral"
                    
                    if classe_alvo:
                        juiz.atualizar_ontologia([termo], classe_alvo)
                juiz.mapear_da_ontologia()

    while True:
        print("\n--- Menu Principal ---")
        print("1. Analisar uma frase manualmente")
        print("2. Analisar base de dados")
        print("3. Coletar novos tweets via API do X (DESATIVADO)")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '4':
            break
            
        elif opcao == '1':
            frase = input("\nDigite a frase: ")
            res = juiz.analisar(frase)
            print(f"Status: {res['status']} | Score: {res['score']} | Termos: {', '.join(res['termos_detectados'])}")
            
        elif opcao == '2':
            print("\nCarregando dataset...")
            df = pd.read_parquet(caminho_parquet)
            
            coluna_texto = 'tweet_content'
            
            if coluna_texto not in df.columns:
                print(f"❌ Coluna '{coluna_texto}' não encontrada. Colunas disponíveis: {list(df.columns)}")
                continue
                
            print(f"Analisando {len(df)} tweets... Aguarde.")
            
            resultados = df[coluna_texto].apply(lambda x: juiz.analisar(str(x)))
            
            df['Score_Ofensa'] = resultados.apply(lambda x: x['score'])
            df['Status'] = resultados.apply(lambda x: x['status'])
            df['Termos_Detectados'] = resultados.apply(lambda x: ", ".join(x['termos_detectados']))
            
            contagem = df['Status'].value_counts()
            
            ordem_severidade = ['Neutro', 'Ofensivo', 'Altamente Hostil']
            contagem = contagem.reindex(ordem_severidade).dropna()
            
            mapeamento_cores = {'Neutro': 'skyblue', 'Ofensivo': 'orange', 'Altamente Hostil': 'red'}
            cores_barras = [mapeamento_cores.get(status) for status in contagem.index]

            print("\nGerando gráficos...")
            
            plt.figure(figsize=(10, 6))
            contagem.plot(kind='bar', color=cores_barras)
            plt.title('Distribuição da Toxicidade nos Tweets (TCC_IA)')
            plt.ylabel('Quantidade de Tweets')
            plt.xlabel('Status de Toxicidade')
            plt.xticks(rotation=45, ha='right')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.tight_layout()
            caminho_grafico_barras = os.path.join(caminho_base, '..', 'dados', 'distribuicao_toxicidade.png')
            plt.savefig(caminho_grafico_barras)
            
            plt.figure(figsize=(8, 8))
            plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores_barras, startangle=140, explode=[0.05]*len(contagem))
            plt.title('Porcentagem de Toxicidade nos Tweets')
            plt.tight_layout()
            caminho_grafico_pizza = os.path.join(caminho_base, '..', 'dados', 'percentual_toxicidade.png')
            plt.savefig(caminho_grafico_pizza)

            print(f"Gráfico de barras salvo em: {caminho_grafico_barras}")
            print(f"Gráfico de pizza salvo em: {caminho_grafico_pizza}")
            
            print("\n✅ Resumo da Classificação:")
            print(df['Status'].value_counts())
            
            print("\n--- Sorteando 2 Exemplos Anonimizados (Com Ofensas) ---")
            df_ofensivos = df[df['Termos_Detectados'] != ""]
            
            if not df_ofensivos.empty:
                amostras = df_ofensivos.dropna(subset=[coluna_texto]).sample(n=min(2, len(df_ofensivos)))
                campos_ocultos = ['user', 'user_info', 'mentions', 'reply_to', 'quoted_from', 'retweeted_from']
                
                for index, row in amostras.iterrows():
                    print(f"\nTweet ID: {row.get('tweet_id', 'Desconhecido')}")
                    print(f"Texto: {row[coluna_texto]}")
                    print(f"Status IA: {row.get('Status')} (Score: {row.get('Score_Ofensa')})")
                    print(f"Ofensas Detectadas: {row.get('Termos_Detectados')}")
                    
                    for campo in campos_ocultos:
                        if campo in df.columns:
                            valor = row[campo]
                            if pd.notna(valor) and str(valor).strip() != "" and str(valor).strip() != "None":
                                print(f"{campo}: [BORRADO]")
                            else:
                                print(f"{campo}: [VAZIO]")
                    print("-" * 50)
            else:
                print("\nNenhum tweet contendo termos da ontologia foi encontrado nesta execução.")
            
            caminho_saida = os.path.join(caminho_base, '..', 'dados', 'dataset_classificado.parquet')
            df.to_parquet(caminho_saida)
            print(f"\nDataset salvo com os resultados em:\n{caminho_saida}")
            
        elif opcao == '3':
            print("\n Desativado Temporariamente")
    
            # from scraping import Scraping
            # token_x = ""
            # termo = input("Digite o termo ou hashtag para buscar no X: ")
            # print(f"Buscando até 500 tweets recentes contendo '{termo}'...")
            # 
            # coletor = Scraping(token_x)
            # df_novos = coletor.buscar_tweets(termo, limite=500)
            # 
            # if df_novos is not None:
            #     caminho_novo_parquet = coletor.salvar_dataset(df_novos, termo, caminho_base)
            #     print(f"✅ Coleta finalizada! {len(df_novos)} tweets salvos em: {caminho_novo_parquet}")
            # else:
            #     print("❌ Nenhum tweet encontrado ou erro na comunicação com a API.")

if __name__ == "__main__":
    main()