import socket
import ftplib
import yagmail
import time
import pandas as pd
from attack_prediction import intrusionPrediction
from datetime import datetime
from io import BytesIO


print("-------------------------------------")

ip_address = socket.gethostbyname(socket.gethostname())
port = 5011

print("[STARTED]  > Server running at : ", ip_address, " ", port)

print()

s = socket.socket()
s.bind((ip_address, port))
s.listen(5)

print("[LISTENING] > Waiting for connection ..")


def insert_into_excel(file, address, res, pro):
    date = datetime.today()
    r2 = pd.read_excel(file)
    new_row = [date, address, res, pro]
    r2.loc[-1] = new_row
    r2 = r2.reset_index(drop=True)
    r2.to_excel(file, index=False)


def check_ip_address(ip):
    r1 = pd.read_excel('responsive_blocked_ip.xlsx')
    flag = False
    for index, row in r1.iterrows():
        if row["IP_ADDRESS"] == str(ip):
            flag = True
    return flag


def sendmail(user_mail, result, p_score, attachment_path):
    try:
        yag = yagmail.SMTP(user='richard.james.data@gmail.com',
                           password='czincablcjrzucce')
        yag.send(to=user_mail, subject=f" {result} Attack Detected.",
                 contents=f" {result} Attack Detected with Probability score {p_score} Add content.\n\n",
                 attachments=attachment_path)
        
        print('[SUCCESS]  > Email sent successfully...')
        return "success"
    except Exception as e:
        print('[FAILED]    >', e)
        return "failed"


while True:
    c, addr = s.accept()
    client_ip = addr[0]
    checking = check_ip_address(client_ip)
    if not checking:
        print()
        print('[CONNECTED]  > Connection got from ' + str(client_ip))
        print()

        msg = "share your email id !!"
        c.send(msg.encode("utf-8"))
        print('')
        print('[MESSAGE SENT]   >', msg)

        email = c.recv(1024)
        email_id = email.decode("utf-8")
        print('')
        print('[MESSAGE RECEIVED]', email_id)

        msg = "Hello... send the packet"
        c.send(msg.encode("utf-8"))
        print("[MESSAGE SENT] > ", msg)
        print('')

        msg = c.recv(20480)
        
        # Convert byte data to a file-like object
        file_like = BytesIO(msg)
        
        # Read the file into a DataFrame
        df = pd.read_excel(file_like)

        # Read the file into a DataFrame
        df = pd.read_excel(file_like)
        
        # Save the DataFrame to an Excel file
        df.to_excel('in_folder/test.xlsx', index=False)
        print("[MESSAGE RECEIVED] >  file writing")
        print(" ")
        time.sleep(20)

        excel_path = 'in_folder/test.xlsx'

        print("excel_path", excel_path)

        print("[MODEL PREDICTION] > Predicting...")

        result_ = intrusionPrediction(excel_path)
        
        
        result = result_[0]
        p_score = result_[1]
        # pro_score = "Nope"
        pro_score = "{:.2f}%".format(p_score * 100)
        print("result : ", result)

        insert_into_excel('ip_log.xlsx', client_ip, result, pro_score)
        print("[MODEL PREDICTED RESULT] > ", result)

        if result != 'BENIGN':
            insert_into_excel(
                'responsive_blocked_ip.xlsx', client_ip, result, pro_score)

            print('')
            print('[SENDING]  >  File Sending to', email_id)
            mail = sendmail(email_id, result, p_score, excel_path)
            msg = ''
            if mail == "success":
                msg = "File sent to " + email_id
            else:
                msg = "Opps!! File sending failed to " + email_id

            c.send(msg.encode("utf-8"))

            print('-----------------------------------------')
            print("[LISTENING] Waiting for new connection ..")

        else:
            msg = "Opps!! Something went wrong"
            c.send(msg.encode("utf-8"))
            c.close()
            print('-----------------------------------------')
            print("[LISTENING] Waiting for new connection ..")

    else:
        print("[WARNING] Blocked Client Found....")
        c.close()
        print('-----------------------------------------')
        print("[LISTENING] Waiting for new connection ..")
