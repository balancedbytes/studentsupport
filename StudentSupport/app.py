from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
from werkzeug.security import check_password_hash
from dotenv import load_dotenv 
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

app.secret_key = os.urandom(24)


genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')



db_path = os.path.join(os.path.dirname(__file__), 'LoginData.db')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    user = cursor.execute("SELECT * FROM USERS WHERE email=?", (email,)).fetchone()
    connection.close()

    if user and check_password_hash(user[3], password):
        session['fname'] = user[0]
        session['lname'] = user[1]
        session['email'] = user[2]
        return redirect('/home')
    else:
        return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/home')
def home():
    fname = session.get('fname')
    lname = session.get('lname')
    if not fname or not lname:
        return "You are not logged in. <a href='/'>Go to login</a>"
    return render_template('home.html', fname=fname, lname=lname)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/next_steps')
def next_steps():
    return render_template('checklist.html')

@app.route('/nicosia')
def nicosia():
    return render_template('nicosia.html')

@app.route('/housing')
def housing():
    return render_template('housing.html')


@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/save_preferences', methods=['POST'])
def save_preferences():
    email = session.get('email')
    if not email:
        return "Not logged in", 403

    cleanliness = request.form.get('cleanliness')
    study_habits = request.form.get('study_habits')
    sleep_schedule = request.form.get('sleep_schedule')
    social_habits = request.form.get('social_habits')
    noise_tolerance = request.form.get('noise_tolerance')
    guests = request.form.get('guests')
    smoking_drinking = request.form.get('smoking_drinking')

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO ROOMMATE_PREFERENCES
        (email, cleanliness, study_habits, sleep_schedule, social_habits, noise_tolerance, guests, smoking_drinking)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, cleanliness, study_habits, sleep_schedule, social_habits, noise_tolerance, guests, smoking_drinking))
    connection.commit()
    connection.close()

    return redirect('/housing')

@app.route('/roommate_results')
def roommate_results():
    email = session.get('email')
    if not email:
        return "Not logged in", 403

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM ROOMMATE_PREFERENCES WHERE email=?", (email,))
    my_prefs = cursor.fetchone()

    if not my_prefs:
        connection.close()
        return "Please fill out your preferences first. <a href='/housing'>Go to Housing</a>"

    cursor.execute("""
        SELECT u.first_name, u.last_name, u.email, u.avatar_seed, u.age, u.country,
            r.cleanliness, r.study_habits, r.sleep_schedule, 
            r.social_habits, r.noise_tolerance, r.guests, r.smoking_drinking
        FROM USERS u
        JOIN ROOMMATE_PREFERENCES r ON u.email = r.email
        WHERE u.email != ?
    """, (email,))
    roommates = cursor.fetchall()

    results = []
    for rm in roommates:
        score = 0
        for i in range(1, len(my_prefs)):
            if my_prefs[i] == rm[i+5]:
                score += 1
        results.append((rm[0], rm[1], rm[2], rm[3], rm[4], rm[5], score))

    results.sort(key=lambda x: x[6], reverse=True)

    connection.close()
    return render_template('roommate_results.html', roommates=results)

@app.route('/chat/<other_email>')
def chat(other_email):
    email = session.get('email')
    if not email:
        return redirect('/')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("SELECT email, first_name, last_name FROM USERS WHERE email=?", (other_email,))
    other = cursor.fetchone()
    if not other:
        connection.close()
        return "User not found", 404
    cursor.execute("SELECT first_name, last_name FROM USERS WHERE email=?", (email,))
    me = cursor.fetchone()
    connection.close()
    me_name = f"{me[0]} {me[1]}" if me and me[0] else email
    other_name = f"{other[1]} {other[2]}" if other[1] else other[0]
    return render_template('chat.html', other_email=other_email, other_name=other_name, current_email=email, current_name=me_name)

@app.route('/messages/<other_email>')
def get_messages(other_email):
    email = session.get('email')
    if not email:
        return jsonify({"error": "not logged in"}), 403
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT sender, receiver, content, timestamp FROM MESSAGES
        WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
        ORDER BY timestamp ASC
    """, (email, other_email, other_email, email))
    msgs = cursor.fetchall()
    connection.close()
    messages = [{"sender": m[0], "receiver": m[1], "content": m[2], "timestamp": m[3]} for m in msgs]
    return jsonify(messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    email = session.get('email')
    if not email:
        return jsonify({"error": "not logged in"}), 403
    receiver = request.form.get('receiver') or (request.json and request.json.get('receiver'))
    content = request.form.get('content') or (request.json and request.json.get('content'))
    if not receiver or not content:
        return jsonify({"error": "missing fields"}), 400
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO MESSAGES (sender, receiver, content) VALUES (?, ?, ?)", (email, receiver, content))
    connection.commit()
    connection.close()
    return jsonify({"status": "ok"})


@app.route('/chat_ai', methods=['POST'])
def chat_ai():
    email = session.get('email')
    if not email:
        return jsonify({'error': 'Not logged in'}), 403
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        context = """You are a helpful AI assistant for Near East University (NEU) students. 
        Answer questions politely and concisely about academics, campus life, and student services. 
        If you don't know something specific about NEU, say so and provide general helpful advice."""
        
        response = model.generate_content(context + "\n\nStudent question: " + user_message)
        
        return jsonify({
            'response': response.text,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return jsonify({'error': 'Sorry, I encountered an error. Please try again.'}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
