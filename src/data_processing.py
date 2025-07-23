import pandas as pd
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from dotenv import load_dotenv
import ipinfo # Nova biblioteca para geolocalização

# Carrega as variáveis do arquivo .env (CLIENT_ID, CLIENT_SECRET, IPINFO_TOKEN)
load_dotenv()

def add_geolocation_data(df):
    """
    Enriquece o DataFrame com dados de geolocalização (cidade, estado, provedor)
    usando a API do ipinfo.io. Usa um cache local para evitar buscas repetidas.
    """
    ipinfo_token = os.getenv("IPINFO_TOKEN")

    # Verifica se o token da API foi fornecido
    if not ipinfo_token:
        print("AVISO: Token do IPINFO_TOKEN não encontrado no arquivo .env. Pulando a geolocalização.")
        # Adiciona colunas vazias para evitar erros no app
        df['city'] = 'N/A'
        df['region'] = 'N/A'
        df['isp'] = 'N/A'
        return df

    # Inicia o manipulador da API com seu token
    handler = ipinfo.getHandler(ipinfo_token)

    # Carrega o cache de geolocalização, se existir
    cache_path = 'data/processed/ip_cache.json'
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            ip_cache = json.load(f)
    else:
        ip_cache = {}

    # Pega a lista de IPs únicos que ainda não estão no cache
    unique_ips = df['ip_addr'].dropna().unique()
    ips_to_fetch = [ip for ip in unique_ips if ip not in ip_cache]

    print(f"Encontrados {len(unique_ips)} IPs únicos. Buscando geolocalização para {len(ips_to_fetch)} novos IPs.")

    # Busca os dados para os novos IPs
    for ip in ips_to_fetch:
        try:
            details = handler.getDetails(ip)
            # Armazena os detalhes que queremos no nosso cache
            ip_cache[ip] = {
                'city': details.city,
                'region': details.region,
                'isp': details.org
            }
            print(f"Dados para '{ip}': Cidade: {details.city}, Provedor: {details.org}")
        except Exception as e:
            # Adiciona ao cache mesmo se der erro, para não tentar de novo
            ip_cache[ip] = {'city': 'Error', 'region': 'Error', 'isp': 'Error'}
            print(f"Erro ao buscar por '{ip}': {e}")
    
    # Salva o cache atualizado
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(ip_cache, f, indent=4)

    # Mapeia os dados de geolocalização para novas colunas no DataFrame
    df['city'] = df['ip_addr'].map(lambda ip: ip_cache.get(ip, {}).get('city', 'N/A'))
    df['region'] = df['ip_addr'].map(lambda ip: ip_cache.get(ip, {}).get('region', 'N/A'))
    df['isp'] = df['ip_addr'].map(lambda ip: ip_cache.get(ip, {}).get('isp', 'N/A'))

    return df


def add_genres(df):
    """
    Enriquece o DataFrame com os gêneros dos artistas usando a API do Spotify.
    Usa um cache local para evitar buscas repetidas.
    """
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    if not client_id or not client_secret:
        print("AVISO: Credenciais do Spotify não encontradas. Pulando a busca de gêneros.")
        df['genres'] = 'N/A'
        return df
    
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    cache_path = 'data/processed/genres_cache.json'
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            genres_cache = json.load(f)
    else:
        genres_cache = {}
        
    unique_artists = df['master_metadata_album_artist_name'].dropna().unique()
    artists_to_fetch = [artist for artist in unique_artists if artist not in genres_cache]

    print(f"Encontrados {len(unique_artists)} artistas únicos. Buscando gêneros para {len(artists_to_fetch)} novos artistas.")

    for artist_name in artists_to_fetch:
        try:
            results = sp.search(q=f"artist:{artist_name}", type='artist', limit=1)
            if results['artists']['items']:
                artist_genres = results['artists']['items'][0]['genres']
                genres_cache[artist_name] = artist_genres
                print(f"Gêneros para '{artist_name}': {artist_genres}")
            else:
                genres_cache[artist_name] = []
                print(f"Artista '{artist_name}' não encontrado no Spotify.")
            time.sleep(0.1)
        except Exception as e:
            print(f"Erro ao buscar por '{artist_name}': {e}")
            genres_cache[artist_name] = []

    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(genres_cache, f, indent=4)

    df['genres'] = df['master_metadata_album_artist_name'].map(lambda x: ', '.join(genres_cache.get(x)) if (x and genres_cache.get(x)) else 'N/A')
    
    return df

def consolidate_data():
    """Lê os arquivos JSON, limpa, enriquece e salva o resultado final."""
    raw_path = 'data/raw'
    processed_path = 'data/processed'
    output_file = os.path.join(processed_path, 'streaming_history_consolidated.csv')
    
    os.makedirs(processed_path, exist_ok=True)

    all_data = []
    json_files = [f for f in os.listdir(raw_path) if f.endswith('.json')]

    for file_name in json_files:
        file_path = os.path.join(raw_path, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)
        print(f"Arquivo '{file_name}' lido com sucesso.")

    df = pd.DataFrame(all_data)

    print("\n--- Iniciando limpeza e transformação dos dados ---")
    df['ts'] = pd.to_datetime(df['ts'])
    df['s_played'] = df['ms_played'] / 1000
    df['min_played'] = df['ms_played'] / 60000
    
    print("\n--- Iniciando enriquecimento com gêneros musicais ---")
    df = add_genres(df)

    print("\n--- Iniciando enriquecimento com geolocalização ---")
    df = add_geolocation_data(df)

    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nDados consolidados, processados e enriquecidos com sucesso em: '{output_file}'")
    return df

if __name__ == '__main__':
    consolidate_data()
