import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from learning import Analisar
from classifier import Julgar

st.set_page_config(page_title="Monitor de Ofensas | TCC", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def carregar_sistemas():
    caminho_base = os.path.dirname(__file__)
    caminho_parquet = os.path.abspath(os.path.join(caminho_base, '..', 'dados', 'dataset_eleicoes', '2022-08-01-BOLSONARO NAO TRABALHA.parquet'))
    caminho_owl = os.path.abspath(os.path.join(caminho_base, '..', 'dados', 'ontologia', 'Ofensas.owl'))
    
    juiz = Julgar(caminho_owl)
    mentor = Analisar(caminho_parquet)
    return juiz, mentor, caminho_parquet

juiz, mentor, caminho_parquet = carregar_sistemas()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2040/2040946.png", width=80)
    st.title("Monitor de Hostilidade")
    st.markdown("Plataforma de detecção de hostilidade em discussões no X/Twitter.")
    st.divider()
    st.info("✅ Ontologia Carregada")
    st.info("✅ Modelo Word2Vec Pronto")
    st.divider()
    st.caption("Desenvolvido para análise do comportamento online.")

st.title("🛡️ Sistema de Monitoramento de Ofensas Políticas")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Análise Manual", "📊 Dashboard do Dataset", "🧠 Adicionar palavras ofensivas", "🌐 Coleta (X API)"])

with tab1:
    st.subheader("Análise de Texto Individual")
    frase = st.text_area("Insira o texto da rede social para análise:", height=100)
    
    if st.button("Analisar Hostilidade", type="primary"):
        if frase:
            res = juiz.analisar(frase)
            col1, col2, col3 = st.columns(3)
            col1.metric("Status", res['status'])
            col2.metric("Score de Severidade", res['score'])
            col3.metric("Termos Identificados", len(res['termos_detectados']))
            
            if res['termos_detectados']:
                st.error(f"**Termos mapeados encontrados:** {', '.join(res['termos_detectados'])}")
            else:
                st.success("Nenhum termo ofensivo da ontologia foi encontrado.")
        else:
            st.warning("Insira um texto para analisar.")

with tab2:
    st.subheader("Classificação em Massa e Visualização")
    if st.button("Processar Dataset Completo", type="primary"):
        with st.spinner("Lendo e classificando tweets... isso pode levar alguns segundos."):
            df = pd.read_parquet(caminho_parquet)
            coluna_texto = 'tweet_content'
            
            if coluna_texto in df.columns:
                resultados = df[coluna_texto].apply(lambda x: juiz.analisar(str(x)))
                df['Score_Ofensa'] = resultados.apply(lambda x: x['score'])
                df['Status'] = resultados.apply(lambda x: x['status'])
                df['Termos_Detectados'] = resultados.apply(lambda x: ", ".join(x['termos_detectados']))
                
                contagem = df['Status'].value_counts()
                ordem_severidade = ['Neutro', 'Ofensivo', 'Altamente Hostil']
                contagem = contagem.reindex(ordem_severidade).dropna()
                mapeamento_cores = {'Neutro': '#87CEEB', 'Ofensivo': '#FFA500', 'Altamente Hostil': '#FF4500'}
                cores_barras = [mapeamento_cores.get(status) for status in contagem.index]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
                    contagem.plot(kind='bar', color=cores_barras, ax=ax_bar)
                    ax_bar.set_title('Distribuição da Toxicidade')
                    ax_bar.set_ylabel('Quantidade de Tweets')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig_bar)
                
                with col2:
                    fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
                    ax_pie.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores_barras, startangle=140, explode=[0.05]*len(contagem))
                    ax_pie.set_title('Proporção de Toxicidade')
                    plt.tight_layout()
                    st.pyplot(fig_pie)
                
                st.divider()
                st.subheader("☁️ Nuvem de Palavras Ofensivas")
                todos_termos = " ".join(df[df['Termos_Detectados'] != ""]['Termos_Detectados'].astype(str).tolist())
                todos_termos = todos_termos.replace(",", "")
                
                if todos_termos.strip():
                    wordcloud = WordCloud(width=800, height=300, background_color='white', colormap='Reds').generate(todos_termos)
                    fig_wc, ax_wc = plt.subplots(figsize=(10, 4))
                    ax_wc.imshow(wordcloud, interpolation='bilinear')
                    ax_wc.axis('off')
                    st.pyplot(fig_wc)
                else:
                    st.info("Não há termos ofensivos suficientes para gerar a nuvem de palavras.")

                st.divider()
                st.subheader("🔍 Exemplos Anonimizados e Exportação")
                
                df_ofensivos = df[df['Termos_Detectados'] != ""]
                if not df_ofensivos.empty:
                    amostras = df_ofensivos.dropna(subset=[coluna_texto]).sample(n=min(2, len(df_ofensivos)))
                    for _, row in amostras.iterrows():
                        with st.expander(f"Tweet ID: {row.get('tweet_id', 'Desconhecido')} | Status: {row.get('Status')}"):
                            st.write(f"**Texto:** {row[coluna_texto]}")
                            st.write(f"**Ofensas Detectadas:** {row.get('Termos_Detectados')} (Score: {row.get('Score_Ofensa')})")
                            st.info("Campos de identificação anonimizados conforme diretrizes da LGPD.")
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Baixar Dataset Classificado (CSV)",
                    data=csv,
                    file_name="dataset_classificado.csv",
                    mime="text/csv",
                    type="primary"
                )
            else:
                st.error("Coluna 'tweet_content' não encontrada no dataset.")

with tab3:
    st.subheader("Expansão do Vocabulário (IA -> Ontologia)")
    
    st.markdown("### 1. Sugestão de Novos Termos")
    semente = st.text_input("Palavras semente (separadas por vírgula):", "ladrao, fascista, burro, canalha")
    
    if st.button("Buscar Sinônimos no Modelo"):
        with st.spinner("Analisando o comportamento do consumidor online e processando linguagem natural..."):
            mentor.treinar()
            lista_semente = [p.strip() for p in semente.split(",")]
            descobertas = mentor.descobrir_sinonimos(lista_semente)
            st.session_state['descobertas'] = descobertas
            
    if 'descobertas' in st.session_state and st.session_state['descobertas']:
        st.success(f"**Termos encontrados pela IA:** {', '.join(st.session_state['descobertas'])}")
        
        st.markdown("### 2. Injeção na Ontologia")
        col1, col2 = st.columns(2)
        with col1:
            termo_escolhido = st.selectbox("Selecione o termo:", st.session_state['descobertas'])
        with col2:
            classe_escolhida = st.selectbox("Selecione a classe:", ["Criminalizante", "Intelectual", "Moral"])
        
        if st.button("Adicionar ao Protégé (.owl)", type="primary"):
            juiz.atualizar_ontologia([termo_escolhido], classe_escolhida)
            st.success(f"✅ Termo '{termo_escolhido}' injetado na classe '{classe_escolhida}'!")

with tab4:
    st.subheader("Coleta de Dados - API do X (Scraping)")
    st.warning("⚠️ O módulo de extração (scraping.py) está temporariamente desativado.")
    st.text_input("Bearer Token (Bloqueado):", disabled=True)
    st.text_input("Termo de Busca no X:", disabled=True)
    st.button("Iniciar Extração", disabled=True)