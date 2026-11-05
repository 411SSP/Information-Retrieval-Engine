import os
import glob

class DocumentLoader:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path
        self.doc_map = {}  # doc_id -> filename

    def load_documents(self):
        # Load all .txt files
        search_pattern = os.path.join(self.corpus_path, '*.txt')
        files = glob.glob(search_pattern)
        
        documents = {} # doc_id -> content
        
        for doc_id, filepath in enumerate(sorted(files), start=1):
            filename = os.path.basename(filepath)
            self.doc_map[doc_id] = filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                documents[doc_id] = content
                
        return documents

    def get_filename(self, doc_id):
        return self.doc_map.get(doc_id)
