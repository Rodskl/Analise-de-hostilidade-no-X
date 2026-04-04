import tweepy
import pandas as pd
import os
from datetime import datetime

class Scraping:
    def __init__(self, bearer_token):
        self.client = tweepy.Client(bearer_token=bearer_token)

    def buscar_tweets(self, termo_busca, limite=500):
        try:
            tweets_coletados = []
            query_formatada = f"{termo_busca} -is:retweet lang:pt"
            
            paginator = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query_formatada,
                tweet_fields=['created_at', 'author_id'],
                max_results=100
            )
            
            for tweet in paginator.flatten(limit=limite):
                tweets_coletados.append({
                    'tweet_id': str(tweet.id),
                    'tweet_content': tweet.text,
                    'created_at': tweet.created_at,
                    'user': str(tweet.author_id),
                    'user_info': None,
                    'mentions': None,
                    'reply_to': None,
                    'quoted_from': None,
                    'retweeted_from': None
                })
            
            if not tweets_coletados:
                return None
                
            df = pd.DataFrame(tweets_coletados)
            return df
            
        except Exception as e:
            print(f"Erro na coleta da API do X: {e}")
            return None

    def salvar_dataset(self, df, termo_busca, caminho_base):
        data_atual = datetime.now().strftime("%Y-%m-%d")
        nome_arquivo = f"{data_atual}-{termo_busca.upper().replace(' ', '_')}.parquet"
        caminho_completo = os.path.join(caminho_base, '..', 'dados', 'dataset_eleicoes', nome_arquivo)
        
        df.to_parquet(caminho_completo)
        return caminho_completo