import streamlit as st
import pandas as pd
import os
import plotly.express as px
# A biblioteca que torna o gráfico clicável
from streamlit_plotly_events import plotly_events



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
    # Garante que a coluna de data esteja no formato correto para manipulação
    df['ts'] = pd.to_datetime(df['ts']) 
    return df

df = load_data()

# Apenas continua se os dados foram carregados com sucesso
if df is not None:
    # --- INÍCIO DA NOVA SEÇÃO INTERATIVA ---
    st.header('Análise Geográfica dos Seus Streamings')

    # Usaremos colunas para organizar o gráfico e a lista de músicas lado a lado
    col1, col2 = st.columns([0.4, 0.6]) # A primeira coluna ocupa 40% e a segunda 60%

    with col1:
        st.subheader("Músicas ouvidas por País")
        
        # 1. Contar quantas músicas foram ouvidas em cada país
        country_counts = df['conn_country'].value_counts()
        
        # 2. Criar a figura do gráfico de pizza com Plotly
        fig_country = px.pie(
            values=country_counts.values, 
            names=country_counts.index,
            title='Distribuição por País',
            hole=.3, # Adiciona um "buraco" no meio para um visual mais moderno (gráfico de rosca)
            color_discrete_sequence=px.colors.sequential.Blues_r,
        )
        fig_country.update_traces(textinfo='percent+label')

        # 3. Usar plotly_events para capturar cliques no gráfico
        #    A variável 'clicked_point' conterá a informação do ponto clicado
        clicked_point = plotly_events(fig_country, click_event=True, key="country_pie")

        # 4. Armazenar o país clicado na "memória" da sessão
        #    Isso garante que a seleção não seja perdida quando o Streamlit re-executa o script
        if clicked_point:
            clicked_index = clicked_point[0]['pointNumber']
            country_name = country_counts.index[clicked_index]
            st.session_state.selected_country = country_name

    with col2:
        # 5. Exibir a lista de músicas se um país foi selecionado
        if 'selected_country' in st.session_state:
            # Pega o país que foi salvo na memória da sessão
            selected_country = st.session_state.selected_country
            
            st.subheader(f"Top 50 Músicas em: {selected_country}")

            # Filtra o DataFrame apenas para o país selecionado
            country_df = df[df['conn_country'] == selected_country]
            
            # Conta as músicas mais ouvidas nesse país
            top_50_tracks = country_df['master_metadata_track_name'].value_counts().head(50)
            
            # Converte a Series para um DataFrame para exibição mais bonita
            top_50_df = top_50_tracks.reset_index()
            top_50_df.columns = ['Música', 'Nº de Plays']
            top_50_df.index = top_50_df.index + 1 # Começa a contagem do índice em 1
            
            # Exibe a tabela com as músicas
            st.dataframe(top_50_df, use_container_width=True, height=500)
        else:
            # Mensagem inicial antes de qualquer clique
            st.info("⬅️ Clique em um país no gráfico para ver as músicas mais ouvidas.")
            
    # Adiciona um separador visual para o resto do dashboard
    st.divider()

    # --- FIM DA NOVA SEÇÃO INTERATIVA ---


    # O resto do seu dashboard continua aqui...
    st.write("Aqui estão os primeiros registros do seu histórico:")
    st.dataframe(df.head())

    # Exemplo de insight: Top 10 artistas
    st.header('Top 10 Artistas Mais Ouvidos')
    top_10_artists = df['master_metadata_album_artist_name'].value_counts().head(10)
    st.bar_chart(top_10_artists)
    
    # Exemplo de insight: Gêneros mais ouvidos
    st.header('Gêneros Musicais Mais Ouvidos')
    genre_counts = df[df['genres'] != 'N/A']['genres'].value_counts()
    top_n = 20
    if len(genre_counts) > top_n:
        top_genres = genre_counts.head(top_n)
        others_count = genre_counts.iloc[top_n:].sum()
        top_genres['Outros'] = others_count
    else:
        top_genres = genre_counts
        
    fig = px.pie(values=top_genres.values, 
             names=top_genres.index, 
             title='Distribuição dos Gêneros Musicais')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top 10 Artistas mais ouvidos em 2014
    st.header('Top 10 Artistas Mais Ouvidos em 2014')
    df_2014 = df[df['ts'].dt.year == 2014]
    top_10_artists_2014 = df_2014['master_metadata_album_artist_name'].value_counts().head(10)
    st.bar_chart(top_10_artists_2014, color='#FFA500')
    
    #Top 10 Músicas mais ouvidas em 2014
    st.header('Top 10 Músicas Mais Ouvidas em 2014')
    top_10_tracks_2014 = df_2014['master_metadata_track_name'].value_counts().head(10)
    st.bar_chart(top_10_tracks_2014, color='#FFA500')
    
    # Top 10 Artistas mais ouvidos em 2015
    st.header('Top 10 Artistas Mais Ouvidos em 2015')
    df_2015 = df[df['ts'].dt.year == 2015]
    top_10_artists_2015 = df_2015['master_metadata_album_artist_name'].value_counts().head(10)
    st.bar_chart(top_10_artists_2015, color='#FF4500')
    
    #Top 10 Músicas mais ouvidas em 2015
    st.header('Top 10 Músicas Mais Ouvidas em 2015')
    top_10_tracks_2015 = df_2015['master_metadata_track_name'].value_counts().head(10)
    st.bar_chart(top_10_tracks_2015, color='#FF4500')
    
    #Top 10 Artistas mais ouvidos em 2024
    st.header('Top 10 Artistas Mais Ouvidos em 2024')
    df_2024 = df[df['ts'].dt.year == 2024]
    top_10_artists_2024 = df_2024['master_metadata_album_artist_name'].value_counts().head(10)
    st.bar_chart(top_10_artists_2024, color='#32CD32')
    
    #Top 10 Músicas mais ouvidas em 2024
    st.header('Top 10 Músicas Mais Ouvidas em 2024')
    top_10_tracks_2024 = df_2024['master_metadata_track_name'].value_counts().head(10)
    st.bar_chart(top_10_tracks_2024, color='#32CD32')
    
    #Musica mais ouvida em dezembro de 2021
    st.header('Música Mais Ouvida em Dezembro de 2021')
    df_dec_2021 = df[(df['ts'].dt.year == 2021) & (df['ts'].dt.month == 12)]
    if not df_dec_2021.empty:
        most_played_dec_2021 = df_dec_2021.groupby('master_metadata_track_name')['s_played'].sum().idxmax()
        st.write(f"A música mais ouvida em dezembro de 2021 foi: {most_played_dec_2021}")
    else:
        st.write("Não há dados disponíveis para dezembro de 2021.")
        
    # Música mais ouvida em janeiro de 2022
    st.header('Música Mais Ouvida em Janeiro de 2022')
    df_jan_2022 = df[(df['ts'].dt.year == 2022) & (df['ts'].dt.month == 1)]
    if not df_jan_2022.empty:
        most_played_jan_2022 = df_jan_2022.groupby('master_metadata_track_name')['s_played'].sum().idxmax()
        st.write(f"A música mais ouvida em janeiro de 2022 foi: {most_played_jan_2022}")
    else:
        st.write("Não há dados disponíveis para janeiro de 2022.")
        
    # Música mais ouvida em janeiro de 2023
    st.header('Música Mais Ouvida em Janeiro de 2023')
    df_jan_2023 = df[(df['ts'].dt.year == 2023) & (df['ts'].dt.month == 1)]
    if not df_jan_2023.empty:
        most_played_jan_2023 = df_jan_2023.groupby('master_metadata_track_name')['s_played'].sum().idxmax()
        st.write(f"A música mais ouvida em janeiro de 2023 foi: {most_played_jan_2023}")
    else:
        st.write("Não há dados disponíveis para janeiro de 2023.")
        
    # Música mais ouvida em julho de 2022
    st.header('Música Mais Ouvida em Julho de 2022')
    df_jul_2022 = df[(df['ts'].dt.year == 2022) & (df['ts'].dt.month == 7)]
    if not df_jul_2022.empty:
        most_played_jul_2022 = df_jul_2022.groupby('master_metadata_track_name')['s_played'].sum().idxmax()
        st.write(f"A música mais ouvida em julho de 2022 foi: {most_played_jul_2022}")
    else:
        st.write("Não há dados disponíveis para julho de 2022.")
        
    # Música mais ouvida em maio de 2022
    st.header('Música Mais Ouvida em Maio de 2022')
    df_may_2022 = df[(df['ts'].dt.year == 2022) & (df['ts'].dt.month == 5)]
    if not df_may_2022.empty:
        most_played_may_2022 = df_may_2022.groupby('master_metadata_track_name')['s_played'].sum().idxmax()
        st.write(f"A música mais ouvida em maio de 2022 foi: {most_played_may_2022}")
    else:
        st.write("Não há dados disponíveis para maio de 2022.")
    
    #Ultima musica ouvida fora do Brasil
    st.header('Última Música Ouvida Fora do Brasil')
    df_outside_brazil = df[df['conn_country'] != 'BR']
    if not df_outside_brazil.empty:
        last_track_outside_brazil = df_outside_brazil.sort_values(by='ts', ascending=False).iloc[0]
        st.write(f"A última música ouvida fora do Brasil foi: {last_track_outside_brazil['master_metadata_track_name']} em {last_track_outside_brazil['ts']} no estado {last_track_outside_brazil['region']} na plataforma {last_track_outside_brazil['platform']} no país {last_track_outside_brazil['conn_country']}")
    else:
        st.write("Não há dados disponíveis para músicas ouvidas fora do Brasil.")
        
    #Ultima musica ouvida no modo offline
    st.header('Última Música Ouvida no Modo Offline')
    df_offline = df[df['offline'] == True]
    if not df_offline.empty:
        last_offline_track = df_offline.sort_values(by='ts', ascending=False).iloc[0]
        st.write(f"A última música ouvida no modo offline foi: {last_offline_track['master_metadata_track_name']} em {last_offline_track['ts']} no país {last_offline_track['conn_country']} na plataforma {last_offline_track['platform']} no estado {last_offline_track['region']}")
    else:
        st.write("Não há dados disponíveis para músicas ouvidas no modo offline.")
        
    # Última música ouvida no modo incognito e em qual país
    st.header('Última Música Ouvida no Modo Incognito')
    df_incognito = df[df['incognito_mode'] == True]
    if not df_incognito.empty:
        last_incognito_track = df_incognito.sort_values(by='ts', ascending=False).iloc[0]
        st.write(f"A última música ouvida no modo incognito foi: {last_incognito_track['master_metadata_track_name']} em {last_incognito_track['ts']} no país {last_incognito_track['conn_country']} na plataforma {last_offline_track['platform']} no estado {last_offline_track['region']}")
    else:
        st.write("Não há dados disponíveis para músicas ouvidas no modo incognito.")
        
    #Ultima musica ouvida fora do estado de São Paulo
    st.header('Última Música Ouvida Fora do Estado de São Paulo')
    df_outside_sp = df[df['region'] != 'São Paulo']
    if not df_outside_sp.empty:
        last_track_outside_sp = df_outside_sp.sort_values(by='ts', ascending=False).iloc[0]
        st.write(f"A última música ouvida fora do estado de São Paulo foi: {last_track_outside_sp['master_metadata_track_name']} em {last_track_outside_sp['ts']} no país {last_track_outside_sp['conn_country']} na plataforma {last_track_outside_sp['platform']} no estado {last_track_outside_sp['region']}")
    else:
        st.write("Não há dados disponíveis para músicas ouvidas fora do estado de São Paulo.")
    
    # Informações das 50 Últimas musicas ouvidas fora do estado de São Paulo
    st.header('50 Últimas Músicas Ouvidas Fora do Estado de São Paulo')
    if not df_outside_sp.empty:
        last_50_tracks_outside_sp = df_outside_sp.sort_values(by='ts', ascending=False).head(50)
        st.dataframe(last_50_tracks_outside_sp[['ts', 'master_metadata_track_name', 'master_metadata_album_artist_name', 'conn_country', 'region', 'platform']], use_container_width=True)
    else:
        st.write("Não há dados disponíveis para músicas ouvidas fora do estado de São Paulo.")
    
    #Grafico de pizza dos países de onde mais se ouviu música
    st.header('Distribuição dos Países de Onde Mais Se Ouviu Música')
    country_counts = df['conn_country'].value_counts()
    fig_country = px.pie(
        values=country_counts.values, 
        names=country_counts.index,
        title='Distribuição por País',
        hole=.3, # Adiciona um "buraco" no meio para um visual mais moderno (gráfico de rosca)
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig_country.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_country, use_container_width=True)