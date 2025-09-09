from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import requests

app = Flask(__name__)

# --- HARDCODED API KEYS (for demonstration only) ---
OPENAI_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyBOi6ArE0_4BnR9wVFd61Kt-xLWC9nhUOs"
GROK_API_KEY = "your_grok_api_key_here"
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()
        if username in users:
            return "<h2 style='color:red; text-align:center;'>User already exists ❌</h2>"
        users[username] = password
        save_users(users)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = load_users()
        if username in users and users[username] == password:
            return f'''
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                    <div style="background: #e0ffe0; border-radius: 10px; padding: 40px 60px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); text-align: center;">
                        <h2 style="color: green; margin-bottom: 10px;">Successful Login</h2>
                        <h3 style="color: #222;">Welcome {username}</h3>
                    </div>
                </div>
                <script>
                    setTimeout(function() {{
                        window.location.href = "/chatbot";
                    }}, 2000);
                </script>
            '''.replace('{{', '{').replace('}}', '}')
        else:
            return "<h2 style='color:red; text-align:center;'>Invalid credentials ❌</h2>"
    return render_template('login.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot/<bot_name>')
def chatbot_ui(bot_name):
    if bot_name not in ['chatgpt', 'gemini', 'grok', 'deepseek']:
        return "Chatbot not found", 404
    return render_template(f'chat_{bot_name}.html')

@app.route('/api/chat/<bot_name>', methods=['POST'])
def chat_api(bot_name):
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    if bot_name == 'chatgpt':
        response = chat_with_chatgpt(user_message)
    elif bot_name == 'gemini':
        response = chat_with_gemini(user_message)
    elif bot_name == 'grok':
        response = chat_with_grok(user_message)
    elif bot_name == 'deepseek':
        response = chat_with_deepseek(user_message)
    else:
        return jsonify({'error': 'Invalid chatbot'}), 400

    return jsonify({'response': response})

def chat_with_chatgpt(message):
    api_key = OPENAI_API_KEY
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def chat_with_gemini(message):
    api_key = GEMINI_API_KEY
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": message}]}]
    }
    params = {"key": api_key}
    try:
        response = requests.post(url, headers=headers, params=params, json=data, timeout=15)
        if response.status_code == 200:
            candidates = response.json().get("candidates", [])
            if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
                return candidates[0]["content"]["parts"][0].get("text", "").strip()
            else:
                return "Gemini: No response."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def chat_with_grok(message):
    api_key = GROK_API_KEY
    # Placeholder: Replace with real Grok API call when available
    return "Grok says: (replace with real API call)"

def chat_with_deepseek(message):
    api_key = DEEPSEEK_API_KEY
    # Placeholder: Replace with real DeepSeek API call when available
    return "DeepSeek says: (replace with real API call)"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)