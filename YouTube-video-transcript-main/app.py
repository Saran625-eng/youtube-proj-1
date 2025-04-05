import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))



prompt = """You are an AI specialized in summarizing technical topics. 
Focus strictly on the core subject of the transcript. Ignore any unrelated words like 'subscribe' or 'like'. 
Provide a structured summary of the main discussion, emphasizing technical details only. 
Summarize the text given here in a point wise manner with proper headings with heavy details and also provide the 
info what you know about it and provide the insights..... ignore like and subsribe words just concentrate aon topic """



# Function to extract YouTube video ID safely
def get_video_id(youtube_link):
    try:
        if "v=" in youtube_link:
            return youtube_link.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_link:
            return youtube_link.split("youtu.be/")[1].split("?")[0]
        else:
            return None
    except IndexError:
        return None


# Function to get transcript data from YouTube videos
# def extract_transcript_details(youtube_video_url):
#     try:
#         video_id = get_video_id(youtube_video_url)
#         if not video_id:
#             return None
#
#         transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
#         transcript = " ".join([i["text"] for i in transcript_data])
#         return transcript
#
#     except (TranscriptsDisabled, NoTranscriptFound):
#         return None  # Handle cases where subtitles are disabled or unavailable
#     except Exception as e:
#         return str(e)

def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        if not video_id:
            return None

        try:
            # Try fetching manually uploaded subtitles
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        except NoTranscriptFound:
            try:
                # Try fetching auto-generated English captions
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            except NoTranscriptFound:
                try:
                    # Try fetching auto-generated captions in other common languages
                    transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'es', 'fr'])
                except NoTranscriptFound:
                    return "Transcript not available for this video. The video may have no subtitles or restricted captions."

        transcript = " ".join([i["text"] for i in transcript_data])
        return transcript

    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "No transcript found. Try a different video."
    except Exception as e:
        return f"Error: {str(e)}"




# Function to generate a summary using Gemini AI
# def generate_gemini_content(transcript_text, prompt):
#     model = genai.GenerativeModel("gemini-pro")
#     response = model.generate_content(prompt + transcript_text)
#     return response.text

# Function to generate a summary using Gemini AI
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")  # Update model name if needed
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"



# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

# Display thumbnail if a valid YouTube link is entered
if youtube_link:
    video_id = get_video_id(youtube_link)

    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    else:
        st.error("Invalid YouTube link. Please enter a valid URL.")

# Button to generate the summary
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
    else:
        st.error("Transcript not available for this video. Please try another link.")