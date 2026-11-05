from src.tokenizer import tokenize
from src.normalizer import normalize

def parse_query(query_string):
    # For a simple search engine, we'll just treat everything as an AND query
    # if no explicit operators are provided, or we can handle basic AND/OR
    # Here we'll do a simple tokenization and normalization of the query
    
    tokens = tokenize(query_string)
    normalized = normalize(tokens)
    
    return normalized
