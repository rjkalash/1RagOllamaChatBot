import os
import faiss
import numpy as np
import requests
import json
import re
from flask import Flask, render_template, request, Response, stream_with_context
from sentence_transformers import SentenceTransformer

app = Flask(__name__)

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"
DATA_PATH = os.path.join("data", "source.txt")
INDEX_PATH = "faiss_index.bin"

# RAG Globals
model = None
index = None
chunks = []

def initialize_rag():
    global model, index, chunks
    print("Initializing Custom RAG pipeline...")
    
    if not os.path.exists(DATA_PATH):
        print("Data source not found.")
        return

    # 1. Load Data
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    
    # 2. Split Data (Regex split by double newlines for robust paragraph chunking)
    # This matches 2 or more newlines, possibly with spaces in between
    raw_chunks = [c.strip() for c in re.split(r'\n\s*\n', text) if c.strip()]
    
    chunks = raw_chunks
    
    # 3. Initialize Model and Embeddings
    print("Loading SentenceTransformer model (this may take a moment)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating embeddings...")
    embeddings = model.encode(chunks)
    
    # 4. Create FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # FAISS expects float32
    index.add(np.array(embeddings).astype('float32'))
    
    print(f"RAG initialized with {len(chunks)} chunks.")

# Initialize on startup
if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    try:
        initialize_rag()
    except Exception as e:
        print(f"Error initializing RAG: {e}")

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return Response("Message cannot be empty", status=400)

    # 1. Retrieve
    context_text = ""
    if index is not None and model is not None:
        try:
            query_embedding = model.encode([user_message]).astype('float32')
            D, I = index.search(query_embedding, k=5)
            
            # Get the chunks
            retrieved_chunks = []
            for idx in I[0]:
                if idx < len(chunks):
                    retrieved_chunks.append(chunks[idx])
            
            context_text = "\n\n".join(retrieved_chunks)
            print(f"Retrieved chunks indices: {I[0]}")
        except Exception as e:
            print(f"Retrieval error: {e}")
            context_text = ""
            
    # 2. Construct Prompt
    prompt = f"""You are a helpful assistant. Use the provided context to answer the question.
    
Context:
{context_text}

Question: 
{user_message}

Answer:"""

    # 3. Generate
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": True 
    }

    def generate():
        try:
            with requests.post(OLLAMA_API_URL, json=payload, stream=True) as resp:
                if resp.status_code != 200:
                    yield json.dumps({"error": f"Error from Ollama: {resp.status_code}"}) + "\n"
                    return

                for line in resp.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        try:
                            json_data = json.loads(decoded_line)
                            chunk = json_data.get("response", "")
                            done = json_data.get("done", False)
                            yield json.dumps({"chunk": chunk, "done": done}) + "\n"
                            if done:
                                break
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.ConnectionError:
            yield json.dumps({"error": "Could not connect to Ollama. Is it running?"}) + "\n"

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

if __name__ == '__main__':
    if index is None:
        initialize_rag()
    print(f"Starting server on http://localhost:5000")
    print(f"Using model: {OLLAMA_MODEL}")
    app.run(debug=True, port=5000)
