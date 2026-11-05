import os
import json
from src.document_loader import DocumentLoader
from src.tokenizer import tokenize
from src.normalizer import normalize
from src.indexer import InvertedIndex

def build_index(corpus_path, index_path):
    loader = DocumentLoader(corpus_path)
    documents = loader.load_documents()
    
    index = InvertedIndex()
    index.total_docs = len(documents)
    
    for doc_id, content in documents.items():
        tokens = tokenize(content)
        normalized_tokens = normalize(tokens)
        
        for pos, term in enumerate(normalized_tokens):
            index.add_term(term, doc_id, pos)
            
    index.save(index_path)
    
    doc_map_path = os.path.join(index_path, 'doc_map.json')
    with open(doc_map_path, 'w', encoding='utf-8') as f:
        json.dump(loader.doc_map, f, indent=4)
        
    print(f"Index built successfully for {len(documents)} documents.")
    
if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corpus_path = os.path.join(base_dir, 'documents')
    index_path = os.path.join(base_dir, 'index')
    build_index(corpus_path, index_path)
