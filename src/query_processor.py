import os
import json
import math
import re
from src.indexer import InvertedIndex
from src.query_parser import parse_query
from src.tokenizer import tokenize
from src.normalizer import normalize
from src.spelling_corrector import SpellingCorrector

class QueryProcessor:
    def __init__(self, index_path):
        self.index = InvertedIndex()
        self.index.load(index_path)
        self.spelling_corrector = SpellingCorrector(self.index.get_dictionary())
        
        self.corpus_path = os.path.join(os.path.dirname(index_path), 'documents')
        
        self.doc_map = {}
        doc_map_path = os.path.join(index_path, 'doc_map.json')
        if os.path.exists(doc_map_path):
            with open(doc_map_path, 'r', encoding='utf-8') as f:
                loaded_map = json.load(f)
                self.doc_map = {int(k): v for k, v in loaded_map.items()}

    def get_snippet(self, filename, raw_query, query_terms):
        filepath = os.path.join(self.corpus_path, filename)
        if not os.path.exists(filepath):
            return "Content not available."
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        clean_full_phrase = raw_query.strip(' "')
        
        # 1. Try finding full combined phrase first
        match_pos = content.lower().find(clean_full_phrase.lower())
        
        # 2. Fallback to first matching individual term
        if match_pos == -1:
            for term in query_terms:
                pos = content.lower().find(term.lower())
                if pos != -1 and (match_pos == -1 or pos < match_pos):
                    match_pos = pos
                    
        if match_pos != -1:
            start = max(0, match_pos - 60)
            end = min(len(content), match_pos + 140)
            snippet = ("..." if start > 0 else "") + content[start:end] + ("..." if end < len(content) else "")
        else:
            snippet = content[:200] + ("..." if len(content) > 200 else "")
            
        # Highlight full phrase together if present in snippet
        if len(clean_full_phrase) > 1 and clean_full_phrase.lower() in snippet.lower():
            pattern = re.compile(re.escape(clean_full_phrase), re.IGNORECASE)
            snippet = pattern.sub(lambda m: f'<mark class="snippet-highlight">{m.group(0)}</mark>', snippet)
        else:
            # Highlight individual terms
            for term in query_terms:
                if len(term) > 1:
                    pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
                    snippet = pattern.sub(lambda m: f'<mark class="snippet-highlight">{m.group(0)}</mark>', snippet)
                
        return snippet

    def process_query(self, query_string, model='tfidf'):
        is_phrase = query_string.strip().startswith('"') and query_string.strip().endswith('"')
        
        process_log = []
        process_log.append({'step': '1. Original Query', 'detail': f"'{query_string}' (Model: {model}) {'[Exact Phrase]' if is_phrase else ''}"})
        
        clean_query = query_string.strip(' "')
        raw_tokens = clean_query.lower().split()
        process_log.append({'step': '2. Tokenization', 'detail': str(raw_tokens)})
        
        final_terms = []
        
        for token in raw_tokens:
            if '*' in token:
                process_log.append({'step': f'3. Wildcard detected for "{token}"', 'detail': 'Looking up in Permuterm index...'})
                matches = self.index.permuterm.get_matches(token)
                process_log.append({'step': f'3a. Wildcard matches for "{token}"', 'detail': str(matches)})
                if matches:
                    if is_phrase:
                        final_terms.append(matches[0])
                    else:
                        final_terms.extend(matches)
            else:
                normalized = normalize([token])
                if not normalized:
                    continue
                term = normalized[0]
                
                corrected_term = self.spelling_corrector.correct(term)
                if term != corrected_term:
                    process_log.append({'step': f'4. Spelling Correction for "{term}"', 'detail': f'Corrected to "{corrected_term}"'})
                    final_terms.append(corrected_term)
                else:
                    final_terms.append(term)
                    
        process_log.append({'step': '5. Final Query Terms', 'detail': str(final_terms)})
        
        if not final_terms:
            return [], process_log
            
        results = []
        
        if is_phrase:
            current_docs = self.index.get_postings(final_terms[0]) # {doc_id: [pos1, pos2]}
            
            for i in range(1, len(final_terms)):
                term = final_terms[i]
                next_docs = self.index.get_postings(term)
                
                intersected_docs = {}
                for doc_id in current_docs:
                    if doc_id in next_docs:
                        pos_list1 = current_docs[doc_id]
                        pos_list2 = next_docs[doc_id]
                        
                        valid_positions = []
                        p1_idx, p2_idx = 0, 0
                        
                        while p1_idx < len(pos_list1) and p2_idx < len(pos_list2):
                            p1 = pos_list1[p1_idx]
                            p2 = pos_list2[p2_idx]
                            
                            if p2 == p1 + 1:
                                valid_positions.append(p2)
                                p1_idx += 1
                                p2_idx += 1
                            elif p2 > p1 + 1:
                                p1_idx += 1
                            else:
                                p2_idx += 1
                                
                        if valid_positions:
                            intersected_docs[doc_id] = valid_positions
                            
                current_docs = intersected_docs
                if not current_docs:
                    break
                    
            for doc_id in sorted(list(current_docs.keys())):
                filename = self.doc_map.get(doc_id, f"Unknown {doc_id}")
                snippet = self.get_snippet(filename, clean_query, raw_tokens)
                results.append({
                    'doc_id': doc_id,
                    'filename': filename,
                    'snippet': snippet,
                    'score': 1.0
                })
            process_log.append({'step': '6. Positional Phrase Intersection', 'detail': f'Found {len(results)} exact phrase match(es)'})
            
        elif model == 'boolean':
            result_docs = None
            for term in final_terms:
                postings = set(self.index.get_postings(term).keys())
                if result_docs is None:
                    result_docs = postings
                else:
                    result_docs = result_docs.intersection(postings)
                    
                if not result_docs:
                    break
                    
            if result_docs:
                for doc_id in sorted(list(result_docs)):
                    filename = self.doc_map.get(doc_id, f"Unknown {doc_id}")
                    snippet = self.get_snippet(filename, clean_query, raw_tokens)
                    results.append({
                        'doc_id': doc_id,
                        'filename': filename,
                        'snippet': snippet,
                        'score': 1.0
                    })
            process_log.append({'step': '6. Boolean Intersection', 'detail': f'Found {len(results)} document(s)'})
            
        elif model == 'tfidf':
            scores = {}
            N = self.index.total_docs
            
            for term in final_terms:
                postings = self.index.get_postings(term)
                df = len(postings)
                if df == 0:
                    continue
                    
                idf = math.log10(N / df)
                
                for doc_id, positions in postings.items():
                    tf = len(positions)
                    wt = (1 + math.log10(tf)) * idf
                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += wt
                    
            ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            for doc_id, score in ranked_docs:
                filename = self.doc_map.get(doc_id, f"Unknown {doc_id}")
                snippet = self.get_snippet(filename, clean_query, raw_tokens)
                results.append({
                    'doc_id': doc_id,
                    'filename': filename,
                    'snippet': snippet,
                    'score': round(score, 4)
                })
            process_log.append({'step': '6. TF-IDF Scoring', 'detail': f'Ranked {len(results)} document(s)'})
            
        return results, process_log
