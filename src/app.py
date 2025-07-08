import streamlit as st
import pandas as pd
import os

# Título do Dashboard
st.title('Meu Dashboard de Streaming do Spotify')

# Carregar os dados
@st.cache_data # Isso faz o cache dos dados para não recarregar a cada interação
def load_data():
    processed_file = 'data/processed/streaming_history_consolidated.csv'
    if not os.path.exists(processed_file):
        st.error("Arquivo de dados processados não encontrado. Execute o script 'data_processing.py' primeiro.")
        return None
    df = pd.read_csv(processed_file)
    df['ts'] = pd.to_datetime(df['ts']) # Garante que a coluna de data esteja no formato correto
    return df

df = load_data()

if df is not None:
    st.write("Aqui estão os primeiros registros do seu histórico:")
    st.dataframe(df.head())

    # Exemplo de insight: Top 10 artistas
    st.header('Top 10 Artistas Mais Ouvidos')
    top_10_artists = df['master_metadata_album_artist_name'].value_counts().head(10)
    st.bar_chart(top_10_artists)