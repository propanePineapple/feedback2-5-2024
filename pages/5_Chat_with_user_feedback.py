from openai import OpenAI
import streamlit as st
from streamlit_feedback import streamlit_feedback
from pymongo import MongoClient
import uuid
import json

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="feedback_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
client = OpenAI(api_key=openai_api_key)
st.title("📝 Provide Gameplay Feedback with Feedback.Ai")


league_questions = {
    'q1': "How satisfied are you with the balance changes made to champions in the January 2024 patch, and why?",
    'q2': "What is your opinion on the new items and item updates introduced in the January 2024 patch?",
    'q3': "How do you rate the changes made to the map in the January 2024 patch in terms of enhancing strategic diversity and gameplay fairness?",
    'q4': "In terms of overall game experience, how has the January 2024 patch affected your enjoyment and engagement with League of Legends?",
    'q5': "What other feedback or suggestions do you have for the League of Legends development team?",
    'q6': "What are your thoughts on the new champion introduced in the January 2024 patch, and how does it impact the game's strategic diversity and competitive landscape?",
    'q7': "How do you feel about the adjustments made to existing champions in the January 2024 patch, and how have they influenced your gameplay experience?"
}
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help you? Leave feedback to help me improve!"}
    ]
if "response" not in st.session_state:
    st.session_state["response"] = None

def save_feedback_to_mongodb(chat_history):
    client = MongoClient("mongodb+srv://srini2000:srini2000@cluster0.avp7aim.mongodb.net/")
    db = client.userCollectedFeedback  # Specify the database name
    collection = db.test  # Specify the collection name

    # Create a dictionary to hold the feedback data
    feedback_data = {
        "_id": str(uuid.uuid4()),
        "chat_history": chat_history
    }

    # Insert the feedback data into MongoDB
    collection.insert_one(feedback_data)



def valorant_prompts(user_input, chat_context):
    # Example of a system message and follow-up question for Valorant
    system_message = "User is providing feedback for Valorant."
    chat_context.append({"role": "system", "content": system_message})
    return chat_context

def fortnite_prompts(user_input, chat_context):
    # Example of a system message and follow-up question for Fortnite
    system_message = "User is providing feedback for Fortnite."
    chat_context.append({"role": "system", "content": system_message})
    return chat_context



#title of the app
st.title("👾 Provide Gameplay Feedback with Feedback.Ai")

#first we choose the game for which we want to provide feedback
#the choice is stored in the game_choice variable


def manage_chat(game_choice):
    # Initialize chat variables if not already present
    if "chat_history" not in st.session_state:
        initialize_chat_variables(game_choice)

    display_chat_history()

    # Generate a unique key for the input field based on the number of total messages
    input_key = f"user_input_{st.session_state.total_messages}"

    # User input with dynamic key to refresh the input field after each submission
    user_input = st.text_input("Your response:", key=input_key)

    if user_input:
        handle_user_input(user_input)
        handle_question_progression()

    handle_feedback_submission()

def initialize_chat_variables(game_choice):
    st.session_state.chat_history = []
    st.session_state.chat_context = []  # Initialize chat context for the current question
    st.session_state.total_messages = 0
    st.session_state.current_question = 'q1'
    st.session_state.follow_ups = 0

    # Welcome message and LLM prompt
    welcome_message = "Welcome to the League of Legends feedback chat. I'm here to discuss the January 2024 patch with you. Your insights are invaluable."
    leagueprompt= "You are to assume the role project manager and game developer with 25 years of experience on the League of Legends Insights team. With a deep understanding of the gaming community's nuances and the evolving landscape of competitive gaming, you are not just a conversational AI but a seasoned strategist in engaging with gamers. You are programmed with an intricate knowledge of League of Legends' history, its patches, and the ever-changing meta. You are  well-versed in the latest game updates, including the minutiae of champion adjustments, item modifications, and significant overhauls to game mechanics and map features introduced in patches 14.1 and 14.2. Your persona is designed to resonate with both veteran players and newcomers, providing a bridge between the rich legacy of the game and its future direction. Your task is to conduct an interview with me to collect feedback from me. You will be extracting deep, actionable insights from me as a player, utilizing a sophisticated understanding of game design principles and player psychology. Your conversations will be meticulously crafted to probe into the layers of player experience, from surface-level reactions to underlying sentiments about the game's balance, strategic diversity, and overall enjoyment. You will seamlessly weave its questions into engaging dialogues, ensuring I feel understood and valued. Your objective is not just to gather feedback but to foster a deeper connection between the game developers and the community, guiding the evolution of League of Legends in a way that honors its rich heritage while embracing innovation. Please assume this role and ask me the first question Now conduct a feedback conversation starting with this question:"


    st.session_state.chat_context.append({"role": "assistant", "content": leagueprompt + " " + league_questions[st.session_state.current_question]})

    # Call LLM with the initial chat context
    call_llm_with_context(st.session_state.chat_context)

def display_chat_history():
    for msg in st.session_state.chat_history:
        st.write(f"{msg['role'].title()}: {msg['content']}")

def handle_user_input(user_input):
    # Append user input to chat history and chat context
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_context.append({"role": "user", "content": user_input})
    st.session_state.total_messages += 1
    st.session_state.follow_ups += 1

    # Call LLM with updated chat context
    call_llm_with_context(st.session_state.chat_context)

def handle_question_progression():
    if st.session_state.follow_ups >= 10 or st.button("Next Question", key=f"next_{st.session_state.current_question}"):
        st.session_state.follow_ups = 0  # Reset follow-up count
        next_question_key = get_next_question_key(st.session_state.current_question)
        if next_question_key:
            st.session_state.current_question = next_question_key
            # Reset chat context for the new question and append the new question
            st.session_state.chat_context = [{"role": "assistant", "content": league_questions[next_question_key]}]
            call_llm_with_context(st.session_state.chat_context)
        else:
            # End of questions
            st.session_state.chat_history.append({"role": "assistant", "content": "Thank you for your feedback!"})

def handle_feedback_submission():
    if st.button("Submit Feedback"):
        save_feedback_to_mongodb(st.session_state.chat_history)
        reset_chat()

def call_llm_with_context(chat_context):
    # Prepare messages for LLM call
    messages = [{"role": msg["role"], "content": msg["content"]} for msg in chat_context]
    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
        response_msg = response.choices[0].message.content.strip()
        # Append LLM response to chat history and chat context
        st.session_state.chat_history.append({"role": "assistant", "content": response_msg})
        st.session_state.chat_context.append({"role": "assistant", "content": response_msg})
    except Exception as e:
        st.error(f"An error occurred while communicating with the LLM: {e}")

def get_next_question_key(current_key):
    # Return the key of the next question in the league_questions dictionary, or None if at the end
    keys = list(league_questions.keys())
    current_index = keys.index(current_key)
    return keys[current_index + 1] if current_index + 1 < len(keys) else None

def reset_chat():
    # Reset the chat-related session state variables
    del st.session_state.chat_history
    del st.session_state.total_messages
    del st.session_state.current_question
    del st.session_state.follow_ups
    del st.session_state.game_choice
def main():
    # Initialize session state for messages if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display game selection buttons only if a game hasn't been chosen yet
    if "game_choice" not in st.session_state or st.session_state.game_choice is None:
        if st.button("League of Legends"):
            st.session_state.game_choice = "League of Legends"
        elif st.button("Valorant"):
            st.session_state.game_choice = "Valorant"
        elif st.button("Fortnite"):
            st.session_state.game_choice = "Fortnite"

    # Use 'in' to safely check if 'game_choice' exists in session_state before accessing it
    if "game_choice" in st.session_state and st.session_state.game_choice:
        manage_chat(st.session_state.game_choice)  # Proceed to manage the chat for feedback

if __name__ == "__main__":
    main()
