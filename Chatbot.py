import os
import nltk
import ssl
import json
import streamlit as st
import random
import datetime
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ssl._create_default_https_context = ssl._create_unverified_context
nltk.data.path.append(os.path.abspath("nltk_data"))
nltk.download('punkt')

intents = [
    {
        "tag": "greeting",
        "patterns": ["Hi", "Hello", "Hey", "How are you", "What's up"],
        "responses": ["Hi there", "Hello", "Hey", "I'm fine, thank you", "Nothing much"]
    },
    {
        "tag": "goodbye",
        "patterns": ["Bye", "See you later", "Goodbye", "Take care"],
        "responses": ["Goodbye", "See you later", "Take care"]
    },
    {
        "tag": "thanks",
        "patterns": ["Thank you", "Thanks", "Thanks a lot", "I appreciate it"],
        "responses": ["You're welcome", "No problem", "Glad I could help"]
    },
    {
        "tag": "about",
        "patterns": ["What can you do", "Who are you", "What are you", "What is your purpose"],
        "responses": ["I am a chatbot", "My purpose is to assist you", "I can answer questions and provide assistance"]
    },
    {
        "tag": "help",
        "patterns": ["Help", "I need help", "Can you help me", "What should I do"],
        "responses": ["Sure, what do you need help with?", "I'm here to help. What's the problem?", "How can I assist you?"]
    },
    {
        "tag": "age",
        "patterns": ["How old are you?", "What is your age?", "Tell me your age"],
        "responses": ["I am an AI created by OpenAI, so I don't have an age like humans."]
    },
    {
        "tag": "weather",
        "patterns": ["What's the weather like", "How's the weather today"],
        "responses": ["I'm checking the weather for you. Please wait a moment."]
    },
    {
        "tag": "budget",
        "patterns": ["How can I make a budget", "What's a good budgeting strategy", "How do I create a budget"],
        "responses": ["To make a budget, start by tracking your income and expenses. Then, allocate your income towards essential expenses like rent, food, and bills. Next, allocate some of your income towards savings and debt repayment. Finally, allocate the remainder of your income towards discretionary expenses like entertainment and hobbies.", "A good budgeting strategy is to use the 50/30/20 rule. This means allocating 50% of your income towards essential expenses, 30% towards discretionary expenses, and 20% towards savings and debt repayment.", "To create a budget, start by setting financial goals for yourself. Then, track your income and expenses for a few months to get a sense of where your money is going. Next, create a budget by allocating your income towards essential expenses, savings and debt repayment, and discretionary expenses."]
    },
    {
        "tag": "credit_score",
        "patterns": ["What is a credit score", "How do I check my credit score", "How can I improve my credit score"],
        "responses": ["A credit score is a number that represents your creditworthiness. It is based on your credit history and is used by lenders to determine whether or not to lend you money. The higher your credit score, the more likely you are to be approved for credit.", "You can check your credit score for free on several websites such as Credit Karma and Credit Sesame."]
    },
    {
        "tag": "time",
        "patterns": ["What time is it", "Tell me the time", "What's the current time"],
        "responses": ["The current time is {}."]
    }
]

# Create the vectorizer and classifier
vectorizer = TfidfVectorizer()
clf = LogisticRegression(random_state=0, max_iter=10000)

# Preprocess the data
tags = []
patterns = []
for intent in intents:
    for pattern in intent['patterns']:
        tags.append(intent['tag'])
        patterns.append(pattern)

# Training the model
x = vectorizer.fit_transform(patterns)
y = tags
clf.fit(x, y)

def chatbot(input_text):
    input_text = vectorizer.transform([input_text])
    tag = clf.predict(input_text)[0]
    for intent in intents:
        if intent['tag'] == tag:
            if tag == "time":
                current_time = get_current_time()
                response = intent['responses'][0].format(current_time)
            else:
                response = random.choice(intent['responses'])
            return response
    return "I'm not sure I understand. Could you please rephrase that?"
def get_weather():
    api_key = "06d3bc87e14dd7a8da3cf6d542828696"  # Replace with your actual API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = "Safi"  # Replace with the name of your city, e.g., "London"
    complete_url = base_url + "q=" + city_name + "&appid=" + api_key + "&units=metric"  # Added units=metric for Celsius temperature
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        weather_description = data["weather"][0]["description"]
        temperature = main["temp"]
        return f"The weather in {city_name} is {weather_description} with a temperature of {temperature}°C."
    else:
        return "I couldn't get the weather details right now."

def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def main():
    if 'responses' not in st.session_state:
        st.session_state.responses = []

    st.markdown("""
    <style>
        .text-input {
            border-radius: 8px;
            border: 2px solid #007bff;
            padding: 10px;
            font-size: 16px;
            width: 100%;
            box-sizing: border-box;
        }
        .user-message {
            background-color: #007bff;
            color: white;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .chatbot-message {
            background-color: #f1f1f1;
            color: #333;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .download-button {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .clear-button {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }
        .message-time {
            font-size: 0.8em;
            color: #666;
            margin-top: 5px;
        }
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Chatbot")

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    def on_enter():
        user_message = st.session_state["user_input"]
        if user_message:
            current_time = get_current_time()
            st.session_state.responses.append({"text": user_message, "type": "user", "time": current_time})
            if "weather" in user_message.lower():
                bot_response = get_weather()
            else:
                bot_response = chatbot(user_message)
            st.session_state.responses.append({"text": bot_response, "type": "bot", "time": current_time})
            st.session_state["user_input"] = ""

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    user_input = st.text_input(
        "You: ",
        key="user_input",
        placeholder="Type your message here and press Enter...",
        on_change=on_enter
    )

    for message in st.session_state.responses:
        if message["type"] == "user":
            st.markdown(f'<div class="user-message">{message["text"]}<div class="message-time">{message["time"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chatbot-message">{message["text"]}<div class="message-time">{message["time"]}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Download Chat History", key="download_button"):
            chat_history = "\n".join([f'{msg["type"].capitalize()}: {msg["text"]} ({msg["time"]})' for msg in st.session_state.responses])
            st.download_button("Download", chat_history, file_name="chat_history.txt", mime="text/plain", key="download")
            
    with col2:
        if st.button("Clear Chat History", key="clear_button"):
            st.session_state.responses = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
