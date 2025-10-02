from youtube_transcript_api import YouTubeTranscriptApi

video_id = "AdI_XWv-ZTk"

print("Testing with INSTANCE methods (v1.2.2 style)")
print("=" * 50)

try:
    # Create an instance
    api = YouTubeTranscriptApi()
    print(f"✅ Created YouTubeTranscriptApi instance")
    
    # Test 1: Try list() method
    print(f"\n1. Trying api.list('{video_id}')...")
    try:
        transcripts = api.list(video_id)
        print(f"✅ list() works!")
        print(f"   Result type: {type(transcripts)}")
        print(f"   Available transcripts:")
        
        # Try to iterate and fetch
        for transcript in transcripts:
            print(f"     - Language: {transcript.language if hasattr(transcript, 'language') else 'unknown'}")
        
        # Get the first transcript
        first_transcript = next(iter(transcripts))
        
    except Exception as e:
        print(f"❌ list() error: {e}")
    
    # Test 2: Try fetch() method
    print(f"\n2. Trying api.fetch('{video_id}')...")
    try:
        result = api.fetch(video_id)
        print(f"✅ fetch() works!")
        print(f"   Result type: {type(result)}")
        print(f"   Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        if isinstance(result, list) and len(result) > 0:
            print(f"   First item: {result[0]}")
            
            # Calculate total text
            text = " ".join([entry['text'] for entry in result])
            print(f"   Total characters: {len(text)}")
            print(f"\n✅ SUCCESS! This is the method that works!")
            
    except Exception as e:
        print(f"❌ fetch() error: {e}")
        
except Exception as e:
    print(f"❌ Failed to create instance: {e}")