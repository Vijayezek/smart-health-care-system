from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from nltk.stem import PorterStemmer
import nltk
import re
import pickle

try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

stemmer = PorterStemmer()

def preprocess_symptoms(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [stemmer.stem(word) for word in words if word not in stop_words]
    return ' '.join(words)

def train_disease_predictor():
    training_data = [
        ("fever high temperature body hot", "Fever"),
        ("headache pain head migraine", "Headache"),
        ("cough dry cough wet cough", "Cough"),
        ("cold runny nose sneezing", "Cold"),
        ("tired fatigue weakness sleepy", "Fatigue"),
        ("sick stomach nausea vomit", "Nausea"),
        ("dizzy light headed vertigo", "Dizziness"),
        ("body pain muscle ache joint pain", "Body Pain"),
        ("fever headache body pain", "Fever"),
        ("cold cough runny nose", "Cold"),
        ("headache nausea dizziness", "Headache"),
        ("fatigue body pain weakness", "Fatigue"),
    ]
    
    texts = [preprocess_symptoms(text) for text, _ in training_data]
    diseases = [disease for _, disease in training_data]
    
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X, diseases)
    
    return model, vectorizer

model, vectorizer = train_disease_predictor()

def predict_disease(symptoms_text):
    processed_text = preprocess_symptoms(symptoms_text)
    text_vector = vectorizer.transform([processed_text])
    prediction = model.predict(text_vector)[0]
    return prediction
