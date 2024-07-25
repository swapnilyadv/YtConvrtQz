import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

# Set up Gemini API (replace with your actual API key)
# Load environment variables from .env file
load_dotenv()

# Get Gemini API key from environment variable
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API with the obtained key
genai.configure(api_key=gemini_api_key)

def extract_video_id(url):
    # Extract video ID from various YouTube URL formats
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def generate_quiz(transcript):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    Based on the following transcript, create a quiz with 10 multiple-choice questions.
    Each question should have 4 options (A, B, C, D) with only one correct answer.
    Format each question as follows:

    Q1. Question text
    A) Option A
    B) Option B
    C) Option C
    D) Option D
    Correct Answer: X

    Transcript: {transcript[:4000]}  # Limiting transcript length to avoid token limits
    """
    
    response = model.generate_content(prompt)
    return response.text

def parse_quiz(quiz_text):
    questions = []
    current_question = None

    for line in quiz_text.split('\n'):
        if line.startswith('Q'):
            if current_question:
                questions.append(current_question)
            current_question = {'question': line, 'options': [], 'correct': None}
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            current_question['options'].append(line)
        elif line.startswith('Correct Answer:'):
            current_question['correct'] = line.split(':')[1].strip()

    if current_question:
        questions.append(current_question)

    return questions

def display_quiz(quiz):
    for i, q in enumerate(quiz, 1):
        print(f"\n{q['question']}")
        for option in q['options']:
            print(option)
        print(f"Correct Answer: {q['correct']}")

def main():
    url = input("Enter YouTube video URL: ")
    video_id = extract_video_id(url)
    
    if not video_id:
        print("Invalid YouTube URL")
        return

    transcript = get_video_transcript(video_id)
    if not transcript:
        return

    quiz_text = generate_quiz(transcript)
    quiz = parse_quiz(quiz_text)
    display_quiz(quiz)

if __name__ == "__main__":
    main()