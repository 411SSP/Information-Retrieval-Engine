# 🐼 PANDA Information Retrieval Engine

An end-to-end, full-stack Information Retrieval (IR) and text search engine built from scratch in Python and Flask.

---

## 🌟 Key Features

- **Dual Retrieval Models**:
  - **TF-IDF Ranked Retrieval**: Vector space ranking using sublinear term frequency $1 + \log_{10}(\text{tf})$ and inverse document frequency $\log_{10}(N/\text{df})$.
  - **Boolean Conjunctive (AND) Retrieval**: Strict set intersection across multiple search terms.
- **Positional Phrase Matching**: Exact phrase searches (e.g. `"machine learning"`) resolved in linear time using positional inverted index offsets without generating raw n-grams.
- **Permuterm Wildcard Matching**: Sub-millisecond prefix, suffix, and infix wildcard resolution (e.g. `mach*`) using a cyclic rotation index.
- **Fault-Tolerant Spelling Correction**: Dynamic programming Levenshtein distance ($\le 2$) automatically suggests and queries corrected terms.
- **Multi-Format Ingestion**: Supports `.txt` files and digital `.pdf` documents with automated text extraction and live index rebuilding.
- **Corpus Document Manager**: Upload, view, and delete documents with instant index synchronization.
- **Modern Interactive UI**: Cyber / Dark mode and Light mode interface with an execution trace drawer, contextual snippet highlights, and modal quick document previews.

---

## 📂 Project Architecture

```
Information-Retrieval Engine/
├── documents/               # Corpus text and converted PDF documents
├── index/                   # Serialized inverted index & permuterm rotations
├── src/                     # Core IR algorithms
│   ├── document_loader.py   # Document ingestion and ID mapping
│   ├── tokenizer.py         # Regex-based word boundary tokenization
│   ├── normalizer.py        # Stopword filtering and Porter stemming
│   ├── indexer.py           # Positional inverted index data structure
│   ├── index_constructor.py # Offline indexing pipeline orchestrator
│   ├── wildcard_processor.py# Permuterm index and cyclic rotation lookup
│   ├── spelling_corrector.py# Dynamic programming Levenshtein distance
│   └── query_processor.py   # Scoring, ranking, and execution trace logger
├── templates/               # Web presentation layer (Jinja2 HTML)
│   ├── base.html            # Theme switcher, navbar, and flash alerts
│   ├── index.html           # Search hero, results view, and logic drawer
│   ├── upload.html          # Document uploader & corpus file manager
│   └── document.html        # Clean full-document viewer
├── .gitignore               # Ignored environments and bytecode
├── app.py                   # Flask server application
└── requirements.txt         # Project dependencies
```

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd "Information-Retrieval Engine"
```

### 2. Create and Activate a Virtual Environment
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Engine
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Search Query Examples

| Query Type | Example Query | How PANDA Handles It |
| :--- | :--- | :--- |
| **Ranked Keyword Search** | `natural language processing` | Computes TF-IDF vector scores and ranks matching documents. |
| **Exact Phrase** | `"machine learning"` | Verifies token adjacency ($p_{i+1} = p_i + 1$) via positional offsets. |
| **Wildcard Match** | `mach*` | Rotates to `$mach*` and performs prefix lookup in the Permuterm index. |
| **Typo Correction** | `enine` | Corrects to `engine` using Levenshtein edit distance. |

---

## 📜 License
This project is open-source and available under the [MIT License](LICENSE).
