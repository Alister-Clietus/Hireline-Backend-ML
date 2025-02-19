from flask import Flask, request, jsonify
from transformers import pipeline
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Load a pre-trained model (e.g., GPT-2 or any other model)
chatbot = pipeline("text-generation", model="gpt2")

@app.route('/chat', methods=['POST'])
def chat():
    # Get user input from the request
    user_input = request.json.get('message')

    # Generate a response using the pre-trained model
    response = chatbot(user_input, max_length=50, num_return_sequences=1)

    # Extract the generated text
    bot_response = response[0]['generated_text']

    # Return the response as JSON
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True,port=5099)