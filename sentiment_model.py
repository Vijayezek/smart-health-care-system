from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.stem import PorterStemmer
import nltk
import re
import pickle
import os

try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

stemmer = PorterStemmer()

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [stemmer.stem(word) for word in words if word not in stop_words]
    return ' '.join(words)

def train_sentiment_model():
    training_data = [
        ("excellent service very helpful", "positive"),
        ("great experience thank you", "positive"),
        ("wonderful treatment very satisfied", "positive"),
        ("good doctor helpful staff", "positive"),
        ("amazing care well organized", "positive"),
        ("poor service not helpful", "negative"),
        ("bad experience terrible", "negative"),
        ("worst treatment ever", "negative"),
        ("disappointed with service", "negative"),
        ("not satisfied at all", "negative"),
        ("okay service average", "neutral"),
        ("normal experience nothing special", "neutral"),
    ]
    
    texts = [preprocess_text(text) for text, _ in training_data]
    labels = [label for _, label in training_data]
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    
    model = MultinomialNB()
    model.fit(X, labels)
    
    return model, vectorizer

model, vectorizer = train_sentiment_model()

def analyze_sentiment(text):
    processed_text = preprocess_text(text)
    text_vector = vectorizer.transform([processed_text])
    prediction = model.predict(text_vector)[0]
    return prediction
