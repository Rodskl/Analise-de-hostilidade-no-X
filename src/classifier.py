from owlready2 import *
from unidecode import unidecode
import re
import os

class Julgar:
    def __init__(self, caminho_owl):
        self.caminho_owl = os.path.abspath(caminho_owl)
        self.dicionario_termos = {}
        self.onto = None
        
        if not os.path.exists(self.caminho_owl):
            print(f"\n  O arquivo não foi encontrado:\n{self.caminho_owl}\n")
            return
            
        try:
            caminho_formatado = self.caminho_owl.replace('\\', '/')
            self.onto = get_ontology(f"file://{caminho_formatado}").load()
            print(f"\n Ontologia carregada com sucesso!")
            self.mapear_da_ontologia()
        except Exception as e:
            print(f"\n Erro ao ler o arquivo: {e}")

    def mapear_da_ontologia(self):
        if not self.onto:
            return
        self.dicionario_termos = {}
        try:
            categorias = self.onto.search(subclass_of=self.onto.Ofensas)
            for cls in categorias:
                valores_peso = getattr(cls, "Peso", [])
                peso = valores_peso[0] if valores_peso else 5
                
                palavras = [unidecode(i.name.lower().replace("_", " ")) for i in cls.instances()]
                self.dicionario_termos[cls.name] = {"palavras": palavras, "peso": peso}
        except Exception as e:
            print(f"Erro ao mapear: {e}")

    def atualizar_ontologia(self, novas_palavras, nome_classe):
        if not self.onto:
            print("Ontologia não está carregada para atualizar.")
            return
        try:
            classe_alvo = getattr(self.onto, nome_classe)
            with self.onto:
                for p in novas_palavras:
                    nome_formatado = p.strip().lower().replace(" ", "_")
                    if not self.onto.search_one(iri=f"*{nome_formatado}"):
                        classe_alvo(nome_formatado)
            
            self.onto.save(file=self.caminho_owl, format="rdfxml")
            self.mapear_da_ontologia()
            print(f"✅ Termo(s) adicionado(s) em '{nome_classe}'")
        except Exception as e:
            print(f"Erro ao atualizar: {e}")

    def analisar(self, texto):
        texto_limpo = unidecode(texto.lower())
        score_total = 0
        termos_detectados = []
        for categoria, dados in self.dicionario_termos.items():
            for palavra in dados['palavras']:
                if re.search(r'\b' + re.escape(palavra) + r'\b', texto_limpo):
                    score_total += dados['peso']
                    termos_detectados.append(palavra)
        status = "Neutro"
        if score_total > 15: status = "Altamente Hostil"
        elif score_total > 0: status = "Ofensivo"
        return {"score": score_total, "status": status, "termos_detectados": list(set(termos_detectados))}