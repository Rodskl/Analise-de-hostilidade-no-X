import re
from unidecode import unidecode

class Julgar:
    def __init__(self, ontologia_base):
        self.ontologia = ontologia_base

    def atualizar_ontologia(self, novas_palavras):
        if "aprendido" not in self.ontologia:
            self.ontologia["aprendido"] = {"palavras": [], "peso": 3}
        
        for p in novas_palavras:
            if p not in self.ontologia["aprendido"]["palavras"]:
                self.ontologia["aprendido"]["palavras"].append(p)

    def analisar(self, texto):
        texto_limpo = unidecode(texto.lower())
        score_total = 0
        detalhes = []

        for categoria, dados in self.ontologia.items():
            for palavra in dados['palavras']:
                if re.search(r'\b' + unidecode(palavra) + r'\b', texto_limpo):
                    score_total += dados['peso']
                    detalhes.append(palavra)

        if score_total == 0:
            status = "Saudável"
            impacto = "Baixo impacto emocional"
        elif score_total < 5:
            status = "Polarizado"
            impacto = "Gera viés de confirmação"
        elif score_total < 15:
            status = "Tóxico"
            impacto = "Ansiedade e hostilidade"
        else:
            status = "Extremista"
            impacto = "Desumanização e humilhação"

        return {
            "texto": texto,
            "score": score_total,
            "status": status,
            "impacto_psicologico": impacto,
            "termos_detectados": detalhes
        }