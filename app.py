import os
from flask import Flask, render_template, request, redirect , url_for
from flask_mail import Mail, Message # type: ignore
import sqlite3
import hashlib
import random
import string
import ssl

context = ssl.SSLContext(ssl.PROTOCOL_TLS)

currentlocation = os.path.dirname(os.path.abspath(__file__))
db_location = os.path.join(currentlocation, 'Login.db')

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'lab4pirgaricristian@outlook.com'  #mail
app.config['MAIL_PASSWORD'] = '123123qweqwe'  #pass
app.config['MAIL_DEFAULT_SENDER'] = 'lab4pirgaricristian@outlook.com'  #sender

mail = Mail(app)

def generate_temp_password():
    
    length = 10
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@app.route('/')
def home():
    return render_template("main.html")

@app.route('/login',  methods=['POST', 'GET'])
def login():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sqlconnection = sqlite3.connect(db_location)
        cursor = sqlconnection.cursor()
        query1 = "SELECT Username, Password, Temp_Password FROM Users WHERE Username = ? AND Password = ?"
        cursor.execute(query1, (username, hashlib.md5(password.encode()).hexdigest()))

        row = cursor.fetchone()

        if row:
            stored_password = row[1]
            if hashlib.md5(password.encode()).hexdigest() == stored_password or password == row[2]:
                return render_template("LoggedIn.html")
            else:
                return redirect("/register")
        else:
            return redirect("/register")
     else:
        return render_template("login.html")


@app.route("/register" , methods= ["GET" , "POST"])
def registerpage():
    if request.method == "POST":
        dusername = request.form["duser"]
        dpassword = request.form["dpass"]
        Uemail = request.form["EmailUser"]
        hashed_password = hashlib.md5(dpassword.encode()).hexdigest()
        
        


        sqlconnection = sqlite3.connect(db_location)
        cursor = sqlconnection.cursor()
        query1 = "INSERT INTO Users (username, password, email) VALUES (?, ?, ?)"
        cursor.execute(query1, (dusername, hashed_password, Uemail))
        sqlconnection.commit()
        return redirect("/")
    return render_template("Register.html")


@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        temp_password = generate_temp_password()
        try:
            sqlconnection = sqlite3.connect(db_location)
            cursor = sqlconnection.cursor()
            query_update = "UPDATE Users SET temp_password = ? WHERE email = ?"
            cursor.execute(query_update, (temp_password, email))
            sqlconnection.commit()
            sqlconnection.close()
            msg = Message('Parola temporara', recipients=[email])
            msg.body = f'Parola temporara voastra este: {temp_password}'
            mail.send(msg)
            return render_template("forgot_password_success.html")
        except Exception as e:
            return f"Eroare: {str(e)}"

    return render_template("forgot_password.html")
        
if __name__ == '__main__':
    app.run(debug=True)
