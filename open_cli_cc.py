import os
import re
import json  # Add this line to import the json module
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import streamlit as st
import keyboard


load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

@st.cache_data
def fetch_questions(youtube_video_url, quiz_difficulty):

    RESPONSE_JSON = {
        "questions" : [
            {
                "question": "Question 1",
                "options": {
                    "a": "choice1",
                    "b": "choice2",
                    "c": "choice3",
                    "d": "choice4"
                },
                "correct_answer": "correct_choice_option",
            },
            {
                "question": "Question 2",
                "options": {
                    "a": "choice1",
                    "b": "choice2",
                    "c": "choice3",
                    "d": "choice4"
                },
                "correct_answer": "correct_choice_option",
            },
            {
                "question": "Question 3",
                "options": {
                    "a": "choice1",
                    "b": "choice2",
                    "c": "choice3",
                    "d": "choice4"
                },
                "correct_answer": "correct_choice_option",
            }
        ]
    }
    
    PROMPT_TEMPLATE="""
    Youtube Video URL: {youtube_video_url}
    You are an expert in generating MCQ type quiz on the basis of the video content.
    Given the above youtube link, create a quiz based on the contents of the video; 3 multiple choice question keeping difficulty level as {quiz_difficulty}
    Make sure the questions are not repeated and check all the questions to be conforming the text as well.
    Make sure to format the your response like RESPONSE_JSON below and use it as a guide.
    Ensure to make an array of 3 MCQs referring the folllowing json.

    Here is the RESPONSE_JSON:
    {RESPONSE_JSON}
    
    """

    formatted_template = PROMPT_TEMPLATE.format(youtube_video_url=youtube_video_url, quiz_difficulty=quiz_difficulty, RESPONSE_JSON=RESPONSE_JSON)

    model = genai.GenerativeModel('gemini-pro')

    response = model.generate_content(formatted_template)

    print(response)

    return json.loads(response).get("questions", [])

def main():
    st.title("YT Qz")

    youtube_video_url = st.text_input("Enter the Youtube video link: ")
    quiz_difficulty = st.selectbox("Select the quiz difficulty level: ", ["easy", "medium", "hard"])

    session_state = st.session_state

    if 'quiz_generated' not in session_state:
        session_state.quiz_generated = False

    if not session_state.quiz_generated:
        session_state.quiz_generated = st.button("Generate Quiz")

    if session_state.quiz_generated:
        questions = fetch_questions(youtube_video_url=youtube_video_url, quiz_difficulty=quiz_difficulty)

    selected_options = []
    correct_answers = []
    for question in questions:
        options = list(question["options"].values())
        selected_option = st.radio(question["question"], options, index=None)
        selected_options.append(selected_option)
        correct_answers.append(question["options"][question["correct_answer"]])

    if st.button("Submit"):
        marks = 0
        st.header("Result: ")
        for i, question in enumerate(questions):
            selected_option = selected_options[i]
            correct_answer = correct_answers[i]
            st.subheader(f"{question['question']}")
            st.write(f"You selected: {selected_option}")
            st.write(f"Correct answer: {correct_answer}")
            if selected_option == correct_answer:
                total_marks += 1
        st.write(f"Total Marks: {total_marks}")

if __name__ == "__main__":
    main()

