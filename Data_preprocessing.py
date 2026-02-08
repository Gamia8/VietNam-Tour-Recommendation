import pandas as pd
import spacy
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.phrases import Phrases, Phraser
import nltk
import json
from multiprocessing import Pool
from pywsd.lesk import simple_lesk
from Topic_LDA import find_optimal_topics

def download_nltk_resources():
    resources = ['stopwords', 'wordnet', 'punkt', 'punkt_tab', 'averaged_perceptron_tagger_eng']
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Error while loading NLTK resource {resource}: {e}")

download_nltk_resources()

try:
    nlp = spacy.load('en_core_web_lg')
except Exception as e:
    print(f"Error while loading the spaCy model: {e}")
    raise

stop_words = set(stopwords.words('english')).union({'place', 'visit', 'vietnam', 'tourist'})

def preprocess_text(text):                      # Tiền xử lý
    if not isinstance(text, str):
        text = str(text)
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if token.text.lower() not in stop_words and token.is_alpha]
    return tokens

def parallel_preprocess(texts):                         # Song song hóa tiền xử lý
    try:
        with Pool() as pool:
            return pool.map(preprocess_text, texts)
    except Exception as e:
        print(f"Error during parallel processing: {e}")
        return [preprocess_text(text) for text in texts]  

def apply_lda(texts, num_topics):                           # Topic Modeling (LDA)
    try:
        dictionary = corpora.Dictionary(texts)
        dictionary.filter_extremes(no_below=10, no_above=0.3)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=20, alpha='auto', beta='auto', iterations=400, random_state=42)
        topics = lda_model.print_topics()
        return topics, lda_model, dictionary, corpus
    except Exception as e:
        print(f"Error while running LDA: {e}")
        return [], None, None, None

def disambiguate_multiple_words(sentence, words=["bay", "cave", "beach", "river"]):                     # Word Sense Disambiguation
    senses = {}
    sentence_lower = sentence.lower() if isinstance(sentence, str) else str(sentence).lower()
    for word in words:
        if word in sentence_lower:
            try:
                sense = simple_lesk(sentence, word, pos='n')
                senses[word] = sense.definition() if sense else f"No sense found for {word}"
            except Exception as e:
                senses[word] = f"Error processing {word}: {e}"
        else:
            senses[word] = f"No {word} in text"
    return json.dumps(senses)

def perform_text_mining(input_file, output_file):
    try:
        df = pd.read_csv(input_file)
        optimal_num_topics = find_optimal_topics(df)  

        df['processed_text'] = parallel_preprocess(df['content'])

        bigram = Phrases(df['processed_text'], min_count=5, threshold=100)
        bigram_phraser = Phraser(bigram)
        df['processed_text'] = [bigram_phraser[text] for text in df['processed_text']]

        lda_topics, lda_model, dictionary, corpus = apply_lda(df['processed_text'].tolist(), optimal_num_topics)  # <-- Truyền optimal_num_topics vào đây
        print("LDA Topics:", lda_topics)

        df['senses'] = df['content'].apply(disambiguate_multiple_words)
 
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Results have been saved to '{output_file}'")
        return df
    except Exception as e:
        print(f"Error during the process: {e}")
        return None
