import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from learning import Analisar
from classifier import Julgar

ONTOLOGIA_INICIAL = {
    "insulto_pessoal": {
        "palavras": ["burro", "idiota", "imbecil", "canalha"], 
        "peso": 5
    },
    "politica_agressiva": {
        "palavras": ["fascista", "comunista", "genocida", "ladrao"], 
        "peso": 8
    }
}

def main():
    caminho_dados = r"C:\Users\rodri\Downloads\TCC_IA\dados\dataset_eleicoes\2022-08-01-BOLSONARO NAO TRABALHA.parquet"
    
    if not os.path.exists(caminho_dados):
        print(f"ERRO: Não encontrei o arquivo em: {caminho_dados}")
        return

    print(f"Iniciando com dados de: {caminho_dados}")
    AnalisarDados = Analisar(caminho_dados)

    caminho_modelo = os.path.join(os.path.dirname(__file__), '..', 'modelos', 'cerebro_politico.model')
    
    if not os.path.exists(caminho_modelo):
        resp = input("Deseja me treinar do zero agora? (s/n): ")
        if resp.lower() == 's':
            AnalisarDados.treinar()
    else:
        resp = input("Modelo já existe. Deseja adicionar outro? (s/n): ")
        if resp.lower() == 's':
            AnalisarDados.treinar()

    palavras_semente = ["ladrao", "burro", "fascista"]
    novas_descobertas = AnalisarDados.descobrir_sinonimos(palavras_semente)
    
    print(f"\nIA sugere adicionar estas palavras à ontologia: {novas_descobertas}")
    
    juiz = Julgar(ONTOLOGIA_INICIAL)
    juiz.atualizar_ontologia(novas_descobertas)
    
    print("\n--- Teste em Tempo Real ---")
    print("Digite uma frase para analisar (ou 'sair'):")
    
    while True:
        texto = input("> ")
        if texto.lower() == 'sair': 
            break
        
        resultado = juiz.analisar(texto)
        print(f"\nStatus: {resultado['status']}")
        print(f"Impacto: {resultado['impacto_psicologico']}")
        print(f"Score: {resultado['score']}")
        print(f"Termos: {', '.join(resultado['termos_detectados'])}")

if __name__ == "__main__":
    main()