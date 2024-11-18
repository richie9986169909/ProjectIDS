from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import pandas as pd
import socket
import sys

app = Flask(__name__)
app.secret_key = 'fogids'

port = 5011


class Client:
    def __init__(self, ip):
        self.content = None
        self.ip = ip
        self.port = port

    def send_file(self, file):
        self.content = file.read()
        return self.content

    def connect(self, selected_file, email):
        try:
            s = socket.socket()
            s.connect((self.ip, self.port))
            print("Connected to server")

            s.recv(1024)

            s.send(email.encode("utf-8"))
            print("Email sent")

            s.recv(1024)

            content = self.send_file(selected_file)
            # print("content ; ", content)
            s.send(content)
            print("File content sent")

            s.recv(2048)

            s.close()

        except Exception as e:
            print("[ERROR] Oops something went wrong, check below error message")
            print("[ERROR MESSAGE] ", e)


@app.route('/client')
def client():
    print("click on client index")
    return render_template('client.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        try:
            ip = request.form['ip']
            email = request.form['email']
            selected_file = request.files['option']
            print("selected_file : ", selected_file)

            client = Client(ip)
            client.connect(selected_file, email)

            print("Successfully Shared.")

            message = "File Shared Successfully."
        except Exception as e:
            print("An error occurred:", str(e))
            message = "Error occurred while sharing file."

        return render_template('client.html', msg=message)
    return render_template('client.html')

# frontend---------------------------------------------------------------------


@app.route("/home")
def home():
    return render_template("client.html")


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["password"]
        r1 = pd.read_excel('user.xlsx')
        for index, row in r1.iterrows():
            if row["email"] == str(email) and row["password"] == str(pwd):

                return redirect(url_for('home'))
        else:
            msg = 'Invalid Login Try Again'
            return render_template('login.html', msg=msg)
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['a_name']
        email = request.form['a_email']
        password = request.form['a_password']
        col_list = ["name", "email", "password"]
        r1 = pd.read_excel('user.xlsx', usecols=col_list)
        new_row = {'name': name, 'email': email, 'password': password}
        r1 = r1.append(new_row, ignore_index=True)
        r1.to_excel('user.xlsx', index=False)
        print("Records created successfully")
        # msg = 'Entered Mail ID Already Existed'
        msg = 'Registration Successfull !! U Can login Here !!!'
        return render_template('login.html', msg=msg)
    return render_template('register.html')


@app.route('/password', methods=['POST', 'GET'])
def password():
    if request.method == 'POST':
        email = request.form['a_email']
        current_pass = request.form['currentpsd']
        new_pass = request.form['newpsd']
        verify_pass = request.form['reenterpsd']

        if not email or not current_pass or not new_pass or not verify_pass:
            msg = 'Please fill in all fields'
            return render_template('password.html', msg=msg)

        r1 = pd.read_excel('user.xlsx')

        for index, row in r1.iterrows():
            if row["password"] == str(current_pass):
                if new_pass == verify_pass:
                    # Hash and store the new password securely in a real-world application
                    r1.loc[index, "password"] = str(verify_pass)
                    r1.to_excel("user.xlsx", index=False)
                    msg = 'Password changed successfully'
                    return render_template('changepsd.html', msg=msg)
                else:
                    msg = 'Re-entered password does not match'
                    return render_template('changepsd.html', msg=msg)

        msg = 'Incorrect email or password'
        return render_template('changepsd.html', msg=msg)

    return render_template('changepsd.html')


@app.route("/graphs")
def graphs():
    return render_template("graphs.html")


def read_excel(file):
    df = pd.read_excel(file)
    cols = list(df.columns)
    df1 = np.asarray(df)
    length = len(df1)
    df2 = []
    count = length
    for i in range(length):
        df2.append(df1[count - 1])
        count -= 1
    print("df2: ", df2)
    return cols, df2


@app.route("/all_ip", methods=['GET', 'POST'])
def all_ip():
    data = read_excel('D:/Project_IDS/server/ip_log.xlsx')
    all_title = "List of All Clients"
    all_ip_delete_btn = "Delete All IP's"
    return render_template("index.html", a_t=all_title, cols=data[0], values=data[1], aidb=all_ip_delete_btn)


@app.route("/clear_data", methods=['GET', 'POST'])
def clear_data():
    df1 = pd.read_excel('D:/Project_IDS/server/ip_log.xlsx')
    df1.drop(df1.index, inplace=True)
    df1.to_excel(
        'D:/Project_IDS/server/ip_log.xlsx', index=False)
    return redirect(url_for('all_ip'))

@app.route("/block_ip", methods=['GET', 'POST'])
def block_ip():
    data = read_excel(
        'D:/Project_IDS/server/responsive_blocked_ip.xlsx')
    d_title = "List of All Blocked Clients"
    b_ip_delete_btn = "Delete Blocked IP's"
    return render_template("index.html", d_t=d_title, cols=data[0], values=data[1], bidb=b_ip_delete_btn)


@app.route("/clear_block_data", methods=['GET', 'POST'])
def clear_block_data():
    df1 = pd.read_excel(
        'D:/Project_IDS/server/responsive_blocked_ip.xlsx')
    df1.drop(df1.index, inplace=True)
    df1.to_excel(
        'D:/Project_IDS/server/responsive_blocked_ip.xlsx', index=False)
    return redirect(url_for('block_ip'))

if __name__ == '__main__':
    app.run(debug=True, port=4890, host='0.0.0.0')
