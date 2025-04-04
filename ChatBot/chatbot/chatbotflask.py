from flask import Flask, request, jsonify
import io
import random
import string
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import WordNetLemmatizer
from flask_cors import CORS

nltk.download('popular', quiet=True)
nltk.download('punkt')
nltk.download('wordnet')

from additional_responses import ADDITIONAL_RESPONSES

app = Flask(__name__)
CORS(app)

# Reading in the corpus
with open('chatbot.txt', 'r', encoding='utf8', errors='ignore') as fin:
    raw = fin.read().lower()

# Tokenization
sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)

# Preprocessing
lemmer = WordNetLemmatizer()


def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]


remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)


def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


# Keyword Matching
GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]


def greeting(sentence):
    """if user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def handle_software_developer(user_response):
    """Handles all software developer-related responses."""
    if user_response == "software developer":
        return {
            "response": "Let's talk about software development!",
            "response_array": [
                "SWE: What does a software developer do?",
                "SWE: How to become a software developer?",
                "SWE: Top programming languages for software developers",
                "SWE: Resources to learn software development"
            ]
        }

    if user_response == "swe: what does a software developer do?":
        return {"response": "A software developer designs, builds, and maintains software applications to solve problems or meet user needs."}

    if user_response == "swe: how to become a software developer?":
        return {"response": "To become a software developer, learn programming languages like Python or Java, build projects, and consider earning a degree or certifications."}

    if user_response == "swe: top programming languages for software developers":
        return {"response": "Top programming languages include Python, JavaScript, Java, C#, and C++."}

    if user_response == "swe: resources to learn software development":
        return {"response": "Great resources include freeCodeCamp, Codecademy, Coursera, and YouTube channels like 'Traversy Media' and 'The Net Ninja'."}

    return None  # Return None if the user response is not related to software development

# Response function
def handle_cybersecurity(user_response):
    """Handles all cybersecurity-related responses."""
    if user_response == "cybersecurity":
        return {
            "response": "Let's talk about cybersecurity!",
            "response_array": [
                "Cyb: What is cybersecurity?",
                "Cyb: How to prepare for Cyber Security?",
                "Cyb: YouTube videos for cybersecurity",
                "Cyb: Important topics for cybersecurity"
            ]
        }

    if user_response == "cyb: what is cybersecurity?":
        return {
            "response": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks.",
            "response_array": [
                "Types of cybersecurity:",
                "- Network Security",
                "- Application Security",
                "- Information Security",
                "- Operational Security",
                "- Disaster Recovery and Business Continuity",
                "- End-user Education"
            ]
        }

    if user_response == "cyb: how to prepare for cyber security?":
        return {
            "response": "To prepare for cybersecurity, start by learning the basics of networking, operating systems, and security principles. Certifications like CompTIA Security+ can also help.",
            "response_array": [
                "Do you want YouTube videos?",
                "Do you want pentesting websites?",
                "Do you want book recommendations?",
                "Do you want online courses?"
            ]
        }

    if user_response == "cyb: youtube videos for cybersecurity":
        return {
            "response": "You can find great cybersecurity tutorials on YouTube channels like 'NetworkChuck', 'The Cyber Mentor', and 'HackerSploit'.",
            "response_array": [
                "Do you want beginner-friendly videos?",
                "Do you want advanced tutorials?",
                "Do you want ethical hacking content?"
            ]
        }

    if user_response == "cyb: important topics for cybersecurity":
        return {
            "response": "Important topics include network security, cryptography, ethical hacking, malware analysis, and incident response.",
            "response_array": [
                "Do you want resources for network security?",
                "Do you want resources for cryptography?",
                "Do you want resources for ethical hacking?",
                "Do you want resources for malware analysis?"
            ]
        }

    return None  # Return None if the user response is not related to cybersecurity


# Response function
def response(user_response):
    robo_response = ''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english', token_pattern=None)
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if req_tfidf == 0:
        robo_response = "I am sorry, I don't understand you."
    else:
        robo_response = sent_tokens[idx]

    if user_response in ADDITIONAL_RESPONSES:
        robo_response = ADDITIONAL_RESPONSES[user_response]

    sent_tokens.remove(user_response)

    # Handle cybersecurity-related responses
    cybersecurity_response = handle_cybersecurity(user_response)
    if cybersecurity_response:
        return cybersecurity_response

    # Add special response for "software developer"
    if user_response == "software developer":
        return {    
            "response": robo_response,
            "response_array": [
                "SWE: What does a software developer do?",
                "SWE: How to become a software developer?",
                "SWE: Top programming languages for software developers",
                "SWE: Resources to learn software development"
            ]
        }

    return {"response": robo_response}


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_response = data.get("message", "").lower()
    print(user_response)
    # Handle "bye" message
    if user_response == 'bye':
        return jsonify({"response": "Goodbye! Feel free to come back if you have more questions."})

    # Handle "thanks" or "thank you" message
    if user_response in ('thanks', 'thank you'):
        return jsonify({"response": "You're welcome."})

    # Handle greetings
    if greeting(user_response) is not None:
        return jsonify({"response": greeting(user_response)})
    print("Response")
    print(user_response[:4])

    if user_response[:4] == "cyb:":
        print("Data is being send to handle_cybersecurity")
        print(user_response)
        cybersecurity_response = handle_cybersecurity(user_response)
        if cybersecurity_response:
            return jsonify(cybersecurity_response)
        # Handle messages starting with "SWE:"

    if user_response[:4] == "swe:":
        print("Data is being sent to handle_software_developer")
        software_developer_response = handle_software_developer(user_response)
        if software_developer_response:
            return jsonify(software_developer_response)

    # Default response
    return jsonify(response(user_response))


if __name__ == '__main__':
    app.run(debug=True, port=5099)