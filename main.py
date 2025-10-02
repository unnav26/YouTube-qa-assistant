# main.py
import streamlit as st
from langchain_helper import get_transcript, build_qa_chain

st.set_page_config(page_title="🎥 YouTube Assistant (Groq)", layout="wide")
st.title("🎥 YouTube Q&A Assistant (Groq-powered)")

# Initialize session state
if 'qa_chain' not in st.session_state:
    st.session_state['qa_chain'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'transcript_loaded' not in st.session_state:
    st.session_state['transcript_loaded'] = False

# Sidebar input
with st.sidebar:
    st.header("Video Input")
    video_url = st.text_input(
        "Enter YouTube URL", 
        placeholder="https://www.youtube.com/watch?v=...",
        key="video_url_input"
    )
    
    if st.button("Load Transcript", type="primary"):
        if video_url:
            with st.spinner("Fetching transcript..."):
                try:
                    # Show the URL being processed
                    st.info(f"🔍 Processing: {video_url[:50]}...")
                    
                    transcript = get_transcript(video_url)
                    st.session_state['qa_chain'] = build_qa_chain(transcript)
                    st.session_state['chat_history'] = []  # Reset chat history
                    st.session_state['transcript_loaded'] = True
                    st.success("✅ Transcript loaded successfully!")
                    st.info(f"📝 Transcript length: {len(transcript)} characters")
                except Exception as e:
                    st.error(f"❌ Failed to load transcript: {e}")
                    st.session_state['transcript_loaded'] = False
                    
                    # Show troubleshooting tips
                    st.markdown("""
                    **Troubleshooting tips:**
                    - Make sure the video URL is correct
                    - Check if the video has subtitles/captions enabled
                    - Try a different video (e.g., popular videos usually have transcripts)
                    - Example working URL format: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
                    """)
        else:
            st.warning("⚠️ Please enter a valid YouTube URL.")
    
    # Show status
    if st.session_state['transcript_loaded']:
        st.success("🟢 Ready to answer questions!")
    else:
        st.info("🔵 Load a video transcript to start.")

# Main chat section
if st.session_state['transcript_loaded'] and st.session_state['qa_chain']:
    st.markdown("### 💬 Ask Questions About the Video")
    
    query = st.text_input(
        "Your question:", 
        placeholder="e.g., What is the main topic of this video?",
        key="question_input"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary")
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state['chat_history'] = []
            st.rerun()
    
    if ask_button and query:
        with st.spinner("🤔 Thinking..."):
            try:
                result = st.session_state['qa_chain'](
                    {"question": query, "chat_history": st.session_state['chat_history']}
                )

                # Update chat memory
                st.session_state['chat_history'].append((query, result['answer']))

                # Display answer
                st.markdown("### 🧠 Answer:")
                st.write(result['answer'])

                # Display sources
                if 'source_documents' in result and result['source_documents']:
                    with st.expander("📖 View Sources"):
                        for i, doc in enumerate(result['source_documents']):
                            st.markdown(f"**Source {i+1}:**")
                            st.text(doc.page_content[:300] + "...")
                            st.divider()

            except Exception as e:
                st.error(f"❌ Error processing question: {e}")
    
    # Display chat history
    if st.session_state['chat_history']:
        st.markdown("---")
        st.markdown("### 📜 Chat History")
        for i, (q, a) in enumerate(reversed(st.session_state['chat_history'])):
            with st.expander(f"Q{len(st.session_state['chat_history']) - i}: {q[:50]}..."):
                st.markdown(f"**Question:** {q}")
                st.markdown(f"**Answer:** {a}")

else:
    st.info("👈 Please load a YouTube video transcript from the sidebar to get started.")
    st.markdown("""
    ### How to use:
    1. Paste a YouTube URL in the sidebar
    2. Click "Load Transcript"
    3. Ask questions about the video content
    4. Get AI-powered answers based on the transcript
    """)