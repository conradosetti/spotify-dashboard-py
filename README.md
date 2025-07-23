# Spotify Streaming History Analysis & Interactive Dashboard

A data engineering and visualization project that processes a user's personal Spotify streaming history, enriches it with external APIs, and presents deep insights in an interactive web dashboard built with Python and Streamlit.

## Description

This project provides a complete pipeline to analyze your personal Spotify data dump. It begins with a robust ETL (Extract, Transform, Load) script that consolidates multiple JSON files, cleans the data, and enriches it by connecting to two external APIs:

* **Spotify API**: To fetch musical genres for each artist.
* **IPinfo API**: To get geolocation data (city, region, ISP) from streaming IP addresses.

The final, enriched dataset powers a feature-rich, interactive dashboard built with Streamlit. This allows for a deep and visual exploration of your personal music listening habits over the years.

## Features

### 📊 Interactive Dashboard

A web application built with Streamlit that provides multiple views into your listening data.

- **Annual & All-Time Retrospective**: Select a specific year or "All Time" to see dynamically updated charts. Use a slider to control how many items (Top 5, Top 10, etc.) are displayed.
- **Artist Deep-Dive**: Search for any artist in your history with dynamic suggestions. View an interactive timeline of their monthly plays, complete with a range slider to zoom in on specific periods and discover your most-played track within that timeframe.
- **Geographic Analysis**: View a breakdown of your listening by country and select a specific country from a dropdown to see a detailed list of your Top 50 most-played tracks there.

### ⚙️ ETL & Data Enrichment Pipeline

A powerful backend script (`data_processing.py`) that prepares the data for analysis.

- **Data Consolidation**: Merges multiple `Streaming_History_*.json` files into a single, clean dataset.
- **API Enrichment**: Adds valuable context (genres, location) that is not present in the original data.
- **Intelligent Caching**: Creates local cache files (`genres_cache.json`, `ip_cache.json`) to store API results. This makes subsequent runs of the script almost instantaneous, as it only fetches data for new artists or IP addresses.

## Project Structure

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

### 1. Clone the Repository

```bash
git clone [https://github.com/conradosetti/spotify-dashboard-py.git](https://github.com/conradosetti/spotify-dashboard-py.git)
cd spotify-dashboard-py
```

### 2. Create and Activate a Virtual Environment

Using a stable Python version like **3.11** is highly recommended for compatibility.

* **Windows:**

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

* **macOS / Linux:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

This project requires API keys to function.

1. Make a copy of the example environment file: `cp .env.example .env`
2. Open the newly created `.env` file and add your credentials:
    * `CLIENT_ID` & `CLIENT_SECRET`: Get these from the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    * `IPINFO_TOKEN`: Get this from your [IPinfo.io dashboard](https://ipinfo.io/signup) after creating a free account.

### 5. Add Your Spotify Data

Place your `Streaming_History_Audio_*.json` files inside the `data/raw/` directory.

## Usage

The project is divided into two main steps: processing the data and running the dashboard.

### 1. Run the ETL Process

Execute the data processing script. This will consolidate your JSON files, fetch data from the APIs, and create the final `streaming_history_consolidated.csv` file.

```bash
python src/data_processing.py
```

*Note: The first run might take several minutes. Subsequent runs will be much faster thanks to the caching system.*

### 2. Launch the Dashboard

Once the data processing is complete, launch the interactive dashboard.

```bash
streamlit run src/app.py
```

This will open a new tab in your web browser with the application.

---

## Building a Portable Executable (Advanced)

This project can also be packaged into a portable desktop application using **Electron** and **@stlite/desktop**. This method runs the Streamlit app in a WebAssembly environment, which has one major limitation: **it cannot make live API calls**.

Therefore, this build process is for creating a **viewer** for an already-processed `streaming_history_consolidated.csv` file. The user must have this file available.

The build process uses `npm` and requires a `package.json` file configured for `@stlite/desktop`.

### Build Steps Explained

1. `npm install`
    * **What it does:** Reads the `devDependencies` in `package.json` and downloads the necessary JavaScript tools, primarily `electron`, `electron-builder`, and `@stlite/desktop`, into a `node_modules` folder. This only needs to be done once.

2. `npm run dump`
    * **What it does:** This is the core command from `@stlite/desktop`. It reads the `"stlite"` configuration in your `package.json` and performs several actions:
        * Finds your Python entrypoint (`streamlit_app.py`).
        * Installs the Python dependencies you listed (like `pandas`, `plotly`) into a WebAssembly-compatible environment.
        * Copies any specified data files (like your `.csv`) into the application bundle.
        * Outputs everything into a `build` directory, ready for Electron.

3. `npm run start`
    * **What it does:** A shortcut to run `electron .`. It opens a development window of your desktop application, allowing you to quickly test how it looks and behaves without creating a final executable.

4. `npm run dist`
    * **What it does:** This is the final step. It runs `electron-builder`, which takes the contents of the `build` directory, packages them with the Electron runtime, and creates a distributable, portable `.exe` file (for Windows) inside a final `dist` folder.
