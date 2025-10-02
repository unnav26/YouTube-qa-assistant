# langchain_helper.py - Compatible with youtube-transcript-api v1.2.2

import os
import re
from dotenv import load_dotenv

# Import for youtube-transcript-api v1.2.2+
from youtube_transcript_api import YouTubeTranscriptApi

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")


# ------------------------------
# Helper: Extract video ID safely
# ------------------------------
def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    if not url:
        raise ValueError("URL cannot be empty")
    
    # Remove whitespace
    url = url.strip()
    
    print(f"DEBUG: Processing URL: {url}")
    
    # Patterns to match YouTube URLs
    patterns = [
        r'(?:youtube\.com\/watch\?v=)([0-9A-Za-z_-]{11})',  # Standard watch URL
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # Shortened URL
        r'(?:youtube\.com\/embed\/)([0-9A-Za-z_-]{11})',  # Embed URL
        r'^([0-9A-Za-z_-]{11})$'  # Just the ID
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            print(f"DEBUG: Pattern {i} matched -> Video ID: {video_id}")
            return video_id
    
    raise ValueError(f"Could not extract video ID from URL: {url}")


# ------------------------------
# Get transcript from YouTube
# ------------------------------
def get_transcript(video_url: str) -> str:
    """Fetch transcript from YouTube video - Compatible with v1.2.2"""
    video_id = None
    try:
        # Extract video ID
        video_id = extract_video_id(video_url)
        print(f"DEBUG: Video ID: {video_id}")
        
        # Create API instance (v1.2.2 requires instantiation)
        api = YouTubeTranscriptApi()
        print(f"DEBUG: Created API instance")
        
        # Try to fetch transcript
        try:
            # Method 1: fetch() with English language preference
            print(f"DEBUG: Attempting fetch with language preference...")
            transcript = api.fetch(video_id, languages=['en'])
            print(f"DEBUG: Successfully fetched English transcript")
        except:
            try:
                # Method 2: fetch() without language specification
                print(f"DEBUG: Attempting fetch without language specification...")
                transcript = api.fetch(video_id)
                print(f"DEBUG: Successfully fetched transcript (any language)")
            except Exception as e:
                print(f"DEBUG: fetch() failed: {str(e)}")
                
                # Method 3: Try list() and iterate
                try:
                    print(f"DEBUG: Attempting list() method...")
                    transcripts = api.list(video_id)
                    
                    # Get first available transcript
                    transcript = None
                    for t in transcripts:
                        if hasattr(t, 'fetch'):
                            transcript = t.fetch()
                        else:
                            transcript = t
                        print(f"DEBUG: Got transcript from list() method")
                        break
                    
                    if not transcript:
                        raise ValueError("No transcripts available")
                        
                except Exception as e2:
                    print(f"DEBUG: list() also failed: {str(e2)}")
                    raise ValueError(f"Could not retrieve transcript: {str(e2)}")

        # Validate transcript
        if not transcript:
            raise ValueError("Transcript is empty")
        
        # In v1.2.2, fetch() returns a FetchedTranscript object which is iterable
        # Convert it to a list
        if not isinstance(transcript, list):
            print(f"DEBUG: Converting {type(transcript).__name__} to list...")
            try:
                transcript = list(transcript)
                print(f"DEBUG: Successfully converted to list with {len(transcript)} items")
            except Exception as e:
                raise ValueError(f"Could not convert transcript to list: {e}")
        
        if len(transcript) == 0:
            raise ValueError("Transcript has no segments")

        # Extract text from each segment
        # In v1.2.2, each item might be a FetchedTranscriptSnippet object
        print(f"DEBUG: Extracting text from segments...")
        text_parts = []
        for entry in transcript:
            try:
                # Try dictionary access first
                if isinstance(entry, dict):
                    text_parts.append(entry['text'])
                # Try attribute access for object
                elif hasattr(entry, 'text'):
                    text_parts.append(entry.text)
                # Try serialize method
                elif hasattr(entry, 'serialize'):
                    serialized = entry.serialize()
                    text_parts.append(serialized.get('text', ''))
                else:
                    print(f"DEBUG: Unknown entry type: {type(entry)}")
            except Exception as e:
                print(f"DEBUG: Error processing entry: {e}")
                continue
        
        if not text_parts:
            raise ValueError("Could not extract any text from transcript segments")
        
        text = " ".join(text_parts)
        print(f"DEBUG: Successfully processed {len(text_parts)} segments, {len(text)} characters")
        
        return text

    except ValueError as e:
        # Re-raise ValueError as-is
        raise e
    except Exception as e:
        error_msg = str(e)
        print(f"DEBUG: Unexpected error: {error_msg}")
        
        # Provide helpful error messages based on error content
        if "Could not retrieve" in error_msg or "TranscriptsDisabled" in error_msg:
            raise ValueError(f"📝 No transcript available for video ID: {video_id}")
        elif "VideoUnavailable" in error_msg:
            raise ValueError(f"🚫 Video unavailable or private (ID: {video_id})")
        else:
            raise ValueError(f"❌ Error: {error_msg}")


# ------------------------------
# Build QA Chain
# ------------------------------
def build_qa_chain(transcript: str):
    """Build conversational QA chain from transcript"""
    if not transcript or len(transcript.strip()) == 0:
        raise ValueError("Transcript is empty. Cannot build QA chain.")
    
    print(f"DEBUG: Building QA chain with transcript of {len(transcript)} characters")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    docs = splitter.create_documents([transcript])
    print(f"DEBUG: Created {len(docs)} document chunks")
    
    if len(docs) == 0:
        raise ValueError("Failed to create document chunks from transcript.")

    # Hugging Face embeddings
    print(f"DEBUG: Loading embeddings model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # Create vector store
    print(f"DEBUG: Creating vector store...")
    vectorstore = FAISS.from_documents(docs, embeddings)

    # Groq LLM
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables.")
    
    print(f"DEBUG: Initializing Groq LLM...")
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # Updated model (mixtral-8x7b-32768 is deprecated)
        temperature=0, 
        groq_api_key=groq_api_key
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Conversational Retrieval Chain
    print(f"DEBUG: Building conversational chain...")
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        verbose=False
    )

    print(f"DEBUG: QA chain ready!")
    return qa_chain