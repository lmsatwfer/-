from flask import Flask, request, jsonify, render_template
import sqlite3
import os
import smtplib
import ssl

app = Flask(__name__)

DATABASE = "data.db"

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS consumption_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                username TEXT,
                password TEXT,
                email TEXT,
                current_energy REAL,
                current_water REAL,
                daily_water REAL,
                daily_energy REAL,
                monthly_water REAL,
                monthly_energy REAL,
                daily_avg_water REAL,
                daily_avg_energy REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                electricity_state TEXT DEFAULT 'ON',
                water_state TEXT DEFAULT 'ON'
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()

    device_id = data.get("device_id")
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    current_energy = data.get("current_energy")
    current_water = data.get("current_water")
    daily_water = data.get("daily_water")
    daily_energy = data.get("daily_energy")
    monthly_water = data.get("monthly_water")
    monthly_energy = data.get("monthly_energy")
    daily_avg_water = data.get("daily_avg_water")
    daily_avg_energy = data.get("daily_avg_energy")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(''' 
        INSERT INTO consumption_data (device_id, username, password, email, current_energy, current_water, 
            daily_water, daily_energy, monthly_water, monthly_energy, daily_avg_water, daily_avg_energy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (device_id, username, password, email, current_energy, current_water, daily_water, daily_energy, 
          monthly_water, monthly_energy, daily_avg_water, daily_avg_energy))
    conn.commit()
    conn.close()

    send_email()

    return jsonify({"status": "success", "message": "Data received and saved"}), 200

def send_email():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM consumption_data ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        daily_energy = row[8] 
        daily_water = row[7] 
        email = row[4]  
        
        if daily_energy > 100:  #تعديل
            subject = "تحذير استهلاك كهرباء مرتفع"
            body = f"تحذير! استهلاك الطاقة اليومي هو {daily_energy} كيلووات وهو مرتفع."
            message = f"Subject: {subject}\n\n{body}"

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_sender, email_pasw)
                server.sendmail(email_sender, email, message)

        if daily_water > 13725.83:  
            subject = "تحذير استهلاك ماء مرتفع"
            body = f"تحذير! استهلاك الماء اليومي هو {daily_water} لتر وهو مرتفع."
            message = f"Subject: {subject}\n\n{body}"

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(email_sender, email_pasw)
                server.sendmail(email_sender, email, message)

@app.route('/update_state', methods=['POST'])
def update_state():
    data = request.get_json()
    electricity_state = data.get("electricity_state", "ON")
    water_state = data.get("water_state", "ON")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(''' 
        UPDATE consumption_data 
        SET electricity_state = ?, water_state = ? 
        WHERE id = (SELECT MAX(id) FROM consumption_data)
    ''', (electricity_state, water_state))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "State updated successfully"}), 200

email_sender = "lmsatwfer@gmail.com"
email_pasw = "hwfw bvay ciwl pyvn"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
