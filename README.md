#  YouTube Q&A Assistant

An AI-powered Streamlit application that fetches YouTube video transcripts and allows you to ask questions about the video content using Groq's LLM.

##  Features

- 📝 Fetch transcripts from any YouTube video with captions
- 🤖 Ask questions about video content using AI (Groq LLM)
- 💬 Conversational interface with chat history
- 🔍 Source citations from the transcript
- ⚡ Fast responses powered by Groq

##  Setup

### Prerequisites

- Python 3.8 or higher
- A Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/youtube-qa-assistant.git
cd youtube-qa-assistant
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create a `.env` file:**
```bash
# Create .env file in the root directory
GROQ_API_KEY=your_groq_api_key_here
```

##  Usage

1. **Run the Streamlit app:**
```bash
streamlit run main.py
```

2. **Use the application:**
   - Paste a YouTube URL in the sidebar
   - Click "Load Transcript"
   - Ask questions about the video content
   - View chat history and source citations

##  Example

```
YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Question: What is the main topic of this video?
Answer: [AI-generated response based on the transcript]
```

##  Tech Stack

- **Streamlit** - Web interface
- **LangChain** - LLM orchestration
- **Groq** - Fast LLM inference
- **FAISS** - Vector storage for semantic search
- **youtube-transcript-api** - Transcript fetching
- **HuggingFace Embeddings** - Text embeddings

##  Project Structure

```
youtube-qa-assistant/
├── main.py                 # Streamlit app interface
├── langchain_helper.py     # Core logic for transcript & QA
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore             # Git ignore file
└── README.md              # This file
```

##  Limitations

- Only works with videos that have captions/subtitles enabled
- Requires a valid Groq API key
- Limited by Groq's rate limits and token limits

##  Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

##  License

This project is open source and available under the [MIT License](LICENSE).

##  Acknowledgments

- Groq for providing fast LLM inference
- LangChain for the excellent framework
- The youtube-transcript-api library maintainers
