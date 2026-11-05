from nltk.stem import PorterStemmer
import nltk

try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

stemmer = PorterStemmer()

def normalize(tokens):
    # Remove stopwords and apply stemming
    normalized_tokens = []
    for token in tokens:
        if token not in stop_words:
            stemmed = stemmer.stem(token)
            normalized_tokens.append(stemmed)
    return normalized_tokens
