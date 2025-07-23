import streamlit as st
import pandas as pd
import os
import plotly.express as px



st.set_page_config(layout="wide")

# Título do Dashboard
st.title('Meu Dashboard de Streaming do Spotify')

@st.cache_data
def load_data():

    processed_file = 'data/processed/streaming_history_consolidated.csv'

    if not os.path.exists(processed_file):

        st.error("Arquivo de dados processados não encontrado. Execute o script 'data_processing.py' primeiro.")

        return None

    df = pd.read_csv(processed_file)
    df['ts'] = pd.to_datetime(df['ts'])

    return df

df = load_data()

# Apenas continua se os dados foram carregados com sucesso
if df is not None:
    
    # --- INÍCIO DA NOVA SEÇÃO: RETROSPECTIVA POR PERÍODO ---
    st.header('Retrospectiva por período')
    
    # 1. Obter a lista de anos únicos e ordená-los
    available_years = sorted(df['ts'].dt.year.unique(), reverse=True)
    dropdown_options = ["Todos os Tempos"] + available_years
    
    # 2. Criar o dropdown para seleção do ano
    selected_year = st.selectbox('Selecione um período para a retrospectiva:', dropdown_options)
    topAmount = st.slider('Quantos itens você gostaria de ver?', min_value=1, max_value=20, value=5, step=1)
    
    # 3. Filtrar o DataFrame para o ano selecionado
    df_year = df[df['ts'].dt.year == selected_year] if selected_year != "Todos os Tempos" else df
    
    # 4. Criar o grid 2x2
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    # Helper function para exibir os "Top n" e evitar repetição de código
    def display_top_n(dataframe, column_name, title, column_title, amount):
        """
        Exibe os 'Top N' itens de uma coluna.
        Possui uma lógica especial para a coluna 'genres' para contar cada gênero individualmente.
        """
        st.subheader(title)
        if dataframe.empty:
            st.write("Nenhum dado disponível para este ano.")
            return
        
        if column_name == "genres":
            # Para gêneros, precisamos separar os generos concatenados por ', '
            genres_series = dataframe[column_name].dropna()
            genres_series = genres_series[genres_series != 'N/A']
            
            if genres_series.empty:
                top_n_data = pd.Series(dtype='float64')
            else:
                top_n_data = genres_series.str.split(', ').explode().value_counts().head(amount)
                
        else:
            top_n_data = dataframe[column_name].value_counts().head(amount)
        
        if top_n_data.empty:
            st.write("Nenhum dado disponível.")
            return
            
        top_n_df = top_n_data.reset_index()
        top_n_df.columns = [column_title, 'Nº de Plays']
        top_n_df.index = top_n_df.index + 1
        
        st.dataframe(top_n_df, use_container_width=True, hide_index=True)
    
    # Quadrante 1: Top n Artistas
    with col1:
        display_top_n(df_year, 'master_metadata_album_artist_name', 'Top ' + str(topAmount) + ' Artistas', 'Artista', topAmount)
        
    # Quadrante 2: Top n Músicas
    with col2:
        display_top_n(df_year, 'master_metadata_track_name', 'Top ' + str(topAmount) + ' Músicas', 'Música', topAmount)
        
    # Quadrante 3: Top n Gêneros
    with col3:
        # Filtra gêneros 'N/A' antes de passar para a função
        df_year_genres = df_year[df_year['genres'] != 'N/A']
        display_top_n(df_year_genres, 'genres', 'Top ' + str(topAmount) + ' Gêneros', 'Gênero', topAmount)
        
    # Quadrante 4: Top n Albuns
    with col4:
        display_top_n(df_year, 'master_metadata_album_album_name', 'Top ' + str(topAmount) + ' Álbuns', 'Álbum', topAmount)
        
    st.divider()
    # --- FIM DA NOVA SEÇÃO ---

    # --- INÍCIO DA NOVA SEÇÃO: ANÁLISE DETALHADA POR ARTISTA ---
    st.header('Análise Detalhada por Artista')

    @st.cache_data
    def get_unique_artists():
        return sorted(df['master_metadata_album_artist_name'].dropna().unique())

    unique_artists = get_unique_artists()

    search_query = st.text_input("Pesquise por um artista:", key="artist_search")

    if search_query:
        suggestions = [artist for artist in unique_artists if artist.lower().startswith(search_query.lower())]
        
        st.write("Sugestões:")
        for suggestion in suggestions[:5]:
            if st.button(suggestion, key=f"btn_{suggestion}"):
                st.session_state.selected_artist = suggestion
    
    if 'selected_artist' in st.session_state:
        selected_artist = st.session_state.selected_artist
        
        st.subheader(f"Evolução dos Plays para: {selected_artist}")

        artist_df = df[df['master_metadata_album_artist_name'] == selected_artist].copy()
        
        # O índice 'ts' agora tem fuso horário UTC
        artist_df.set_index('ts', inplace=True)
        
        monthly_plays = artist_df.resample('ME').size()
        monthly_plays_df = monthly_plays.reset_index()
        monthly_plays_df.columns = ['Mês', 'Número de Plays']

        if not monthly_plays_df.empty:
            fig_artist = px.line(
                monthly_plays_df, 
                x='Mês', 
                y='Número de Plays',
                title=f"Plays Mensais de {selected_artist}",
                markers=True
            )
            
            fig_artist.update_xaxes(rangeslider_visible=True)
            
            st.plotly_chart(fig_artist, use_container_width=True)

            # --- INÍCIO DO TRECHO DE CÓDIGO CORRIGIDO ---
            
            st.subheader("Análise do Período")

            if len(monthly_plays_df) > 1:
                month_options = monthly_plays_df['Mês'].dt.strftime('%Y-%m').tolist()
                
                start_month, end_month = st.select_slider(
                    'Selecione um intervalo de meses para analisar em detalhe:',
                    options=month_options,
                    value=(month_options[0], month_options[-1])
                )

                # --- CORREÇÃO: Tornar as datas conscientes do fuso horário UTC ---
                # Adiciona o fuso horário UTC para corresponder ao fuso horário do índice
                start_date = pd.to_datetime(start_month).tz_localize('UTC')
                # Garante que a data final cubra o mês inteiro
                end_date = (pd.to_datetime(end_month) + pd.offsets.MonthEnd(1)).tz_localize('UTC')

                period_df = artist_df[(artist_df.index >= start_date) & (artist_df.index < end_date)]

            else:
                period_df = artist_df
                start_date = period_df.index.min()
                end_date = period_df.index.max()

            if not period_df.empty:
                top_track_in_period = period_df['master_metadata_track_name'].value_counts().idxmax()
                top_track_plays = period_df['master_metadata_track_name'].value_counts().max()

                st.info(f"Analisando o período de **{start_date.strftime('%d/%m/%Y')}** a **{end_date.strftime('%d/%m/%Y')}**")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric(label="Música Mais Ouvida no Período", value=top_track_in_period)
                with metric_col2:
                    st.metric(label="Total de Plays (da música)", value=f"{top_track_plays} plays")
            else:
                st.write("Nenhum play registado no período selecionado.")

            # --- FIM DO TRECHO DE CÓDIGO CORRIGIDO ---

        else:
            st.write("Nenhum dado de play encontrado para este artista.")

    st.divider()
    # --- FIM DA NOVA SEÇÃO ---