from imapclient import IMAPClient
from backports import ssl
from email.header import  Header, decode_header, make_header
from socketIO_client import SocketIO

import email, imapclient, threading, time,datetime, json, mydb
import paho.mqtt.client as mqtt

def request_to_worker(data):
    global call_method, io

    method = list(data["request"].keys())[0]

    try:
        call_method[method](data["master"], data["request"][method])

    except:
        print("Have no method or Error in this method ")
        io.emit("message", "worker have no '%s' method.Or Error in this method" %method)

def email_check(master,data):
    global io
    context = imapclient.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    user_email = list(data.keys())[0]
    user_password = data[user_email]

    index = user_email.find("@")
    host = "imap." + user_email[index+1:]

    try:
        server = IMAPClient(host, use_uid = True, ssl = True, ssl_context = context)

    except :
        print("Error of 'host' or 'ssl_context'. Check please!")

    responses = dict()
    responses["master"] = master
    responses["responses"] = { "responses_email_check" : user_email }

    try:
        server.login(user_email,user_password)
        print("Login success--'%s'" %user_email)
        io.emit("message", "login success")

        try:
            if mydb.email_exist(master, user_email) == False:
                mydb.add_email(master, user_email, user_password)
                responses["success"] = True
                print("Add new email")
            else:
                responses["success"] = False
                print("Already exists")

        except:
            print("Error in 'email_exist' or 'add_email' in mydb.py")
            responses["success"] = False


    except:
        responses["success"] = False
        io.emit("message", "login fail")

    io.emit("to-master", responses)


class Sensor(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.io = socket

    def on_connect(self, client, userdata, flag, rc) :
        print("Connected with result coe " + str(rc))
        print(str(flag))
        client.subscribe("#", 0)

    def on_message(self, client, userdata, msg):
        Iot_Sensor = mydb.Sensor_Table(mydb.get_db())

        now = datetime.datetime.now().replace(microsecond = 0)
        msg.payload = msg.payload.decode("utf-8")
        dict = json.loads(msg.payload)
        iot_topic = "iot_" + dict["place"].replace("/","_") + "_"

        print("Topic: " + msg.topic + '\nMessage: ' + msg.payload)

        for name in dict["value"].keys():
            iot_name = iot_topic + name
            if Iot_Sensor.table_check(iot_name) == False:
                check_table = False
                print("%s table does not exists" % iot_name)
                Iot_Sensor.table_create(iot_name)
                Iot_Sensor.inspectdb()

            Iot_Sensor.insert_data(iot_name, dict["value"][name])
            print(iot_name + " " + str(dict["value"][name]) + " " + str(now))

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.0.13", 1883, 60)
        self.client.loop_forever()

class Mail(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.io = socket
        self.context = imapclient.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE
        #context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

        self.server = IMAPClient('imap.gmail.com', use_uid = True, ssl = True, ssl_context = self.context)
        self.server.login('email_account', 'email_password')
        self.select_info = self.server.select_folder('INBOX')
        self.server.idle()

    def run(self):
        start = time.time()
        while 1:
            self.responses = self.server.idle_check(1200)
            if not self.responses :
                print(self.responses)
            self.server.idle_done()
            self.server.idle()

print(datetime.datetime.now())
print("Worker starts work!")

global call_method
call_method = globals()

#mail_1 = Mail(io)
#mail_1.start()

#sensor = Sensor(io)
#sensor.start()
global io
io = SocketIO('localhost', 8080)
io.emit("connected", "Worker")
io.on("Worker", request_to_worker)

io.wait()
