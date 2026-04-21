import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline
import nltk

def download_nltk_resources():
    try:
        nltk.download('vader_lexicon', quiet=True)
    except Exception as e:
        print(f"Error while loading NLTK vader_lexicon: {e}")

download_nltk_resources()

try:
    vader = SentimentIntensityAnalyzer()
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    print(f"Error while initializing VADER or BERT: {e}")
    raise

def vader_sentiment(text):                    # VADER
    try:
        scores = vader.polarity_scores(str(text))
        compound = scores['compound']
        if compound >= 0.05:
            return 'positive', compound
        elif compound <= -0.05:
            return 'negative', compound
        else:
            return 'neutral', compound
    except Exception as e:
        print(f"Error while running VADER sentiment analysis: {e}")
        return 'neutral', 0.0

def bert_sentiment(text):                    # BERT
    try:
        result = sentiment_pipeline(str(text), truncation=True, max_length=512)
        label = result[0]['label'].lower()
        score = result[0]['score']
        if 0.4 <= score <= 0.6:
            return 'neutral', score
        return label, score
    except Exception as e:
        print(f"Error while running BERT sentiment analysis: {e}")
        return 'neutral', 0.5

def normalize_bert_score(label, score):                 # Chuẩn hóa bert_score về [-1, 1]
    try:
        if label == 'positive':
            return score
        elif label == 'negative':
            return -score
        else:
            return score - 0.5  
    except Exception as e:
        print(f"Error while normalizing BERT score: {e}")
        return 0.0

def combine_sentiment(vader_score, bert_score_normalized):                  # (70% BERT, 30% VADER)
    try:
        weight_vader = 0.3
        weight_bert = 0.7
        combined_score = (weight_vader * vader_score + weight_bert * bert_score_normalized)
        if combined_score >= 0.05:
            return 'positive', combined_score
        elif combined_score <= -0.05:
            return 'negative', combined_score
        else:
            return 'neutral', combined_score
    except Exception as e:
        print(f"Error while combining sentiment: {e}")
        return 'neutral', 0.0

def perform_sentiment_analysis(input_file, output_file):
    try:
        df = pd.read_csv(input_file)

        df['vader_sentiment'], df['vader_score'] = zip(*df['content'].apply(vader_sentiment))
        df['bert_sentiment'], df['bert_score'] = zip(*df['content'].apply(bert_sentiment))
        df['bert_score_normalized'] = df.apply(lambda x: normalize_bert_score(x['bert_sentiment'], x['bert_score']), axis=1)

        df['combined_sentiment'], df['combined_score'] = zip(*df.apply(lambda x: combine_sentiment(x['vader_score'], x['bert_score_normalized']), axis=1))

        df['is_positive'] = df['bert_score'].apply(lambda x: x > 0.8 if x is not None else False)

        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Sentiment Analysis results have been saved to '{output_file}'")
        print(df[['content', 'vader_sentiment', 'vader_score', 'bert_sentiment', 'bert_score', 'combined_sentiment', 'combined_score', 'is_positive']].head())
        return df
    except Exception as e:
        print(f"Error during the sentiment analysis process: {e}")
        return None
