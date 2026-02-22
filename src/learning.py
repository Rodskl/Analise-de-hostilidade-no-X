import pandas as pd
import re
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import nltk
import os

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

class Analisar:
    def __init__(self, caminho_dados):
        self.caminho_dados = caminho_dados
        self.modelo = None
        self.caminho_modelo = os.path.join(os.path.dirname(__file__), '..', 'modelos', 'cerebro_politico.model')

    def limpar_texto(self, texto):
        if not isinstance(texto, str): return ""
        texto = texto.lower()
        texto = re.sub(r'http\S+', '', texto)
        texto = re.sub(r'[^a-záéíóúãõçñ ]', '', texto)
        return texto

    def treinar(self):
        print("--- Fase 1: Treinamento da IA ---")
        print(f"Lendo dados de {self.caminho_dados}...")
        try:
            df = pd.read_parquet(self.caminho_dados)
            coluna_texto = 'tweet_content' 
            frases_brutas = df[coluna_texto].dropna().tolist()
            frases_tokenizadas = [word_tokenize(self.limpar_texto(txt)) for txt in frases_brutas]  
            print(f"Analisando {len(frases_tokenizadas)} tweets.")
            self.modelo = Word2Vec(sentences=frases_tokenizadas, vector_size=200, window=10, min_count=3, workers=4)
            pasta_modelos = os.path.dirname(self.caminho_modelo)
            if not os.path.exists(pasta_modelos): 
                os.makedirs(pasta_modelos)
            
            self.modelo.save(self.caminho_modelo)
            print("Processo concluido")
            
        except Exception as e:
            print(f"Erro ao analisar: {e}")

    def descobrir_sinonimos(self, palavras_semente):
        if not self.modelo:
            try:
                self.modelo = Word2Vec.load(self.caminho_modelo)
            except:
                print("Modelo não reconhecido.")
                return []

        print("\n--- Fase 2: Expansão de Vocabulário ---")
        novas_palavras = []
        
        for palavra in palavras_semente:
            if palavra in self.modelo.wv:
                similares = self.modelo.wv.most_similar(palavra, topn=3)
                print(f"Palavra '{palavra}' é usada como: {[s[0] for s in similares]}")
                
                for termo, score in similares:
                    if score > 0.6:
                        novas_palavras.append(termo)
            else:
                print(f"A palavra '{palavra}' não foi reconhecida.")
                
        return list(set(novas_palavras))