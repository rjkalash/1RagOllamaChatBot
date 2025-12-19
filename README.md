# Ollama Gemma Bot (RAG)

This project is a local RAG (Retrieval-Augmented Generation) chat bot application that uses Flask, FAISS, Sentence Transformers, and Ollama to answer questions based on a provided text source.

## 🚀 Features

- **Local LLM Inference**: Uses [Ollama](https://ollama.com/) to run LLMs locally (default: Mistral).
- **RAG Pipeline**:
  - **Ingestion**: Reads text from `data/source.txt`.
  - **Chunking**: Splits text into paragraphs.
  - **Embedding**: Uses `all-MiniLM-L6-v2` via `sentence-transformers`.
  - **Vector Search**: Uses FAISS for efficient similarity search.
- **Streaming Responses**: Real-time token streaming from the LLM to the UI.
- **Simple Web Interface**: Clean chat UI built with HTML/CSS.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**
2.  **Ollama**: Download and install from [ollama.com](https://ollama.com/).

### Setup Ollama Model

This project is configured to use the `mistral` model by default (configurable in `app.py`). You need to pull it first:

```bash
ollama pull mistral
```

*Note: If you want to use Gemma (as the project name suggests), you can pull `ollama pull gemma` and update `OLLAMA_MODEL` in `app.py`.*

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ollama-gemma-bot
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 Usage

1.  **Prepare your data:**
    Edit `data/source.txt` and paste the text content you want the bot to know about.

2.  **Make sure Ollama is running:**
    Refer to Ollama documentation for your OS. Usually, it runs in the background or you can start it with `ollama serve`.

3.  **Start the application:**
    ```bash
    python app.py
    ```

4.  **Access the bot:**
    Open your browser and navigate to output: `http://localhost:5000`

## ⚙️ Configuration

You can modify the following constants in `app.py` to customize the behavior:

-   `OLLAMA_API_URL`: URL of the Ollama API (default: `http://localhost:11434/api/generate`)
-   `OLLAMA_MODEL`: The LLM model to use (default: `mistral`)
-   `DATA_PATH`: Path to the source text file (default: `data/source.txt`)

## 📂 Project Structure

```
ollama-gemma-bot/
├── app.py                 # Main Flask application and RAG logic
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── data/
│   └── source.txt         # Source text for RAG
├── static/
│   └── index.html         # Frontend HTML/JS
└── faiss_index/           # (Generated) FAISS index storage
```

## ❓ Troubleshooting

-   **"Could not connect to Ollama":** Ensure Ollama is installed and running (`ollama serve`). Check if `http://localhost:11434` is accessible.
-   **"Data source not found":** Ensure `data/source.txt` exists and contains text.
-   **Model not found:** Run `ollama list` to see installed models. If `mistral` is missing, run `ollama pull mistral`.
