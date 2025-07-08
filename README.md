# Spotify Streaming History Analysis & Interactive Dashboard

A data engineering and visualization project that processes personal Spotify streaming history, enriches it with external APIs, and presents the insights in an interactive web dashboard built with Streamlit.

## Description

This project provides a complete pipeline to analyze your personal Spotify data dump. It starts with a robust ETL (Extract, Transform, Load) process that consolidates multiple JSON files from your Spotify data request. The core of the project lies in its data enrichment capabilities, where it connects to the Spotify API to fetch musical genres for each artist and to the IPinfo API to get geolocation data (city, region, ISP) from the streaming IP addresses.
The final, enriched dataset is then used to power a web-based, interactive dashboard built with Python and Streamlit, allowing for a deep and visual exploration of your personal music listening habits.

## Features

1. *ETL Pipeline:*

- Consolidates and cleans raw JSON data from Spotify's data dump.

2. *Data Enrichment:*

- Fetches artist genres using the Spotify API.
- Retrieves geolocation data (city, region, ISP) from IP addresses using the IPinfo API.
- Caching system for both APIs to avoid redundant calls and speed up subsequent runs.

3. *Interactive Dashboard:*

- A web application built with Streamlit to visualize insights.Dynamic Visualizations:Interactive drill-down charts to explore data by country, region, or city.
- Analysis of top tracks, artists, and genres over different time periods.
- Geographic analysis of listening habits.
- Insights into offline listening, incognito mode usage, and more.
Project Structure

```
spotify-dashboard-py/
│
├── data/
│   ├── raw/                  # Place your original Spotify JSON files here
│   └── processed/            # Stores the final CSV and API caches
│
├── src/
│   ├── __init__.py
│   ├── data_processing.py    # The main ETL and data enrichment script
│   └── app.py                # The Streamlit dashboard application
│
├── .env                      # Stores API keys and secrets (not committed to Git)
├── .env.example              # Template for the .env file
├── .gitignore
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```

## Setup and Installation

Follow these steps to get the project running on your local machine.

1. *Clone the Repository*

```
git clone https://github.com/conradosetti/spotify-dashboard-py.git
cd spotify-dashboard-py
```

2. *Create and Activate a Virtual Environment*

It is highly recommended to use a virtual environment to manage project dependencies.

*Windows:*

```
python -m venv venv
venv\Scripts\activate
```
*macOS / Linux:*
```
python -m venv venv
source venv/bin/activate
```

3. *Install Dependencies*

Install all the required Python libraries using pip.

```
pip install -r requirements.txt
```

4. *Set Up Environment Variables*

This project requires API keys to function. Make a copy of the example environment file:

```
# For Windows
copy .env.example .env

# For macOS / Linux
cp .env.example .env
```

5.  Open the newly created .env file and add your credentials:

- `CLIENT_ID` & `CLIENT_SECRET`: Get these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
- `IPINFO_TOKEN`: Get this from your [IPinfo](https://ipinfo.io/signup) dashboard after creating a free account.
Your .env file should look like this:

```
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
IPINFO_TOKEN=your_ipinfo_token
```

5. *Add Your Spotify Data*

Place your `Streaming_History_Audio_*.json` files inside the data/raw/ directory (if you don't have a raw dir create one).

## Usage

The project is divided into two main steps: processing the data and running the dashboard.
1. *Run the ETL Process*

Execute the data processing script. This will consolidate your JSON files, fetch data from the APIs, and create the final `streaming_history_consolidated.csv` file in the data/processed/ folder.

```
python src/data_processing.py
```
*Note*: The first run might take several minutes, as it needs to fetch data for all your unique artists and IP addresses. Subsequent runs will be much faster thanks to the caching system.

2. *Launch the Dashboard*
Once the data processing is complete, you can launch the interactive dashboard.

```
streamlit run src/app.py
```
This will open a new tab in your web browser with the dashboard application.
