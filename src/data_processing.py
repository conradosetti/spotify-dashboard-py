import pandas as pd
import json
import os

def consolidate_data():
    """Lê os arquivos JSON da pasta data/raw, consolida e salva como CSV em data/processed."""
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

    # --- Aqui é um bom lugar para a limpeza de dados no futuro ---
    # Ex: Converter a coluna 'ts' para datetime
    df['ts'] = pd.to_datetime(df['ts'])
    # Ex: Converter 'ms_played' para segundos ou minutos
    df['s_played'] = df['ms_played'] / 1000
    df['min_played'] = df['ms_played'] / 60000

    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\nDados consolidados e processados com sucesso em: '{output_file}'")
    return df

if __name__ == '__main__':
    consolidate_data()