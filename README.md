
#  Sistema de Monitoramento de Ofensas 

Este projeto é parte de um Trabalho de Conclusão de Curso (TCC) focado na análise do comportamento online e detecção de hostilidade em discussões no X (antigo Twitter). A plataforma utiliza Processamento de Linguagem Natural (NLP) associado a uma Ontologia construída no Protégé para classificar tweets de forma automatizada.

----

## Funcionalidades

* **Classificação Baseada em Ontologia:** Mapeamento de termos ofensivos em categorias (Criminalizante, Intelectual, Moral) utilizando `owlready2`.
* **Descoberta de Novos Termos (IA):** Utilização de modelos de linguagem (Word2Vec) para encontrar sinônimos e gírias emergentes, permitindo a evolução contínua da ontologia.
* **Dashboard Interativo:** Interface web amigável construída com `Streamlit` para visualização de dados, gráficos de distribuição e nuvens de palavras.
* **Adequação à LGPD:** Anonimização automática de identificadores de usuários e menções nos exemplos exportados.
* **Processamento em Lote:** Capacidade de ler, classificar e exportar arquivos `.parquet` contendo milhares de tweets.

----

## Como Instalar e Configurar
Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina.

1. Crie um ambiente virtual (recomendado):
Abra o terminal na pasta do projeto e digite:

```
python -m venv .venv
```

2. Ative o ambiente virtual:

No Windows:

```
.venv\Scripts\activate
```

No Linux/Mac:

```
source .venv/bin/activate
```
3. Instale as dependências:
Com o ambiente ativado, instale todas as bibliotecas necessárias:

```
pip install -r requirements.txt
```
----
💻 Como Usar (Executando a Interface)
Para iniciar a plataforma analítica, utilize o comando do Streamlit no seu terminal

```
streamlit run src/interface.py
```
O sistema abrirá automaticamente uma aba no seu navegador padrão (geralmente em http://localhost:8501) contendo 4 abas principais:

Análise Manual: Teste o modelo com frases avulsas.

Dashboard do Dataset: Classifique o dataset de exemplo, visualize gráficos de toxicidade, gere a nuvem de palavras e baixe os resultados em CSV.

Adicionar palavras ofensivas: Utilize a IA para buscar sinônimos de ofensas e injetá-los diretamente no arquivo .owl da ontologia.

Coleta (X API): Módulo temporariamente desativado por padrão.

----

⚠️ Observações Acadêmicas
Privacidade (LGPD): A plataforma mascara colunas de identificação pessoal (user, mentions, etc.) antes de exibir exemplos qualitativos.

API do X: O módulo scraping.py exige uma conta de desenvolvedor no X. Para utilizá-lo, é necessário inserir o BEARER_TOKEN no código fonte e remover a trava de segurança na aba 4 da interface.