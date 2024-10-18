from flask import Flask, render_template, request, jsonify, session
from google.cloud import dialogflow_v2 as dialogflow
import os
# from dotenv import loadenv
import uuid
import google.generativeai as genai

api_key = "AIzaSyCC8w3fxJw3txacXivVYoYNlDbGmupkL44"

genai.configure(api_key=api_key)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

history = []

app = Flask(__name__, template_folder='template', static_folder='static')

@app.route("/")
def index():
    if 'conversation' not in session:
        session['conversation'] = []
        session['session_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    session['conversation'].append({'role': 'user', 'content': msg})
    response = get_chat_response(msg)
    session['conversation'].append({'role': 'assistant', 'content': response})
    return jsonify({"response": response})

def get_chat_response(text_input):
    try:
        model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        )

        

        chat_session = model.start_chat(
        history=history
        )

        response = chat_session.send_message(text_input)

        if len(history) <= 5:
            history.append({'role': 'user',
                            'content': text_input,
                            'role': 'assistant',
                            'content': response.text})
        else:
            history.pop(0)
            history.append({'role': 'user',
                            'content': text_input,
                            'role': 'assistant',
                            'content': response.text})


        return response.text
    except Exception as e:
        return str(e)

@app.route("/clear", methods=["POST"])
def clear_conversation():
    session.pop('conversation', None)
    session.pop('session_id', None)
    return jsonify({"response": "Conversation cleared!"})

if __name__ == '__main__':
    app.run(debug=True)
