# Imports
import pandas as pd
import numpy as np
import os
import nltk
from nltk.corpus import stopwords
import re

from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import LinearSVC
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from textblob import TextBlob, Word

'''
Validate and condense import calls
'''



# takes airline review(s) and returns the tfidf.
# can be used for text only prediction or as input into full model
def make_tfidf(reviews):
    # generate tokens
    tokens = reviews.apply(lambda x: x.split(" "))

    #load stop words - basic english dictionary. Possible area for improvement
    stops = set(stopwords.words('english'))

    # remove stops, numbers and symbols
    clean = tokens.apply(lambda x: [word for word in x if word not in stops])
    clean = clean.apply(lambda x: [word for word in x if re.search('^[a-zA-Z]+', word)])

    # Lemmatizer
    lemmatizer = nltk.WordNetLemmatizer()
    clean = clean.apply(lambda x: [lemmatizer.lemmatize(word) for word in x])

    # join tokes back into strings with spaces
    ready =  clean.apply(lambda x: ' '.join(x))

    # load the model
    tfidf = joblib.load('tfidf.pkl')

    # apply the loaded tfidf to the processed data and convert the results to a DF
    X = tfidf.transform(ready)
    X = pd.DataFrame(X.toarray())

    return X

# take review text in a series and return sentiment scores. Only using 1 sentiment score but could incorporate others.
def get_sentiment(reviews):

    # create a text blob column
    blob = reviews.apply(lambda x: TextBlob(x))

    polarity = [sent.sentiment.polarity for sent in blob]

    return polarity

# predict using only the review as an input. Use logreg_tfidf_and_sent.pkl
def text_only_predict(review):

    # turn review into TFIDF record
    X = make_tfidf(review)

    # add on the polarity and text length
    X['polarity'] = get_sentiment(review)
    X['text_len'] = len(review)

    # load the model
    logreg = joblib.load('logreg_tfidf_and_sent.pkl')

    # predict recommendation and return prediction
    pred = logreg.predict(X)
    pred_prob = logreg.predict_proba(X)

    return pred, pred_prob

# predict using full model. Note df is assumed to be the result of a submitted SurveyForm.
def predict_recommend(df):

    # turn review into TFIDF record
    X = pd.concat([df, make_tfidf(df.content)], axis=1)

    # add on the polarity and text length
    X['polarity'] = get_sentiment(df.content)
    X['text_len'] = len(df.content)

    # populate dummies for cabin flow
    if df.cabin_flown.iloc[0] == "Business Class":
        X['cabin_flown_Business Class'] = 1
    else:
        X['cabin_flown_Business Class'] = 0

    if df.cabin_flown.iloc[0] == "Economy Class":
        X['cabin_flown_Economy Class'] = 1
    else:
        X['cabin_flown_Economy Class'] = 0

    if df.cabin_flown.iloc[0] == "First Class":
        X['cabin_flown_First Class'] = 1
    else:
        X['cabin_flown_First Class'] = 0

    if df.cabin_flown.iloc[0] == "Premium Economy":
        X['cabin_flown_Premium Economy'] = 1
    else:
        X['cabin_flown_Premium Economy'] = 0

    # populate dummies for type traveller
    if df.type_traveller.iloc[0] == "Business":
        X['type_traveller_Business'] = 1
    else:
        X['type_traveller_Business'] = 0

    if df.type_traveller.iloc[0] == "Couple Leisure":
        X['type_traveller_Couple Leisure'] = 1
    else:
        X['type_traveller_Couple Leisure'] = 0

    if df.type_traveller.iloc[0] == "Family Leisure":
        X['type_traveller_Family Leisure'] = 1
    else:
        X['type_traveller_Family Leisure'] = 0

    if df.type_traveller.iloc[0] == "Solo Leisure":
        X['type_traveller_Solo Leisure'] = 1
    else:
        X['type_traveller_Solo Leisure'] = 0

    # prep prediction input
    X.drop(columns=['content', 'type_traveller', 'cabin_flown', 'inflight_entertainment_rating', 'ground_service_rating','wifi_connectivity_rating'], inplace=True)

    # load the model
    logreg = joblib.load('logreg.pkl')

    # predict recommendation and return prediction
    pred = logreg.predict(X)
    pred_prob = logreg.predict_proba(X)

    return pred, pred_prob
