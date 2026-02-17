import pandas as pd
import spacy
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.phrases import Phrases, Phraser
from gensim.models.coherencemodel import CoherenceModel
import nltk
from multiprocessing import Pool

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

nlp = spacy.load('en_core_web_lg')
stop_words = set(stopwords.words('english')).union({'place', 'visit', 'vietnam', 'tourist'})

def preprocess_text(text):                      # Tiền xử lý 
    if not isinstance(text, str):
        text = str(text)
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if token.text.lower() not in stop_words and token.is_alpha]
    return tokens if len(tokens) >= 5 else [] 

def parallel_preprocess(texts):
    with Pool() as pool:
        return pool.map(preprocess_text, texts)

def find_optimal_topics(df, input_file='data.csv', start=3, limit=21, step=1):
    if df is None:
        df = pd.read_csv(input_file)

    df['processed_text'] = parallel_preprocess(df['content'])
    df = df[df['processed_text'].apply(len) > 0]

    bigram = Phrases(df['processed_text'], min_count=5, threshold=100)
    bigram_phraser = Phraser(bigram)
    df['processed_text'] = [bigram_phraser[text] for text in df['processed_text']]

    dictionary = corpora.Dictionary(df['processed_text'])
    dictionary.filter_extremes(no_below=10, no_above=0.3)
    corpus = [dictionary.doc2bow(text) for text in df['processed_text']]
    
    # Tính coherence score
    def compute_coherence_values(corpus, dictionary, texts, start, limit, step):
        coherence_values = []
        model_list = []
        for num_topics in range(start, limit, step):
            lda_model = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, passes=30, alpha='symmetric', eta=0.01, iterations=400, random_state=42)
            model_list.append(lda_model)
            coherencemodel = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
            coherence_values.append(coherencemodel.get_coherence())
            print(f"Num Topics: {num_topics}, Coherence Score: {coherence_values[-1]}")
        return model_list, coherence_values
    
    model_list, coherence_values = compute_coherence_values(corpus=corpus, dictionary=dictionary, texts=df['processed_text'].tolist(), start=start, limit=limit, step=step)

    optimal_num_topics = start + coherence_values.index(max(coherence_values))
    print(f"Optimal number of topics: {optimal_num_topics} (Coherence Score: {max(coherence_values)})")
    
    return optimal_num_topics 