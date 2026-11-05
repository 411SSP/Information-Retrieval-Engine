import re

def tokenize(text):
    # Convert to lowercase and split on non-alphanumeric characters
    # Returns a list of tokens
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens
