import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import keyboard  # Requires the 'keyboard' library

# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment variable
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API with the obtained key
genai.configure(api_key=gemini_api_key)

def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    video_id = None
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)'
    ]
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            video_id = match.group(1)
            break
    return video_id

def get_video_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry['text'] for entry in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def get_response_gemini(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt])
    return response.text

def generate_quiz(transcript, difficulty):
    prompt = f"""
    Generate a quiz based on the following transcript:
    {transcript}
    The quiz should have 5 single-choice questions with 4 options each.
    Difficulty: {difficulty}
    """
    response = get_response_gemini(prompt)
    questions = response.split('\n\n')  # Assuming each question is separated by double newlines
    return questions

def display_questions(questions):
    for i, question in enumerate(questions):
        print(f"\n\n{question}\n")
        if i < len(questions) - 1:
            print("Press 'Space' for the question...")
            keyboard.wait('space')

if __name__ == "__main__":
    yt_link = input("Enter the Youtube video link: ").strip()
    difficulty = input("Enter the difficulty level (easy, medium, hard): ").strip().lower()

    video_id = extract_video_id(yt_link)
    if not video_id:
        print("Invalid YouTube URL")
    else:
        transcript = get_video_transcript(video_id)
        if not transcript:
            print("Could not fetch transcript")
        else:
            quiz_questions = generate_quiz(transcript, difficulty)
            display_questions(quiz_questions[:5])  # Display only the first 5 questions

    print("Goodbye!")