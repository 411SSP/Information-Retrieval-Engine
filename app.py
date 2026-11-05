from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sys
from pypdf import PdfReader

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.query_processor import QueryProcessor
from src.index_constructor import build_index

app = Flask(__name__)
app.secret_key = 'super_secret_key'

base_dir = os.path.dirname(os.path.abspath(__file__))
corpus_path = os.path.join(base_dir, 'documents')
index_path = os.path.join(base_dir, 'index')

# Build the index on startup
print("Building index...")
build_index(corpus_path, index_path)
processor = QueryProcessor(index_path)

@app.route('/', methods=['GET', 'POST'])
def home():
    query = ""
    model = "tfidf"
    results = []
    process_log = []
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        model = request.form.get('model', 'tfidf')
        if query:
            results, process_log = processor.process_query(query, model=model)
            
    return render_template('index.html', query=query, results=results, process_log=process_log, model=model)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'document' not in request.files:
            flash('No file provided.', 'error')
            return redirect(request.url)
            
        file = request.files['document']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
            
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.txt':
            filepath = os.path.join(corpus_path, filename)
            file.save(filepath)
            flash(f'Text file "{filename}" uploaded and indexed successfully!', 'success')
            
        elif ext == '.pdf':
            try:
                reader = PdfReader(file)
                extracted_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
                        
                if not extracted_text.strip():
                    flash(f'Warning: Could not extract readable text from PDF "{filename}" (it might be a scanned image).', 'error')
                    return redirect(request.url)
                    
                txt_filename = os.path.splitext(filename)[0] + "_pdf.txt"
                filepath = os.path.join(corpus_path, txt_filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                    
                flash(f'PDF "{filename}" converted to text ({len(reader.pages)} page(s)) and indexed successfully!', 'success')
            except Exception as e:
                flash(f'Error processing PDF file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Only .txt and .pdf files are supported.', 'error')
            return redirect(request.url)
            
        # Rebuild index and reload processor
        build_index(corpus_path, index_path)
        global processor
        processor = QueryProcessor(index_path)
        
        return redirect(url_for('home'))
            
    # List existing files in the corpus
    corpus_files = []
    if os.path.exists(corpus_path):
        corpus_files = [f for f in sorted(os.listdir(corpus_path)) if f.endswith('.txt')]
        
    return render_template('upload.html', corpus_files=corpus_files)

@app.route('/delete/<filename>', methods=['POST'])
def delete_document(filename):
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(corpus_path, safe_filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            
            # Rebuild index and reload processor
            build_index(corpus_path, index_path)
            global processor
            processor = QueryProcessor(index_path)
            
            flash(f'Document "{safe_filename}" deleted and index updated successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting document: {str(e)}', 'error')
    else:
        flash(f'Document "{safe_filename}" not found.', 'error')
        
    return redirect(url_for('upload'))

@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    filename = processor.doc_map.get(doc_id)
    if not filename:
        return "Document not found", 404
        
    filepath = os.path.join(corpus_path, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template('document.html', filename=filename, content=content)
    return "File missing on disk", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
