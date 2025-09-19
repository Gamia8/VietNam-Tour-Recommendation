# Vietnam Tourism Recommendation System

## Overview

This project develops an advanced hybrid tourism recommendation system for destinations in Vietnam. The system integrates content-based filtering (using sentiment analysis and natural language processing from user reviews) with collaborative filtering (employing the SVD algorithm for historical user ratings predictions). Users can input natural language queries, such as "I want to climb a mountain in spring," allowing the system to extract preferences (locations, activities, seasons) and suggest the most suitable destinations with scores, addresses, and interactive maps.

Data is sourced from Google Reviews, categorized into 11 types (bays, caves, historical relics, pagodas, lakes, waterfalls, rivers, jungles, beaches, mountains, and islands). Beyond personalized recommendations, the system supports sentiment analysis, seasonal trends, and activity extraction, aiding users in effective travel planning. The project emphasizes accuracy, scalability, and a user-friendly interface, catering to both end-users and developers.

Key benefits:
- Highly personalized recommendations based on real user data.
- Integrated visualization with Plotly maps and result tables.
- Robust error handling for invalid queries or mismatches.

## Project Structure

The project is organized with separate Python scripts and a Jupyter Notebook to ensure modularity and maintainability. Below is a detailed description of each key file:

- **`main.ipynb`**: The central Jupyter Notebook that manages the entire workflow. It integrates and calls functions from other scripts to execute the process from data collection to final recommendations. The file includes sections for data crawling, location addition, preprocessing, sentiment analysis, seasonal reasoning, activity extraction, and Streamlit integration for the user interface.

- **`add_location.py`**: Responsible for adding latitude and longitude information to locations using geographic APIs or manual data to ensure high accuracy. Input: `data_crawl.csv`; Output: `data.csv`.

- **`app.py`**: The main Streamlit file to run the interactive web interface. It provides a form for users to input their name and queries, displaying results as a top 5 table and an interactive map. This file can be run independently for demo purposes.

- **`crawl_data.py`**: Handles data scraping from Google Reviews, including place names, ratings, reviews, and dates. Supports a configurable limit on the number of reviews (e.g., up to 200 reviews per location). Output: `data_crawl.csv`.

- **`data_preprocessing.py`**: Performs text preprocessing, including cleaning, noise removal, tokenization, and topic modeling integration from `topic_lda.py`. Ensures data readiness for subsequent analysis steps. Input: `data.csv`; Output: `data_clear.csv`.

- **`extraction_event.py`**: Extracts activities related to each location from review content using NLP to identify relevant verbs and nouns (e.g., "climbing," "swimming"). Also generates an activity frequency file. Input: `data_season.csv`; Output: `data_recommender.csv` and `data_activity_freq.csv`.

- **`latitude_longitude.py`**: Manages and processes latitude and longitude data, supporting `add_location.py` in geographic lookup and updates.

- **`place_crawl.py`**: Contains a hardcoded or file-loaded list of locations to scrape, covering approximately 300 Vietnamese tourist spots categorized by type.

- **`recommender.py`**: Implements the core recommendation algorithm, blending content scores (sentiment + seasonality + activities) and collaborative scores (SVD from the Surprise library). Uses flexible weighting and normalization for final scoring.

- **`sentiment_bert_vader.py`**: Performs sentiment analysis on user reviews using BERT and VADER models to compute combined scores (`combined_score`, `is_positive`). Input: `data_clear.csv`; Output: `data_sentiment.csv`.

- **`temporal_season.py`**: Extracts seasonal information from review dates and content, analyzing trends across seasons (spring, summer, autumn, winter). Generates seasonal and location-season analysis files. Input: `data_sentiment.csv`; Output: `data_season.csv`, `data_season_analysis.csv`, `data_location_season_analysis.csv`.

- **`topic_lda.py`**: Computes the optimal number of topics and applies the LDA (Latent Dirichlet Allocation) model for topic modeling, integrated into `data_preprocessing.py` to enhance preprocessing quality.

## Workflow

The system follows a linear process, executable via `main.ipynb` or individual scripts:

1. **Data Collection**: `crawl_data.py` scrapes data from Google Reviews based on the list from `place_crawl.py`, with a configurable review limit to avoid overload.

2. **Geographic Location Addition**: `add_location.py` and `latitude_longitude.py` append latitude and longitude, enabling map visualization.

3. **Data Preprocessing**: `data_preprocessing.py` cleans data and integrates `topic_lda.py` for topic modeling, ensuring noise-free input.

4. **Sentiment Analysis**: `sentiment_bert_vader.py` evaluates positive/negative sentiments from review content.

5. **Seasonal Analysis**: `temporal_season.py` identifies seasonal trends to optimize recommendations.

6. **Activity Extraction**: `extraction_event.py` determines popular activities at each location.

7. **Recommendation**: `recommender.py` calculates hybrid scores and ranks top suggestions.

8. **User Interface and Display**: `app.py` provides a UI for user interaction and result visualization.

## Installation

To set up the project, please follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Gamia8/VietNam-Tour-Recommendation.git
   cd vietnam-tourism-recommendation-system
   ```

2. **Set Up a Virtual Environment** (recommended to avoid library conflicts):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Required Libraries** (requires Python 3.11 or higher):
   ```bash
   pip install pandas numpy streamlit plotly spacy surprise scikit-learn nltk transformers torch
   ```

4. **Download Models and Additional Data**:
   - SpaCy model: `python -m spacy download en_core_web_lg`
   - NLTK data: Run in Python:
     ```python
     import nltk
     nltk.download('wordnet')
     ```

5. **Prepare Data**: Ensure output CSV files (e.g., `data_crawl.csv`) are generated or downloaded as needed.

## Usage

1. **Run via Jupyter Notebook**:
   - Open `main.ipynb`:
     ```bash
     jupyter notebook
     ```
   - Execute cells sequentially to run the full process. For example, input a query and view recommendations directly in the notebook.

2. **Run the Streamlit Interface**:
   ```bash
   streamlit run app.py
   ```
   - Access `http://localhost:8501` in your browser.
   - Enter your name and a query (e.g., "I want to visit a beach in summer").
   - View results: A top 5 table with details (name, address, score) and an interactive map.

## Notes and Limitations

- **Data Quality**: Relies on Google Reviews data; inaccuracies may occur if the source data is flawed.
- **Language Support**: Currently supports English queries only; Vietnamese support may be added in the future.
- **Blocked File**: The `data_preprocessing.py` file may be blocked due to filter settings; please check and unblock if necessary.
- **Environment**: No internet access during code execution; all libraries must be imported directly.
- **Scalability**: For large datasets, consider optimizing SVD or switching to a database instead of CSV files.

## Contributing

We warmly welcome contributions to enhance the project! To contribute:
- Fork the repository on GitHub.
- Create a new branch for your changes.
- Commit and push your changes, then submit a Pull Request with a detailed description.
- Report bugs or suggest features via the Issues section on GitHub.

## Contact

For questions, feedback, or technical support, please reach out via:
- **GitHub Issues**: Open a new issue at [https://github.com/Gamia8/VietNam-Tour-Recommendation.git/issues](https://github.com/Gamia8/VietNam-Tour-Recommendation.git/issues) for public discussion.
- **Email**: Send an email to [tranthigam27072004@gmail.com](mailto:tranthigam27072004@gmail.com) with a clear subject line (e.g., "Support for Vietnam Tourism Recommendation System").
- **GitHub Profile**: Follow and contact us via the GitHub account [Gamia8](https://github.com/Gamia8) or related platforms.

We commit to responding within 48 business hours.

## License

This project is licensed under the MIT License. See the `LICENSE` file for full details. You are free to use, modify, and distribute the source code, provided copyright notices are retained.

---

### Notes
- The content is written in a professional tone, with detailed explanations for each component and step.
- The date and time (11:18 AM +07, Saturday, August 30, 2025) are reflected in the context but not explicitly mentioned unless requested. Let me know if you need adjustments!