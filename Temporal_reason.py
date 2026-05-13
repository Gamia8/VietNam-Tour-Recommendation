import pandas as pd

def get_season(month):                      
    try:
        if month in [1, 2, 3]:
            return 'spring'
        elif month in [4, 5, 6]:
            return 'summer'
        elif month in [7, 8, 9]:
            return 'autumn'
        elif month in [10, 11, 12]:
            return 'winter'
        return 'unknown'
    except Exception as e:
        print(f"Error while assigning season: {e}")
        return 'unknown'

def perform_season_analysis(input_file, output_file, season_output, location_season_output):
    try:
        df = pd.read_csv(input_file)

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        invalid_dates = df['date'].isna().sum()
        print(f"Invalid number of days {invalid_dates}")
        df['season'] = df['date'].dt.month.apply(get_season)
  
        season_sentiment = df.groupby('season').agg({'vader_score': 'mean', 'bert_score': 'mean', 'combined_score': 'mean', 'is_positive': 'mean'}).reset_index()
        location_season_sentiment = df.groupby(['location', 'season']).agg({'vader_score': 'mean', 'bert_score': 'mean', 'combined_score': 'mean', 'is_positive': 'mean', 'rating': lambda x: pd.to_numeric(x.str.split().str[0], errors='coerce').mean()}).reset_index()

        df.to_csv(output_file, index=False, encoding='utf-8')
        season_sentiment.to_csv(season_output, index=False, encoding='utf-8')
        location_season_sentiment.to_csv(location_season_output, index=False, encoding='utf-8')
        
        print(f"Data with 'season' column has been saved to '{output_file}'")
        print(f"Seasonal sentiment trends have been saved to '{season_output}'")
        print(f"Sentiment trends by location and season have been saved to '{location_season_output}'")
        print("Seasonal sentiment trends:")
        print(season_sentiment)
        print("\nSentiment trends by location and season:")
        print(location_season_sentiment)
        
        return df, season_sentiment, location_season_sentiment
    except Exception as e:
        print(f"Error during season analysis {e}")
        return None, None, None