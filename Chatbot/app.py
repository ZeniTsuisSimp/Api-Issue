from flask import Flask, render_template, request, jsonify, session
import google.cloud.dialogflow_v2 as dialogflow

import os

app = Flask(__name__,
            template_folder='template',
            static_folder='static')

# Set a secret key to use Flask session
app.secret_key = 'your-secure-secret-key'

# Set your Google Cloud API key JSON file path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\AMAN\Downloads\gen-lang-client-0686806593-4598614b122d.json'

# Dialogflow project ID (replace with your actual project ID)
DIALOGFLOW_PROJECT_ID = 'gen-lang-client-0686806593'
DIALOGFLOW_LANGUAGE_CODE = 'en'  # Change this to your preferred language code
SESSION_ID = 'current-user-session'  # You can use session id dynamically

@app.route("/")
def index():
    # Initialize conversation memory in session if not already initialized
    if 'conversation' not in session:
        session['conversation'] = []  # Empty list to store conversation history
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]  # Get the message from the form

    # Store user's message in the session conversation history
    session['conversation'].append({'role': 'user', 'content': msg})

    # Get chat response using Dialogflow API
    response = get_chat_response(msg)

    # Append the response to the conversation history
    session['conversation'].append({'role': 'assistant', 'content': response})

    return jsonify({"response": response})  # Return JSON response

def get_chat_response(text_input):
    try:
        # Set up the Dialogflow client
        session_client = dialogflow.SessionsClient()
        dialogflow_session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)


        # Create a text input query
        text_input_query = dialogflow.types.TextInput(
            text=text_input, language_code=DIALOGFLOW_LANGUAGE_CODE)

        # Build the query input
        query_input = dialogflow.types.QueryInput(text=text_input_query)

        # Send the query to Dialogflow
        response = session_client.detect_intent(session=session, query_input=query_input)

        # Get the response message from Dialogflow
        return response.query_result.fulfillment_text

    except Exception as e:
        return str(e)  # Return error if API call fails

@app.route("/clear", methods=["POST"])
def clear_conversation():
    # Clear the conversation history if user wants to reset the chat
    session.pop('conversation', None)
    return jsonify({"response": "Conversation cleared!"})

if __name__ == '__main__':
    app.run(debug=True)
