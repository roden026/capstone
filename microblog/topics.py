import os
import numpy as np
import pandas as pd
import re, nltk, spacy, gensim
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords

# Sklearn
from sklearn.decomposition import LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import GridSearchCV
from pprint import pprint
from sklearn.externals import joblib

# Plotting tools
import pyLDAvis
import pyLDAvis.sklearn
import matplotlib.pyplot as plt

# Show top n keywords for each topic
def show_topics(vectorizer, lda_model, n_words=20):
    keywords = np.array(vectorizer.get_feature_names())
    topic_keywords = []
    for topic_weights in lda_model.components_:
        top_keyword_locs = (-topic_weights).argsort()[:n_words]
        topic_keywords.append(keywords.take(top_keyword_locs))
    return topic_keywords

# function to take in a new review and generate topics for it. wrap text in [] when calling
def predict_topic(text):

    # load models
    best_lda_model = joblib.load('lda.pkl')
    vectorizer = joblib.load('vectorizer.pkl')

    topic_keywords = show_topics(vectorizer=vectorizer, lda_model=best_lda_model, n_words=15)

    # Topic Keywords Dataframe
    df_topic_keywords = pd.DataFrame(topic_keywords)
    df_topic_keywords.columns = ['Word '+str(i) for i in range(df_topic_keywords.shape[1])]
    df_topic_keywords.index = ['Topic '+str(i) for i in range(df_topic_keywords.shape[0])]

    # generate tokens
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = pd.DataFrame(text)[0].apply(tokenizer.tokenize)

    # load stop words
    stops = set(stopwords.words('english'))

    # remove stops and make all same case
    text_clean = tokens.apply(lambda x: [word.lower() for word in x if word not in stops])

    # remove punctuation and numbers
    text_clean = text_clean.apply(lambda x: [word for word in x if re.search('^[a-zA-Z]+', word)])

    # Lemmatizer
    lemmatizer = nltk.WordNetLemmatizer()

    # lemmatize
    text_clean = text_clean.apply(lambda x: [lemmatizer.lemmatize(word) for word in x])
    text_ready =  text_clean.apply(lambda x: ' '.join(x))

    # Step 3: Vectorize transform
    mytext = vectorizer.transform(text_ready)

    # Step 4: LDA Transform
    topic_probability_scores = best_lda_model.transform(mytext)
    topic = df_topic_keywords.iloc[np.argmax(topic_probability_scores), :].values.tolist()
    return topic, topic_probability_scores
