import streamlit as st
import pandas as pd
from datetime import datetime
import random
import cloudinary
import cloudinary.uploader
import os
st.markdown(
    """
    <style>
    .st-emotion-cache-1huvf7z {
        display: none; /* Hides the button */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Use Streamlit's image function to show the image on the left side
col1, col2 = st.columns([1, 3])  # Create 2 columns with ratios (left narrower than right)

with col1:  # Left column
    st.image("Huawei.jpg", width=80)

cloudinary.config(
    cloud_name="drpkmvcdb",  # Replace with your Cloudinary cloud name
    api_key="421723639371647",        # Replace with your Cloudinary API key
    api_secret="AWpJzomMBrw-5DHNqujft5scUbM"   # Replace with your Cloudinary API secret
)

def upload_to_cloudinary(file_path, public_id):
    try:
        response = cloudinary.uploader.upload(
            file_path,
            resource_type="raw",
            public_id=public_id,
            overwrite=True,  # Allow overwriting
            invalidate=True,  # Invalidate cached versions on CDN
            unique_filename=False,  # Do not generate a unique filename
            use_filename=True  # Use the file's original filename
        )
        return response['secure_url']
    except cloudinary.exceptions.Error as e:
        st.error(f"Cloudinary upload failed: {str(e)}")
        return None

# Function to save results to Excel
def save_results(username, total_attempted, correct_answers, wrong_answers, total_score, time_taken, details):   
    try:
        df = pd.read_excel("quiz_results_wireless.xlsx")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])

    new_data = pd.DataFrame([[username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), total_attempted, correct_answers, wrong_answers, total_score, time_taken, details]],
                            columns=["Username", "Date", "Total Attempted", "Correct Answers", "Wrong Answers", "Total Score", "Time Taken", "Details"])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel("quiz_results_wireless.xlsx", index=False)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'flattened_questions' not in st.session_state:
    st.session_state.flattened_questions = []
# List of allowed usernames
allowed_usernames = {
"HIC_ISB_TrainingTeam_01.",
"HIC_ISB_TrainingTeam_02",
"HIC_ISB_TrainingTeam_03",
"HIC_ISB_TrainingTeam_04",
"HIC_ISB_TrainingTeam_05"
    
}
# Define your questions
power = {
    "true_false": [
        
    ],
    "choose_correct": [
        
         
        
    ],
    "multiple_choice": [
       
    ]
}
# Flatten questions for navigation
if not st.session_state.flattened_questions:
    flattened_questions = []

    for category, qs in power.items():
        for q in qs:
            q['type'] = category  # Set the type for each question
            flattened_questions.append(q)

    # Shuffle questions within each type
    random.shuffle(flattened_questions)

    true_false_questions = [q for q in flattened_questions if q['type'] == 'true_false']
    choose_correct_questions = [q for q in flattened_questions if q['type'] == 'choose_correct']
    mcq_questions = [q for q in flattened_questions if q['type'] == 'multiple_choice']

    # Combine the questions in the desired order
    all_questions = (
    true_false_questions[:15] + 
    choose_correct_questions[:10] + 
    mcq_questions[:15]
)

    # Limit to the first 40 questions
    st.session_state.flattened_questions = all_questions[:40]

# Initialize answers
if len(st.session_state.answers) != len(st.session_state.flattened_questions):
    st.session_state.answers = [None] * len(st.session_state.flattened_questions)


# Login form
if not st.session_state.logged_in:
    st.header("Welcome to Huawei Quiz Portal")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")  # You might want to handle password validation separately

    if st.button("Login"):
        if username in allowed_usernames and password:  # Add password validation as needed
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.start_time = datetime.now()  # Track start time on login
            st.success("Logged in successfully!")
            st.session_state.logged_in = True
            st.experimental_set_query_params()  # Ensures the state is saved and reloaded without rerunning the entire script
              
        else:
            st.error("Please enter a valid username and password.")
else:
    st.sidebar.markdown(f"## Welcome **{st.session_state.username}** For The Quiz Of Wireless ")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_question = 0  # Reset current question
        st.session_state.answers = [None] * len(st.session_state.flattened_questions)  # Reset answers
        st.session_state.username = ""
        st.session_state.quiz_submitted = False  # Reset quiz submission status
        st.session_state.flattened_questions = []  # Reset questions
        st.success("You have been logged out.")
        # st.experimental_rerun()  # Refresh the page to reflect the new state

    # Quiz Page
    st.header(f"Welcome {st.session_state.username} For The Quiz Of Wireless")
    
    # Navigation buttons
    col1, col2 = st.columns(2)

    # Only show navigation buttons if the quiz hasn't been submitted
    if not st.session_state.quiz_submitted:
        if st.session_state.current_question > 0:
            with col1:
                if st.button("Previous", key="prev"):
                    st.session_state.current_question -= 1

    if st.session_state.current_question < len(st.session_state.flattened_questions) - 1:  # Show "Next" button if not on the last question
        with col2:
            if st.button("Next", key="next"):
                st.session_state.current_question += 1

    if st.session_state.current_question == len(st.session_state.flattened_questions) - 1 and not st.session_state.quiz_submitted:
        if st.button("Submit", key="submit"):
            if not st.session_state.quiz_submitted:  # Only process if not already submitted
                total_score = 0
                questions_attempted = 0
                correct_answers = 0
                wrong_answers = 0
                result_details = []

                for idx, question_detail in enumerate(st.session_state.flattened_questions):
                    user_answer = st.session_state.answers[idx]
                    if user_answer is not None:
                        questions_attempted += 1
                        
                        if question_detail["type"] == "true_false":
                            
                            score = 2
                            if user_answer == question_detail["answer"]:
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))
                        elif question_detail["type"] == "choose_correct":
                            score = 4
                            if sorted(user_answer) == sorted(question_detail["answer"]):
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))
                        elif question_detail["type"] == "multiple_choice":
                            score = 2
                            if user_answer == question_detail["answer"]:
                                correct_answers += 1
                                total_score += score
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Correct"))
                            else:
                                wrong_answers += 1
                                result_details.append((question_detail["question"], user_answer, question_detail["answer"], "Wrong"))

                end_time = datetime.now()
                time_taken = end_time - st.session_state.start_time
                
                save_results(st.session_state.username, questions_attempted, correct_answers, wrong_answers, total_score, str(time_taken), str(result_details))
                st.success("Quiz submitted successfully!")
                st.session_state.quiz_submitted = True

                total_marks = 100  # Total marks for the quiz
                percentage = (total_score / total_marks) * 100
                result_message = "<h1 style='color: green;'>Congratulations! You passed the Test!</h1>" if percentage >= 70 else "<h1 style='color: red;'>Sorry You Have Failed The Test!.</h1>"

                # Display results in a card
                st.markdown("<div class='card'><h3>Quiz Results</h3>", unsafe_allow_html=True)
                st.markdown(result_message, unsafe_allow_html=True)
                st.write(f"**Total Questions Attempted:** {questions_attempted}")
                st.write(f"**Correct Answers:** {correct_answers}")
                st.write(f"**Wrong Answers:** {wrong_answers}")
                st.write(f"**Total Score:** {total_score}")
                st.write(f"**Percentage:** {percentage:.2f}%")
                st.markdown("</div>", unsafe_allow_html=True)

    # CSS for enhanced design
    st.markdown("""<style>
        .card {
            background-color: #ffcccc; /* Light background */
            border: 1px solid #ddd; /* Subtle border */
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .question-card {
            background-color: #ffcccc; /* Light red color for questions */
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
    </style>""", unsafe_allow_html=True)

    # Display current question if quiz is not submitted
    if not st.session_state.quiz_submitted and st.session_state.current_question < len(st.session_state.flattened_questions):
        current_question = st.session_state.flattened_questions[st.session_state.current_question]
        total_questions = 40
        question_number = st.session_state.current_question + 1 
        progress_percentage = question_number / total_questions
        st.write(f"**Question {question_number} of {total_questions}**")  # Question count
        st.progress(progress_percentage)
        
        st.markdown(f"<div class='question-card'><h4>Question {question_number}: {current_question['question']}</h4></div>", unsafe_allow_html=True)

        # Display options based on question type
        if current_question["type"] == "multiple_choice":
            st.header('Multiple Choice Questions')
            st.session_state.answers[st.session_state.current_question] =  st.radio("Choose an option:", current_question["options"], key=f"mc_{st.session_state.current_question}")
        elif current_question["type"] == "true_false":
            st.header('True False')
         
            st.session_state.answers[st.session_state.current_question] =st.radio("Choose an option:", ["True", "False"], key=f"tf_{st.session_state.current_question}")
        elif current_question["type"] == "choose_correct":
            st.header('Choose The Correct')
           
            st.session_state.answers[st.session_state.current_question] =st.multiselect("Choose correct options:", current_question["options"], key=f"cc_{st.session_state.current_question}")

# Add a footer
st.markdown("<footer style='text-align: center; margin-top: 20px;'>© 2024 Huawei Training Portal. All Rights Reserved.</footer>", unsafe_allow_html=True)