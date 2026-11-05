import json
import os
from src.wildcard_processor import PermutermIndex

class InvertedIndex:
    def __init__(self):
        # postings: term -> {doc_id: [pos1, pos2, ...]}
        self.postings = {}
        self.permuterm = PermutermIndex()
        self.total_docs = 0

    def add_term(self, term, doc_id, pos):
        if term not in self.postings:
            self.postings[term] = {}
            self.permuterm.add_term(term)
            
        if doc_id not in self.postings[term]:
            self.postings[term][doc_id] = []
            
        self.postings[term][doc_id].append(pos)

    def get_postings(self, term):
        # returns {doc_id: [pos1, pos2, ...]}
        return self.postings.get(term, {})
        
    def get_dictionary(self):
        return list(self.postings.keys())
        
    def save(self, index_path):
        dictionary_path = os.path.join(index_path, 'dictionary', 'dict.json')
        postings_path = os.path.join(index_path, 'postings', 'postings.json')
        permuterm_path = os.path.join(index_path, 'permuterm', 'permuterm.json')
        
        os.makedirs(os.path.dirname(dictionary_path), exist_ok=True)
        os.makedirs(os.path.dirname(postings_path), exist_ok=True)
        os.makedirs(os.path.dirname(permuterm_path), exist_ok=True)
        
        dictionary = {term: len(docs) for term, docs in self.postings.items()}
        
        with open(dictionary_path, 'w', encoding='utf-8') as f:
            json.dump({'total_docs': self.total_docs, 'dictionary': dictionary}, f, indent=4)
            
        with open(postings_path, 'w', encoding='utf-8') as f:
            json.dump(self.postings, f, indent=4)
            
        with open(permuterm_path, 'w', encoding='utf-8') as f:
            json.dump(self.permuterm.index, f, indent=4)

    def load(self, index_path):
        dictionary_path = os.path.join(index_path, 'dictionary', 'dict.json')
        postings_path = os.path.join(index_path, 'postings', 'postings.json')
        permuterm_path = os.path.join(index_path, 'permuterm', 'permuterm.json')
        
        if os.path.exists(dictionary_path):
            with open(dictionary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.total_docs = data.get('total_docs', 0)
                
        if os.path.exists(postings_path):
            with open(postings_path, 'r', encoding='utf-8') as f:
                loaded_postings = json.load(f)
                self.postings = {term: {int(doc_id): positions for doc_id, positions in docs.items()} for term, docs in loaded_postings.items()}
                
        if os.path.exists(permuterm_path):
            with open(permuterm_path, 'r', encoding='utf-8') as f:
                self.permuterm.index = json.load(f)
