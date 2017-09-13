import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
#from dmia.gradient_check import *
from dmia.classifiers import LogisticRegression

if __name__ == '__main__':
    train_df = pd.read_csv('./data/train.csv')
    print train_df.shape
    print train_df.Prediction.value_counts(normalize=True)
    review_summaries = list(train_df['Reviews_Summary'].values)
    review_summaries = [l.lower() for l in review_summaries]
    print review_summaries[:5]
    vectorizer = TfidfVectorizer()
    tfidfed = vectorizer.fit_transform(review_summaries)
    X = tfidfed
    y = train_df.Prediction.values
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42)
    X_train_sample = X_train[:10000]
    y_train_sample = y_train[:10000]
    clf = LogisticRegression()
    clf.w = np.random.randn(X_train_sample.shape[1] + 1) * 2
    loss, grad = clf.loss(LogisticRegression.append_biases(X_train_sample), y_train_sample, 0.0)